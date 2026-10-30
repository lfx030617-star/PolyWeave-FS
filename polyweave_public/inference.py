"""Inference-only CLI for the accepted full-data DPO seed101 model."""
from pathlib import Path
import argparse,csv,json,sys
from .evaluator import make_condition,compile_condition,compact,RULES,rdBase,evaluate_candidate,summarize_attempts,stable_hash
from .model_artifact import verify_model

ROOT=Path(__file__).resolve().parents[1]

def prompt_for(condition):
    compile_condition(compact(condition))
    size=condition['heavy_atom_range'] or RULES['pilot_heavy_atom_range']
    return (f"fragment={condition['fragment_smarts']}; ports=2; port_degree=1; port_bond=SINGLE; "
            f"elements=C,H,N,O,S,F,Cl,Br; heavy_atoms={size[0]}:{size[1]}; radicals=0")

def strict_ids(text,tokenizer):
    ids=tokenizer.encode(text,add_special_tokens=True)
    if tokenizer.unk_token_id in ids or len(ids)>256:raise ValueError('Input has unknown tokens or exceeds 256 tokens; truncation is not allowed')
    if tokenizer.decode(ids,skip_special_tokens=True,clean_up_tokenization_spaces=False)!=text:raise ValueError('Tokenizer does not preserve the exact task prompt')
    return ids

def main(argv=None):
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--model-dir',type=Path)
    source=ap.add_mutually_exclusive_group(required=True)
    source.add_argument('--fragment',help='Connected SMARTS query with 4..12 real heavy atoms')
    source.add_argument('--example-index',type=int,help='0..29: use one published condition, without using its target')
    ap.add_argument('--size',help='Optional frozen size bin: 10:19,20:29,30:39,40:59,60:80')
    ap.add_argument('--attempts',type=int,default=20);ap.add_argument('--batch-size',type=int,default=4)
    ap.add_argument('--device',default='auto');ap.add_argument('--decode-seed',type=int,default=20261016)
    ap.add_argument('--output',type=Path,default=ROOT/'results/generated')
    ap.add_argument('--validate-input-only',action='store_true')
    a=ap.parse_args(argv)
    if a.example_index is not None:
        if a.size is not None:ap.error('--size is only used with --fragment')
        from .data import condition_targets
        examples=list(condition_targets())
        if not 0<=a.example_index<len(examples):ap.error('Example index must be 0..29')
        condition=examples[a.example_index]['condition']
    else:
        try:size=[int(v) for v in a.size.split(':')] if a.size else None
        except ValueError:ap.error('Use a size bin such as 40:59')
        condition=make_condition(a.fragment,size)
    text=prompt_for(condition)
    if a.validate_input_only:
        print(json.dumps({'condition':condition,'input_text':text,'model_loaded':False},indent=2));return
    if a.model_dir is None:ap.error('--model-dir is required; the trained checkpoint is not bundled with the source repository')
    if not 1<=a.attempts<=1000 or not 1<=a.batch_size<=32:ap.error('attempts must be 1..1000 and batch-size 1..32')
    if rdBase.rdkitVersion!=RULES['expected_rdkit_version']:raise ValueError('Use the frozen RDKit '+RULES['expected_rdkit_version']+' evaluator')
    expected=json.loads((ROOT/'MODEL_RELEASE.json').read_text())['expected_identity']
    artifact=verify_model(a.model_dir,expected)
    import torch
    from transformers import AutoTokenizer,AutoModelForSeq2SeqLM
    from .sampling import sample_ids,decode
    device='cuda:0' if a.device=='auto' and torch.cuda.is_available() else 'cpu' if a.device=='auto' else a.device
    if device.startswith('cuda') and not torch.cuda.is_available():raise ValueError('Requested accelerator is unavailable')
    tok=AutoTokenizer.from_pretrained(a.model_dir,local_files_only=True,trust_remote_code=False,use_fast=True)
    if len(tok)!=32115:raise ValueError('Use the adapted 32115-vocabulary tokenizer')
    input_ids=strict_ids(text,tok)
    model=AutoModelForSeq2SeqLM.from_pretrained(a.model_dir,local_files_only=True,trust_remote_code=False,attn_implementation='eager')
    if model.config.vocab_size!=32115:raise ValueError('Wrong model vocabulary')
    torch.set_num_threads(4);model.to(device).eval()
    output=a.output.resolve()
    if output.is_relative_to(ROOT) and not output.is_relative_to(ROOT/'results'):raise ValueError('Use results/ or an external output directory, not published source/data directories')
    output.mkdir(parents=True,exist_ok=False)
    records=[]
    for first in range(0,a.attempts,a.batch_size):
        indices=list(range(first,min(first+a.batch_size,a.attempts)))
        seeds=[int(stable_hash('step4-decode',a.decode_seed,101,condition['condition_id'],i)[:15],16) for i in indices]
        x=torch.tensor([input_ids]*len(indices),dtype=torch.long,device=device)
        raw,_=sample_ids(model,x,torch.ones_like(x),seeds,max_new_tokens=256,temperature=1.0,top_p=0.95,top_k=0)
        for i,seed,r in zip(indices,seeds,raw):
            decoded=decode(r['generated_ids'],tok,model.config)
            score=evaluate_candidate(decoded,condition)
            records.append({**r,**score,'sample_index':i,'decode_seed':seed,'training_seed':101,'model_fingerprint':artifact['model_fingerprint']})
        print('GENERATION_PROGRESS',len(records),a.attempts,flush=True)
    with (output/'attempts.jsonl').open('w',encoding='utf-8') as f:
        for r in records:f.write(json.dumps(r,ensure_ascii=False,separators=(',',':'))+'\n')
    unique={}
    for r in records:
        if r['joint_satisfied']:unique.setdefault(r['graph_id'],r)
    with (output/'qualified_unique.csv').open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=['graph_id','canonical_psmiles','sample_index']);w.writeheader()
        for r in unique.values():w.writerow({k:r[k] for k in w.fieldnames})
    summary=summarize_attempts(records)
    for name in ['Y_training','Y_training_union_PI1M']:summary.pop(name,None)
    summary.update(model=artifact['artifact_name'],condition=condition,full_reference_novelty_computed=False,all_failures_and_duplicates_retained=True)
    (output/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
    print('GENERATION_COMPLETED',output,'qualified_unique',len(unique),flush=True)

if __name__=='__main__':main()
