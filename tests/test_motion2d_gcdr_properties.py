#!/usr/bin/env python3
"""Regression tests for Motion-in-2D GCDR scientific property sweeps."""
from __future__ import annotations

import unittest

from Physics.tools import motion2d_gcdr_properties


class Motion2DGCDRPropertiesTest(unittest.TestCase):
    def test_motion2d_gcdr_properties_hold(self):
        report = motion2d_gcdr_properties.audit()
        self.assertTrue(report["passed"], report["findings"])
        self.assertEqual(report["findings"], [])


if __name__ == "__main__":
    unittest.main()
