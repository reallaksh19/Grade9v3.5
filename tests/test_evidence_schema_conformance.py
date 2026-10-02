import unittest
import json
import jsonschema
from pathlib import Path
from Shared.tools.assurance_record import make_evidence, validate_evidence
from Shared.tools.assurance_product import check_missing

REPO = Path(__file__).resolve().parents[1]

class TestEvidenceSchemaConformance(unittest.TestCase):
    def setUp(self):
        schema_path = REPO / "Shared" / "assurance" / "assurance-evidence.schema.json"
        with schema_path.open("r", encoding="utf-8") as f:
            self.schema = json.load(f)

    def test_evidence_record_matches_schema(self):
        ev = make_evidence(
            assurance_type="STRUCTURAL_VALIDITY",
            subject_kind="library",
            subject_id="test_subject",
            outcome="PASS",
            producer_name="test_producer",
            producer_version="1.0.0"
        )
        jsonschema.validate(instance=ev, schema=self.schema)
        self.assertTrue(validate_evidence(ev))

    def test_evidence_fail_has_severity(self):
        ev = make_evidence(
            assurance_type="STRUCTURAL_VALIDITY",
            subject_kind="product",
            subject_id="test_subject",
            outcome="FAIL",
            producer_name="test_producer",
            producer_version="1.0.0",
            severity="S1"
        )
        self.assertIn("severity", ev)
        self.assertEqual(ev["severity"], "S1")
        jsonschema.validate(instance=ev, schema=self.schema)
        self.assertTrue(validate_evidence(ev))

    def test_evidence_pass_no_severity(self):
        ev = make_evidence(
            assurance_type="STRUCTURAL_VALIDITY",
            subject_kind="product",
            subject_id="test_subject",
            outcome="PASS",
            producer_name="test_producer",
            producer_version="1.0.0",
            severity="S1"
        )
        self.assertNotIn("severity", ev)
        jsonschema.validate(instance=ev, schema=self.schema)
        self.assertTrue(validate_evidence(ev))

    def test_not_run_does_not_satisfy_required_pass(self):
        ev_list = [{
            "assurance_type": "REQUIRED_PASS",
            "outcome": "NOT_RUN"
        }]
        policy = {
            "required_pass": ["REQUIRED_PASS"]
        }
        missing = check_missing(ev_list, policy)
        self.assertIn("REQUIRED_PASS", missing)

    def test_eligible_requires_all_required_pass(self):
        # Already tested by check_missing basically, but let's do a simple check
        ev_list = []
        policy = {
            "required_pass": ["REQUIRED_PASS"]
        }
        missing = check_missing(ev_list, policy)
        self.assertIn("REQUIRED_PASS", missing)

if __name__ == "__main__":
    unittest.main()
