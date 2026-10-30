"""Download verified Release pieces and restore the unchanged model ZIP."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import argparse,hashlib,json,os,re,shutil,stat,tempfile,time,urllib.request,zipfile
from .model_artifact import sha,verify_model

ROOT=Path(__file__).resolve().parents[1]
ASSET_BASE='https://github.com/lfx030617-star/PolyWeave-FS/releases/download/model-dpo-full-seed101-v1.0.0/'

def validate_manifest(manifest):
    if manifest.get('format')!='polyweave_multipart_zip_v1':raise ValueError('Unknown model download format')
    archive=manifest['archive_name'];directory=manifest['model_directory']
    for name in [archive,directory]:
        if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]*',name) or name in ['.','..']:raise ValueError('Unsafe download name')
    if not archive.endswith('.zip') or not re.fullmatch('[0-9a-f]{64}',manifest['archive_sha256']):raise ValueError('Invalid archive identity')
    parts=manifest['parts']
    if not 1<=len(parts)<=32:raise ValueError('Invalid piece count')
    for i,p in enumerate(parts,1):
        if p['name']!=archive+'.part'+str(i).zfill(3) or p['url']!=ASSET_BASE+p['name']:raise ValueError('Unsafe piece path or URL')
        if type(p['bytes']) is not int or not 0<p['bytes']<=128000000 or not re.fullmatch('[0-9a-f]{64}',p['sha256']):raise ValueError('Invalid piece size or checksum')
    if sum(p['bytes'] for p in parts)!=manifest['archive_bytes']:raise ValueError('Piece sizes differ from archive size')
    return manifest

def assemble(manifest,parts_dir,archive):
    validate_manifest(manifest);parts_dir=Path(parts_dir);archive=Path(archive)
    if archive.exists():
        if archive.is_symlink() or archive.stat().st_size!=manifest['archive_bytes'] or sha(archive)!=manifest['archive_sha256']:raise ValueError('Existing archive differs; it will not be overwritten')
        return archive
    archive.parent.mkdir(parents=True,exist_ok=True);temporary=None
    try:
        full=hashlib.sha256()
        with tempfile.NamedTemporaryFile(prefix='model-assemble-',suffix='.partial',dir=archive.parent,delete=False) as out:
            temporary=Path(out.name)
            for p in manifest['parts']:
                f=parts_dir/p['name']
                if f.is_symlink() or not f.is_file() or f.stat().st_size!=p['bytes']:raise ValueError('Missing or changed piece: '+p['name'])
                h=hashlib.sha256()
                with f.open('rb') as source:
                    for b in iter(lambda:source.read(1024*1024),b''):out.write(b);h.update(b);full.update(b)
                if h.hexdigest()!=p['sha256']:raise ValueError('Piece checksum differs: '+p['name'])
        if full.hexdigest()!=manifest['archive_sha256']:raise ValueError('Restored archive checksum differs')
        os.replace(temporary,archive);temporary=None
        return archive
    finally:
        if temporary is not None and temporary.exists():temporary.unlink()

def fetch(part,directory):
    target=directory/part['name']
    if target.exists():
        if not target.is_symlink() and target.stat().st_size==part['bytes'] and sha(target)==part['sha256']:return target
        raise ValueError('Existing piece differs; inspect it before retrying: '+str(target))
    for attempt in range(3):
        temporary=None
        try:
            req=urllib.request.Request(part['url'],headers={'User-Agent':'PolyWeave-FS-model-download/1'})
            with tempfile.NamedTemporaryFile(prefix=part['name']+'.',suffix='.partial',dir=directory,delete=False) as out:
                temporary=Path(out.name);h=hashlib.sha256();size=0
                with urllib.request.urlopen(req,timeout=60) as response:
                    for block in iter(lambda:response.read(1024*1024),b''):
                        size+=len(block)
                        if size>part['bytes']:raise ValueError('Download is larger than expected')
                        out.write(block);h.update(block)
            if size!=part['bytes'] or h.hexdigest()!=part['sha256']:raise ValueError('Download checksum differs: '+part['name'])
            os.replace(temporary,target);temporary=None;print('PIECE_VERIFIED',part['name'],flush=True);return target
        except (OSError,ValueError):
            if attempt==2:raise
            time.sleep(attempt+1)
        finally:
            if temporary is not None and temporary.exists():temporary.unlink()

def main(argv=None):
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--output-dir',type=Path,default=ROOT/'models');ap.add_argument('--workers',type=int,default=4)
    a=ap.parse_args(argv)
    if not 1<=a.workers<=8:ap.error('workers must be 1..8')
    manifest=validate_manifest(json.loads((ROOT/'MODEL_DOWNLOAD.json').read_text()))
    expected=json.loads((ROOT/'MODEL_RELEASE.json').read_text())['expected_identity']
    if manifest['model_directory']!=expected['artifact_name']:raise ValueError('Model/download identity differs')
    output=a.output_dir.resolve()
    if output.is_relative_to(ROOT) and not output.is_relative_to(ROOT/'models'):raise ValueError('Use models/ or an external output directory')
    output.mkdir(parents=True,exist_ok=True);model=output/manifest['model_directory']
    if model.exists():verify_model(model,expected);print('MODEL_ALREADY_VERIFIED',model);return
    archive=output/manifest['archive_name']
    if not archive.exists():
        directory=output/'parts';directory.mkdir(exist_ok=True)
        with ThreadPoolExecutor(max_workers=a.workers) as pool:list(pool.map(lambda p:fetch(p,directory),manifest['parts']))
    else:directory=output/'parts'
    assemble(manifest,directory,archive)
    archive.with_suffix('.zip.sha256').write_text(manifest['archive_sha256']+'  '+archive.name+'\n')
    with tempfile.TemporaryDirectory(prefix='model-extract-',dir=output) as temporary:
        staging=Path(temporary)
        with zipfile.ZipFile(archive) as z:
            for member in z.infolist():
                path=Path(member.filename)
                if path.is_absolute() or len(path.parts)!=2 or path.parts[0]!=manifest['model_directory'] or '..' in path.parts or stat.S_ISLNK(member.external_attr>>16):raise ValueError('Unsafe model archive path')
            z.extractall(staging)
        verify_model(staging/manifest['model_directory'],expected)
        os.replace(staging/manifest['model_directory'],model)
    print('MODEL_DOWNLOAD_COMPLETED',model,flush=True)

if __name__=='__main__':main()
