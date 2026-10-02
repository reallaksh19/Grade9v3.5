import html
import re
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
PRACTICE = REPO / "standalone" / "practice"

PLACEHOLDERS = (
    "Apply 2D projectile kinematic decomposition.",
    "Follow step-by-step kinematics setup and verify dimensional units.",
    "Apply 2D vector kinematics and equations of motion.",
    "Apply ΣF = ma along acceleration axis.",
    "Use kinematic equations: v = u + at, s = ut + 0.5at², v² - u² = 2as.",
)

def text_of(path):
    return path.read_text(encoding="utf-8", errors="replace")

def prompts(markup):
    return [
        html.unescape(re.sub(r"<[^>]+>", " ", x)).strip()
        for x in re.findall(r'<p class="q-prompt">(.*?)</p>', markup, flags=re.S)
    ]

class TestPracticeContentQuality(unittest.TestCase):
    def test_generic_reveal_placeholders_are_removed(self):
        targets = [
            "core2-motion-1d-straight-line-tablet.html",
            "core1a-physics-nlm-tablet.html",
            "core1a-physics-motion-2d-ncert-tablet.html",
            "core1a-sba-motion-in-a-plane-master-tablet.html",
            "core2-motion-consolidated-practice-tablet.html",
        ]
        for name in targets:
            markup = text_of(PRACTICE / name)
            for placeholder in PLACEHOLDERS:
                self.assertNotIn(placeholder, markup, f"{name} still contains generic reveal text")

    def test_attempt_prompts_are_complete_questions(self):
        cases = [
            ("core2-motion-1d-straight-line-tablet.html", 14),
            ("core1a-physics-nlm-tablet.html", 20),
            ("core1a-physics-motion-2d-ncert-tablet.html", 9),
        ]
        for name, count in cases:
            ps = prompts(text_of(PRACTICE / name))[:count]
            self.assertEqual(len(ps), count, f"{name}: expected {count} attempt prompts")
            for p in ps:
                self.assertNotIn("answer protected QUESTION", p, f"{name}: extraction wrapper leaked into prompt")
                self.assertRegex(p, r"[?.!]$", f"{name}: incomplete/truncated prompt: {p}")

    def test_method_cards_are_explicitly_answerable(self):
        sba = text_of(PRACTICE / "core1a-sba-motion-in-a-plane-master-tablet.html")
        consolidated = text_of(PRACTICE / "core2-motion-consolidated-practice-tablet.html")
        self.assertGreaterEqual(sba.count("Method check —"), 50)
        self.assertGreaterEqual(consolidated.count("Method check —") + consolidated.count("Review check —"), 48)

    def test_motion_2d_attempts_are_self_contained_short_answer_tasks(self):
        markup = text_of(PRACTICE / "core2-motion-in-a-plane-tablet.html")
        cards = re.findall(r'<article[^>]*id="q\d{2}"[^>]*>(.*?)</article>', markup, flags=re.S)
        self.assertEqual(len(cards), 59)
        for index, card in enumerate(cards, start=1):
            self.assertIn("attempt-question-card", card, f"q{index:02d}: missing visible learner question")
            self.assertNotIn('<button class="opt-btn"', card, f"q{index:02d}: unrecoverable A/B/C/D choice UI remains")
            self.assertIn("Short-answer task", card, f"q{index:02d}: answer mode not made explicit")

        q13 = re.search(r'<article[^>]*id="q13"[^>]*>(.*?)</article>', markup, flags=re.S).group(1)
        self.assertIn("u = 8 m s⁻¹", q13)
        self.assertIn("θ = 60°", q13)
        self.assertIn("g = 10 m s⁻²", q13)

        q23 = re.search(r'<article[^>]*id="q23"[^>]*>(.*?)</article>', markup, flags=re.S).group(1)
        self.assertIn("u = 20 m s⁻¹", q23)
        self.assertIn("g = 10 m s⁻²", q23)
        self.assertIn("starts 24 m", q23)

        q29 = re.search(r'<article[^>]*id="q29"[^>]*>(.*?)</article>', markup, flags=re.S).group(1)
        self.assertIn("100 cm s⁻¹", q29)
        self.assertIn("30 cm", q29)
        self.assertIn("980 cm s⁻²", q29)

        q34 = re.search(r'<article[^>]*id="q34"[^>]*>(.*?)</article>', markup, flags=re.S).group(1)
        self.assertIn("78.4 m", q34)
        self.assertIn("10 m s⁻¹", q34)
        self.assertIn("20 m s⁻¹", q34)
        self.assertIn("g = 9.8 m s⁻²", q34)

    def test_motion_2d_reasoning_and_ambiguous_source_regressions(self):
        markup = text_of(PRACTICE / "core2-motion-in-a-plane-tablet.html")
        self.assertNotIn("√(2/5) times the launch speed", markup)
        q40 = re.search(r'<article[^>]*id="q40"[^>]*>(.*?)</article>', markup, flags=re.S).group(1)
        self.assertIn("v_apex² = (2/5)v_half²", q40)
        self.assertIn("5uₓ² = 2uₓ² + uᵧ²", q40)

        q37 = re.search(r'<article[^>]*id="q37"[^>]*>(.*?)</article>', markup, flags=re.S).group(1)
        self.assertIn("540 km h⁻¹ = 540/3.6 = 150 m s⁻¹", q37)
        self.assertIn("500 sinφ = 150", q37)

        q48 = re.search(r'<article[^>]*id="q48"[^>]*>(.*?)</article>', markup, flags=re.S).group(1)
        self.assertIn("Δx = ½(g/4)(2uᵧ/g)² = uᵧ²/(2g) = H", q48)

        for qid in ("q49", "q51"):
            card = re.search(rf'<article[^>]*id="{qid}"[^>]*>(.*?)</article>', markup, flags=re.S).group(1)
            self.assertIn("SOURCE INCOMPLETE", card)
            self.assertNotRegex(card, r"Option [A-D]|option \([a-d]\)")
            self.assertNotIn("source answer key", card.lower())
            self.assertNotIn("printed source key", card.lower())

    def test_reported_figure_label_contradictions_are_removed(self):
        vectors = text_of(PRACTICE / "core1a-physics-vectors-tablet.html")
        self.assertNotIn("Q0uadrant", vectors)
        self.assertNotIn("Quadrant II", vectors)
        self.assertNotIn("Aₓ < 0", vectors)
        self.assertNotIn("+8 m east", vectors)
        self.assertNotIn("-5 m west", vectors)

        one_d = text_of(PRACTICE / "core2-motion-1d-straight-line-tablet.html")
        self.assertNotIn("200 m ahead", one_d)
        self.assertNotIn("utnimdeer", one_d)
        self.assertNotIn("passeAs ixs", one_d)

    def test_advanced_core2_items_are_labelled_extensions(self):
        markup = text_of(PRACTICE / "core2-motion-in-a-plane-tablet.html")
        for qid in ("q45", "q46", "q50", "q53", "q57"):
            m = re.search(rf'<article[^>]*id="{qid}"[^>]*>(.*?)</article>', markup, flags=re.S)
            self.assertIsNotNone(m, f"{qid} missing")
            self.assertIn("Declared extension", m.group(1), f"{qid} missing extension label")
        self.assertIn("SBA-21 · Declared extension", text_of(PRACTICE / "core1a-sba-motion-in-a-plane-master-tablet.html"))

if __name__ == "__main__":
    unittest.main()
