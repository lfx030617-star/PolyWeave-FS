"""Validate the allowlisted model artifact before loading any weights."""
from pathlib import Path
import hashlib,json,re

def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
    return h.hexdigest()

def verify_model(directory,expected):
    directory=Path(directory).resolve()
    p=directory/'MODEL_MANIFEST.json'
    if not p.is_file() or p.is_symlink():raise ValueError('Missing model export manifest; use the exported fine-tuned checkpoint')
    manifest=json.loads(p.read_text())
    for key in ['artifact_name','arm','scale','training_seed','model_fingerprint','vocab_size']:
        if manifest.get(key)!=expected[key]:raise ValueError('Wrong published model identity: '+key)
    allowed={'config.json','generation_config.json','model.safetensors.index.json','LICENSE','MODEL_CARD.md','NOTICE',*expected['tokenizer_files']}
    names=set();weights=[]
    for entry in manifest['files']:
        name=entry['path'];rel=Path(name)
        if rel.name!=name or rel.is_absolute() or name in names:raise ValueError('Unsafe or duplicate model file path')
        is_weight=bool(re.fullmatch(r'model(?:-\d{5}-of-\d{5})?\.safetensors',name))
        if name not in allowed and not is_weight:raise ValueError('Unexpected model file: '+name)
        f=directory/name
        if not f.is_file() or f.is_symlink() or f.stat().st_size!=entry['bytes']:raise ValueError('Missing/changed model file: '+name)
        h=sha(f)
        if h!=entry['sha256']:raise ValueError('Model checksum differs: '+name)
        if is_weight:weights.append((name,h))
        names.add(name)
    mandatory={'config.json','generation_config.json','LICENSE','MODEL_CARD.md','NOTICE',*expected['tokenizer_files']}
    if not mandatory<=names or not weights:raise ValueError('Model artifact is incomplete')
    actual={p.name for p in directory.iterdir() if not p.name.startswith('._') and p.name!='.DS_Store'}
    if actual!=names|{'MODEL_MANIFEST.json'}:raise ValueError('Unlisted files exist in the model directory')
    if 'model.safetensors.index.json' in names:
        index=json.loads((directory/'model.safetensors.index.json').read_text())
        if set(index['weight_map'].values())!={n for n,_ in weights}:raise ValueError('Weight index does not match the declared shards')
    elif len(weights)!=1 or weights[0][0]!='model.safetensors':raise ValueError('Sharded model needs a matching index')
    fp=hashlib.sha256(json.dumps(sorted(weights),ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    if fp!=expected['model_fingerprint']:raise ValueError('Not the accepted final DPO weights')
    for name,h in {**expected['configuration_files'],**expected['tokenizer_files']}.items():
        if sha(directory/name)!=h:raise ValueError('Configuration/tokenizer identity differs: '+name)
    config=json.loads((directory/'config.json').read_text())
    if config.get('model_type')!='t5' or config.get('vocab_size')!=32115:raise ValueError('Wrong adapted model configuration')
    return manifest
