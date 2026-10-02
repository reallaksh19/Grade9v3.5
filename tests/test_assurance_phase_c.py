import unittest
from Shared.tools.assurance_answerability import verify_self_containment, verify_answer_correctness, verify_dimensional_correctness

class TestPhaseC(unittest.TestCase):
    def test_self_containment_pass(self):
        q = {
            "answer": {"summary": "The range R is u", "numeric": {"value": 10}},
            "extensions": {
                "problem_specification": {
                    "visible_facts": [{"symbol": "u"}],
                    "permitted_constants": [{"symbol": "R"}],
                    "declared_assumptions": []
                }
            }
        }
        res, det = verify_self_containment(q)
        self.assertEqual(res, "PASS")

    def test_self_containment_fail_hidden_given(self):
        q = {
            "answer": {"summary": "Use g and t", "numeric": {"value": 10}},
            "extensions": {
                "problem_specification": {
                    "visible_facts": [{"symbol": "t"}],
                    "permitted_constants": [],
                    "declared_assumptions": []
                }
            }
        }
        res, det = verify_self_containment(q)
        self.assertEqual(res, "FAIL")
        self.assertIn("g", det["symbols"])

    def test_answer_correctness_projectile_range(self):
        q = {
            "answer": {"numeric": {"value": 40.0}},
            "extensions": {
                "computation_model": {
                    "model_type": "PROJECTILE_NO_DRAG",
                    "variables": {
                        "u": {"value": 20},
                        "theta": {"value": 45},
                        "g": {"value": 10}
                    }
                }
            }
        }
        res, det = verify_answer_correctness(q)
        self.assertEqual(res, "PASS")

    def test_answer_correctness_wrong(self):
        q = {
            "answer": {"numeric": {"value": 45.0}},
            "extensions": {
                "computation_model": {
                    "model_type": "PROJECTILE_NO_DRAG",
                    "variables": {
                        "u": {"value": 20},
                        "theta": {"value": 30},
                        "g": {"value": 10}
                    }
                }
            }
        }
        res, det = verify_answer_correctness(q)
        self.assertEqual(res, "FAIL")

    def test_dimensional_correctness_length(self):
        q = {
            "answer": {"numeric": {"unit": "m"}},
            "extensions": {
                "answer_contract": {
                    "expected_dimension": "LENGTH"
                }
            }
        }
        res, det = verify_dimensional_correctness(q)
        self.assertEqual(res, "PASS")

    def test_dimensional_correctness_wrong_unit(self):
        q = {
            "answer": {"numeric": {"unit": "s"}},
            "extensions": {
                "answer_contract": {
                    "expected_dimension": "LENGTH"
                }
            }
        }
        res, det = verify_dimensional_correctness(q)
        self.assertEqual(res, "FAIL")

if __name__ == '__main__':
    unittest.main()
