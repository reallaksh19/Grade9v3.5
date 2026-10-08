"""Falsifiers for organizer sample Q5's new agent-only supplementary-angle proof."""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]/"TEST"/"imo-research"
sys.path.insert(0,str(ROOT))
from validate_seed import SeedError  # noqa: E402
from validate_sample_q5_geometry import validate_proof, independent_ray_angle_check  # noqa: E402


class SampleQ5GeometryTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.proof=Path(self.tmp.name)/"candidate.json"
        self.proof.write_bytes((ROOT/"verification"/"official-sample-q5-agent-geometry-proof.v1.json").read_bytes())

    def validate(self):
        return validate_proof(proof=self.proof)

    def change(self,fn):
        d=json.loads(self.proof.read_text(encoding="utf-8"))
        fn(d)
        self.proof.write_text(json.dumps(d))

    def test_new_q5_proof_is_candidate_only(self):
        r=self.validate()
        self.assertEqual(r["agent_printed_option_match"],"C")
        self.assertEqual(r["symbolic_relation"],"x + 2y = 180°")
        self.assertEqual((r["independent_human_signoffs"],r["accepted_qrt_cells"],r["core_eligible"]),(0,0,0))

    def test_separate_unit_vector_geometry(self):
        self.assertEqual(independent_ray_angle_check(),[75,60,50])
        self.assertEqual(independent_ray_angle_check((10,50,70)),[85,65,55])

    def test_altered_source_option_fails(self):
        self.change(lambda d:d.update(printed_sof_answer_key_option="B"))
        with self.assertRaises(SeedError):self.validate()

    def test_new_agent_answer_conflict_fails(self):
        self.change(lambda d:d.update(independent_agent_mathematical_result="y=90°−2x"))
        with self.assertRaises(SeedError):self.validate()

    def test_wrong_source_document_fails(self):
        self.change(lambda d:d.update(official_sample_pdf_url="https://example.invalid/paper.pdf"))
        with self.assertRaises(SeedError):self.validate()

    def test_wrong_pdf_page_fails(self):
        self.change(lambda d:d.update(source_pdf_zero_index_page=0))
        with self.assertRaises(SeedError):self.validate()

    def test_two_source_y_sectors_must_remain(self):
        self.change(lambda d:d["source_diagram_facts_requiring_external_confirmation"].pop())
        with self.assertRaises(SeedError):self.validate()

    def test_equal_y_sectors_cannot_be_changed_to_unequal(self):
        self.change(lambda d:d["source_diagram_facts_requiring_external_confirmation"].__setitem__(
            4,"An oblique ray divides the marked supplementary angle into y and z."))
        with self.assertRaises(SeedError):self.validate()

    def test_corresponding_parallel_transfer_step_required(self):
        self.change(lambda d:d["agent_proof_steps"][0].update(reason="By visual guess and no source rays."*5))
        with self.assertRaises(SeedError):self.validate()

    def test_supplementary_sector_cannot_be_skipped(self):
        self.change(lambda d:d["agent_proof_steps"][1].update(claim="coincidence"))
        with self.assertRaises(SeedError):self.validate()

    def test_vector_witness_wrong_expected_y_fails(self):
        self.change(lambda d:d["independent_analytic_check"].update(expected_each_y_degrees=[75,60,40]))
        with self.assertRaises(SeedError):self.validate()

    def test_fake_independent_human_signature_fails(self):
        self.change(lambda d:d.update(independent_human_mathematical_signoff="SIGNED"))
        with self.assertRaises(SeedError):self.validate()

    def test_wrongly_published_figure_fails(self):
        self.change(lambda d:d.update(source_original_figure_copied=True))
        with self.assertRaises(SeedError):self.validate()

    def test_qrts_must_not_be_accepted_by_figured_answer(self):
        self.change(lambda d:d.update(qrt_acceptance="QRT-JUSTIFY-D2"))
        with self.assertRaises(SeedError):self.validate()

    def test_core_eligibility_fails_without_real_rights(self):
        self.change(lambda d:d.update(core_eligible=True))
        with self.assertRaises(SeedError):self.validate()

    def test_verbatim_source_diagram_not_copied(self):
        self.change(lambda d:d.update(source_diagram_svg="<svg>original figure traced</svg>"))
        with self.assertRaises(SeedError):self.validate()


if __name__=="__main__":
    unittest.main()
