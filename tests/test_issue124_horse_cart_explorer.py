"""Issue #124: horse-cart transfer inside the existing NLM third-law explorer."""
from __future__ import annotations

import json
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


class HorseCartExplorerContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.package = json.loads(
            (REPO / "Physics/library/phy-nlm-first-law.v1.json").read_text(encoding="utf-8")
        )
        cls.html = (
            REPO / "public/physics/nlm/explorers/connected-blocks/index.html"
        ).read_text(encoding="utf-8")
        cls.resources = {row["id"]: row for row in cls.package["resources"]}

    def test_reuses_existing_canonical_activity_owner(self):
        row = self.resources["ACT-NLM-CONNECTED-BLOCKS-THIRD-LAW"]
        self.assertEqual(
            row["locator"],
            "public/physics/nlm/explorers/connected-blocks/index.html",
        )
        self.assertIn("CAP-NLM-THIRD-LAW", row["supports_claims"])
        self.assertIn("CAP-NLM-FBD-BODY-OWNERSHIP", row["supports_claims"])
        self.assertNotIn("ACT-NLM-HORSE-CART-SYSTEM-BOUNDARY", self.resources)

    def test_horse_cart_transfer_is_interactive(self):
        for control in (
            'id="horseMass"',
            'id="cartMass"',
            'id="groundTraction"',
            "syncHorseCart()",
            "resetHorseCart()",
        ):
            self.assertIn(control, self.html)

    def test_explorer_keeps_partner_forces_on_different_bodies(self):
        self.assertIn("horse on cart = +T", self.html)
        self.assertIn("cart on horse = -T", self.html)
        self.assertIn("they act on different bodies", self.html)
        self.assertIn("one body's net-force equation", self.html)

    def test_combined_system_uses_external_ground_force(self):
        self.assertIn(
            "Ground-on-horse traction crosses the system boundary and remains external",
            self.html,
        )
        self.assertIn(
            "F<sub>g</sub> = (m<sub>h</sub> + m<sub>c</sub>)a",
            self.html,
        )
        self.assertIn(
            "the horse–cart interaction is internal",
            self.html,
        )

    def test_single_body_equations_preserve_third_law_ownership(self):
        self.assertIn(
            "Horse: F<sub>g</sub> - T = m<sub>h</sub>a",
            self.html,
        )
        self.assertIn(
            "Cart: T = m<sub>c</sub>a",
            self.html,
        )

    def test_slice_does_not_expand_to_other_open_backlog(self):
        lower = self.html.lower()
        horse_section = lower[lower.index("horse–cart transfer"):]
        self.assertNotIn("pseudo force", horse_section)
        self.assertNotIn("centripetal", horse_section)


if __name__ == "__main__":
    unittest.main()
