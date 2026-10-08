"""Bounded GitHub witness authentication contract (#68, no network in unit tests)."""
from __future__ import annotations

import unittest

from Shared.tools import test_source_custody, verify_test_source_witnesses


class WitnessAuthenticationTest(unittest.TestCase):
    def setUp(self):
        self.ref = "github:reallaksh19/Grade9v3.5#68:6050805060"
        self.body = "ieep202.pdf ieep2an.pdf u02-q02 u02-q06 verbatim"
        self.payload = {
            "id": 6050805060,
            "html_url": "https://github.com/reallaksh19/Grade9v3.5/issues/68#issuecomment-6050805060",
            "user": {"login": "reallaksh19"},
            "body": self.body,
        }

    def test_pinned_comment_identity_and_context(self):
        self.assertTrue(test_source_custody._evidence_ref(self.ref))
        verify_test_source_witnesses.verify_payload(self.ref, self.payload)

    def test_corrected_q1_witness_requires_exact_ncERT_source_context(self):
        ref = "github:reallaksh19/Grade9v3.5#68:6053770988"
        payload = {
            "id": 6053770988,
            "html_url": "https://github.com/reallaksh19/Grade9v3.5/issues/68#issuecomment-6053770988",
            "user": {"login": "reallaksh19"},
            "body": "ieep202.pdf ieep2an.pdf Which one of the following is a polynomial? Q1 (C)",
        }
        verify_test_source_witnesses.verify_payload(ref, payload)
        payload["body"] = "ieep202.pdf ieep2an.pdf Q1 (C)"
        with self.assertRaisesRegex(ValueError, "context absent"):
            verify_test_source_witnesses.verify_payload(ref, payload)

    def test_unknown_or_spoofed_witness_fails_closed(self):
        self.assertFalse(test_source_custody._evidence_ref(
            "github:reallaksh19/Grade9v3.5#68:9999999999"))
        for mutation in (
            {"id": 6050805061},
            {"html_url": "https://github.com/elsewhere/issues/68#issuecomment-6050805060"},
            {"user": {"login": "unreviewed-contributor"}},
            {"body": "ieep202.pdf only"},
        ):
            with self.subTest(mutation=mutation):
                payload = dict(self.payload, **mutation)
                with self.assertRaisesRegex(ValueError, "mismatch|context absent"):
                    verify_test_source_witnesses.verify_payload(self.ref, payload)


if __name__ == "__main__":
    unittest.main()
