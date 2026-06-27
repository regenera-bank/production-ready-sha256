import json
from common import TempCase
from regenera_tools.sbom import from_pyproject, from_package_lock
from regenera_tools.workspace import validate_workspace, lint_workflow

class SbomWorkspaceTest(TempCase):
    def test_pyproject_empty(self):
        (self.root / "p.toml").write_text("dependencies = []")
        self.assertEqual(from_pyproject(self.root / "p.toml"), [])

    def test_pyproject_dep(self):
        (self.root / "p.toml").write_text('dependencies = ["x>=1", "y"]')
        self.assertEqual(len(from_pyproject(self.root / "p.toml")), 2)

    def test_lock(self):
        (self.root / "l.json").write_text(json.dumps({"packages": {"": {"name": "root"}, "node_modules/x": {"version": "1.2.3"}}}))
        self.assertEqual(from_package_lock(self.root / "l.json")[0]["name"], "x")

    def test_required(self): self.assertTrue(validate_workspace(self.root, ["x"]))
    def test_required_ok(self):
        (self.root / "x").write_text("x")
        self.assertEqual(validate_workspace(self.root, ["x"]), [])
    def test_residue(self):
        (self.root / ".DS_Store").write_text("x")
        self.assertTrue(validate_workspace(self.root, []))
    def test_zip(self):
        (self.root / "x.zip").write_text("x")
        self.assertTrue(validate_workspace(self.root, []))
    def test_symlink(self):
        (self.root / "x").write_text("x")
        (self.root / "y").symlink_to(self.root / "x")
        self.assertTrue(validate_workspace(self.root, []))
    def test_workflow_ok(self):
        text = "permissions:\n  contents: read\nsteps:\n - uses: x/y@" + "a" * 40
        self.assertEqual(lint_workflow(text), [])
    def test_workflow_permission(self): self.assertTrue(lint_workflow("steps:\n - run: true"))
    def test_workflow_branch(self): self.assertTrue(lint_workflow("permissions:\n  contents: read\n - uses: x/y@main"))
    def test_workflow_tag(self): self.assertTrue(lint_workflow("permissions:\n  contents: read\n - uses: x/y@v4"))
