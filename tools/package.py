#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Create versioned vendor assets from curated, checksum-locked local files."""
import argparse,gzip,hashlib,io,json,tarfile
from pathlib import Path,PurePosixPath
r=Path(__file__).resolve().parents[1]
def digest(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for chunk in iter(lambda:f.read(4*1024*1024),b''):h.update(chunk)
 return h.hexdigest()
def encoded(value):return (json.dumps(value,indent=2,ensure_ascii=False)+'\n').encode()
def member(tf,name,data,mode):
 p=PurePosixPath(name)
 if p.is_absolute() or '..' in p.parts:raise ValueError('Invalid archive member')
 ti=tarfile.TarInfo(name);ti.uid=ti.gid=0;ti.mode=mode&0o755;ti.mtime=0;ti.size=len(data);tf.addfile(ti,io.BytesIO(data))
def main():
 p=argparse.ArgumentParser();p.add_argument('--catalog',type=Path,default=r/'devices/a081/catalog.json');p.add_argument('--source-root',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();catalog=json.loads(a.catalog.read_text())
 if a.output.exists() or a.output.is_symlink():p.error('Choose a new output directory')
 # Check the entire source set before generating release assets.
 for bundle in catalog['bundles'].values():
  for entry in bundle['files']:
   src=a.source_root/entry['source_file']
   if src.is_symlink() or not src.is_file() or digest(src)!=entry['sha256']:raise ValueError('Source checksum mismatch: '+entry['source_file'])
 a.output.mkdir(parents=True)
 lock={'schema':1,'repository':'bitsk/qiyu-vendor','visibility':'public','tag':catalog['snapshot'],'model':catalog['model'],'catalog_sha256':digest(a.catalog),'per_device_calibration_included':False,'bundles':{}}
 for name,bundle in catalog['bundles'].items():
  entries=[{k:e[k] for k in ['path','sha256','bytes','mode','install_path']} for e in bundle['files']];asset=catalog['model']+'-'+name+'-'+catalog['snapshot']+'.tar.gz';archive=a.output/asset
  manifest={'schema':1,'model':catalog['model'],'snapshot':catalog['snapshot'],'bundle':name,'files':entries,'device_tested_after_packaging':False}
  with archive.open('wb') as raw:
   with gzip.GzipFile(filename='',mode='wb',fileobj=raw,mtime=0) as gz:
    with tarfile.open(fileobj=gz,mode='w',format=tarfile.PAX_FORMAT) as tf:
     member(tf,'bundle.json',encoded(manifest),0o644)
     for e in bundle['files']:member(tf,e['path'],(a.source_root/e['source_file']).read_bytes(),e['mode'])
  lock['bundles'][name]={'asset':asset,'sha256':digest(archive),'bytes':archive.stat().st_size,'files':entries}
 (a.output/'vendor.lock.json').write_bytes(encoded(lock));(a.output/'SHA256SUMS').write_text(''.join(digest(q)+'  '+q.name+'\n' for q in sorted(a.output.iterdir()) if q.is_file() and q.name!='SHA256SUMS'))
 print(json.dumps({n:{'files':len(x['files']),'archive_bytes':x['bytes'],'sha256':x['sha256']} for n,x in lock['bundles'].items()},indent=2))
if __name__=='__main__':main()
