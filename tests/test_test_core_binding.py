from __future__ import annotations

import json
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]


class TestTestProductionCoreBinding(unittest.TestCase):
    def test_shared_package_schema_is_the_only_package_schema_for_test(self):
        schema_path = REPO / "Shared/library/package.schema.json"
        schema = json.loads(schema_path.read_text(encoding="utf-8"))

        self.assertIn("TEST", schema["properties"]["subject"]["enum"])
        self.assertEqual(
            list((REPO / "TEST").rglob("package.schema.json")),
            [],
            "TEST must consume the production package schema rather than fork it",
        )


if __name__ == "__main__":
    unittest.main()
