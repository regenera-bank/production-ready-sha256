import os
from pathlib import Path
from common import TempCase
from regenera_tools.paths import normalized_relative,resolve_within,has_residue
from regenera_tools.files import atomic_write,safe_remove
from regenera_tools.errors import SecurityError
class PathsFilesTest(TempCase):
 def test_normalized(self): self.assertEqual(normalized_relative("a/b.txt"),Path("a/b.txt"))
 def test_absolute_blocked(self): self.assertRaises(SecurityError,normalized_relative,"/etc/passwd")
 def test_parent_blocked(self): self.assertRaises(SecurityError,normalized_relative,"a/../b")
 def test_empty_blocked(self): self.assertRaises(SecurityError,normalized_relative,"")
 def test_within(self): self.assertEqual(resolve_within(self.root,"a/b").parent,self.root/"a")
 def test_symlink_blocked(self):
  (self.root/"real").mkdir(); (self.root/"link").symlink_to(self.root/"real",target_is_directory=True)
  self.assertRaises(SecurityError,resolve_within,self.root,"link/x")
 def test_residue(self): self.assertTrue(has_residue(Path("a/__pycache__/x")))
 def test_atomic_write(self): self.assertEqual(atomic_write(self.root,"a.txt",b"x").read_bytes(),b"x")
 def test_atomic_no_overwrite(self):
  atomic_write(self.root,"a.txt",b"x"); self.assertRaises(FileExistsError,atomic_write,self.root,"a.txt",b"y")
 def test_atomic_overwrite(self):
  atomic_write(self.root,"a.txt",b"x"); atomic_write(self.root,"a.txt",b"y",overwrite=True); self.assertEqual((self.root/"a.txt").read_bytes(),b"y")
 def test_remove_requires_approval(self):
  (self.root/"a").write_text("x"); self.assertRaises(PermissionError,safe_remove,self.root,"a")
 def test_remove_dry_run(self):
  (self.root/"a").write_text("x"); self.assertTrue(safe_remove(self.root,"a",approved=True,dry_run=True)); self.assertTrue((self.root/"a").exists())
 def test_remove_real(self):
  (self.root/"a").write_text("x"); self.assertTrue(safe_remove(self.root,"a",approved=True,dry_run=False)); self.assertFalse((self.root/"a").exists())
