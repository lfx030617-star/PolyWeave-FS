"""Selected frozen candidate evaluator. No model training or generation."""
from functools import lru_cache
from pathlib import Path
import hashlib,json,re
from rdkit import Chem,rdBase
from ._graph import compact,strict_parse,normalize_target,graph_id
RULES=json.loads((Path(__file__).parent/'rules.json').read_text())
QUERY_VERSION='element_aromatic_charge_isotope_available_stereo_query_v1'
CONDITION_VERSION='fragment_ports_optional_heavy_bin_v1'
BINS=((10,19),(20,29),(30,39),(40,59),(60,80))
def stable_hash(*parts):
    return hashlib.sha256('|'.join(map(str,parts)).encode()).hexdigest()

def make_condition(smarts, size=None):
    query=Chem.MolFromSmarts(smarts)
    if query is None or len(Chem.GetMolFrags(query))!=1 or any(a.GetAtomicNum()<=1 for a in query.GetAtoms()):
        raise ValueError('Condition requires one connected non-dummy heavy-atom query')
    if not 4<=query.GetNumAtoms()<=12:raise ValueError('Fragment must have 4..12 heavy atoms')
    if size is not None and (any(type(n) is not int for n in size) or list(size) not in [list(x) for x in BINS]):
        raise ValueError('Size condition must be one frozen inclusive bin')
    content={'version':CONDITION_VERSION,'fragment_query_version':QUERY_VERSION,
             'fragment_smarts':smarts,'fragment_id':stable_hash(QUERY_VERSION,smarts),
             'heavy_atom_range':list(size) if size is not None else None,
             'ports':{'count':2,'degree':1,'bond':'SINGLE','notation':'*','roles':'symmetric'},
             'domain':{'allowed_atomic_numbers':RULES['allowed_pilot_atomic_numbers'],
                       'heavy_atom_range':RULES['pilot_heavy_atom_range'],'exclude_radicals':True},
             'use_chirality':True}
    content['condition_id']=stable_hash(CONDITION_VERSION,compact(content))
    return content

@lru_cache(maxsize=8192)
def compile_condition(text):
    condition=json.loads(text)
    expected=make_condition(condition['fragment_smarts'],condition['heavy_atom_range'])
    if expected!=condition: raise ValueError('Condition hash or fixed semantics changed')
    query=Chem.MolFromSmarts(condition['fragment_smarts'])
    return condition,query

def evaluate_candidate(text, condition, training_ids=None, pi1m_ids=None):
    condition,query=compile_condition(compact(condition))
    flags=['parse_ok','single_component_ok','real_backbone_ok','port_count_ok','port_degree_ok',
           'port_bond_ok','port_notation_ok','port_attributes_ok','graph_types_ok','domain_ok','fragment_ok','size_ok']
    out={key:None for key in flags}
    out.update(raw_output=text,condition_id=condition['condition_id'],canonical_psmiles=None,graph_id=None,
               joint_satisfied=False,novel_vs_training=None,novel_vs_training_union_PI1M=None,
               failure_reasons=[],preference_positive_eligible=False,preference_negative_eligible=False)
    if not isinstance(text,str) or not text.strip():
        out['parse_ok']=False;out['failure_reasons']=['empty_output'];return out
    mol=strict_parse(text.strip())
    if mol is None:
        out['parse_ok']=False;out['failure_reasons']=['parse_or_sanitize_failed'];return out
    out['parse_ok']=True
    heavy=sum(a.GetAtomicNum()>1 for a in mol.GetAtoms())
    ports=[a for a in mol.GetAtoms() if a.GetAtomicNum()==0]
    out.update(single_component_ok=len(Chem.GetMolFrags(mol))==1,real_backbone_ok=heavy>0,
        port_count_ok=len(ports)==2,port_degree_ok=len(ports)==2 and all(a.GetDegree()==1 for a in ports),
        port_notation_ok=len(ports)==2 and not re.search(r'\[[^\]]*\*[^\]]*\]',text),
        port_attributes_ok=len(ports)==2 and all(not (a.GetIsotope() or a.GetFormalCharge() or
                           a.GetNumRadicalElectrons() or a.GetNumExplicitHs()) for a in ports),
        graph_types_ok=not(any(a.HasQuery() for a in mol.GetAtoms()) or any(b.HasQuery() or
            b.GetBondType() in (Chem.BondType.ZERO,Chem.BondType.UNSPECIFIED) for b in mol.GetBonds())),
        real_heavy_atom_count=heavy)
    out['port_bond_ok']=out['port_degree_ok'] and all(a.GetBonds()[0].GetBondType()==Chem.BondType.SINGLE for a in ports)
    out['domain_ok']=(all(a.GetAtomicNum() in set(RULES['allowed_pilot_atomic_numbers'])|{0} for a in mol.GetAtoms())
                      and 10<=heavy<=80 and not any(a.GetNumRadicalElectrons() for a in mol.GetAtoms()))
    out['fragment_ok']=mol.HasSubstructMatch(query,useChirality=True)
    size=condition['heavy_atom_range']
    out['size_ok']=size is None or size[0]<=heavy<=size[1]
    structural=['parse_ok','single_component_ok','real_backbone_ok','port_count_ok','port_degree_ok',
                'port_bond_ok','port_notation_ok','port_attributes_ok','graph_types_ok']
    if all(out[k] for k in structural):
        normalized=normalize_target(text,RULES)
        if 'rejection' in normalized: raise RuntimeError('Evaluator and frozen target normalization disagree: '+normalized['rejection'])
        out['canonical_psmiles']=normalized['canonical_psmiles'];out['graph_id']=normalized['graph_id']
        if training_ids is not None:
            out['novel_vs_training']=out['graph_id'] not in training_ids
            if pi1m_ids is not None:
                out['novel_vs_training_union_PI1M']=out['novel_vs_training'] and out['graph_id'] not in pi1m_ids
    out['joint_satisfied']=all(out[k] for k in flags)
    out['failure_reasons']=[key for key in flags if out[key] is False]
    out['preference_positive_eligible']=out['joint_satisfied']
    out['preference_negative_eligible']=(all(out[k] for k in structural) and out['domain_ok'] and
                                         (out['fragment_ok'] is False or out['size_ok'] is False))
    return out

def summarize_attempts(evaluations):
    n=len(evaluations)
    joint=[r for r in evaluations if r['joint_satisfied']]
    unique={r['graph_id'] for r in joint}
    def novel(key):
        return len({r['graph_id'] for r in joint if r[key]}) if all(r[key] is not None for r in joint) else None
    return {'attempt_count':n,'parseable_count':sum(r['parse_ok'] is True for r in evaluations),
            'joint_satisfying_count':len(joint),'joint_satisfaction_rate':len(joint)/n if n else None,
            'U':len(unique),'Y_training':novel('novel_vs_training'),
            'Y_training_union_PI1M':novel('novel_vs_training_union_PI1M'),
            'any_satisfying_structure':bool(unique)}
