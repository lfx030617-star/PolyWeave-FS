from pathlib import Path
from tempfile import TemporaryDirectory
import hashlib,unittest
from polyweave_public.download import ASSET_BASE,assemble,validate_manifest

ROOT=Path(__file__).resolve().parents[1]

class DownloadChecks(unittest.TestCase):
    def setUp(self):
        parent=ROOT/'.test_tmp';parent.mkdir(exist_ok=True);self.temp=TemporaryDirectory(dir=parent);self.root=Path(self.temp.name)
        self.parts=self.root/'parts';self.parts.mkdir();self.data=b'unchanged-archive-bytes';chunks=[self.data[:7],self.data[7:15],self.data[15:]]
        entries=[]
        for i,chunk in enumerate(chunks,1):
            name='example.zip.part'+str(i).zfill(3);(self.parts/name).write_bytes(chunk)
            entries.append({'name':name,'bytes':len(chunk),'sha256':hashlib.sha256(chunk).hexdigest(),'url':ASSET_BASE+name})
        self.manifest={'format':'polyweave_multipart_zip_v1','archive_name':'example.zip','archive_bytes':len(self.data),'archive_sha256':hashlib.sha256(self.data).hexdigest(),'model_directory':'example-model','parts':entries}
        self.archive=self.root/'example.zip'
    def tearDown(self):
        self.temp.cleanup()
        try:(ROOT/'.test_tmp').rmdir()
        except OSError:pass
    def test_exact_restore_and_existing_valid_archive(self):
        assemble(self.manifest,self.parts,self.archive);self.assertEqual(self.archive.read_bytes(),self.data)
        assemble(self.manifest,self.parts,self.archive)
    def test_changed_piece_rejected_without_final_archive(self):
        (self.parts/'example.zip.part002').write_bytes(b'bad-data')
        with self.assertRaises(ValueError):assemble(self.manifest,self.parts,self.archive)
        self.assertFalse(self.archive.exists());self.assertFalse(list(self.root.glob('*.partial')))
    def test_existing_wrong_archive_preserved(self):
        self.archive.write_bytes(b'do-not-overwrite')
        with self.assertRaises(ValueError):assemble(self.manifest,self.parts,self.archive)
        self.assertEqual(self.archive.read_bytes(),b'do-not-overwrite')
    def test_unsafe_piece_name_rejected(self):
        self.manifest['parts'][0]['name']='../outside'
        with self.assertRaises(ValueError):validate_manifest(self.manifest)

if __name__=='__main__':unittest.main()
