"""Selected frozen graph-evaluation helpers; preparation pipelines are excluded."""
import hashlib,json
from rdkit import Chem,rdBase
from rdkit.Chem.Scaffolds import MurckoScaffold
GRAPH_VERSION="finite_graph_plain_star_ports_v2"
SCAFFOLD_VERSION="murcko_or_acyclic_backbone_elements_v1"
def compact(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"))

def graph_id(canonical):
    return hashlib.sha256((GRAPH_VERSION + "|" + canonical).encode()).hexdigest()

def assigned_split(group_id, seed, weights):
    if len(weights) != 3 or any(type(x) is not int or x <= 0 for x in weights):
        raise ValueError("Three positive integer split weights are required")
    value = int(hashlib.sha256(f"split-v1|{seed}|{group_id}".encode()).hexdigest()[:16], 16)
    total = sum(weights)
    if value * total < weights[0] * 2**64:
        return "train"
    if value * total < (weights[0] + weights[1]) * 2**64:
        return "validation"
    return "test"

def strict_parse(smiles):
    params = Chem.SmilesParserParams()
    params.parseName = False
    params.allowCXSMILES = False
    return Chem.MolFromSmiles(smiles, params)

def scaffold_group(mol, ports):
    clean = Chem.Mol(mol)
    for atom in clean.GetAtoms():
        atom.SetAtomMapNum(0)
    scaffold = MurckoScaffold.GetScaffoldForMol(clean)
    if scaffold.GetNumAtoms():
        key = ["murcko", Chem.MolToSmiles(scaffold, canonical=True, isomericSmiles=False)]
    else:
        # Acyclic connected graphs have a unique path between the two ports.
        # Using a path plus element set avoids putting every chain in one group.
        path = Chem.GetShortestPath(clean, ports[0], ports[1])
        backbone = Chem.MolFragmentToSmiles(clean, atomsToUse=list(path), canonical=True,
                                           isomericSmiles=False)
        elements = sorted({a.GetAtomicNum() for a in clean.GetAtoms() if a.GetAtomicNum()})
        key = ["acyclic_backbone_elements", backbone, elements]
    return hashlib.sha256((SCAFFOLD_VERSION + "|" + compact(key)).encode()).hexdigest(), key

def normalize_target(smiles, config):
    if not isinstance(smiles, str) or not smiles.strip():
        return {"rejection": "empty_smiles"}
    mol = strict_parse(smiles.strip())
    if mol is None:
        return {"rejection": "parse_or_sanitize_failed"}
    if len(Chem.GetMolFrags(mol)) != 1:
        return {"rejection": "multiple_fragments"}
    heavy = sum(a.GetAtomicNum() > 1 for a in mol.GetAtoms())
    if heavy == 0:
        return {"rejection": "empty_real_backbone"}
    ports = [a.GetIdx() for a in mol.GetAtoms() if a.GetAtomicNum() == 0]
    if len(ports) != 2:
        return {"rejection": "connection_count_not_two"}
    if any(mol.GetAtomWithIdx(i).GetIsotope() or
           mol.GetAtomWithIdx(i).GetFormalCharge() or
           mol.GetAtomWithIdx(i).GetNumRadicalElectrons() or
           mol.GetAtomWithIdx(i).GetNumExplicitHs() for i in ports):
        return {"rejection": "connection_attributes_not_supported"}
    if any(mol.GetAtomWithIdx(i).GetDegree() != 1 for i in ports):
        return {"rejection": "connection_degree_not_one"}
    if any(mol.GetAtomWithIdx(i).GetBonds()[0].GetBondType() != Chem.BondType.SINGLE for i in ports):
        return {"rejection": "connection_bond_not_single"}
    if any(a.HasQuery() for a in mol.GetAtoms()) or any(b.HasQuery() for b in mol.GetBonds()):
        return {"rejection": "query_graph_not_supported"}
    if any(b.GetBondType() in (Chem.BondType.UNSPECIFIED, Chem.BondType.ZERO) for b in mol.GetBonds()):
        return {"rejection": "unspecified_or_zero_bond"}
    if config["endpoint_roles"] != "symmetric_degree1_single_bond_ports":
        raise ValueError("Port swapping is only implemented for endpoint-symmetric task semantics")
    # Both connection points have the same role. Clear all bookkeeping maps;
    # ordinary degree-one dummy atoms are serialized as bare stars. Preserve
    # real-atom isotopes, formal charges and defined stereochemistry throughout.
    for atom in mol.GetAtoms():
        atom.SetAtomMapNum(0)
    # RDKit may bracket neutral dummy atoms attached to metals. The validated
    # ports have no isotope/charge/H/radical attributes, so use bare-star spelling
    # for these as well; keep all real-atom brackets unchanged.
    canonical = Chem.MolToSmiles(mol, canonical=True, isomericSmiles=True).replace("[*]", "*")
    excluded = []
    allowed = set(config["allowed_pilot_atomic_numbers"])
    if any(a.GetAtomicNum() not in allowed and a.GetAtomicNum() != 0 for a in mol.GetAtoms()):
        excluded.append("pilot_element_domain")
    low, high = config["pilot_heavy_atom_range"]
    if not low <= heavy <= high:
        excluded.append("pilot_heavy_atom_range")
    if config["exclude_pilot_radicals"] and any(a.GetNumRadicalElectrons() for a in mol.GetAtoms()):
        excluded.append("pilot_radical")
    eligible = not excluded
    scaffold_id, scaffold_key = (None, None)
    if eligible and config["make_scaffold_protocol"]:
        scaffold_id, scaffold_key = scaffold_group(mol, ports)
    gid = graph_id(canonical)
    return {"graph_id": gid, "canonical_psmiles": canonical,
            "real_heavy_atom_count": heavy, "ring_count": mol.GetRingInfo().NumRings(),
            "formal_charge": Chem.GetFormalCharge(mol), "pilot_eligible": eligible,
            "pilot_exclusion_reasons": excluded, "scaffold_group_id": scaffold_id,
            "scaffold_key": scaffold_key,
            "graph_split": assigned_split(gid, config["split_seed"], config["split_weights"]),
            "scaffold_split": assigned_split(scaffold_id, config["split_seed"], config["split_weights"]) if scaffold_id else None}
