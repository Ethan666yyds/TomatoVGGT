"""Download release files and restore exact archives; Python standard library only."""
from concurrent.futures import ThreadPoolExecutor
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import time
from urllib.parse import quote
from urllib.request import Request, urlopen

def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(8*1024*1024),b''):h.update(chunk)
    return h.hexdigest()

def restore(manifest,directory,download=False,workers=4):
    directory.mkdir(parents=True,exist_ok=True)
    headers={'User-Agent':'TomatoVGGT-download/1.0'}
    files={f['file']:f for package in manifest['packages'] for f in package['parts']}
    def verify_or_download(item):
        name,record=item
        if Path(name).name!=name:raise ValueError('Unsafe filename in manifest')
        path=directory/name
        if path.exists() and path.stat().st_size==record['bytes'] and sha(path)==record['sha256']:return
        if not download:raise FileNotFoundError(f'Missing or invalid file: {name}; use --download or download all parts')
        url=manifest['record_url']+'/files/'+quote(name)+'?download=1'
        for attempt in range(4):
            temporary=path.with_suffix(path.suffix+'.partial')
            try:
                with urlopen(Request(url,headers=headers),timeout=120) as source,temporary.open('wb') as target:
                    shutil.copyfileobj(source,target,1024*1024)
                if temporary.stat().st_size!=record['bytes'] or sha(temporary)!=record['sha256']:raise ValueError(f'Download checksum failed: {name}')
                temporary.replace(path);print('Verified',name,flush=True);return
            except Exception:
                if attempt==3:raise
                time.sleep(2)
    with ThreadPoolExecutor(max_workers=workers) as pool:list(pool.map(verify_or_download,files.items()))
    for package in manifest['packages']:
        name=package['file']
        if Path(name).name!=name:raise ValueError('Unsafe archive name')
        target=directory/name
        if len(package['parts'])==1 and package['parts'][0]['file']==name:
            if target.stat().st_size!=package['bytes'] or sha(target)!=package['sha256']:raise ValueError('Archive checksum failed')
            continue
        if target.exists() and target.stat().st_size==package['bytes'] and sha(target)==package['sha256']:
            print('Already restored',name,flush=True);continue
        temporary=target.with_suffix(target.suffix+'.partial');h=hashlib.sha256()
        with temporary.open('wb') as out:
            for part in package['parts']:
                with (directory/part['file']).open('rb') as source:
                    for block in iter(lambda:source.read(8*1024*1024),b''):h.update(block);out.write(block)
        if temporary.stat().st_size!=package['bytes'] or h.hexdigest()!=package['sha256']:raise ValueError(f'Restored checksum failed: {name}')
        temporary.replace(target);print('Restored and verified',name,flush=True)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--manifest',type=Path,default=Path(__file__).with_name('download_manifest.json'))
    p.add_argument('--directory',type=Path,default=Path('.'))
    p.add_argument('--download',action='store_true')
    p.add_argument('--workers',type=int,default=4)
    a=p.parse_args()
    if not 1<=a.workers<=16:raise ValueError('--workers must be between 1 and 16')
    restore(json.loads(a.manifest.read_text()),a.directory,a.download,a.workers)

if __name__=='__main__':main()
