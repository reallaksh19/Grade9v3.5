"""Phase 7 ratchet: a product's gap count may only go down (products/ratchet.v1.json)."""
from __future__ import annotations

import json
import sys
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


if __name__ == "__main__":
    unittest.main()
