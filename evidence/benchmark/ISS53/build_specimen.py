#!/usr/bin/env python3
"""Build the Issue #53 Mathematics: Polynomials in One Variable specimen.

This is evidence for the minimal-prompt authoring workflow (Agent B).
The ten owner questions stay verbatim and carry OWNER_SUPPLIED custody.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

REPO = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
OUT = HERE / "generated"
OUT.mkdir(parents=True, exist_ok=True)

# Historical candidate QRT evidence is retained for answer/hint provenance.
qrt_path = HERE / "qrt-review.json"
QRT = json.loads(qrt_path.read_text(encoding="utf-8"))

# Current academic authority for this repair wave.  This file deliberately
# supersedes historical classification/acceptance claims without rewriting them.
reanalysis_path = HERE / "academic-reanalysis.v1.json"
REANALYSIS = json.loads(reanalysis_path.read_text(encoding="utf-8"))
ACADEMIC = {row["q"]: row for row in REANALYSIS["rows"]}

# Load verbatim stems from owner-core-prompt.md
core_text = (HERE / "owner-core-prompt.md").read_text(encoding="utf-8")
lines = core_text.splitlines()

STEMS: dict[str, str] = {}
curr_q = None
curr_lines = []
for line in lines:
    if line.startswith("### Q"):
        if curr_q:
            STEMS[curr_q] = "\n\n".join([p for p in "\n".join(curr_lines).split("\n\n") if p.strip()]).strip()
        curr_q = line.strip().split()[1]
        curr_lines = []
    elif line.startswith("## B —") or line.startswith("## B"):
        if curr_q:
            STEMS[curr_q] = "\n\n".join([p for p in "\n".join(curr_lines).split("\n\n") if p.strip()]).strip()
            curr_q = None
    elif curr_q:
        curr_lines.append(line)

print("Parsed stems count:", len(STEMS))

SRC = "SRC-OWNER-ISSUE53-POLY"
BUCKET = "BUCKET-MATH-09-POLYNOMIALS"

CAP_TERMS = "CAP-MATH-POLY-TERMS-COEFFS"
CAP_DEF   = "CAP-MATH-POLY-DEFINITION-CLASSIFICATION"
CAP_ID    = "CAP-MATH-POLY-IDENTITIES-AND-CONSTRUCTION"

MIC_TERMS = "MIC-MATH-POLY-TERMS-COEFFS"
MIC_DEF   = "MIC-MATH-POLY-DEFINITION-CLASSIFICATION"
MIC_ID    = "MIC-MATH-POLY-IDENTITIES-AND-CONSTRUCTION"

REP_COEFF = "REP-MATH-POLY-COEFF-TABLE"
REP_EXP   = "REP-MATH-POLY-EXPONENT-CLASSIFICATION"
REP_AREA  = "REP-MATH-POLY-SQUARE-CONSTRUCTION"
REP_RECT  = "REP-MATH-POLY-RECTANGLE-AREA"
REP_LIN   = "REP-MATH-POLY-LINEAR-ZERO"

REL_STD = "REL-MATH-POLY-STANDARD-FORM"
REL_SQR = "REL-MATH-POLY-SQUARE-IDENTITY"
REL_DIF = "REL-MATH-POLY-DIFF-SQUARES"
REL_LIN = "REL-MATH-POLY-LINEAR-ROOT"
REL_REC = "REL-MATH-POLY-RECT-AREA"

FAM_TERMS = "FAM-MATH-POLY-TERMS"
FAM_DEF   = "FAM-MATH-POLY-DEFINITIONS"
FAM_ID    = "FAM-MATH-POLY-IDENTITIES"
FAM_LIN   = "FAM-MATH-POLY-LINEAR"

BANK_IDS = {f"Q{i}": f"OWN-ISSUE53-POLY-{i:02d}" for i in range(1, 11)}

PRIMARY_CAP = {
    "Q1": CAP_TERMS, "Q2": CAP_DEF, "Q3": CAP_DEF, "Q4": CAP_TERMS, "Q5": CAP_TERMS,
    "Q6": CAP_ID,    "Q7": CAP_ID,  "Q8": CAP_ID,  "Q9": CAP_ID,    "Q10": CAP_ID,
}
PRIMARY_MIC = {
    "Q1": MIC_TERMS, "Q2": MIC_DEF, "Q3": MIC_DEF, "Q4": MIC_TERMS, "Q5": MIC_TERMS,
    "Q6": MIC_ID,    "Q7": MIC_ID,  "Q8": MIC_ID,  "Q9": MIC_ID,    "Q10": MIC_ID,
}
FAMILY = {
    "Q1": FAM_TERMS, "Q2": FAM_DEF, "Q3": FAM_DEF, "Q4": FAM_TERMS, "Q5": FAM_TERMS,
    "Q6": FAM_ID,    "Q7": FAM_ID,  "Q8": FAM_ID,  "Q9": FAM_ID,    "Q10": FAM_LIN,
}
# The supplied source questions contain no source-given figures.  Authored
# representations are therefore not attached to the independent Core2 attempt.
# Exact-case teaching representations are owned by Core1A / post-attempt support.
QUESTION_FIGURES = {f"Q{i}": [] for i in range(1, 11)}

def base(record_id: str, source: bool = True) -> dict:
    return {
        "id": record_id,
        "version": "0.1.0",
        "status": "CANDIDATE",
        "source_refs": [SRC] if source else [],
        "evidence_refs": [],
        "extensions": {},
    }

def step(step_id: str, role: str, action: str, why: str, output: str) -> dict:
    return {"id": step_id, "role": role, "action": action, "why_valid": why, "inputs": [], "output": output}

def model_answer(summary: str, reasoning: list[str], check: str) -> dict:
    return {
        "kind": "MODEL_RESPONSE",
        "summary": summary,
        "reasoning": reasoning,
        "check": check,
        "acceptable_alternatives": [],
        "subpart_answers": [],
        "verification_status": "CHECKED_BY_AUTHOR",
    }

def misconception(wrong: str, diagnostic: str, repair: str) -> dict:
    return {"wrong_idea": wrong, "diagnostic_prompt": diagnostic, "repair": repair}

def representation(record_id: str, kind: str, purpose: str, asset: str, stages: list[tuple[str, str, str]], correspondence: list[dict]) -> dict:
    return {
        **base(record_id, source=False),
        "kind": kind,
        "purpose": purpose,
        "required_elements": [s[1] for s in stages],
        "relation_refs": {
            REP_COEFF: [REL_STD],
            REP_EXP: [REL_STD],
            REP_AREA: [REL_SQR],
            REP_RECT: [REL_REC],
            REP_LIN: [REL_LIN],
        }.get(record_id, []),
        "read_order": [s[2] for s in stages],
        "instance_constraints": ["Pre-attempt stages must orient without disclosing the final target answer W."],
        "accessibility": ["The SVG has an accessible name, title and description.", "Text labels duplicate any line-style meaning."],
        "misleading_alternatives": ["Treating missing terms as non-existent rather than coefficient 0.", "Omitting cross-terms when squaring binomials."],
        "rendered_asset_refs": [asset],
        "scene_instances": [],
        "correspondence": correspondence,
        "reveal_stages": [{"id": sid, "label": label, "purpose": job, "visible_elements": [label]} for sid, label, job in stages],
        "extensions": {"grade9v3:stage_mode": "CUMULATIVE"},
    }

resource = {
    **base(SRC, source=False),
    "title": "Issue #53 owner-supplied Grade 9 Mathematics Polynomials benchmark questions",
    "origin": "AUTHORED",
    "locator": "https://github.com/reallaksh19/Grade9v3.5/issues/53",
    "edition": "Owner prompt captured 2026-10-05",
    "section": "CORE PROMPT — VERBATIM OWNER INPUT / THE 10 QUESTIONS",
    "last_checked": "2026-10-05",
    "access_status": "FULL_ITEM_INSPECTED",
    "rights_status": "Owner-supplied text; no exam, textbook, year or official-answer identity claimed.",
    "snapshot_ref": None,
    "snapshot_digest": None,
    "role": ["QUESTION_BANK", "AUTHOR_CREATED"],
    "supports_claims": [],
    "entry_capabilities": [],
    "depth": ["COMPETITION"],
    "selection_reason": "Exact custody surface for the ten questions used by the Issue #53 run.",
    "fallback": [],
}

bucket = {
    **base(BUCKET),
    "title": "Polynomials in One Variable with Real Coefficients",
    "topic": "Polynomials",
    "intrinsic_badge": "MEDIUM",
    "badge_reason": "Core difficulty involves positional power alignment with explicit zero entries, algebraic identity expansion without omitting cross-terms, and synthesizing unique linear polynomials from constraints.",
    "depth_overlay": "FOUNDATION",
    "curriculum_mappings": [],
    "prerequisite_refs": [],
    "primary_representation_ref": REP_COEFF,
}

capabilities = [
    {
        **base(CAP_TERMS),
        "action": "Inventory polynomial degree, leading coefficient, constant term, and missing coefficients in one variable; represent terms in positional tables with explicit zero entries and perform like-term addition",
        "success_criterion": "Accurately state degree, leading coefficient, and constant; place missing powers as coefficient 0; add polynomials by grouping like terms in descending order",
        "prerequisite_refs": [],
        "curriculum_mappings": [],
        "external_provider": None,
        "acceptance_status": "CANDIDATE"
    },
    {
        **base(CAP_DEF),
        "action": "Evaluate algebraic expressions against defining criteria of polynomials in one variable with real coefficients (non-negative integer exponents, real coefficients) and compute polynomial values at specific points",
        "success_criterion": "Identify non-negative integer exponents W = {0, 1, 2, ...}; state degrees of valid polynomials and failed conditions for rejected expressions; evaluate p(k) with brackets",
        "prerequisite_refs": [CAP_TERMS],
        "curriculum_mappings": [],
        "external_provider": None,
        "acceptance_status": "CANDIDATE"
    },
    {
        **base(CAP_ID),
        "action": "Apply standard algebraic identities (square of binomial, difference of squares), geometric area models, universal algebraic proofs, and synthesize unique linear polynomials from constraints",
        "success_criterion": "Expand products using distributivity without omitting cross-terms; factorise difference of squares; model rectangular area with physical units; construct and prove uniqueness of linear polynomials",
        "prerequisite_refs": [CAP_TERMS, CAP_DEF],
        "curriculum_mappings": [],
        "external_provider": None,
        "acceptance_status": "CANDIDATE"
    },
]

relations = [
    {
        **base(REL_STD),
        "expression": "p(x) = a_n x^n + a_{n-1} x^{n-1} + ... + a_1 x + a_0",
        "meaning": "Standard polynomial form in one variable x as a finite sum of terms whose exponents are non-negative integers.",
        "symbols": [
            {"symbol": "x", "meaning": "variable", "unit_or_domain": "real numbers R"},
            {"symbol": "n", "meaning": "degree of the polynomial", "unit_or_domain": "non-negative integers W = {0, 1, 2, ...}"},
            {"symbol": "a_n", "meaning": "leading coefficient", "unit_or_domain": "non-zero real numbers R \\ {0}"},
            {"symbol": "a_0", "meaning": "constant term", "unit_or_domain": "real numbers R"}
        ],
        "conditions": ["n in W", "a_n != 0 for degree n"],
        "derivation": [
            step("STD-D1", "DECLARE", "State the general form of a single-variable polynomial.", "Axiomatic polynomial ring definition over R.", "polynomial formula")
        ],
        "limits": ["Zero polynomial has undefined degree."],
        "checks": ["Verify non-negative integer exponents for all terms."],
        "gate_relation_ref": None
    },
    {
        **base(REL_SQR),
        "expression": "(a + b)^2 = a^2 + 2ab + b^2",
        "meaning": "Expansion of a binomial square via the distributive law yields four terms combining to three distinct terms with cross-term 2ab.",
        "symbols": [
            {"symbol": "a", "meaning": "first term", "unit_or_domain": "real numbers R"},
            {"symbol": "b", "meaning": "second term", "unit_or_domain": "real numbers R"}
        ],
        "conditions": ["Holds for all a, b in R"],
        "derivation": [
            step("SQR-D1", "TRANSFORM", "Expand (a+b)(a+b) = a^2 + ab + ba + b^2.", "Distributive property of multiplication over addition.", "four term sum"),
            step("SQR-D2", "TRANSFORM", "Combine middle terms ab + ba = 2ab.", "Commutative property of multiplication in R.", "a^2 + 2ab + b^2")
        ],
        "limits": ["Does not equate to a^2 + b^2 unless 2ab = 0."],
        "checks": ["Check with numerical values e.g. a=1, b=3: (4)^2 = 16 = 1 + 6 + 9."],
        "gate_relation_ref": None
    },
    {
        **base(REL_DIF),
        "expression": "a^2 - b^2 = (a - b)(a + b)",
        "meaning": "Difference of two squares factors into the product of conjugate binomials whose cross-terms cancel.",
        "symbols": [
            {"symbol": "a", "meaning": "first term", "unit_or_domain": "real numbers R"},
            {"symbol": "b", "meaning": "second term", "unit_or_domain": "real numbers R"}
        ],
        "conditions": ["Holds for all a, b in R"],
        "derivation": [
            step("DIF-D1", "TRANSFORM", "Multiply (a-b)(a+b) = a^2 + ab - ba - b^2.", "Distributive property in R.", "four term sum"),
            step("DIF-D2", "TRANSFORM", "Cancel additive inverse terms +ab - ba = 0.", "Commutative and inverse properties in R.", "a^2 - b^2")
        ],
        "limits": ["Requires difference of squares, not sum of squares over R."],
        "checks": ["Verify by multiplying factors back: +ab - ab = 0."],
        "gate_relation_ref": None
    },
    {
        **base(REL_LIN),
        "expression": "p(x) = ax + b, a != 0, zero at x = -b/a",
        "meaning": "A linear polynomial has constant term p(0)=b and a unique zero at x = -b/a.",
        "symbols": [
            {"symbol": "a", "meaning": "leading coefficient", "unit_or_domain": "non-zero real numbers R \\ {0}"},
            {"symbol": "b", "meaning": "constant term", "unit_or_domain": "real numbers R"},
            {"symbol": "x", "meaning": "zero of polynomial", "unit_or_domain": "real numbers R"}
        ],
        "conditions": ["a != 0"],
        "derivation": [
            step("LIN-D1", "TRANSFORM", "Solve ax + b = 0 for x.", "Subtract b and divide by non-zero a.", "x = -b/a")
        ],
        "limits": ["If a = 0, the polynomial is constant and has either no zero (b != 0) or infinitely many zeroes (b = 0)."],
        "checks": ["Substitute zero back: a(-b/a) + b = -b + b = 0."],
        "gate_relation_ref": None
    },
    {
        **base(REL_REC),
        "expression": "Area(x) = (x + a)(x + b) = x^2 + (a + b)x + ab",
        "meaning": "Physical rectangular area is modeled by the product of length and width binomials in cm^2.",
        "symbols": [
            {"symbol": "x", "meaning": "variable dimension parameter", "unit_or_domain": "non-negative real numbers x >= 0"},
            {"symbol": "a", "meaning": "length offset", "unit_or_domain": "real numbers R"},
            {"symbol": "b", "meaning": "width offset", "unit_or_domain": "real numbers R"},
            {"symbol": "Area", "meaning": "enclosed rectangular area", "unit_or_domain": "square centimetres cm^2"}
        ],
        "conditions": ["x >= 0", "length > 0", "width > 0"],
        "derivation": [
            step("REC-D1", "DECLARE", "Apply rectangular area formula Area = length * width.", "Definition of 2D Euclidean area.", "Area product formula"),
            step("REC-D2", "TRANSFORM", "Expand (x+a)(x+b) = x^2 + (a+b)x + ab.", "Distributive law for polynomial products.", "decomposed area sum")
        ],
        "limits": ["Requires non-negative side lengths."],
        "checks": ["Check dimensions cm * cm = cm^2."],
        "gate_relation_ref": None
    }
]

representations = [
    representation(
        REP_COEFF,
        "TABLE_OF_VALUES",
        "Changed authored coefficient-table example displaying powers 3, 2, 1, 0 with an explicit zero entry.",
        "evidence/benchmark/ISS53/assets/poly-coeff-table.svg",
        [
            ("COEFF-STAGE-1", "Power Inventory", "Examine given polynomial powers and identify present and omitted exponents."),
            ("COEFF-STAGE-2", "Tabular Zero Entry", "Align coefficients by power row, inserting 0 for omitted power 2."),
            ("COEFF-STAGE-3", "Reconstruction Check", "Confirm polynomial reconstruction and index-aligned operations.")
        ],
        [
            {"element": "Power row k=2 with entry 0", "symbol": "0 · x²", "in_words": "explicit zero entry for the omitted quadratic term"},
            {"element": "Leading power row k=3", "symbol": "6 · x³", "in_words": "changed-anchor leading term of degree 3"},
            {"element": "Constant power row k=0", "symbol": "4 · x⁰", "in_words": "changed-anchor constant term"}
        ]
    ),
    representation(
        REP_EXP,
        "TABLE_OF_VALUES",
        "Changed authored examples for the non-negative-integer exponent criterion plus a separate bracketed-substitution example.",
        "evidence/benchmark/ISS53/assets/poly-exponent-classification.svg",
        [
            ("EXP-STAGE-1", "Whole Number Exponent Domain W", "Evaluate exponents against the whole-number domain W = {0, 1, 2, ...}."),
            ("EXP-STAGE-2", "Excluded Exponent Forms", "Identify non-polynomial expressions with negative or fractional exponents."),
            ("EXP-STAGE-3", "Point Evaluation Precedence", "Evaluate polynomial values at input points with bracketed substitution.")
        ],
        [
            {"element": "Whole-number exponent set", "symbol": "{0, 1, 2, ...}", "in_words": "defining exponent requirement for a polynomial in x"},
            {"element": "Changed boundary powers", "symbol": "x^-1, x^(2/3)", "in_words": "negative or fractional exponents violate the criterion"},
            {"element": "Bracketed substitution", "symbol": "s(3)=2(3)^2+(3)-1", "in_words": "replace every occurrence of the variable before arithmetic"}
        ]
    ),
    representation(
        REP_AREA,
        "AREA_MODEL",
        "2D geometric area decomposition illustrating polynomial multiplication, cross-terms, and identity expansions.",
        "evidence/benchmark/ISS53/assets/poly-area-model.svg",
        [
            ("AREA-STAGE-1", "Rectangle Frame", "Define outer dimensions length (x+3) and width (x+1)."),
            ("AREA-STAGE-2", "Decomposed Area Sub-regions", "Subdivide area into x^2, 3x, 1x, and 3 sub-rectangles."),
            ("AREA-STAGE-3", "Combined Like Terms & Identity Contrast", "Synthesize total area x^2+4x+3 cm^2 and contrast with (x+3)^2 error.")
        ],
        [
            {"element": "Square sub-region", "symbol": "x²", "in_words": "area formed by multiplying dimension x by x"},
            {"element": "Rectangular side strips", "symbol": "3x + 1x", "in_words": "cross-term areas combining to 4x"},
            {"element": "Unit squares block", "symbol": "3", "in_words": "constant corner area formed by 3 times 1"}
        ]
    ),
    representation(
        REP_LIN,
        "COORDINATE_GRAPH",
        "Cartesian coordinate plane illustrating constant term y-intercept, zero x-intercept, and uniqueness of linear line.",
        "evidence/benchmark/ISS53/assets/poly-linear-zero.svg",
        [
            ("LIN-STAGE-1", "Constant Term Point", "Plot y-intercept (0, 2) corresponding to constant term p(0)=2."),
            ("LIN-STAGE-2", "Zero Root Point", "Plot x-intercept (1, 0) corresponding to zero p(1)=0."),
            ("LIN-STAGE-3", "Unique Linear Polynomial", "Draw straight line y = -2x + 2 and prove uniqueness of linear polynomial.")
        ],
        [
            {"element": "Y-axis intercept point (0, 2)", "symbol": "p(0) = 2", "in_words": "constant term fixes the vertical intercept of the linear line"},
            {"element": "X-axis intercept point (1, 0)", "symbol": "p(1) = 0", "in_words": "zero of the polynomial fixes the horizontal root on the x-axis"},
            {"element": "Unique straight line slope", "symbol": "m = -2", "in_words": "slope uniquely fixed by the two constraint points yielding y = -2x + 2"}
        ]
    )
]

microtopics = [
    {
        **base(MIC_TERMS),
        "title": "Polynomial definition, terms, coefficient tables, and like-term addition",
        "bucket_id": BUCKET,
        "primary_capability_ref": CAP_TERMS,
        "intrinsic_badge": "MEDIUM",
        "badge_reason": "Learners must record omitted powers as coefficient 0 and group terms by identical exponents.",
        "entry_assumptions": ["Integer arithmetic, signed-number operations, powers."],
        "inferential_jump": "When a power of the variable does not appear in a polynomial, its coefficient is 0, contributing 0 to the sum while preserving positional alignment.",
        "teaching_path": [
            step("TERMS-T1", "DECLARE", "Identify polynomial degree as the highest power with non-zero coefficient, and identify leading and constant terms.", "Axiomatic polynomial definitions.", "identified degree and main terms"),
            step("TERMS-T2", "TRANSFORM", "Decompose polynomial into tabular rows for each power, inserting coefficient 0 for missing terms.", "Zero times any power contributes zero to the value.", "complete positional table with explicit zero entries"),
            step("TERMS-T3", "VERIFY", "Add polynomials by grouping like terms having identical exponents and combining coefficients via distributivity.", "Only like terms share a common variable factor.", "verified polynomial sum in descending order")
        ],
        "relation_refs": [REL_STD],
        "representation_refs": [REP_COEFF],
        "question_family_refs": [FAM_TERMS],
        "misconceptions": [
            misconception(
                "A missing term has no coefficient or is undefined rather than coefficient 0.",
                "What number multiplied by x^2 leaves the polynomial value unchanged?",
                "0 * x^2 = 0, so the omitted power is present with coefficient 0."
            )
        ],
        "exit_task": {
            "prompt": "For p(x) = 7x^4 - 3x + 1, list the coefficients of x^4, x^3, x^2, x^1, and x^0.",
            "source_ref": SRC,
            "answer": model_answer("Coefficients: x^4 is 7; x^3 is 0; x^2 is 0; x^1 is -3; x^0 is 1.", ["Powers 3 and 2 do not appear explicitly.", "Missing powers are assigned coefficient 0."], "Reconstruction: 7x^4 + 0x^3 + 0x^2 - 3x + 1 = 7x^4 - 3x + 1."),
            "oracle": {"no_numeric_claim": "The task checks coefficient assignment with explicit zero entries."}
        },
        "research_contribution": "Q1, Q4, and Q5 establish positional coefficient alignment and like-term operations.",
        "prerequisite_refs": [],
        "lineage": [],
        "elicitation": {
            "predict": {"prompt": "Can a term with x^2 be added to 5x^3 - 2x + 7 without changing its value?", "defensible_answer": "Yes, by adding 0x^2, since 0 times x^2 equals 0."},
            "attempt": {
                "produces": "A coefficient table inventorying powers 3, 2, 1, 0.",
                "closure": "RUBRIC",
                "rubric": [{"criterion": "Assigns coefficient 0 to power 2.", "evidence_of": "Understands null zero-value entry in polynomials."}],
                "accepted": ["Coefficient of x^2 is 0."],
                "rejected": ["Coefficient of x^2 is none or undefined."]
            },
            "reconstruct": {
                "route": [
                    {"ask": "What is the highest power present with a non-zero coefficient?", "why_this_ask": "Defines degree."},
                    {"ask": "How do we represent omitted powers in positional arithmetic?", "why_this_ask": "Establishes explicit zero coefficient entry."}
                ],
                "differs_from_teaching_path": "Starts from degree identification rather than general polynomial definition."
            },
            "boundary_test": {"prompt": "What is the degree of a non-zero constant polynomial like -5?", "answer": "Degree 0, since -5 = -5x^0.", "confirms": "Constant polynomials possess degree 0."}
        },
        "construction_units": [
            {
                "id": "CU-MATH-TERMS-COEFFS",
                "decision": "Record missing powers with coefficient 0 and group like terms by exponent",
                "step_refs": ["TERMS-T1", "TERMS-T2", "TERMS-T3"],
                "representation_ref": REP_COEFF,
                "reveal_stage_refs": ["COEFF-STAGE-1", "COEFF-STAGE-2", "COEFF-STAGE-3"],
                "bank_anchor_ref": BANK_IDS["Q1"],
                "crux_question_refs": [BANK_IDS["Q1"], BANK_IDS["Q4"], BANK_IDS["Q5"]],
                "crux_step_ref": "TERMS-T2",
                "misconception_indexes": [0],
                "independent_checks": [
                    {"statement": "CHECK: Reconstruct polynomial from table: sum a_k x^k matches original.", "role": "CHECK"},
                    {"statement": "APPLY: Add 2x^2 + 3x - 5 and -x^2 + 4x + 2 by combining coefficients of like powers.", "role": "APPLY"},
                    {"statement": "CONNECT: Connect zero entry to null contribution 0 * x^2 = 0.", "role": "CONNECT"}
                ]
            }
        ],
        "compact_anchor": {"prompt": "Missing power in a polynomial? Insert coefficient 0.", "result": "0 * x^k = 0 preserves value and column alignment.", "representation_ref": REP_COEFF}
    },
    {
        **base(MIC_DEF),
        "title": "Polynomial classification, exponent conditions, and evaluation at a point",
        "bucket_id": BUCKET,
        "primary_capability_ref": CAP_DEF,
        "intrinsic_badge": "MEDIUM",
        "badge_reason": "Learners must verify that all exponents of the variable are non-negative integers W = {0, 1, 2, ...}.",
        "entry_assumptions": ["Exponent rules, index notation (negative and fractional exponents)."],
        "inferential_jump": "An expression is a polynomial if and only if all powers of the variable are whole numbers; reciprocals (x^-1) and radicals (x^1/2) fail this condition.",
        "teaching_path": [
            step("DEF-T1", "DECLARE", "State the defining criterion: every exponent of x must be a non-negative integer {0, 1, 2, ...}.", "Formal polynomial definition over R.", "polynomial criterion"),
            step("DEF-T2", "TRANSFORM", "Rewrite candidate expressions in power form and evaluate exponents against W.", "Index laws convert reciprocals and radicals into exponents.", "evaluated exponent set"),
            step("DEF-T3", "VERIFY", "Evaluate polynomial at an input point using bracketed substitution and order of operations.", "Evaluation p(k) follows standard arithmetic precedence.", "evaluated polynomial value")
        ],
        "relation_refs": [REL_STD],
        "representation_refs": [REP_EXP],
        "question_family_refs": [FAM_DEF],
        "misconceptions": [
            misconception(
                "A constant like -5 is not a polynomial because no variable is visible, or 1/x is a polynomial because power of x in denominator is 1.",
                "What is the exponent of x when 1/x is written in index form x^n?",
                "1/x = x^-1 has negative exponent -1 not in W; constant -5 = -5x^0 has valid whole-number exponent 0."
            )
        ],
        "exit_task": {
            "prompt": "Determine whether x^3 - 4/x^2 + 5 is a polynomial in x. Justify your answer.",
            "source_ref": SRC,
            "answer": model_answer("No, it is not a polynomial. In index form, 4/x^2 = 4x^-2, which has a negative exponent (-2), violating the non-negative integer exponent condition.", ["Exponents of x are 3, -2, 0.", "-2 is not a whole number."], "Condition failed: negative exponent -2."),
            "oracle": {"no_numeric_claim": "The task assesses polynomial defining condition verification."}
        },
        "research_contribution": "Q2 and Q3 establish boundary conditions for polynomial classification and evaluation.",
        "prerequisite_refs": [CAP_TERMS],
        "lineage": [],
        "elicitation": {
            "predict": {"prompt": "Is sqrt(x) + 1 a polynomial in x?", "defensible_answer": "No, because sqrt(x) has fractional exponent 1/2, which is not a whole number."},
            "attempt": {
                "produces": "Classification of expressions into polynomials and non-polynomials with reason.",
                "closure": "RUBRIC",
                "rubric": [{"criterion": "Identifies negative and fractional exponents as non-polynomial.", "evidence_of": "Understands exponent constraint."}],
                "accepted": ["Rejected due to negative or fractional power."],
                "rejected": ["Claiming 1/x is polynomial because power is 1."]
            },
            "reconstruct": {
                "route": [
                    {"ask": "What is the defining condition on exponents for a polynomial?", "why_this_ask": "Grounds classification in axioms."},
                    {"ask": "How do you rewrite 1/x and sqrt(x) in exponent form?", "why_this_ask": "Exposes non-integer and negative powers."}
                ],
                "differs_from_teaching_path": "Starts from radical and reciprocal forms rather than standard definition."
            },
            "boundary_test": {"prompt": "Is (x^2 - 1)/(x - 1) a polynomial in x?", "answer": "No; rational expressions with variable denominators are rational functions, not polynomials in x (undefined at x=1).", "confirms": "Domain and algebraic form boundaries."}
        },
        "construction_units": [
            {
                "id": "CU-MATH-POLY-DEF",
                "decision": "Check all exponents against non-negative integers {0, 1, 2, ...} and evaluate with brackets",
                "step_refs": ["DEF-T1", "DEF-T2", "DEF-T3"],
                "representation_ref": REP_EXP,
                "reveal_stage_refs": ["EXP-STAGE-1", "EXP-STAGE-2", "EXP-STAGE-3"],
                "bank_anchor_ref": BANK_IDS["Q2"],
                "crux_question_refs": [BANK_IDS["Q2"], BANK_IDS["Q3"]],
                "crux_step_ref": "DEF-T2",
                "misconception_indexes": [0],
                "independent_checks": [
                    {"statement": "CHECK: Verify all exponents of 3x^2 - 2x + 1 belong to {0, 1, 2}.", "role": "CHECK"},
                    {"statement": "APPLY: Substitute x=2 into p(x) with brackets: (2)^2 - 3(2) + 4 = 2.", "role": "APPLY"},
                    {"statement": "CONNECT: Connect constant -5 to non-zero constant polynomial of degree 0.", "role": "CONNECT"}
                ]
            }
        ],
        "compact_anchor": {"prompt": "Is it a polynomial? Check every exponent.", "result": "Exponents must be whole numbers {0, 1, 2, ...}; coefficients must be real.", "representation_ref": REP_EXP}
    },
    {
        **base(MIC_ID),
        "title": "Algebraic identities, geometric area models, universal proof, and linear construction",
        "bucket_id": BUCKET,
        "primary_capability_ref": CAP_ID,
        "intrinsic_badge": "HARD",
        "badge_reason": "Learners must handle distributive cross-terms in identities, geometric 2D area models, universal deductive proof vs point substitution, and synthesizing unique linear polynomials from constraints.",
        "entry_assumptions": ["Distributive property, basic factoring, linear equations."],
        "inferential_jump": "Identities hold for all real numbers due to algebraic field axioms; linear polynomials are uniquely fixed by two independent constraints (constant term and zero).",
        "teaching_path": [
            step("ID-T1", "DECLARE", "Apply distributive law to expand binomial products without omitting cross-terms: (a+b)^2 = a^2 + 2ab + b^2.", "Distributivity generates all pairwise term products.", "expanded identity with cross-terms"),
            step("ID-T2", "TRANSFORM", "Model polynomial products geometrically as decomposed 2D rectangular area in cm^2.", "Geometric area model visualizes cross-terms as area rectangles.", "geometric area model"),
            step("ID-T3", "TRANSFORM", "Prove universal equality across R using field axioms rather than empirical point checks.", "Deductive proof holds unconditionally across infinite real domain.", "universal algebraic proof"),
            step("ID-T4", "VERIFY", "Synthesize linear polynomial p(x) = ax + b from constant term and zero, and prove uniqueness.", "System of linear coefficient equations has unique non-zero solution.", "unique synthesized linear polynomial")
        ],
        "relation_refs": [REL_SQR, REL_DIF, REL_LIN, REL_REC],
        "representation_refs": [REP_AREA, REP_LIN],
        "question_family_refs": [FAM_ID, FAM_LIN],
        "misconceptions": [
            misconception(
                "(a+b)^2 = a^2 + b^2 omitting the middle cross-term 2ab, or assuming point substitution proves an identity universally.",
                "Evaluate (1+3)^2 versus 1^2 + 3^2, or ask if x^2 = x holding at x=0, 1 makes it an identity.",
                "Distributivity produces two middle terms ab + ba = 2ab; point checks do not establish universal validity."
            )
        ],
        "exit_task": {
            "prompt": "Construct a linear polynomial whose constant term is -6 and whose zero is 3. Prove that it is unique.",
            "source_ref": SRC,
            "answer": model_answer("Linear polynomial: p(x) = 2x - 6. Constant term p(0) = b = -6; zero at 3 gives 3a - 6 = 0 => 3a = 6 => a = 2 (non-zero). Unique because linear equation 3a - 6 = 0 has exactly one root in R.", ["Form p(x) = ax + b with a != 0.", "Constant term fixes b = -6.", "Zero condition gives 3a - 6 = 0 => a = 2.", "Unique solution to linear equation in a."], "p(0) = -6 and p(3) = 2(3) - 6 = 0; degree is 1."),
            "oracle": {"no_numeric_claim": "The task assesses linear polynomial synthesis and uniqueness proof."}
        },
        "research_contribution": "Q6, Q7, Q8, Q9, and Q10 establish the progression from identity mechanics to universal proof and linear synthesis.",
        "prerequisite_refs": [CAP_TERMS, CAP_DEF],
        "lineage": [],
        "elicitation": {
            "predict": {"prompt": "Can more than one linear polynomial have constant term 2 and zero 1?", "defensible_answer": "No; any linear polynomial has form ax + b, and these two conditions uniquely fix b = 2 and a = -2."},
            "attempt": {
                "produces": "Synthesized polynomial p(x) = -2x + 2 with checks and uniqueness proof.",
                "closure": "RUBRIC",
                "rubric": [{"criterion": "Solves for both coefficients and proves uniqueness.", "evidence_of": "Understands linear polynomial constraints."}],
                "accepted": ["p(x) = -2x + 2, unique linear polynomial."],
                "rejected": ["Claiming multiple polynomials exist.", "Constructing a quadratic."]
            },
            "reconstruct": {
                "route": [
                    {"ask": "What is the general form of a linear polynomial?", "why_this_ask": "Fixes two degrees of freedom (a, b)."},
                    {"ask": "How does the constant term determine b?", "why_this_ask": "p(0) = b."},
                    {"ask": "How does the zero condition determine a?", "why_this_ask": "p(1) = a + b = 0."}
                ],
                "differs_from_teaching_path": "Starts from inverse constraint matching rather than forward expansion."
            },
            "boundary_test": {"prompt": "What if the required zero was at x = 0 with constant term 2?", "answer": "Impossible for any polynomial, since p(0) cannot simultaneously equal 2 and 0.", "confirms": "Consistency of polynomial conditions."}
        },
        "construction_units": [
            {
                "id": "CU-MATH-POLY-IDENTITIES-CONSTRUCTION",
                "decision": "Expand identities with cross-terms, model 2D area in cm^2, and synthesize unique linear polynomials",
                "step_refs": ["ID-T1", "ID-T2", "ID-T3", "ID-T4"],
                "representation_ref": REP_AREA,
                "reveal_stage_refs": ["AREA-STAGE-1", "AREA-STAGE-2", "AREA-STAGE-3"],
                "bank_anchor_ref": BANK_IDS["Q10"],
                "crux_question_refs": [BANK_IDS["Q6"], BANK_IDS["Q7"], BANK_IDS["Q8"], BANK_IDS["Q9"], BANK_IDS["Q10"]],
                "crux_step_ref": "ID-T4",
                "misconception_indexes": [0],
                "independent_checks": [
                    {"statement": "CHECK: Expand (x+3)^2 = x^2 + 6x + 9, identifying middle term 6x.", "role": "CHECK"},
                    {"statement": "APPLY: Rectangle area (x+3)(x+1) = x^2 + 4x + 3 cm^2 with length cm * width cm = cm^2.", "role": "APPLY"},
                    {"statement": "CONNECT: Verify p(x) = -2x + 2: p(0)=2, p(1)=0, deg 1, unique.", "role": "CONNECT"}
                ]
            }
        ],
        "compact_anchor": {"prompt": "Two constraints on a linear polynomial? Set p(x) = ax + b.", "result": "Constant term fixes b; zero fixes a; solution is unique.", "representation_ref": REP_LIN}
    }
]

question_families = [
    {
        **base(FAM_TERMS),
        "title": "Polynomial Degree, Terms, and Like-Term Operations",
        "capability_refs": [CAP_TERMS],
        "solution_structure": [
            "Identify the highest power of variable x with a non-zero coefficient to find degree.",
            "Record leading coefficient from the highest degree term, and constant term independent of x.",
            "Record any missing power between 0 and degree as coefficient 0.",
            "Add polynomials by grouping like terms possessing identical powers of x and combining coefficients."
        ],
        "demand_dimensions": {
            "model_choice": "Distinguish monomial powers and recognise explicit zero entry for missing terms.",
            "representation_translation": "Translate standard algebraic polynomial expressions into power-indexed tables.",
            "reasoning_steps": "Inventory terms, group like powers, combine coefficients via distributivity.",
            "novelty": "Missing powers and negative coefficients as potential points of confusion."
        },
        "safe_variations": ["Vary degree, leading coefficient, and positions of missing powers."],
        "transfer_boundaries": ["Negative or fractional powers do not form polynomials."],
        "common_wrong_routes": ["Omit missing terms from tables or combine unlike powers."],
        "item_refs": [BANK_IDS[x] for x in ("Q1", "Q4", "Q5")]
    },
    {
        **base(FAM_DEF),
        "title": "Polynomial Definitions and Point Evaluation",
        "capability_refs": [CAP_DEF],
        "solution_structure": [
            "Check all exponents of variable x against non-negative integers W = {0, 1, 2, ...}.",
            "Identify defining condition violations for reciprocals (negative powers) and radicals (fractional powers).",
            "State degree as 0 for non-zero constant polynomials.",
            "Evaluate polynomial at a given real value using explicit bracket substitution and arithmetic precedence."
        ],
        "demand_dimensions": {
            "model_choice": "Apply the formal definition of polynomial in one variable with real coefficients.",
            "representation_translation": "Rewrite reciprocal 1/x as x^-1 and radical sqrt(x) as x^(1/2).",
            "reasoning_steps": "Convert to index form, test exponents against W, determine degrees or identify failed conditions.",
            "novelty": "Constants lacking visible variables and reciprocal powers in denominators."
        },
        "safe_variations": ["Test polynomials of various degrees against non-polynomial algebraic expressions."],
        "transfer_boundaries": ["Rational expressions and multivariable expressions require separate definitions."],
        "common_wrong_routes": ["Reject constants or accept reciprocals because variable has power 1 in denominator."],
        "item_refs": [BANK_IDS[x] for x in ("Q2", "Q3")]
    },
    {
        **base(FAM_ID),
        "title": "Algebraic Identities, Area Models, and Universal Proof",
        "capability_refs": [CAP_ID],
        "solution_structure": [
            "Expand binomial squares using the distributive property without omitting cross-terms: (a+b)^2 = a^2 + 2ab + b^2.",
            "Model rectangular areas as decomposed products in cm^2 for non-negative parameter x >= 0.",
            "Factorise difference of squares a^2 - b^2 into conjugate binomials (a-b)(a+b) and verify cancellation.",
            "Deduce universal algebraic equality across R using field axioms rather than empirical point checks."
        ],
        "demand_dimensions": {
            "model_choice": "Select appropriate algebraic identity or geometric area model.",
            "representation_translation": "Connect symbolic products with subdivided 2D rectangular areas.",
            "reasoning_steps": "Expand pairwise products, combine like terms, attach compound physical units.",
            "novelty": "Refuting the common error (a+b)^2 = a^2 + b^2 and proving identities across infinite domains."
        },
        "safe_variations": ["Vary constants in binomial factors and rectangular dimensions."],
        "transfer_boundaries": ["Cubic identities and trinomial expansions belong to advanced units."],
        "common_wrong_routes": ["Square terms individually omitting cross-terms, or treat sample substitution as proof."],
        "item_refs": [BANK_IDS[x] for x in ("Q6", "Q7", "Q8", "Q9")]
    },
    {
        **base(FAM_LIN),
        "title": "Linear Polynomial Synthesis and Zeroes",
        "capability_refs": [CAP_ID],
        "solution_structure": [
            "Express general linear polynomial as p(x) = ax + b with leading coefficient a != 0.",
            "Use constant term condition p(0) = b to fix b.",
            "Use zero condition p(x_0) = 0 to establish linear equation ax_0 + b = 0 and solve for a.",
            "Verify both conditions and prove uniqueness from the unique solvability of linear equation in R."
        ],
        "demand_dimensions": {
            "model_choice": "Inverse problem: synthesize polynomial from structural conditions.",
            "representation_translation": "Translate constant term to y-intercept (0, b) and zero to x-intercept (x_0, 0).",
            "reasoning_steps": "Set up coefficient system, solve for a and b, verify conditions, prove uniqueness.",
            "novelty": "Synthesizing an object from properties and establishing formal uniqueness."
        },
        "safe_variations": ["Vary required constant terms and zero roots."],
        "transfer_boundaries": ["Higher-degree polynomials with multiple zeroes require the Factor Theorem."],
        "common_wrong_routes": ["Construct a non-linear polynomial or assume multiple polynomials exist."],
        "item_refs": [BANK_IDS["Q10"]]
    }
]

# Package definition
package = {
    "schema_version": "0.2.0",
    "package_id": "LIB-MATH-09-POLYNOMIALS-ISSUE53",
    "title": "Polynomials in One Variable with Real Coefficients",
    "version": "0.1.0",
    "status": "CANDIDATE",
    "subject": "Mathematics",
    "scope_summary": "Grade 9 Mathematics curriculum on polynomials in one variable: definitions, degree, coefficients, operations, algebraic identities, area models, and linear polynomial zeroes.",
    "curriculum_mappings": [],
    "resources": [resource],
    "buckets": [bucket],
    "capabilities": capabilities,
    "microtopics": microtopics,
    "relations": relations,
    "representations": representations,
    "question_families": question_families,
    "questions": [],
    "data": [],
    "teaching_routes": [],
    "practice_profiles": [],
    "evidence": [],
    "known_issues": [],
    "extensions": {},
    "application_contexts": []
}

(OUT / "package.v1.json").write_text(json.dumps(package, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print("Wrote package.v1.json successfully")

# Move specifications per question
MOVES_PER_Q = {
    "Q1": [
        ("DECIDE", "Identify degree from highest power", "The degree of a polynomial is the highest power of the variable with a non-zero coefficient. In 4x^3 - 2x + 7, the highest power is 3.", "Degree = 3", "degree identification"),
        ("CONNECT", "Extract leading coefficient and constant term", "The leading coefficient is the coefficient of the highest power term (4 for x^3), and the constant term is the term independent of x (7).", "Leading coeff = 4, Constant term = 7", "main terms extraction"),
        ("TRANSFORM", "Evaluate missing x^2 term coefficient", "The power x^2 does not appear explicitly in the polynomial. Its coefficient is recorded as 0 because 0 * x^2 = 0 contributes nothing to the sum.", "Coefficient of x^2 = 0", "missing power coefficient"),
        ("VERIFY", "Confirm complete power sequence", "Writing p(x) = 4x^3 + 0x^2 - 2x + 7 shows all integer powers 3, 2, 1, 0 are accounted for.", "Verified complete representation", "verified inventory")
    ],
    "Q2": [
        ("DECIDE", "State polynomial defining criteria", "A polynomial in x with real coefficients requires all exponents of x to be non-negative integers (whole numbers W = {0, 1, 2, ...}) and all coefficients to be real numbers.", "Defining condition: exponents in W, coefficients in R", "defining criteria"),
        ("TRANSFORM", "Express each candidate expression in index power form", "Rewrite: 3x^2 - 2x + 1 has powers 2, 1, 0; 1/x + 3 = x^-1 + 3 has power -1; sqrt(x) + 1 = x^(1/2) + 1 has power 1/2; -5 = -5x^0 has power 0.", "Index forms: x^2, x^-1, x^(1/2), x^0", "index conversion"),
        ("CONNECT", "Classify accepted polynomials and state degrees", "3x^2 - 2x + 1 is a polynomial of degree 2 (highest power 2); -5 is a constant polynomial of degree 0 (power 0 in W).", "Accepted: 3x^2-2x+1 (deg 2), -5 (deg 0)", "accepted classification"),
        ("VERIFY", "Identify defining condition failures for rejected expressions", "1/x + 3 fails because exponent -1 is negative (-1 not in W); sqrt(x) + 1 fails because exponent 1/2 is a fraction (1/2 not in W).", "Rejected: 1/x+3 (negative exponent -1), sqrt(x)+1 (fractional exponent 1/2)", "rejected classification")
    ],
    "Q3": [
        ("REPRESENT", "Substitute input point with explicit brackets", "Replace every occurrence of x with (2) enclosed in brackets: p(2) = (2)^2 - 3(2) + 4.", "p(2) = (2)^2 - 3(2) + 4", "bracket substitution"),
        ("TRANSFORM", "Evaluate powers and products according to operator precedence", "Compute square (2)^2 = 4 and product 3(2) = 6 before addition/subtraction.", "p(2) = 4 - 6 + 4", "precedence evaluation"),
        ("TRANSFORM", "Combine terms from left to right", "Perform addition and subtraction: 4 - 6 = -2, then -2 + 4 = 2.", "p(2) = 2", "arithmetic combination"),
        ("VERIFY", "Check via factored grouping", "Rewrite p(x) = x(x-3) + 4; at x=2, p(2) = 2(2-3) + 4 = 2(-1) + 4 = -2 + 4 = 2.", "Verified value p(2) = 2", "independent evaluation check")
    ],
    "Q4": [
        ("DECIDE", "Identify like terms across both polynomials", "Like terms have the identical power of x: quadratic terms are 2x^2 and -x^2; linear terms are 3x and 4x; constant terms are -5 and 2.", "Like terms identified by power", "like-term identification"),
        ("CONNECT", "Group like terms using distributive property", "Group by common power: (2x^2 - x^2) + (3x + 4x) + (-5 + 2) = (2 - 1)x^2 + (3 + 4)x + (-5 + 2).", "Grouped expression by powers", "power grouping"),
        ("TRANSFORM", "Combine numerical coefficients in each group", "Add coefficients: (2-1)x^2 = 1x^2, (3+4)x = 7x, (-5+2) = -3.", "x^2 + 7x - 3", "coefficient addition"),
        ("VERIFY", "Verify descending order and numerical evaluation", "Powers are in descending order (2, 1, 0). At x=1, p(1)=0, q(1)=5, sum=5; (1)^2+7(1)-3 = 5.", "Verified sum x^2 + 7x - 3", "verified sum")
    ],
    "Q5": [
        ("REPRESENT", "Decompose polynomial into power-indexed table rows", "Create rows for powers 3, 2, 1, 0: power 3 term is 5x^3 (coeff 5), power 2 term is missing (coeff 0), power 1 term is -2x (coeff -2), power 0 term is 7 (coeff 7).", "Table rows for 3, 2, 1, 0 with coefficients 5, 0, -2, 7", "table construction"),
        ("CONNECT", "Reconstruct polynomial from table entries", "Sum the product of each power and coefficient: 5x^3 + 0x^2 + (-2)x + 7 = 5x^3 - 2x + 7.", "Reconstructed 5x^3 - 2x + 7", "polynomial reconstruction"),
        ("TRANSFORM", "Explain meaning and necessity of zero entry", "A zero entry means the term contributes 0 to the sum (0 * x^2 = 0), serving as a crucial zero entry to preserve index and column alignment in positional operations.", "Zero entry has null contribution (0 * x^2 = 0)", "zero entry interpretation"),
        ("VERIFY", "Confirm exact algebraic agreement", "Original p(x) and reconstructed polynomial agree identically for all values of x.", "Verified identity agreement", "verified table translation")
    ],
    "Q6": [
        ("DECIDE", "Express binomial square as product of two identical binomials", "By definition of squaring, (x+3)^2 = (x+3)(x+3).", "(x+3)(x+3)", "product definition"),
        ("TRANSFORM", "Expand product term-by-term via distributive property", "Apply distributivity: x(x+3) + 3(x+3) = x*x + x*3 + 3*x + 3*3 = x^2 + 3x + 3x + 9.", "x^2 + 3x + 3x + 9", "distributive expansion"),
        ("CONNECT", "Locate student error and combine middle cross-terms", "The student squared each term separately (x^2 + 9) and omitted the two middle rectangles 3x + 3x = +6x.", "Error: missing middle cross-term +6x", "error diagnosis"),
        ("VERIFY", "State corrected expansion and verify with numerical counterexample", "Corrected expansion is x^2 + 6x + 9. At x=1, student claims (4)^2 = 1^2+9=10 (false), while 1+6+9 = 16 (true).", "Corrected: x^2 + 6x + 9", "verified expansion and refutation")
    ],
    "Q7": [
        ("DECIDE", "Model area as product of length and width", "For a rectangle, Area = length * width = (x+3) * (x+1) cm * cm.", "Area(x) = (x+3)(x+1)", "geometric modeling"),
        ("TRANSFORM", "Expand binomial product and combine like terms", "Multiply: x(x+1) + 3(x+1) = x^2 + x + 3x + 3 = x^2 + 4x + 3.", "x^2 + 4x + 3", "polynomial multiplication"),
        ("CONNECT", "Identify output physical units", "Multiplying dimensions in cm by cm yields square centimetres (cm^2).", "Unit: cm^2", "unit determination"),
        ("VERIFY", "State represented physical feature and domain", "The polynomial represents the total two-dimensional surface area enclosed by the rectangle for any valid parameter x >= 0.", "Total enclosed 2D surface area (x >= 0)", "feature representation")
    ],
    "Q8": [
        ("DECIDE", "Pattern match to difference of two squares identity", "Recognize that x^2 is the square of x and 9 is the square of 3 (3^2 = 9), matching a^2 - b^2.", "Matches a^2 - b^2 with a=x, b=3", "identity matching"),
        ("TRANSFORM", "Apply identity a^2 - b^2 = (a-b)(a+b)", "Substitute a=x and b=3: x^2 - 9 = (x - 3)(x + 3).", "Factors: (x - 3)(x + 3)", "factorisation"),
        ("CONNECT", "Check factorisation by multiplying factors", "Expand (x-3)(x+3) = x(x+3) - 3(x+3) = x^2 + 3x - 3x - 9.", "x^2 + 3x - 3x - 9", "expansion check"),
        ("VERIFY", "Confirm cross-term cancellation restores original binomial", "The middle terms +3x and -3x cancel out (+3x - 3x = 0), leaving x^2 - 9. Check verified.", "Verified restoration of x^2 - 9", "verified factorisation")
    ],
    "Q9": [
        ("DECIDE", "Formulate requirement for universal algebraic proof", "An equality between expressions holding for all real x is an identity; empirical numerical substitutions check specific instances but cannot prove universal truth across infinite R.", "Universal proof required via field axioms", "proof requirement"),
        ("CONNECT", "Invoke distributive axiom of multiplication over addition in R", "For any real numbers a, b, c, the distributive property states a*(b+c) = a*b + a*c.", "Distributive law: a(b+c) = ab + ac in R", "axiomatic warrant"),
        ("TRANSFORM", "Instantiate distributive axiom for x(x+1)", "Setting a=x, b=x, c=1 gives x*(x+1) = x*x + x*1 = x^2 + x by definition of powers and multiplicative identity.", "x(x+1) = x^2 + x", "axiomatic deduction"),
        ("VERIFY", "Confirm identity across entire real domain R", "Because the equality is deduced directly from real field axioms, it holds universally for every real number x without exception.", "Equal for every real x (algebraic identity)", "verified universal identity")
    ],
    "Q10": [
        ("DECIDE", "Formulate general linear polynomial", "A linear polynomial in one variable has the general form p(x) = ax + b, where a, b in R and leading coefficient a != 0.", "p(x) = ax + b, a != 0", "linear form formulation"),
        ("CONNECT", "Apply constant term condition to determine b", "The constant term is p(0) = a(0) + b = b. Given constant term is 2, so b = 2.", "b = 2", "constant term determination"),
        ("TRANSFORM", "Apply zero condition", "A zero at x=1 means p(1) = 0. Substituting x=1 and b=2 gives a(1) + 2 = 0.", "a(1) + 2 = 0", "zero condition formulation"),
        ("TRANSFORM", "Solve for leading coefficient a", "Solving the linear equation a + 2 = 0 yields a = -2, which is non-zero (degree 1 holds).", "a = -2 (non-zero)", "leading coefficient solution"),
        ("VERIFY", "Verify both conditions and prove uniqueness", "Check: p(0) = -2(0) + 2 = 2; p(1) = -2(1) + 2 = 0; deg = 1. Uniqueness: a+2=0 has a unique solution in R, so exactly ONE linear polynomial satisfies both conditions.", "Constructed p(x) = -2x + 2; unique linear polynomial", "verified synthesis and uniqueness")
    ]
}

CRUX_REF = {
    "Q1": "OWN-ISSUE53-POLY-01-MOVE-3",
    "Q2": "OWN-ISSUE53-POLY-02-MOVE-3",
    "Q3": "OWN-ISSUE53-POLY-03-MOVE-2",
    "Q4": "OWN-ISSUE53-POLY-04-MOVE-3",
    "Q5": "OWN-ISSUE53-POLY-05-MOVE-3",
    "Q6": "OWN-ISSUE53-POLY-06-MOVE-3",
    "Q7": "OWN-ISSUE53-POLY-07-MOVE-2",
    "Q8": "OWN-ISSUE53-POLY-08-MOVE-2",
    "Q9": "OWN-ISSUE53-POLY-09-MOVE-3",
    "Q10": "OWN-ISSUE53-POLY-10-MOVE-3",
}

bank_questions = []
for qid in [f"Q{i}" for i in range(1, 11)]:
    stem = STEMS[qid]
    moves_spec = MOVES_PER_Q[qid]
    crux_id = CRUX_REF[qid]

    qrt_item = next(it for it in QRT["items"] if it["question_id"] == qid)
    academic = ACADEMIC[qid]
    hints = list(qrt_item["hints"])

    move_rows = []
    for n, (kind, action, why, output, role_name) in enumerate(moves_spec, 1):
        move_rows.append({
            "id": f"{BANK_IDS[qid]}-MOVE-{n}",
            "kind": kind,
            "action": action,
            "why_valid": why,
            "inputs": ["stated givens and prior move"],
            "output": output
        })

    stages = ["KEY_CONCEPT", "REPRESENTATION", "FIRST_MOVE", "FORMAL_MODEL", "CHECKPOINT"]
    kinds = ["CONNECT", "REPRESENT", "EXECUTE", "EXECUTE", "EXECUTE"]
    reveals = ["CONCEPT", "METHOD", "METHOD", "METHOD", "METHOD"]
    scaffolds = [
        {
            "text": text,
            "support_kind": kinds[i],
            "reveals": reveals[i],
            "learner_stage": stages[i],
            "supports_move_ref": move_rows[min(i, len(move_rows)-1)]["id"]
        }
        for i, text in enumerate(hints)
    ]

    stem_sha = "sha256:" + hashlib.sha256(stem.encode("utf-8")).hexdigest()

    q_obj = {
        "id": BANK_IDS[qid],
        "original_identifier": qid,
        "stem": stem,
        "conditions": list(academic["conditions"]),
        "family_ref": FAMILY[qid],
        "figure_refs": list(QUESTION_FIGURES[qid]),
        "answer": {
            "kind": "EXACT",
            "summary": qrt_item["verified_answer"],
            "reasoning_route": move_rows,
            "crux_move_ref": crux_id,
            "check": qrt_item["independent_check"],
            "verification_status": "CHECKED_BY_AUTHOR"
        },
        "scaffolds": scaffolds,
        "primary_capability_ref": PRIMARY_CAP[qid],
        "extensions": {
            "grade9v3:source_custody": {
                "authority_class": "OWNER_SUPPLIED_RAW_INPUT",
                "intake_ref": qid,
                "wording_custody": "VERBATIM",
                "text_sha256": stem_sha
            },
            "grade9v3:analysis": {
                "learner_question_type": "constructed_response",
                "difficulty": {
                    "band": academic["difficulty"]["band"],
                    "requested_band": "D1",
                    "score": academic["difficulty"]["score"],
                    "components": academic["difficulty"]["components"],
                    "basis": (
                        f"Fresh ISS29/N2 reanalysis. Protected work: {academic['W']} "
                        f"Total score {academic['difficulty']['score']} -> {academic['difficulty']['band']}."
                    )
                },
                "common_wrong_route": qrt_item["misconception"]["M1"],
                "expected_time_seconds": 90 if academic["difficulty"]["band"] == "D1" else 150 if academic["difficulty"]["band"] == "D2" else 240,
                "cognitive_demand": academic["demand"]["primary"],
                "stable_crux_move": academic["W"]
            },
            "grade9v3:math_spans": [],
            "grade9v3:core2_support_plan": {
                "protected_move_refs": [crux_id]
            },
            "grade9v3:component_waivers": {
                "TRAP": (
                    "No misconception-specific repair is pre-authorized from the source question alone. "
                    "The authored wrong-route hypothesis remains reviewer evidence until diagnostic evidence is CONFIRMED."
                ),
                "REPRESENTATION": (
                    "No authored visual is attached to the independent Core2 attempt. "
                    "Exact-case representations are learner-requested/post-attempt support or Core1A teaching."
                ),
                "CHECK": f"Post-solution author check is available: {qrt_item['independent_check']}"
            }
        }
    }
    bank_questions.append(q_obj)

owner_bank = {
    "schema_version": "grade9v3-owner-supplied-bank-v1",
    "bank_id": "own-issue53-poly",
    "questions": bank_questions
}

(OUT / "owner.bank.json").write_text(json.dumps(owner_bank, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print("Wrote owner.bank.json successfully")

# Product manifest
manifest = {
    "schema": "product-manifest/v1",
    "product_id": "EVIDENCE-MATH-ISSUE53-POLY-D1",
    "subject": "Mathematics",
    "home_href": "index.html",
    "question_bank_href": "core2.html",
    "package_refs": [
        "evidence/benchmark/ISS53/generated/package.v1.json"
    ],
    "bank_refs": [
        "evidence/benchmark/ISS53/generated/owner.bank.json"
    ],
    "selection": {
        "microtopics": [
            MIC_TERMS,
            MIC_DEF,
            MIC_ID
        ],
        "core2": [BANK_IDS[f"Q{i}"] for i in range(1, 11)],
        "core2a": [],
        "core2b": []
    },
    "output_roles": [
        "CORE1A",
        "CORE2"
    ]
}

(OUT / "product.manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print("Wrote product.manifest.json successfully")
