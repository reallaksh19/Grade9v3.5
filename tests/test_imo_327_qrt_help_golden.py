"""#327: three 4×7 QRT-cell golden examples for item hints vs Core1A repair.

These are authored TEST fixtures, not three original SOF Core2 questions.
The compiled 4×7 QRT source remains authoritative for review jobs; H1-H3 are
semantic review objectives, not a mandatory production limit on hint count.
No runtime concept gate, telemetry, independent mastery or Owner approval.
"""
from __future__ import annotations

import copy
import json
import math
import unittest
from pathlib import Path

from Shared.tools import question_review_matrix as qrt, question_difficulty

ROOT = Path(__file__).resolve().parents[1]
FOLDER = ROOT / "TEST" / "imo-research" / "golden"
FILES = {
    "GOLDEN-IMO327-EXPLAIN-D2": "imo-327-explain-d2.v1.json",
    "GOLDEN-IMO327-MODEL-D3": "imo-327-model-d3.v1.json",
    "GOLDEN-IMO327-JUSTIFY-D4": "imo-327-justify-d4.v1.json",
}
EXPECT = {
    "GOLDEN-IMO327-EXPLAIN-D2": ("EXPLAIN", "D2", 3, (0, 0, 1, 0, 2)),
    "GOLDEN-IMO327-MODEL-D3": ("MODEL", "D3", 7, (2, 1, 2, 1, 1)),
    "GOLDEN-IMO327-JUSTIFY-D4": ("JUSTIFY", "D4", 8, (2, 1, 2, 1, 2)),
}
PRELUDE = ("NEUTRAL_DEMONSTRATION", "GENERAL_PRINCIPLE", "CONCEPT_CHECK",
           "GUIDED_APPLICATION", "FRESH_INDEPENDENT_EXIT")
HINT_PURPOSES = ("ORIENT", "CONNECT", "OPEN_THE_WAY")
D4_FORBIDDEN = ("k>0", "k<0", "(a-1)t=k", "t=k/(a-1)", "log_a", "iff")


def load_fixtures() -> dict[str, dict]:
    return {key: json.loads((FOLDER / name).read_text(encoding="utf-8"))
            for key, name in FILES.items()}


def verify_fixture(f: dict, matrix: dict, vocab: dict) -> dict:
    fid = f["fixture_id"]
    if f.get("schema") != "imo-327-qrt-core1a-vs-hints-golden/v1" or fid not in EXPECT:
        raise ValueError("Only one of the three scoped v1 golden examples is allowed")
    if f.get("status") != "AUTHOR_REVIEW_FIXTURE_NOT_LEARNER_PRODUCT" or f.get("origin") != "WHOLLY_AUTHORED_NOT_SOF":
        raise ValueError("False academic/product or authentic SOF authority")
    gate = f["governance"]
    if (gate.get("issue"), gate.get("pr")) != (327, 333):
        raise ValueError("Fixture no longer belongs to #327/#333")
    if any(gate.get(key) != "NOT_GRANTED" for key in
           ("academic_review", "qrt_review", "owner_release")):
        raise ValueError("Invented academic/QRT/Owner acceptance")
    if gate.get("source_core2_admitted") is not False or gate.get("published") is not False:
        raise ValueError("Source-Core2 admission or publication forged")
    demand, band, score, components = EXPECT[fid]
    metadata = f["matrix"]
    if (metadata.get("path") != "Shared/quality/question-demand-matrix.v1.json"
            or metadata.get("vocabulary") != "Shared/vocabularies/cognitive-demand.v1.json"
            or (metadata.get("expected_cell"), metadata.get("primary_demand"), metadata.get("derived_band"))
            != (f"QRT-{demand}-{band}", demand, band)):
        raise ValueError("Wrong base QRT cell or imaginary source matrix")
    item = f["task"]
    if not item["stem"] or "AUTHENTIC_CORE2" not in item["role"] and "DEMONSTRATION" not in item["role"]:
        raise ValueError("Missing independent authored case role")
    question = f["qrt_question"]
    if question["id"] != fid or question["answer"]["crux_move_ref"] != f["item_help"]["protected_decision_ref"]:
        raise ValueError("The protected move must bind to the exact QRT crux")
    values = question["difficulty"]
    if tuple(values["components"][key] for key in question_difficulty.COMPONENT_KEYS) != components:
        raise ValueError("Golden 5-component difficulty evidence drifted")
    if question_difficulty.derive(values)["score"] != score:
        raise ValueError("Difficulty score is not independently derived")
    if question["extensions"]["grade9v3:cognitive_demand"]["primary"] != demand:
        raise ValueError("False demand")
    result = qrt.resolve_review(
        question,
        {"profile_id": "SYNTHETIC-GOLDEN-REVIEW-NOT-LEARNER",
         "provenance": "SYNTHETIC_TEST_ONLY",
         "held": {question["primary_capability_ref"]: "UNCERTAIN"},
         "knowledge_percentage": 40,
         "measured_fit_claim": False},
        matrix, vocab)
    if (result["template_id"], result["classification"]["band"],
            result["classification"]["difficulty_score"]) != (f"QRT-{demand}-{band}", band, score):
        raise ValueError("QRT resolver did not derive declared cell")
    if tuple(result["review"]) != qrt.ASKS or "Band protection:" not in qrt.compile_templates(matrix, vocab)[
         next(i for i, cell in enumerate(qrt.compile_templates(matrix, vocab))
              if cell["template_id"] == result["template_id"])]["slots"]["W"]:
        raise ValueError("The 12 QRT review jobs or protected W disappeared")

    supports = f["item_help"]
    if supports.get("role") != "ITEM_SCOPED_HINTS" or supports.get("assisted_attempt_if_any_hint_used") is not True:
        raise ValueError("Unassisted credit could be awarded after hints")
    rungs = supports.get("rungs") or []
    if (len(rungs) != 3 or tuple(r["id"] for r in rungs) != ("H1", "H2", "H3")
            or tuple(r["purpose"] for r in rungs) != HINT_PURPOSES):
        raise ValueError("Missing or reordered authored demo hint sequence")
    for rung in rungs:
        text = rung.get("text", "")
        if not isinstance(text, str) or len(text) < 25:
            raise ValueError("Hint lacks actionable language")
        if any(secret in text for secret in supports["must_not_reveal_before_attempt"]):
            raise ValueError("Hint disclosed protected relation, solution or warrant")
        if text == result["slots"]["W"]["text"]:
            raise ValueError("Question hint is the protected answer")
    if demand == "JUSTIFY" and any(v in " ".join(r["text"] for r in rungs) for v in D4_FORBIDDEN):
        raise ValueError("D4 hints handed away the existence criterion")
    if demand == "MODEL" and ("t=4" in " ".join(r["text"] for r in rungs)
                              or "4t" in " ".join(r["text"] for r in rungs)):
        raise ValueError("D3 hints answered the model choice")

    lesson = f["core1a_repair"]
    if (lesson.get("role") != "CONCEPT_FIRST_NOT_TARGET_SOLUTION"
            or tuple(s["stage"] for s in lesson["sequence"]) != PRELUDE
            or lesson.get("checkpoint_before_target_aid") is not True
            or lesson.get("checkpoint_enforced_by_current_renderer") is not False
            or lesson.get("return_to_new_unseen_task_required") is not True
            or lesson.get("return_enforced_by_current_renderer") is not False):
        raise ValueError("Concept-first sequence missing or fictitiously implemented")
    if "original question" in lesson["sequence"][0]["text"].lower():
        raise ValueError("Neutral concept stage contains target worked question")
    if not lesson["sequence"][2]["text"] or not lesson["sequence"][-1]["text"]:
        raise ValueError("Missing neutral concept probe or fresh unassisted exit")
    if lesson["sequence"][-1]["text"] == item["stem"]:
        raise ValueError("Fresh retry repeats the protected original question")
    policy = f["evidence_rules"]
    if (policy.get("hint_used") != "ASSISTED_NOT_INDEPENDENT_MASTERY"
            or policy.get("repair_viewed") != "CONCEPT_EXPOSED_NOT_MASTERY"
            or policy.get("attempt_capture_available_in_fixture") is not False
            or policy.get("learner_telemetry") != "NOT_IMPLEMENTED"):
        raise ValueError("Unimplemented mastery or telemetry forged")
    if not f.get("reviewer_only", {}).get("expected_explanation"):
        raise ValueError("Golden expected explanation missing from reviewer-only space")
    return result


class GoldenHintConceptModes(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = load_fixtures()
        cls.matrix = qrt.load(qrt.MATRIX_PATH)
        cls.vocab = qrt.load(qrt.VOCAB_PATH)

    def test_three_distinct_authoritative_qrt_cells_not_full_coverage(self):
        self.assertEqual(set(self.rows), set(EXPECT))
        self.assertEqual(len(qrt.compile_templates(self.matrix, self.vocab)), 28)
        self.assertEqual({(d,b) for d,b,*_ in EXPECT.values()},
                         {("EXPLAIN","D2"),("MODEL","D3"),("JUSTIFY","D4")})
        self.assertEqual(qrt.check_paths(), [])

    def test_three_golden_cases_resolve_exact_cells(self):
        for fid, row in self.rows.items():
            with self.subTest(fid=fid):
                self.assertEqual(verify_fixture(row, self.matrix, self.vocab)["template_id"],
                                 row["matrix"]["expected_cell"])

    def test_actual_model_d3_question_is_the_goldens_own_item_not_sof(self):
        pkg = json.loads((ROOT / "TEST/imo-research/candidates/imo-g9-q26-common-base-core1a.v1.json").read_text(encoding="utf-8"))
        golden = self.rows["GOLDEN-IMO327-MODEL-D3"]
        question = next(q for q in pkg["questions"] if q["id"] == golden["task"]["candidate_question_id"])
        self.assertEqual(question["stem"], golden["task"]["stem"])
        self.assertEqual(question["difficulty"]["components"], golden["qrt_question"]["difficulty"]["components"])
        self.assertEqual(question["extensions"]["grade9v3:cognitive_demand"]["primary"], "MODEL")
        self.assertEqual(question["exposure"][0]["core"], "CORE2A")
        self.assertEqual(question["origin"], "AUTHORED")
        self.assertEqual(pkg["extensions"]["grade9v3:core2_source_custody_granted"], False)

    def test_learner_percentage_never_changes_the_cell(self):
        for row in self.rows.values():
            q = row["qrt_question"]
            a = qrt.resolve_review(q, {"profile_id": "P", "held": {}, "knowledge_percentage": 5},
                                   self.matrix, self.vocab)
            b = qrt.resolve_review(q, {"profile_id": "P", "held": {}, "knowledge_percentage": 95},
                                   self.matrix, self.vocab)
            self.assertEqual(a["template_id"], b["template_id"])

    def test_author_math_d2_explains_not_adds(self):
        for n in (-2, 0, 1, 1.5):
            self.assertTrue(math.isclose(5**(n+1), 5*5**n, rel_tol=1e-12))
        self.assertNotEqual(5**(0+1), 5**0 + 5)

    def test_author_math_d3_and_fresh_exit(self):
        self.assertEqual(4**(2*1.5+1), 16**1.5+192)
        self.assertEqual(5**(2*1+1), 25**1+100)

    def test_author_math_d4_two_sign_domains_and_zero(self):
        for a, k, works in ((3, 18, True), (3, -2, False), (3, 0, False),
                            (0.5, -6, True), (0.5, 1, False), (0.5, 0, False)):
            t=k/(a-1)
            self.assertEqual(t>0, works)
            if works:
                x=math.log(t,a)/2
                self.assertTrue(math.isclose(a**(2*x+1), (a*a)**x+k, rel_tol=1e-12,abs_tol=1e-12))

    def test_falsifier_unreviewed_fixture_cannot_claim_source_core2(self):
        row = copy.deepcopy(self.rows["GOLDEN-IMO327-MODEL-D3"])
        row["governance"]["source_core2_admitted"] = True
        with self.assertRaises(ValueError):
            verify_fixture(row,self.matrix,self.vocab)

    def test_falsifier_hint_cannot_reveal_answer(self):
        row = copy.deepcopy(self.rows["GOLDEN-IMO327-MODEL-D3"])
        row["item_help"]["rungs"][1]["text"] += " Set t=64 and u=3/2."
        with self.assertRaises(ValueError):
            verify_fixture(row,self.matrix,self.vocab)

    def test_falsifier_d4_hint_cannot_reveal_warrant(self):
        row = copy.deepcopy(self.rows["GOLDEN-IMO327-JUSTIFY-D4"])
        row["item_help"]["rungs"][2]["text"] += " k>0 is the criterion."
        with self.assertRaises(ValueError):
            verify_fixture(row,self.matrix,self.vocab)

    def test_falsifier_unenforced_runtime_cannot_be_advertised_as_complete(self):
        row = copy.deepcopy(self.rows["GOLDEN-IMO327-EXPLAIN-D2"])
        row["core1a_repair"]["checkpoint_enforced_by_current_renderer"] = True
        with self.assertRaises(ValueError):
            verify_fixture(row,self.matrix,self.vocab)

    def test_falsifier_concept_first_cannot_be_an_answer_toggle(self):
        row = copy.deepcopy(self.rows["GOLDEN-IMO327-EXPLAIN-D2"])
        row["core1a_repair"]["sequence"] = row["core1a_repair"]["sequence"][2:]
        with self.assertRaises(ValueError):
            verify_fixture(row,self.matrix,self.vocab)

    def test_falsifier_bogus_qr_t_cell_is_detected(self):
        row = copy.deepcopy(self.rows["GOLDEN-IMO327-MODEL-D3"])
        row["matrix"]["expected_cell"] = "QRT-APPLY-D2"
        with self.assertRaises(ValueError):
            verify_fixture(row,self.matrix,self.vocab)

    def test_falsifier_score_and_band_must_derive(self):
        row = copy.deepcopy(self.rows["GOLDEN-IMO327-JUSTIFY-D4"])
        row["qrt_question"]["difficulty"]["score"] = 7
        with self.assertRaises((ValueError, question_difficulty.DifficultyContractError)):
            verify_fixture(row,self.matrix,self.vocab)

    def test_falsifier_hinted_attempt_cannot_gain_independent_credit(self):
        row = copy.deepcopy(self.rows["GOLDEN-IMO327-JUSTIFY-D4"])
        row["evidence_rules"]["hint_used"] = "INDEPENDENT_MASTERY"
        with self.assertRaises(ValueError):
            verify_fixture(row,self.matrix,self.vocab)


if __name__ == "__main__":
    unittest.main()
