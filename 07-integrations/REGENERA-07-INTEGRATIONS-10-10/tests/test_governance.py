import json
from pathlib import Path
import sys
import tomllib
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from regenera_integrations.adapters import ADAPTERS


class GovernanceTests(unittest.TestCase):
    def test_registry_matches_code(self):
        registry = json.loads((ROOT / "governance/INTEGRATION-REGISTRY.json").read_text(encoding="utf-8"))
        self.assertEqual({item["code"] for item in registry["integrations"]}, set(ADAPTERS))

    def test_all_external_adapters_are_blocked(self):
        registry = json.loads((ROOT / "governance/INTEGRATION-REGISTRY.json").read_text(encoding="utf-8"))
        unsupported = [item["code"] for item in registry["integrations"] if item["status"] == "PRODUCTION_ACTIVE"]
        self.assertEqual(unsupported, [])

    def test_self_approval_is_not_present(self):
        approval = json.loads((ROOT / "governance/APPROVAL-RECORD.json").read_text(encoding="utf-8"))
        self.assertNotEqual(approval["author"], approval["independent_approver"])
        self.assertFalse(approval["release_authorized"])

    def test_unsigned_release_is_blocked(self):
        approval = json.loads((ROOT / "governance/APPROVAL-RECORD.json").read_text(encoding="utf-8"))
        self.assertIsNone(approval["signature_reference"])
        self.assertFalse(approval["release_authorized"])

    def test_control_matrix_has_blocking_evidence(self):
        matrix = json.loads((ROOT / "governance/CONTROL-MATRIX.json").read_text(encoding="utf-8"))
        self.assertGreaterEqual(len(matrix["controls"]), 20)
        self.assertTrue(all(control["evidence"] and control["owner"] for control in matrix["controls"]))
        self.assertTrue(all(control["blocking"] for control in matrix["controls"]))

    def test_runbooks_have_decision_gates(self):
        unknown = (ROOT / "docs/runbooks/UNKNOWN-OUTCOME.md").read_text(encoding="utf-8")
        outage = (ROOT / "docs/runbooks/PROVIDER-OUTAGE.md").read_text(encoding="utf-8")
        self.assertIn("## Gates de decisão", unknown)
        self.assertIn("## Gates de decisão", outage)

    def test_policies_have_operational_sections(self):
        sections = {"## Objetivo", "## Escopo", "## Responsabilidades", "## Controles obrigatórios", "## Evidências", "## Exceções", "## Revisão"}
        for path in (ROOT / "docs/policies").glob("*.md"):
            text = set(line.strip() for line in path.read_text(encoding="utf-8").splitlines())
            self.assertFalse(sections - text, path.name)

    def test_release_has_no_nested_archive(self):
        archives = [path for path in ROOT.rglob("*") if path.is_file() and path.suffix.lower() in {".zip", ".rar", ".7z"} and "dist" not in path.parts]
        self.assertEqual(archives, [])

    def test_standard_library_only(self):
        data = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
        self.assertNotIn("dependencies", data["project"])

    def test_build_provenance_declares_no_network(self):
        script = (ROOT / "scripts/build_release.py").read_text(encoding="utf-8")
        self.assertIn('"network_used": False', script)
        self.assertIn('"external_dependencies_installed": False', script)

    def test_exception_register_is_empty_and_blocking(self):
        register = json.loads((ROOT / "governance/EXCEPTION-REGISTER.json").read_text(encoding="utf-8"))
        self.assertEqual(register["exceptions"], [])
        self.assertIn("bloqueia", register["rule"].lower())

    def test_origin_claim_is_careful(self):
        text = (ROOT / "DECLARACAO-PROCEDENCIA.md").read_text(encoding="utf-8")
        self.assertIn("Aprovação institucional", text)
        self.assertNotIn("100% humano", text)

    def test_source_inventory_records_original_contamination(self):
        inventory = json.loads((ROOT / "governance/SOURCE-INVENTORY.json").read_text(encoding="utf-8"))
        self.assertEqual(inventory["top_level_integration_directories"], 14)
        self.assertGreater(inventory["gitkeep_files"], 300)
        self.assertGreater(inventory["ds_store_files"], 0)
        self.assertIn("não promovida", inventory["decision"])


if __name__ == "__main__":
    unittest.main()
