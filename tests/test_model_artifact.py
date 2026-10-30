from pathlib import Path
from tempfile import TemporaryDirectory
import hashlib,json,unittest
from polyweave_public.model_artifact import verify_model

ROOT=Path(__file__).resolve().parents[1]

class ArtifactChecks(unittest.TestCase):
    def setUp(self):
        parent=ROOT/'.test_tmp';parent.mkdir(exist_ok=True)
        self.tmp=TemporaryDirectory(dir=parent);self.directory=Path(self.tmp.name)
        payload={'model.safetensors':b'engineering-fixture-not-a-real-model','config.json':b'{"model_type":"t5","vocab_size":32115}','generation_config.json':b'{}','tokenizer.json':b'{}','LICENSE':b'test notice','MODEL_CARD.md':b'engineering fixture','NOTICE':b'test notice'}
        entries=[]
        for name,content in payload.items():
            (self.directory/name).write_bytes(content)
            entries.append({'path':name,'bytes':len(content),'sha256':hashlib.sha256(content).hexdigest()})
        weights=sorted((e['path'],e['sha256']) for e in entries if e['path'].endswith('.safetensors'))
        fp=hashlib.sha256(json.dumps(weights,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
        self.identity={'artifact_name':'engineering-fixture','arm':'DPO','scale':'full','training_seed':101,'model_fingerprint':fp,'vocab_size':32115,'tokenizer_files':{'tokenizer.json':hashlib.sha256(payload['tokenizer.json']).hexdigest()},'configuration_files':{n:hashlib.sha256(payload[n]).hexdigest() for n in ['config.json','generation_config.json']}}
        self.manifest={k:self.identity[k] for k in ['artifact_name','arm','scale','training_seed','model_fingerprint','vocab_size']};self.manifest['files']=entries
        self.write_manifest()

    def write_manifest(self):(self.directory/'MODEL_MANIFEST.json').write_text(json.dumps(self.manifest))
    def tearDown(self):
        self.tmp.cleanup()
        try:(ROOT/'.test_tmp').rmdir()
        except OSError:pass

    def test_allowlisted_complete_artifact(self):
        self.assertEqual(verify_model(self.directory,self.identity)['artifact_name'],'engineering-fixture')

    def test_corrupt_weight_rejected(self):
        (self.directory/'model.safetensors').write_bytes(b'corrupt')
        with self.assertRaises(ValueError):verify_model(self.directory,self.identity)

    def test_path_traversal_rejected(self):
        self.manifest['files'].insert(0,{'path':'../outside','bytes':0,'sha256':'0'*64});self.write_manifest()
        with self.assertRaises(ValueError):verify_model(self.directory,self.identity)

    def test_other_seed_rejected(self):
        self.manifest['training_seed']=202;self.write_manifest()
        with self.assertRaises(ValueError):verify_model(self.directory,self.identity)

    def test_unlisted_weight_rejected(self):
        (self.directory/'pytorch_model.bin').write_bytes(b'unlisted')
        with self.assertRaises(ValueError):verify_model(self.directory,self.identity)

if __name__=='__main__':unittest.main()
