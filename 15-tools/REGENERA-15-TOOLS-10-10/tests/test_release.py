import json
from common import TempCase
from regenera_tools.release import create_manifest,verify_manifest,payload_files
from regenera_tools.errors import IntegrityError
class ReleaseTest(TempCase):
 def seed(self): (self.root/"a.txt").write_text("a"); (self.root/"b.txt").write_text("b")
 def test_create(self): self.seed();self.assertEqual(create_manifest(self.root,set())["file_count"],2)
 def test_sorted(self): self.seed();self.assertEqual([x["path"] for x in create_manifest(self.root,set())["files"]],["a.txt","b.txt"])
 def test_verify(self): self.seed();m=create_manifest(self.root,set());self.assertEqual(verify_manifest(self.root,m),[])
 def test_tamper(self): self.seed();m=create_manifest(self.root,set());(self.root/"a.txt").write_text("x");self.assertTrue(verify_manifest(self.root,m))
 def test_extra(self): self.seed();m=create_manifest(self.root,set());(self.root/"c.txt").write_text("c");self.assertTrue(verify_manifest(self.root,m))
 def test_missing(self): self.seed();m=create_manifest(self.root,set());(self.root/"a.txt").unlink();self.assertTrue(verify_manifest(self.root,m))
 def test_exclusion(self): self.seed();m=create_manifest(self.root,{"a.txt"});self.assertEqual(m["file_count"],1)
 def test_zip_block(self): (self.root/"x.zip").write_bytes(b"x");self.assertRaises(IntegrityError,payload_files,self.root,set())
 def test_residue_block(self): (self.root/".DS_Store").write_bytes(b"x");self.assertRaises(IntegrityError,payload_files,self.root,set())
 def test_pyc_block(self): (self.root/"x.pyc").write_bytes(b"x");self.assertRaises(IntegrityError,payload_files,self.root,set())
 def test_symlink_block(self):
  (self.root/"a").write_text("x");(self.root/"b").symlink_to(self.root/"a");self.assertRaises(IntegrityError,payload_files,self.root,set())
 def test_directory_symlink_block(self):
  (self.root/"real").mkdir();(self.root/"link").symlink_to(self.root/"real",target_is_directory=True);self.assertRaises(IntegrityError,payload_files,self.root,set())
 def test_size(self): self.seed();m=create_manifest(self.root,set());self.assertEqual(m["files"][0]["size"],1)
