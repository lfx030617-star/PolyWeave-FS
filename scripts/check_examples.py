from pathlib import Path
import json,sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from polyweave_public.data import structures,condition_targets
from polyweave_public.evaluator import evaluate_candidate,RULES,rdBase
from polyweave_public._graph import normalize_target

if __name__=='__main__':
    if rdBase.rdkitVersion!=RULES['expected_rdkit_version']:raise ValueError('Use the frozen RDKit '+RULES['expected_rdkit_version']+' runtime')
    n=0
    for row in structures():
        norm=normalize_target(row['canonical_psmiles'],RULES)
        if norm.get('graph_id')!=row['graph_id'] or not norm['pilot_eligible']:raise ValueError('Structure/example identity mismatch '+row['example_id'])
        n+=1
    m=0
    for row in condition_targets():
        score=evaluate_candidate(row['target_psmiles'],row['condition'])
        if not score['joint_satisfied'] or score['graph_id']!=row['graph_id']:raise ValueError('Condition-target example mismatch')
        m+=1
    print(json.dumps({'status':'PASS','structure_examples_checked':n,'existing_condition_target_pairs_checked':m,'rdkit_runtime':rdBase.rdkitVersion,'generated_candidates_evaluated':0,'full_reference_novelty_computed':False,'new_model_training':False},indent=2))
