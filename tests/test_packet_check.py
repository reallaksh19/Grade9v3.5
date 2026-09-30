"""A counted packet is not necessarily a complete or supported packet."""
import copy
import unittest
from Shared.tools import packet_check, quality_observe, render_core


def question():
    return {"id": "Q-ONE", "stem": "Find the value.", "difficulty": {"band": "D3"},
            "hints": [{"text": "A source hint"}],
            "scaffolds": [{"text": t} for t in ("Orient yourself", "Choose a relation", "Check the crux")],
            "answer": {"summary": "The result", "reasoning_route": [
                {"id": "M1", "kind": "CONNECT", "action": "Connect the givens", "why_valid": "By the definition",
                 "inputs": ["givens"], "output": "relation"}]}}


def context(q):
    return render_core.Ctx({"product_id": "TEST", "output_roles": ["CORE2"]}, [], [q], {},
                           selection_rows={"core2": [q]})


def page(ctx, q):
    return {"core2.html": f'<article data-g9-unit="{q["id"]}">{render_core.core2(ctx, q)}</article>'}


def result(report, check):
    return next(r for r in report["checks"] if r["check"] == check)


class PacketCheck(unittest.TestCase):
    def test_declared_math_only_and_nested_literal_is_not_double_typeset(self):
        q = question(); ctx = context(q)
        q["extensions"] = {"grade9v3:math_spans": [
            {"target": "stem", "literal": "x^2", "tex": "x^{2}", "display": False},
            {"target": "stem", "literal": "sqrt(x^2)", "tex": r"\sqrt{x^{2}}", "display": False}]}
        value = render_core.question_text(ctx, q, "stem", "sqrt(x^2); x^2; z^2 < text")
        self.assertEqual(value.count('<math '), 2)
        self.assertIn("z^2 &lt; text", value)
        self.assertFalse(ctx.gaps)

    def test_equal_counts_do_not_hide_substitution(self):
        q = question(); ctx = context(q)
        pages = page(ctx, q)
        pages["core2.html"] = pages["core2.html"].replace('data-g9-unit="Q-ONE"', 'data-g9-unit="Q-OTHER"')
        report = packet_check.inspect(ctx, pages)
        self.assertEqual(result(report, "HTML_ID_TALLY")["status"], "FAIL")

    def test_duplicate_article_fails(self):
        q = question(); ctx = context(q); pages = page(ctx, q)
        pages["core2.html"] *= 2
        self.assertEqual(result(packet_check.inspect(ctx, pages), "HTML_UNIQUE_IDS")["status"], "FAIL")

    def test_source_hints_never_count_as_authored_help(self):
        q = question(); q.pop("scaffolds")
        q["hint_ladder"] = [{"order": n, "from": "hints[0]"} for n in (1, 2, 3)]
        ctx = context(q)
        report = packet_check.inspect(ctx, page(ctx, q))
        self.assertEqual(result(report, "AUTHORED_HINT_LADDER")["status"], "FAIL")

    def test_authored_content_is_inert_and_has_independent_ladder_identity(self):
        q = question(); ctx = context(q); pages = page(ctx, q)
        root = quality_observe.parse(pages["core2.html"])
        block = next(n for n in root.find_all(attr="data-g9-block") if n.attrs["data-g9-block"] == "authored_hints")
        self.assertTrue(any(a.tag == "template" for a in block.ancestors()))
        refs = [n.attrs["data-g9-ladder-ref"] for n in root.find_all(attr="data-g9-ladder-ref")]
        self.assertEqual(len(refs), len(set(refs)))
        report = packet_check.inspect(ctx, pages)
        self.assertEqual(result(report, "AUTHORED_HINT_LADDER")["status"], "PASS")
        self.assertEqual(result(report, "REASONING_ROUTE")["status"], "PASS")

    def test_visual_exception_goes_stale_after_question_change(self):
        q = question()
        q["extensions"] = {}
        q["extensions"]["grade9v3:visual_review"] = {"applicable": False, "reason": "No spatial relation",
              "reviewer": "independent-test-reviewer", "question_digest": packet_check.question_digest(q)}
        ctx = context(q)
        self.assertEqual(result(packet_check.inspect(ctx, page(ctx, q)), "HARD_VISUAL")["status"], "PASS")
        q["stem"] += " with a plot"
        self.assertEqual(result(packet_check.inspect(ctx, page(ctx, q)), "HARD_VISUAL")["status"], "FAIL")

    def test_unknown_upload_and_browser_are_never_pass(self):
        q = question(); ctx = context(q)
        report = packet_check.inspect(ctx, page(ctx, q))
        for check in ("UPLOAD_TALLY", "TABLET_LANDSCAPE", "KEY_PDF"):
            self.assertEqual(result(report, check)["status"], "NOT_RUN")

    def test_inventory_omission_is_shown_even_with_matching_selected_html(self):
        q = question(); ctx = context(q)
        inventory = {"items": [{"item_id": "I1", "question_card": "Q-ONE"},
                               {"item_id": "I2", "question_card": "Q-TWO"}], "counts": {"items": 2}}
        row = result(packet_check.inspect(ctx, page(ctx, q), inventory), "UPLOAD_TALLY")
        self.assertEqual(row["status"], "FAIL")
        self.assertEqual(row["detail"]["mapping"][1]["questions"], [])

    def test_repeated_filler_rungs_fail(self):
        q = question(); q["scaffolds"] = [{"text": "Try harder"}] * 3
        ctx = context(q)
        self.assertEqual(result(packet_check.inspect(ctx, page(ctx, q)), "AUTHORED_HINT_LADDER")["status"], "FAIL")


if __name__ == "__main__":
    unittest.main()
