from collections import Counter
from pathlib import Path
import re,unittest
from polyweave_public.data import structures,condition_targets,endpoints
from polyweave_public.results import summarize

class PublicContract(unittest.TestCase):
    def test_structure_subset_and_origins(self):
        rows=list(structures());self.assertEqual(len(rows),300);self.assertEqual(len({r['graph_id'] for r in rows}),300)
        self.assertEqual(Counter(r['primary_source'] for r in rows),{'PI1M':100,'OMG':100,'SMiPoly':100})
        for r in rows:
            self.assertEqual(r['graph_split'],'train');self.assertIn(r['primary_source'],r['sources'].split('|'))
            self.assertEqual(r['canonical_psmiles'].count('*'),2);self.assertIsNone(re.search(r'\[[^\]]*\*[^\]]*\]',r['canonical_psmiles']))

    def test_conditions_are_subset_targets_and_not_formal_queries(self):
        master={r['graph_id']:r for r in structures()};rows=list(condition_targets());self.assertEqual(len(rows),30)
        self.assertEqual(Counter(r['condition_type'] for r in rows),{'F+B':15,'F+B+D':15})
        self.assertEqual(Counter(r['sampling_source'] for r in rows),{'PI1M':10,'OMG':10,'SMiPoly':10})
        for r in rows:
            self.assertEqual(r['partition'],'train');self.assertEqual(r['query_origin'],'train')
            self.assertEqual(r['target_psmiles'],master[r['graph_id']]['canonical_psmiles'])

    def test_results_reproduce_main_means(self):
        rows=list(endpoints());self.assertEqual(len(rows),60)
        summary=summarize(rows);self.assertEqual(len(summary),12)
        vals={r['arm']:r['Y_common_mean'] for r in summary if r['experiment']=='C' and r['scale']=='full'}
        self.assertAlmostEqual(vals['DPO'],50.85,places=3);self.assertAlmostEqual(vals['POS'],34.315,places=3)
        self.assertAlmostEqual(vals['CHOSEN1'],46.626,places=3)

    def test_duplicate_training_seed_is_rejected(self):
        rows=[r for r in endpoints() if r['experiment']=='C' and r['scale']=='full' and r['arm']=='DPO']
        rows[-1]=dict(rows[0])
        with self.assertRaises(ValueError):summarize(rows)

    def test_no_large_binary_payloads(self):
        root=Path(__file__).resolve().parents[1]
        for p in root.rglob('*'):
            if p.is_file() and not any(x.startswith('.') or x=='__pycache__' for x in p.relative_to(root).parts):
                self.assertLess(p.stat().st_size,200000)
                self.assertNotIn(p.suffix,['.zip','.gz','.tar','.bin','.pt','.safetensors','.sqlite','.docx'])

if __name__=='__main__':unittest.main()
