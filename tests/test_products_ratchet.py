"""Phase 7 ratchet: a product's gap count may only go down (products/ratchet.v1.json)."""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from Shared.tools import build_products  # noqa: E402


class Ratchet(unittest.TestCase):
    def test_no_product_gains_gaps(self):
        base = json.loads(build_products.RATCHET.read_text(encoding="utf-8"))["gaps"]
        now = build_products.current_gaps()
        worse = {k: (base[k], v) for k, v in now.items() if k in base and v > base[k]}
        self.assertEqual(worse, {}, "a change added gaps to a product; supply the records or lower nothing else")

    def test_every_product_is_in_the_baseline(self):
        base = json.loads(build_products.RATCHET.read_text(encoding="utf-8"))["gaps"]
        self.assertEqual(set(build_products.current_gaps()) - set(base), set(),
                         "new product: run build_products.py ratchet --write to record its baseline")


class ReviewClearance(unittest.TestCase):
    """A gate PASS is not enough: an independent review of the exact render must leave no S0/S1 open."""

    def clearance(self, review):
        folder = Path(tempfile.mkdtemp())
        if review is not None:
            (folder / "p.review.json").write_text(json.dumps(review), encoding="utf-8")
        return build_products.review_clearance("p", "abc", folder)

    def test_missing_stale_or_blocking_reviews_hold_the_product_back(self):
        self.assertEqual(self.clearance(None), "NO_REVIEW")
        self.assertEqual(self.clearance({"findings": []}), "REVIEW_STALE")
        self.assertEqual(self.clearance({"render_digest": "old", "findings": []}), "REVIEW_STALE")
        self.assertEqual(self.clearance({"render_digest": "abc", "findings": [{"severity": "S1"}]}), "REVIEW_BLOCKING")

    def test_a_clean_review_of_this_render_clears_it(self):
        self.assertIsNone(self.clearance({"render_digest": "abc", "findings": [{"severity": "S2"}]}))
        self.assertIsNone(self.clearance({"render_digest": "abc", "findings": [{"severity": "S1", "resolved": "fixed in abc"}]}))


if __name__ == "__main__":
    unittest.main()
