from pathlib import Path
import tempfile, unittest
class TempCase(unittest.TestCase):
    def setUp(self):
        self._tmp=tempfile.TemporaryDirectory(); self.root=Path(self._tmp.name)
    def tearDown(self): self._tmp.cleanup()
