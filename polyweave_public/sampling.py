"""Batched cached seq2seq sampler with a separate uniform stream per candidate.

No inherited beam/min-length/repetition settings. Nucleus sampling retains the
first token crossing p. All rows (including already finished rows) consume the
same precomputed uniform position, so stopping another row cannot shift RNG.
"""
import random
import time
import torch
def sync(device):
    if str(device).startswith('cuda'):torch.cuda.synchronize(device)


def uniforms(seeds, steps, device):
    if not seeds or steps<1:raise ValueError('Nonempty seed list and positive step count required')
    return torch.tensor(
        [[rng.random() for _ in range(steps)] for rng in [random.Random(s) for s in seeds]],
        dtype=torch.float64,device=device)


def categorical(logits, u, temperature=1.0, top_p=0.95, top_k=0):
    if temperature<=0 or not 0<top_p<=1 or top_k<0: raise ValueError('Invalid sampling parameters')
    if not torch.isfinite(logits).all(): raise FloatingPointError('Non-finite decoder logits')
    values, indices = (logits.float()/temperature).sort(dim=-1,descending=True,stable=True)
    if top_k:
        values[:, min(top_k,values.shape[-1]):] = -torch.inf
    cumulative = values.softmax(-1).cumsum(-1)
    remove = cumulative > top_p
    remove[:,1:] = remove[:,:-1].clone()
    remove[:,0] = False
    values = values.masked_fill(remove,-torch.inf)
    cdf = values.softmax(-1).double().cumsum(-1)
    cdf = cdf / cdf[:,-1:]
    cdf[:,-1] = 1.0
    pos = torch.searchsorted(cdf.contiguous(),u[:,None].contiguous(),right=True).clamp_max(cdf.shape[-1]-1)
    return indices.gather(1,pos).squeeze(1)


@torch.inference_mode()
def sample_ids(model, input_ids, attention_mask, seeds, max_new_tokens=256,
               temperature=1.0, top_p=0.95, top_k=0, use_cache=True):
    if input_ids.shape[0]!=len(seeds) or not seeds or max_new_tokens<1:
        raise ValueError('One independent seed per candidate required')
    model.eval()
    device=input_ids.device
    u=uniforms(seeds,max_new_tokens,device)
    decoder=torch.full((len(seeds),1),model.config.decoder_start_token_id,dtype=torch.long,device=device)
    finished=torch.zeros(len(seeds),dtype=torch.bool,device=device)
    eos=model.config.eos_token_id
    if isinstance(eos,list): raise ValueError('This frozen T5 interface requires one EOS ID')
    sync(device);started=time.perf_counter()
    encoded=model.get_encoder()(input_ids=input_ids,attention_mask=attention_mask,return_dict=True)
    past=None;pieces=[]
    for t in range(max_new_tokens):
        out=model(encoder_outputs=encoded,attention_mask=attention_mask,
                  decoder_input_ids=decoder[:,-1:] if use_cache and past is not None else decoder,
                  past_key_values=past,use_cache=use_cache,return_dict=True)
        next_id=categorical(out.logits[:,-1,:],u[:,t],temperature,top_p,top_k)
        next_id=torch.where(finished,model.config.pad_token_id,next_id)
        pieces.append(next_id)
        finished |= next_id==eos
        decoder=torch.cat([decoder,next_id[:,None]],dim=1)
        past=out.past_key_values if use_cache else None
        if bool(finished.all()): break
    sync(device);seconds=time.perf_counter()-started
    all_ids=torch.stack(pieces,dim=1).cpu().tolist()
    result=[]
    for seq in all_ids:
        ended=eos in seq
        seq=seq[:seq.index(eos)+1] if ended else seq
        result.append({'generated_ids':seq,'hit_length_limit':not ended,
                       'generation_seconds':seconds/len(seeds)})
    return result,seconds


def decode(ids, tok, model_config):
    # Structural special IDs are removed by ID, without chemistry text edits.
    reserved=set(tok.all_special_ids)|{model_config.pad_token_id,model_config.eos_token_id,
                                      model_config.decoder_start_token_id}
    return tok.decode([i for i in ids if i not in reserved],skip_special_tokens=False,
                      clean_up_tokenization_spaces=False).strip()
