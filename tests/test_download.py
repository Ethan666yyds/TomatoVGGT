import hashlib
import importlib.util
from io import BytesIO
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

spec=importlib.util.spec_from_file_location('release_restore',Path(__file__).resolve().parents[1]/'restore_archives.py')
restore=importlib.util.module_from_spec(spec)
spec.loader.exec_module(restore)

class DownloadBehaviorTests(unittest.TestCase):
    def fixture(self,root):
        chunks=[b'first\x00binary',b'second\nchunk'];parts=[]
        for i,chunk in enumerate(chunks):
            name=f'archive.zip.part-{i:03d}'
            (root/name).write_bytes(chunk)
            parts.append({'file':name,'bytes':len(chunk),'sha256':hashlib.sha256(chunk).hexdigest()})
        combined=b''.join(chunks)
        return {'packages':[{'file':'archive.zip','bytes':len(combined),'sha256':hashlib.sha256(combined).hexdigest(),'parts':parts}]},combined

    def test_binary_merge_checksum_and_safe_rerun(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);manifest,combined=self.fixture(root)
            restore.restore(manifest,root)
            self.assertEqual((root/'archive.zip').read_bytes(),combined)
            modified=(root/'archive.zip').stat().st_mtime_ns
            restore.restore(manifest,root)
            self.assertEqual((root/'archive.zip').stat().st_mtime_ns,modified)

    def test_corrupt_part_rejected_before_output(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);manifest,_=self.fixture(root)
            (root/'archive.zip.part-000').write_bytes(b'bad')
            with self.assertRaises(FileNotFoundError):restore.restore(manifest,root)
            self.assertFalse((root/'archive.zip').exists())

    def test_public_download_uses_no_authorization_and_restores_exact_bytes(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);manifest,combined=self.fixture(root)
            manifest['record_url']='https://zenodo.org/records/123'
            payloads={part['file']:(root/part['file']).read_bytes()
                      for part in manifest['packages'][0]['parts']}
            for name in payloads:(root/name).unlink()
            requests=[]
            def public_response(request,timeout):
                requests.append(request)
                name=request.full_url.rsplit('/',1)[1].split('?')[0]
                self.assertEqual(request.full_url,
                                 f'https://zenodo.org/records/123/files/{name}?download=1')
                self.assertFalse(request.has_header('Authorization'))
                return BytesIO(payloads[name])
            with patch.object(restore,'urlopen',side_effect=public_response):
                restore.restore(manifest,root,download=True,workers=1)
            self.assertEqual(len(requests),len(payloads))
            self.assertEqual((root/'archive.zip').read_bytes(),combined)

if __name__=='__main__':unittest.main()
