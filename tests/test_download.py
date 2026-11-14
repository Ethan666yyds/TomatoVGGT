import hashlib
import importlib.util
from pathlib import Path
import tempfile
import unittest

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

    def test_owner_token_cannot_be_sent_to_another_host(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);manifest,_=self.fixture(root)
            manifest['record_url']='https://example.invalid/records/123'
            token=root/'token.txt';token.write_text('test-only-token')
            with self.assertRaisesRegex(ValueError,'official HTTPS Zenodo'):
                restore.restore(manifest,root,token_file=token)

if __name__=='__main__':unittest.main()
