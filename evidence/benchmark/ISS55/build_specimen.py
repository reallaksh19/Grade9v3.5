#!/usr/bin/env python3
"""Test generator for Issue #55 candidate package and bank."""
import json
import re
import sys
from pathlib import Path

REPO = Path.cwd()
sys.path.insert(0, str(REPO))

from Shared.tools import owner_bank
from jsonschema import Draft202012Validator

HERE = REPO / "evidence" / "benchmark" / "ISS55"
OUT = HERE / "generated"
LEDGER = json.loads((HERE / "question-ledger.json").read_text(encoding="utf-8"))
CARDS = json.loads((HERE / "source-cards.json").read_text(encoding="utf-8"))
PROMPT = (HERE / "owner-core-prompt.md").read_text(encoding="utf-8")

_matches = re.findall(r"### Q(\d+)\n\n(.*?)(?=\n\n### Q\d+|\n\n## B — FINAL DELIVERABLES)", PROMPT, flags=re.S)
STEMS = {f"Q{n}": text.strip() for n, text in _matches}

SRC_OWNER = "SRC-OWNER-ISS55-POLYNOMIALS"
SRC_NCERT = "SRC-NCERT-CLASS9-MATH-CH2-POLYNOMIALS"
SRC_LANG = "SRC-ALGEBRA-LANG-POLYNOMIALS"
SRC_COMP = "SRC-COMPETITION-POLYNOMIAL-ALGEBRA"

BUCKET = "BUCKET-MATH-POLY-STRESS-ISS55"

CAP_PARAM = "CAP-MATH-POLY-FACTOR-PARAMETER"
CAP_MULT = "CAP-MATH-POLY-MULTIPLICITY-SIGN"
CAP_INTERP = "CAP-MATH-POLY-INTERPOLATION-DEGREE-BOUND"
CAP_AREA = "CAP-MATH-POLY-GEOMETRIC-AREA-DEGREE"
CAP_SIGN = "CAP-MATH-POLY-SIGN-CHART-RIGOR"
CAP_MONIC = "CAP-MATH-POLY-FACTOR-VALUE-CONSTRUCTION"
CAP_DIV = "CAP-MATH-POLY-FACTOR-DIVISIBILITY-DEGREE"
CAP_IDENT = "CAP-MATH-POLY-IDENTITY-THEOREM-DEGREE"
CAP_FAM = "CAP-MATH-POLY-PARAMETER-DEGREE-ZERO"
CAP_SUBST = "CAP-MATH-POLY-CHANGE-OF-VARIABLE-DOMAIN"

MIC_IDENT = "MIC-MATH-POLY-IDENTITY-DEGREE-BOUND"
MIC_SIGN = "MIC-MATH-POLY-SIGN-MULTIPLICITY"
MIC_SUBST = "MIC-MATH-POLY-AUXILIARY-DOMAIN"

REP_SIGN_TABLE = "REP-MATH-POLY-SIGN-TABLE"
REP_CARD_CUTOUT = "REP-MATH-POLY-GEOMETRIC-CARD-CUTOUT"
REP_IDENT_DIFF = "REP-MATH-POLY-DIFFERENCE-POLYNOMIAL"
REP_AUX_DOMAIN = "REP-MATH-POLY-SUBSTITUTION-MAPPING"
REP_GROUPING = "REP-MATH-POLY-GROUPING-ALGEBRA"
REP_SIGN_TEST = "REP-MATH-POLY-SIGN-TEST"
REP_INTERP = "REP-MATH-POLY-QUADRATIC-COEFFICIENTS"
REP_MONIC = "REP-MATH-POLY-MONIC-FACTOR-MODEL"
REP_QUARTIC_CE = "REP-MATH-POLY-COUNTEREXAMPLE-QUARTIC"
REP_PARAM_COEFF = "REP-MATH-POLY-PARAMETER-COEFFICIENT-ANALYSIS"

FAM_FACTOR = "FAM-MATH-POLY-CUBIC-FACTORISATION"
FAM_MULT = "FAM-MATH-POLY-ZERO-MULTIPLICITY"
FAM_SUFF = "FAM-MATH-POLY-DATA-SUFFICIENCY"
FAM_CANCEL = "FAM-MATH-POLY-DEGREE-CANCELLATION"
FAM_SIGNS = "FAM-MATH-POLY-FACTOR-SIGNS"
FAM_DEGREE = "FAM-MATH-POLY-DEGREE-SUFFICIENCY"
FAM_IDENT = "FAM-MATH-POLY-POLYNOMIAL-IDENTITY"
FAM_PARAM = "FAM-MATH-POLY-PARAMETER-FAMILIES"
FAM_BIQUAD = "FAM-MATH-POLY-BIQUADRATIC-EQUATIONS"

by_qid = {row["question_id"]: row for row in LEDGER["items"]}
BANK_IDS = {qid: row["stable_id"] for qid, row in by_qid.items()}

TEACHING_STEMS = {
    "Q1": "In p(x) = x^3 - 3x^2 - 4x + k, determine k so that (x - 3) is a factor, and find all real zeros by grouping.",
    "Q2": "For p(x) = (x - 1)^2(x - 2), identify the distinct zeros and their multiplicities, and test whether the sign changes across each root.",
    "Q3": "Determine the unique quadratic p(x) passing through (0, 1), (1, 3), and (2, 7), and evaluate whether p(3) = 14 is compatible.",
    "Q4": "Given an outer rectangle (x+4) by (x+2) and an inner cutout x by x, write the remaining area polynomial and explain why its degree is 1.",
    "Q5": "For p(x) = (x - 1)(x - 2)(x - 3), construct an interval sign chart on R by tabulating the signs of individual factors.",
    "Q6": "Construct a monic cubic polynomial with zeros at 1 and -1 satisfying p(2) = 6, and find its third real zero.",
    "Q7": "If a polynomial p(x) has zeros at 1 and -1, prove that (x^2 - 1) divides p(x), and explain why degree bounds are needed before asserting p(x) = c(x^2 - 1).",
    "Q8": "If two quadratics p(x) and q(x) agree at three distinct points, prove by difference polynomial d(x) = p(x) - q(x) that p(x) = q(x) everywhere.",
    "Q9": "For the family p_a(x) = (a - 1)x^2 - 2x + a, determine a so that x = 1 is a root, examine degree reduction, and determine if p_a(x) can be the zero polynomial.",
    "Q10": "Solve the biquadratic equations x^4 - 5x^2 + 4 = 0 and x^4 + x^2 - 2 = 0 over real numbers using substitution u = x^2 >= 0."
}

def base(record_id: str, source_refs=None) -> dict:
    return {
        "id": record_id,
        "version": "0.1.0",
        "status": "CANDIDATE",
        "source_refs": list(source_refs if source_refs is not None else [SRC_OWNER]),
        "evidence_refs": [],
        "extensions": {},
    }

def package_resource(card: dict) -> dict:
    role = ["SCIENTIFIC_CHECK"]
    origin = "WEB"
    if card["id"] == SRC_OWNER:
        role = ["QUESTION_BANK", "AUTHOR_CREATED"]
        origin = "AUTHORED"
    elif card["id"] == SRC_NCERT:
        role = ["CURRICULUM", "SCIENTIFIC_CHECK"]
    row = base(card["id"], [])
    row.update({
        "title": card["id"].replace("SRC-", "").replace("-", " ").title(),
        "origin": origin,
        "locator": card["locator"],
        "edition": "Issue #55 round-1 source check",
        "section": "; ".join(card["claims_supported"]),
        "last_checked": CARDS["checked_on"],
        "access_status": "SECTION_INSPECTED",
        "rights_status": "Reference/custody evidence only; no external publication authority is inherited.",
        "snapshot_ref": None,
        "snapshot_digest": None,
        "role": role,
        "supports_claims": list(card["claims_supported"]),
        "entry_capabilities": [],
        "depth": ["COMPETITION"],
        "selection_reason": card["model_boundary"],
        "fallback": [],
    })
    return row

resources = [package_resource(card) for card in CARDS["cards"]]

bucket = {
    **base(BUCKET, [SRC_OWNER, SRC_NCERT]),
    "title": "Polynomial Algebra and Degree Constraints — Issue #55 Candidate",
    "topic": "Polynomials in one variable with real coefficients",
    "intrinsic_badge": "HARD",
    "badge_reason": "Coordinating root multiplicity with interval sign charts, proving polynomial identity under degree bounds, and enforcing auxiliary variable domain restrictions.",
    "depth_overlay": "ADVANCED",
    "curriculum_mappings": [],
    "prerequisite_refs": [],
    "primary_representation_ref": REP_IDENT_DIFF,
    "conventions": [
        {"id": "real_domain", "statement": "All polynomials are in one variable x with real coefficients; roots are evaluated over the real numbers R unless explicitly stated otherwise."},
        {"id": "degree_definition", "statement": "The degree of a non-zero polynomial is the highest power of x with a non-zero coefficient. The zero polynomial 0(x) has all coefficients zero and its degree is undefined or -infinity."},
        {"id": "factor_multiplicity", "statement": "A zero r has multiplicity m if (x - r)^m divides p(x) but (x - r)^(m+1) does not. Distinct zeros count the cardinality of the zero set."},
        {"id": "auxiliary_variables", "statement": "When substituting an auxiliary variable u = g(x), the domain of u is restricted to the range of g over real numbers (e.g., u = x^2 >= 0)."}
    ],
}

def cap_row(cid: str, action: str, criterion: str) -> dict:
    row = base(cid)
    row.update({
        "action": action,
        "success_criterion": criterion,
        "prerequisite_refs": [],
        "curriculum_mappings": [],
        "external_provider": None,
        "acceptance_status": "CANDIDATE"
    })
    return row

capabilities = [
    cap_row(CAP_PARAM, "Determine polynomial parameters via factor theorem and real factorization.", "Applies p(c)=0 when (x-c) divides p(x) to solve for parameter k, then factors completely by grouping."),
    cap_row(CAP_MULT, "Distinguish root multiplicity from zero counts and analyze local sign change.", "Factors cubic with repeated roots, separates distinct zeros from multiplicity, and tests nearby points for sign changes."),
    cap_row(CAP_INTERP, "Evaluate polynomial uniqueness and degree compatibility from point data.", "Constructs unique quadratic through 3 points and evaluates whether a 4th point is compatible with degree bound."),
    cap_row(CAP_AREA, "Model geometric area and explain degree reduction via leading term cancellation.", "Subtracts interior cutout area from outer rectangle and explains why leading coefficient cancellation drops degree from 2 to 1."),
    cap_row(CAP_SIGN, "Construct rigorous sign charts from linear factor signs partitioned across real intervals.", "Partitions R at zeros, evaluates signs of individual factors, and deduces product sign from negative factor parity."),
    cap_row(CAP_MONIC, "Construct monic polynomials from zeros and value constraints.", "Coordinates factor model with value condition to determine monic cubic and verifies via independent linear system."),
    cap_row(CAP_DIV, "Deduce factor divisibility from roots and bound degree to avoid unwarranted forms.", "Applies factor theorem to deduce (x^2-1)q(x), constructs quartic counterexample to c(x^2-1), and states degree bound."),
    cap_row(CAP_IDENT, "Prove polynomial identity for bounded degree via difference polynomials and root bounds.", "Forms d(x) = p(x) - q(x), deduces d(x) has 3 zeros, contradicts root bound for non-zero polynomials, and concludes identity."),
    cap_row(CAP_FAM, "Analyze parameter families for root conditions, degree reduction, and zero polynomial impossibility.", "Solves parameter conditions for root and degree collapse, explains their relationship, and proves constant linear term prevents zero polynomial."),
    cap_row(CAP_SUBST, "Solve biquadratic polynomials via substitution while enforcing real domain constraints.", "Substitutes u = x^2 with constraint u >= 0, solves for u, rejects negative roots, and maps to real zeros.")
]

def representation(rep_id: str, kind: str, purpose: str, asset: str, stages: list[tuple[str, str, str]], correspondence: list[dict]) -> dict:
    row = base(rep_id, [])
    row.update({
        "kind": kind,
        "purpose": purpose,
        "required_elements": [label for _, label, _ in stages],
        "relation_refs": [],
        "read_order": [job for _, _, job in stages],
        "instance_constraints": ["Pre-attempt stages orient without displaying the protected final conclusion."],
        "accessibility": ["SVG has role=img, title and description.", "Text labels duplicate orientation/line meaning."],
        "misleading_alternatives": ["Assuming degree equals the number of distinct real zeros.", "Treating auxiliary variables as unrestricted real numbers."],
        "rendered_asset_refs": [asset],
        "scene_instances": [],
        "correspondence": correspondence,
        "reveal_stages": [{"id": sid, "label": label, "purpose": job, "visible_elements": [label]} for sid, label, job in stages],
    })
    return row

representations = [
    representation(REP_SIGN_TABLE, "TABLE_OF_VALUES", "Stage the factored polynomial -> partition of R -> factor signs -> product sign deduction.", "evidence/benchmark/ISS55/assets/polynomial-sign-chart.svg", [
        ("POLY-SIGN-1", "Factored form and real zeros", "Locate zeros x=1, 2, 3 partitioning R into intervals."),
        ("POLY-SIGN-2", "Individual factor signs across regions", "Evaluate signs of (x-1), (x-2), (x-3) across intervals."),
        ("POLY-SIGN-3", "Negative factor count (parity)", "Count negative factors to determine product sign in each region."),
        ("POLY-SIGN-4", "Rigorous sign chart with boundary zeros", "Final rigorous table showing zeros and signs."),
    ], [
        {"element": "real line partitioned at 1, 2, 3", "symbol": "(-inf, 1), 1, (1, 2), 2, (2, 3), 3, (3, inf)", "in_words": "zeros partition the continuous domain into sign-invariant intervals"},
        {"element": "factor sign rows", "symbol": "sgn(x - c)", "in_words": "linear factors change sign strictly at their roots"},
        {"element": "product sign row", "symbol": "parity of negatives", "in_words": "even negative count yields positive, odd yields negative"}
    ]),
    representation(REP_CARD_CUTOUT, "AREA_MODEL", "Stage the geometric card dimensions -> area polynomials -> quadratic term cancellation -> linear remainder.", "evidence/benchmark/ISS55/assets/card-cutout-area.svg", [
        ("POLY-AREA-1", "Card and cutout geometry", "Display outer rectangle (x+4) by (x+2) and inner square x by x."),
        ("POLY-AREA-2", "Outer and inner polynomial areas", "Area_outer = x^2 + 6x + 8 and Area_inner = x^2."),
        ("POLY-AREA-3", "Area subtraction and leading cancellation", "Area_rem = (x^2 + 6x + 8) - x^2 = 6x + 8; x^2 cancels."),
        ("POLY-AREA-4", "Linear remainder and degree conclusion", "Remaining area is linear of degree 1."),
    ], [
        {"element": "outer and inner rectangles", "symbol": "A_outer - A_inner", "in_words": "subtraction of inner cutout area from outer card"},
        {"element": "quadratic leading terms", "symbol": "x^2 - x^2 = 0", "in_words": "equal leading coefficients cancel completely upon subtraction"},
        {"element": "linear polynomial remainder", "symbol": "deg(6x + 8) = 1", "in_words": "the resulting polynomial has degree 1 rather than 2"}
    ]),
    representation(REP_IDENT_DIFF, "TABLE_OF_VALUES", "Stage difference polynomial d(x) = p(x) - q(x) -> degree bound <= 2 -> 3 zeros -> d(x) = 0.", "evidence/benchmark/ISS55/assets/polynomial-identity-difference.svg", [
        ("POLY-IDENT-1", "Difference polynomial setup", "Define d(x) = p(x) - q(x) with d(x_i) = 0 at given points."),
        ("POLY-IDENT-2", "Degree bound constraint", "State deg(d) <= max(deg p, deg q) <= 2 unless d is the zero polynomial."),
        ("POLY-IDENT-3", "Root count contradiction", "Non-zero polynomial of degree <= 2 cannot have 3 distinct zeros."),
        ("POLY-IDENT-4", "Zero polynomial identity conclusion", "Conclude d(x) is identically zero, so p(x) = q(x) for all x in R."),
    ], [
        {"element": "difference definition d(x) = p(x) - q(x)", "symbol": "p(x_i) = q(x_i) => d(x_i) = 0", "in_words": "points of agreement become roots of the difference polynomial"},
        {"element": "degree bound deg(d) <= 2", "symbol": "deg(p - q) <= max(deg p, deg q)", "in_words": "polynomial subtraction cannot increase degree"},
        {"element": "contradiction with root bound", "symbol": "roots(d) = 3 > deg(d)", "in_words": "a non-zero polynomial cannot possess more roots than its degree"},
        {"element": "identically zero conclusion", "symbol": "d(x) = 0 for all x", "in_words": "the difference polynomial is the zero polynomial, proving exact identity"}
    ]),
    representation(REP_AUX_DOMAIN, "TABLE_OF_VALUES", "Stage substitution u = x^2 with domain restriction u >= 0 -> quadratic in u -> real root extraction.", "evidence/benchmark/ISS55/assets/auxiliary-variable-domain.svg", [
        ("POLY-SUBST-1", "Change of variable for biquadratics", "Map even powers x^4 and x^2 to quadratic variable u = x^2."),
        ("POLY-SUBST-2", "Essential domain restriction: u >= 0", "Illustrate that real x requires u = x^2 >= 0."),
        ("POLY-SUBST-3", "Solving p(x) with positive roots", "Positive roots u=1, 4 generate 4 real zeros x = +/-1, +/-2."),
        ("POLY-SUBST-4", "Solving q(x) and rejecting u = -2", "Negative root u=-2 violates u >= 0, producing zero real zeros."),
    ], [
        {"element": "transformation u = x^2", "symbol": "u >= 0", "in_words": "squares of real numbers are non-negative"},
        {"element": "positive u roots", "symbol": "x = +/- sqrt(u)", "in_words": "each positive root generates two distinct real zeros"},
        {"element": "negative u root", "symbol": "no real x", "in_words": "negative auxiliary root produces zero real zeros"}
    ]),
    representation(REP_GROUPING, "ALGEBRA_TILES", "Factoring by grouping pairs in cubic polynomials.", "evidence/benchmark/ISS55/assets/polynomial-sign-chart.svg", [
        ("POLY-GRP-1", "Pairwise grouping", "Group x^3 - 3x^2 and -4x + 12."),
        ("POLY-GRP-2", "Common binomial", "Extract (x - 3) leaving (x^2 - 4)."),
        ("POLY-GRP-3", "Complete factoring", "Expand difference of squares into (x - 2)(x + 2)."),
        ("POLY-GRP-4", "Roots extraction", "Extract zeros {-2, 2, 3}."),
    ], [{"element": "grouping", "symbol": "(x^2-4)(x-3)", "in_words": "factoring by grouping"}]),
    representation(REP_SIGN_TEST, "TABLE_OF_VALUES", "Direct evaluation of test points near root.", "evidence/benchmark/ISS55/assets/polynomial-sign-chart.svg", [
        ("POLY-TEST-1", "Identify zeros", "Zeros at x = 1, 2."),
        ("POLY-TEST-2", "Nearby test points", "Points at 0, 1.5, 3."),
        ("POLY-TEST-3", "Evaluate values", "Values -2, -0.125, 4."),
        ("POLY-TEST-4", "Sign conclusion", "Constancy at 1, change at 2."),
    ], [{"element": "nearby points", "symbol": "p(0), p(1.5), p(3)", "in_words": "testing sign on adjacent intervals"}]),
    representation(REP_INTERP, "COORDINATE_GRAPH", "Polynomial interpolation linear system from 3 points.", "evidence/benchmark/ISS55/assets/polynomial-identity-difference.svg", [
        ("POLY-INT-1", "Form quadratic", "ax^2 + bx + c."),
        ("POLY-INT-2", "Solve system", "c=1, a+b=2, 2a+b=3."),
        ("POLY-INT-3", "Unique model", "x^2 + x + 1."),
        ("POLY-INT-4", "Contradiction", "p(3)=13 != 14."),
    ], [{"element": "interpolation", "symbol": "x^2 + x + 1", "in_words": "unique quadratic through 3 points"}]),
    representation(REP_MONIC, "TABLE_OF_VALUES", "Monic cubic factor model coordination with value condition.", "evidence/benchmark/ISS55/assets/polynomial-identity-difference.svg", [
        ("POLY-MON-1", "Known factors", "(x^2 - 1)."),
        ("POLY-MON-2", "Undetermined root", "(x - r)."),
        ("POLY-MON-3", "Value constraint", "p(2) = 6."),
        ("POLY-MON-4", "Complete polynomial", "x^3 - x."),
    ], [{"element": "monic model", "symbol": "(x^2 - 1)(x - r)", "in_words": "monic cubic factor model"}]),
    representation(REP_QUARTIC_CE, "COORDINATE_GRAPH", "Counterexample construction for polynomial divisibility.", "evidence/benchmark/ISS55/assets/polynomial-identity-difference.svg", [
        ("POLY-QCE-1", "Divisibility fact", "(x^2 - 1) divides p(x)."),
        ("POLY-QCE-2", "Counterexample selection", "p(x) = x^4 - 1."),
        ("POLY-QCE-3", "Real root verification", "Zeros are only 1 and -1."),
        ("POLY-QCE-4", "Degree check", "Degree 4 != 2, disproving claim."),
    ], [{"element": "counterexample", "symbol": "x^4 - 1", "in_words": "quartic counterexample"}]),
    representation(REP_PARAM_COEFF, "TABLE_OF_VALUES", "Parameter family coefficient vanishing analysis.", "evidence/benchmark/ISS55/assets/polynomial-identity-difference.svg", [
        ("POLY-PAR-1", "Root condition", "p_a(1) = 2a - 2 = 0."),
        ("POLY-PAR-2", "Degree condition", "a - 1 = 0."),
        ("POLY-PAR-3", "Relationship", "Both hold at a = 1."),
        ("POLY-PAR-4", "Zero polynomial check", "Linear coeff -2 != 0, impossible."),
    ], [{"element": "coefficients", "symbol": "2a-2, a-1, -2", "in_words": "parameter family coefficient analysis"}])
]

families = [
    {**base(FAM_FACTOR), "title": "Cubic polynomial factorisation and root determination", "capability_refs": [CAP_PARAM], "solution_structure": ["Apply factor theorem to identify known factor.", "Factor quotient quadratic or group terms.", "List distinct real zeros.", "Verify complete polynomial independently."], "demand_dimensions": {"model_choice": "Factor theorem with parameter/value constraints.", "representation_translation": "Polynomial expression to complete linear factors.", "reasoning_steps": "Substitute, solve, factor, verify.", "novelty": "Parameter determination and independent root verification."}, "safe_variations": ["Vary parameter position or integer root values."], "transfer_boundaries": ["Does not extend to cubics with no rational roots without numerical methods."], "common_wrong_routes": ["Equating coefficients prematurely or checking only the given root."], "item_refs": [BANK_IDS["Q1"]]},
    {**base("FAM-MATH-POLY-CUBIC-CONSTRUCTION"), "title": "Monic polynomial construction from zeros and values", "capability_refs": [CAP_MONIC], "solution_structure": ["Represent monic cubic as (x^2 - 1)(x - r) using known zeros.", "Substitute given value point p(2) = 6 into factor model.", "Solve linear equation for undetermined root r.", "Expand polynomial and verify via independent linear system."], "demand_dimensions": {"model_choice": "Monic factor model combined with point constraint.", "representation_translation": "Roots and value condition to linear equation in undetermined root.", "reasoning_steps": "Set up factor model, substitute value, solve for third root, expand.", "novelty": "Direct determination of third root without full cubic expansion."}, "safe_variations": ["Vary roots or value constraint."], "transfer_boundaries": ["Requires monic condition; non-monic requires an additional leading coefficient parameter."], "common_wrong_routes": ["Assuming third root must be zero without checking value condition."], "item_refs": [BANK_IDS["Q6"]]},
    {**base(FAM_MULT), "title": "Root multiplicity and local sign behaviour", "capability_refs": [CAP_MULT], "solution_structure": ["Factor cubic to identify repeated factors.", "Distinguish distinct zeros from multiplicity count.", "Evaluate exact nearby test points.", "Deduce local sign change vs constancy."], "demand_dimensions": {"model_choice": "Even vs odd multiplicity factor behaviour.", "representation_translation": "Factored form to local sign values.", "reasoning_steps": "Factor, separate multiplicity, evaluate, conclude.", "novelty": "Local sign preservation at even multiplicity zeros."}, "safe_variations": ["Test cubics with triple roots or single repeated roots."], "transfer_boundaries": ["Sign chart requires continuity; does not apply to rational functions with poles without pole analysis."], "common_wrong_routes": ["Assuming every polynomial zero causes the graph to cross the axis."], "item_refs": [BANK_IDS["Q2"]]},
    {**base(FAM_SUFF), "title": "Polynomial data sufficiency and degree uniqueness", "capability_refs": [CAP_INTERP, CAP_IDENT], "solution_structure": ["Set up linear system for polynomial coefficients.", "Solve unique polynomial matching base points.", "Evaluate additional record to test compatibility.", "Explain implications for degree bound vs data accuracy."], "demand_dimensions": {"model_choice": "Polynomial uniqueness theorem.", "representation_translation": "Point data to coefficient linear system.", "reasoning_steps": "Set up, solve, test 4th point, explain contradiction.", "novelty": "Overdetermined polynomial systems and degree bound violation."}, "safe_variations": ["Use 4 points for cubics or 2 points for linear polynomials."], "transfer_boundaries": ["Does not apply if points have repeated x coordinates (not a function)."], "common_wrong_routes": ["Assuming any 4 points can fit a quadratic with flexible coefficients."], "item_refs": [BANK_IDS[x] for x in ("Q3", "Q8")]},
    {**base(FAM_CANCEL), "title": "Degree reduction via leading coefficient cancellation", "capability_refs": [CAP_AREA, CAP_PARAM], "solution_structure": ["Form polynomial expressions for components.", "Subtract or combine expressions.", "Observe cancellation of leading degree terms.", "Verify resulting lower-degree polynomial."], "demand_dimensions": {"model_choice": "Degree behaviour under polynomial operations.", "representation_translation": "Geometric or parameter situation to algebraic polynomials.", "reasoning_steps": "Expand, subtract, identify cancellation, explain degree drop.", "novelty": "Difference of degree 2 polynomials yielding degree 1."}, "safe_variations": ["Vary geometric shapes or parameter coefficients."], "transfer_boundaries": ["Degree of sum/difference is bounded by max degree; equality holds only when leading terms do not cancel."], "common_wrong_routes": ["Assuming degree of difference must always equal the degree of the operands."], "item_refs": [BANK_IDS[x] for x in ("Q4", "Q9")]},
    {**base(FAM_SIGNS), "title": "Interval sign charts from linear factor parity", "capability_refs": [CAP_SIGN], "solution_structure": ["Factor polynomial completely into linear factors.", "Partition real line into open intervals separated by zeros.", "Tabulate signs of each factor in each region.", "Deduce product sign from parity of negative factors."], "demand_dimensions": {"model_choice": "Factor sign analysis and Intermediate Value Theorem.", "representation_translation": "Factored polynomial to 2D sign chart.", "reasoning_steps": "Factor, partition, tabulate factor signs, multiply parities.", "novelty": "Rigorous algebraic derivation of signs without sketching."}, "safe_variations": ["Apply to higher-degree polynomials with distinct real roots."], "transfer_boundaries": ["Irreducible quadratic factors must be evaluated as strictly positive or negative."], "common_wrong_routes": ["Drawing a curve without justifying the signs on interval endpoints."], "item_refs": [BANK_IDS["Q5"]]},
    {**base(FAM_DEGREE), "title": "Factor divisibility and degree sufficiency", "capability_refs": [CAP_DIV], "solution_structure": ["Apply factor theorem to establish dividing polynomial.", "Express general polynomial as product with arbitrary quotient.", "Construct higher-degree counterexample.", "Identify degree bound condition that forces scalar quotient."], "demand_dimensions": {"model_choice": "Divisibility in polynomial rings.", "representation_translation": "Zero conditions to polynomial divisibility relation.", "reasoning_steps": "Deduce (x^2-1)q(x), disprove scalar claim via counterexample, state degree bound.", "novelty": "Distinguishing root specification from polynomial uniqueness."}, "safe_variations": ["Test polynomials with 3 zeros or higher degree requirements."], "transfer_boundaries": ["Zeros only determine linear factors; irreducible quadratic factors can exist with no real zeros."], "common_wrong_routes": ["Believing that knowing all real roots fixes the polynomial up to a scalar constant."], "item_refs": [BANK_IDS["Q7"]]},
    {**base(FAM_IDENT), "title": "Polynomial identity and difference polynomial deduction", "capability_refs": [CAP_IDENT], "solution_structure": ["Form difference polynomial d(x) = p(x) - q(x).", "Bound degree of difference: deg(d) <= max(deg p, deg q).", "Count zeros of d from points of agreement.", "Apply root bound theorem by contradiction to force zero polynomial."], "demand_dimensions": {"model_choice": "Difference polynomial transformation and root bound theorem.", "representation_translation": "Point agreement conditions to roots of difference polynomial.", "reasoning_steps": "Form difference, bound degree, count roots, deduce zero polynomial identity.", "novelty": "Proof of identity everywhere from agreement at finite degree-bounded points."}, "safe_variations": ["Vary degree bound or number of agreement points."], "transfer_boundaries": ["Does not apply if agreement points count <= max degree (insufficient data)."], "common_wrong_routes": ["Equating coefficients point-by-point without establishing uniqueness or difference polynomial."], "item_refs": [BANK_IDS["Q8"]]},
    {**base(FAM_PARAM), "title": "Parameter families, roots, and degree collapse", "capability_refs": [CAP_FAM], "solution_structure": ["Set parameter conditions for specified root.", "Set parameter conditions for leading coefficient vanishing.", "Compare parameter values for root existence and degree collapse.", "Examine remaining coefficients to test zero polynomial impossibility."], "demand_dimensions": {"model_choice": "Parameter variation in polynomial equations.", "representation_translation": "Parameter condition system to root and degree behaviour.", "reasoning_steps": "Solve root condition, solve degree condition, compare, test zero polynomial.", "novelty": "Distinguishing degree reduction from zero polynomial identity."}, "safe_variations": ["Vary parameter coefficients or root location."], "transfer_boundaries": ["Does not apply if all coefficients vanish simultaneously (which yields the zero polynomial)."], "common_wrong_routes": ["Assuming degree reduction automatically implies the zero polynomial."], "item_refs": [BANK_IDS["Q9"]]},
    {**base(FAM_BIQUAD), "title": "Biquadratic equations and auxiliary domain restrictions", "capability_refs": [CAP_SUBST], "solution_structure": ["Identify even-power structure and substitute u = x^2.", "State domain restriction u >= 0 over reals.", "Solve quadratic equation for u.", "Reject negative roots and solve x = +/- sqrt(u) for non-negative roots."], "demand_dimensions": {"model_choice": "Auxiliary variable substitution with domain constraints.", "representation_translation": "Quartic polynomial to quadratic equation in u, then to real roots in x.", "reasoning_steps": "Substitute, state u >= 0, solve for u, filter admissible u, extract real x.", "novelty": "Non-linear root mapping and rejection of negative auxiliary roots."}, "safe_variations": ["Vary coefficients to produce two positive roots, one positive and one negative, or two negative roots."], "transfer_boundaries": ["Does not apply to quartics with odd powers of x without more general transformations."], "common_wrong_routes": ["Treating u as unrestricted and claiming real roots exist from negative u."], "item_refs": [BANK_IDS["Q10"]]}
]

def make_cu(mic_id: str, qid: str, decision: str, step_ids: list[str], crux_step: str, rep_id: str, stage_ids: list[str]) -> dict:
    ev = by_qid[qid]
    b_id = BANK_IDS[qid]
    cu_id = f"CU-{mic_id}-{qid}"
    return {
        "id": cu_id,
        "decision": decision,
        "step_refs": step_ids,
        "representation_ref": rep_id,
        "reveal_stage_refs": stage_ids,
        "bank_anchor_ref": b_id,
        "crux_question_refs": [b_id],
        "crux_step_ref": crux_step,
        "misconception_indexes": [0],
        "independent_checks": [
            {"role": "CHECK", "statement": ev["independent_check"]},
            {"role": "APPLY", "statement": ev["Y"]},
            {"role": "CONNECT", "statement": ev["W"]}
        ]
    }

def make_repair(mic_id: str, qid: str, cu_id: str) -> dict:
    ev = by_qid[qid]
    b_id = BANK_IDS[qid]
    return {
        "clarify": ev["X"],
        "connect": ev["W"],
        "way": ev["Y"],
        "rule": ev["Z"],
        "check": ev["independent_check"],
        "probe": f"Explain why {ev['misconception']['M1']} fails for {qid}.",
        "pattern": f"Misconception M1: {ev['misconception']['M1']}",
        "transfer": f"Apply the principle of {qid} to a variant case.",
        "wrong_idea": ev["misconception"]["M1"],
        "question_ref": b_id,
        "label": qid,
        "construction_ref": cu_id,
        "microtopic_ref": mic_id,
        "status": "CORRECTION_CANDIDATE",
        "parent_issue": 55,
        "crux_move_ref": f"{b_id}-MOVE-4"
    }

def make_anchor(qid: str, cu_id: str) -> dict:
    ev = by_qid[qid]
    b_id = BANK_IDS[qid]
    return {
        "id": f"ANCHOR-{cu_id}",
        "stem": TEACHING_STEMS[qid],
        "answer": {
            "summary": ev["verified_answer"],
            "reasoning": [move[1] for move in ev["solution_route"]],
            "check": ev["independent_check"]
        },
        "target_question_ref": b_id,
        "target_crux_move_ref": f"{b_id}-MOVE-4",
        "construction_ref": cu_id
    }

# 1. MIC_IDENT: Q8, Q3, Q7
cu_ident_q8 = make_cu(MIC_IDENT, "Q8", "Form difference polynomial d(x) = p(x) - q(x) and deduce identity from root bound contradiction.", ["IDENT-T1", "IDENT-T2", "IDENT-T3", "IDENT-T4"], "IDENT-T4", REP_IDENT_DIFF, ["POLY-IDENT-1", "POLY-IDENT-2", "POLY-IDENT-3", "POLY-IDENT-4"])
cu_ident_q3 = make_cu(MIC_IDENT, "Q3", "Evaluate quadratic uniqueness from 3 points and check 4th point degree compatibility.", ["IDENT-T1", "IDENT-T2", "IDENT-T3"], "IDENT-T3", REP_INTERP, ["POLY-INT-1", "POLY-INT-2", "POLY-INT-3", "POLY-INT-4"])
cu_ident_q7 = make_cu(MIC_IDENT, "Q7", "Deduce factor divisibility (x^2-1)q(x) and bound degree to avoid unwarranted scalar form.", ["IDENT-T1", "IDENT-T2", "IDENT-T3"], "IDENT-T2", REP_QUARTIC_CE, ["POLY-QCE-1", "POLY-QCE-2", "POLY-QCE-3", "POLY-QCE-4"])

repairs_ident = [make_repair(MIC_IDENT, qid, f"CU-{MIC_IDENT}-{qid}") for qid in ("Q8", "Q3", "Q7")]
anchors_ident = {f"CU-{MIC_IDENT}-{qid}": make_anchor(qid, f"CU-{MIC_IDENT}-{qid}") for qid in ("Q8", "Q3", "Q7")}

mic_ident = {
    **base(MIC_IDENT),
    "title": "Degree-Bounded Polynomial Identity and Difference Polynomials",
    "bucket_id": BUCKET,
    "primary_capability_ref": CAP_IDENT,
    "intrinsic_badge": "HARD",
    "badge_reason": "The decisive inference requires transforming agreement at points into roots of a difference polynomial and applying root bound theorems.",
    "entry_assumptions": [
        "Demonstrated evaluating polynomial values at given inputs.",
        "Demonstrated setting up and solving linear systems for coefficients.",
        "Demonstrated the factor theorem for linear factors."
    ],
    "inferential_jump": "Prove that two polynomials of degree at most two agreeing at three points agree everywhere by forming d(x) = p(x) - q(x) and showing d(x) must be identically zero.",
    "teaching_path": [
        {"id": "IDENT-T1", "role": "DECLARE", "action": "Define difference polynomial d(x) = p(x) - q(x) when p and q agree at given points.", "why_valid": "Agreement p(x_i) = q(x_i) implies d(x_i) = 0 for all agreement points.", "inputs": ["polynomials p(x) and q(x) with common values"], "output": "d(x_i) = 0 for each agreement input"},
        {"id": "IDENT-T2", "role": "TRANSFORM", "action": "Bound the degree of the difference: deg(d) <= max(deg p, deg q), unless d is the zero polynomial.", "why_valid": "Subtracting polynomials of degree <= 2 cannot produce terms of degree higher than 2.", "inputs": ["deg(p) <= 2 and deg(q) <= 2"], "output": "deg(d) <= 2 or d(x) = 0 identically"},
        {"id": "IDENT-T3", "role": "TRANSFORM", "action": "Apply the root bound theorem by contradiction: a non-zero polynomial of degree <= 2 has at most 2 zeros.", "why_valid": "Having 3 distinct roots directly contradicts d(x) being a non-zero polynomial of degree <= 2.", "inputs": ["d(x) has 3 distinct zeros"], "output": "d(x) cannot be a non-zero polynomial"},
        {"id": "IDENT-T4", "role": "VERIFY", "action": "Conclude d(x) is identically zero and distinguish non-zero polynomials from the zero polynomial.", "why_valid": "All coefficients of d(x) must vanish, establishing p(x) = q(x) for all x in R.", "inputs": ["d(x) is identically zero"], "output": "p(x) = q(x) everywhere"}
    ],
    "relation_refs": [],
    "representation_refs": [REP_IDENT_DIFF, REP_INTERP, REP_QUARTIC_CE],
    "question_family_refs": [FAM_SUFF, FAM_DEGREE, FAM_IDENT],
    "misconceptions": [
        {
            "wrong_idea": "Assuming a polynomial of degree <= 2 cannot agree with another at 3 points, or confusing a zero polynomial with degree 0.",
            "diagnostic_prompt": "What is the value of 0(x) at x = 1, 2, 3, 4? Does 0(x) have only two zeros, or infinitely many zeros?",
            "repair": "The theorem 'at most n zeros' applies strictly to NON-ZERO polynomials. When a degree <= n difference has n + 1 zeros, it forces the difference to be the zero polynomial."
        }
    ],
    "exit_task": {
        "prompt": "Two quadratics p and q agree at inputs -1, 0, and 2. What can be concluded about their values at x = 100?",
        "source_ref": SRC_OWNER,
        "answer": {
            "kind": "MODEL_RESPONSE",
            "summary": "By the polynomial identity theorem for degree <= 2, their difference d(x) has 3 zeros and must be identically zero, so p(100) = q(100).",
            "reasoning": [
                "Form the difference polynomial d(x) = p(x) - q(x).",
                "deg(d) <= 2 because deg(p) <= 2 and deg(q) <= 2.",
                "d(-1) = 0, d(0) = 0, and d(2) = 0 provide 3 distinct zeros.",
                "A non-zero polynomial of degree <= 2 has at most 2 zeros.",
                "Therefore, d(x) is identically zero, so p(x) = q(x) for all x, including x = 100."
            ],
            "check": "Verify that (p - q) is zero by testing the degree bound against root count.",
            "acceptable_alternatives": [],
            "subpart_answers": [],
            "verification_status": "CHECKED_BY_AUTHOR"
        },
        "oracle": {"no_numeric_claim": "Conceptual polynomial identity proof; no numeric oracle required."}
    },
    "research_contribution": "Issue #55 independent Set B construction derived from Q1-Q10 plus cited model-boundary checks.",
    "prerequisite_refs": [],
    "lineage": [],
    "elicitation": {
        "predict": {
            "prompt": "Predict whether two quadratics agreeing at 3 distinct points can have different values at any other real number.",
            "defensible_answer": "No; two quadratics agreeing at 3 distinct points must be identical everywhere."
        },
        "attempt": {
            "produces": "A written proof using difference polynomial d(x) = p(x) - q(x) and root bound contradiction.",
            "closure": "RUBRIC",
            "rubric": [
                {"criterion": "Defines difference polynomial d(x) and identifies 3 zeros.", "evidence_of": "Algebraic model selection."},
                {"criterion": "Applies non-zero root bound to establish contradiction.", "evidence_of": "Warranted deduction."}
            ],
            "accepted": ["Proofs that construct d(x) = p(x) - q(x) and conclude d(x) = 0 identically via root bound."],
            "rejected": ["Assuming without proof that 3 points uniquely determine a quadratic without degree bound justification."],
            "task": {
                "prompt": "Two polynomials p(x) and q(x) of degree at most 2 satisfy p(-1)=q(-1), p(0)=q(0), and p(2)=q(2). Prove that p(100) = q(100).",
                "givens": [],
                "representation_ref": REP_IDENT_DIFF
            }
        },
        "reconstruct": {
            "route": [
                {"ask": "What auxiliary polynomial converts points of agreement into roots?", "why_this_ask": "Difference polynomial d(x) = p(x) - q(x) standardizes agreement to finding zeros."},
                {"ask": "What is the maximum degree of d(x) if it is non-zero?", "why_this_ask": "Degree bounds constrain the number of possible roots."},
                {"ask": "How many distinct roots does d(x) possess?", "why_this_ask": "Direct counting of known agreement points."},
                {"ask": "Which theorem prevents a non-zero polynomial of degree <= 2 from having 3 roots?", "why_this_ask": "Root bound theorem for non-zero polynomials."}
            ],
            "differs_from_teaching_path": "Reconstruction starts from the learner's observation of point agreement and builds backward to the contradiction."
        },
        "boundary_test": {
            "prompt": "Would the conclusion still follow if deg(p) <= 3 and deg(q) <= 3 while agreeing at only 3 points?",
            "answer": "No; a non-zero cubic difference can possess 3 distinct roots without being the identically zero polynomial.",
            "confirms": "The learner relies on the strict inequality between root count and degree bound rather than memorizing agreement."
        }
    },
    "construction_units": [cu_ident_q8, cu_ident_q3, cu_ident_q7],
    "compact_anchor": {
        "prompt": "Degree-Bounded Polynomial Identity and Difference Polynomials",
        "result": "Prove that two polynomials of degree at most two agreeing at three points agree everywhere by forming d(x) = p(x) - q(x) and showing d(x) must be identically zero.",
        "representation_ref": REP_IDENT_DIFF
    },
    "extensions": {
        "grade9v3:learner_metadata": {"purpose": "COMPETITION", "learner_profile_ref": "PROFILE-ISS55-POLYNOMIALS-COMPETITION", "provenance": "SIMULATED_OWNER_PRESET"},
        "grade9v3:question_repairs": repairs_ident,
        "grade9v3:lesson_anchors": anchors_ident,
        "grade9v3:component_waivers": {"EQUATIONS": "This unit teaches a qualitative/formal polynomial argument; the inferential act is grounded in root bounds and domain constraints."}
    }
}

# 2. MIC_SIGN: Q5, Q2, Q4
cu_sign_q5 = make_cu(MIC_SIGN, "Q5", "Construct rigorous interval sign chart from linear factor signs partitioned at roots.", ["SIGN-T1", "SIGN-T2", "SIGN-T3", "SIGN-T4"], "SIGN-T4", REP_SIGN_TABLE, ["POLY-SIGN-1", "POLY-SIGN-2", "POLY-SIGN-3", "POLY-SIGN-4"])
cu_sign_q2 = make_cu(MIC_SIGN, "Q2", "Distinguish root multiplicity from zero counts and analyze local sign behaviour.", ["SIGN-T1", "SIGN-T2", "SIGN-T3"], "SIGN-T3", REP_SIGN_TEST, ["POLY-TEST-1", "POLY-TEST-2", "POLY-TEST-3", "POLY-TEST-4"])
cu_sign_q4 = make_cu(MIC_SIGN, "Q4", "Model geometric area difference and explain leading term cancellation causing degree drop.", ["SIGN-T1", "SIGN-T2", "SIGN-T3"], "SIGN-T1", REP_CARD_CUTOUT, ["POLY-AREA-1", "POLY-AREA-2", "POLY-AREA-3", "POLY-AREA-4"])

repairs_sign = [make_repair(MIC_SIGN, qid, f"CU-{MIC_SIGN}-{qid}") for qid in ("Q5", "Q2", "Q4")]
anchors_sign = {f"CU-{MIC_SIGN}-{qid}": make_anchor(qid, f"CU-{MIC_SIGN}-{qid}") for qid in ("Q5", "Q2", "Q4")}

mic_sign = {
    **base(MIC_SIGN),
    "title": "Interval Sign Charts and Root Multiplicity",
    "bucket_id": BUCKET,
    "primary_capability_ref": CAP_SIGN,
    "intrinsic_badge": "HARD",
    "badge_reason": "Deducing polynomial sign requires tracking parity of linear factors across partitioned intervals and respecting even vs odd multiplicity.",
    "entry_assumptions": [
        "Demonstrated factoring quadratics and cubics over integers.",
        "Demonstrated locating zeros on a real number line."
    ],
    "inferential_jump": "Construct a rigorous sign chart for a factored polynomial by partitioning the real line at its zeros and determining interval signs from the parity of negative factors.",
    "teaching_path": [
        {"id": "SIGN-T1", "role": "DECLARE", "action": "Factor the polynomial into linear factors and locate all real zeros.", "why_valid": "Continuous polynomials can only change sign at real zeros.", "inputs": ["polynomial in standard form"], "output": "factored form and set of real zeros"},
        {"id": "SIGN-T2", "role": "TRANSFORM", "action": "Partition the real line into open intervals separated by the zeros.", "why_valid": "Zeros serve as strict boundary points where polynomial evaluates to 0.", "inputs": ["real zeros in ascending order"], "output": "disjoint open intervals spanning R"},
        {"id": "SIGN-T3", "role": "TRANSFORM", "action": "Determine the sign of each linear factor across all intervals.", "why_valid": "Factor (x - c) is negative for x < c and positive for x > c.", "inputs": ["linear factors and open intervals"], "output": "tabulation of factor signs"},
        {"id": "SIGN-T4", "role": "VERIFY", "action": "Compute the product sign by counting negative factors and mark boundary zeros.", "why_valid": "An odd count of negative factors produces a negative product; an even count produces positive.", "inputs": ["factor signs per interval"], "output": "complete sign profile across R"}
    ],
    "relation_refs": [],
    "representation_refs": [REP_SIGN_TABLE, REP_SIGN_TEST, REP_CARD_CUTOUT],
    "question_family_refs": [FAM_SIGNS, FAM_MULT, FAM_CANCEL],
    "misconceptions": [
        {
            "wrong_idea": "Sketching a curve through roots without checking interval signs, or assuming roots always alternate sign regardless of multiplicity.",
            "diagnostic_prompt": "What is the sign of (x - 2)^2 when x = 1 and when x = 3? Does a squared factor change sign across its root?",
            "repair": "Signs across intervals are determined by counting negative factors; factors of even multiplicity preserve sign, while factors of odd multiplicity alternate sign."
        }
    ],
    "exit_task": {
        "prompt": "For p(x) = (x - 1)^2 (x - 4), what is the sign of p(x) for x in (1, 4)?",
        "source_ref": SRC_OWNER,
        "answer": {
            "kind": "MODEL_RESPONSE",
            "summary": "For x in (1, 4), (x - 1)^2 is positive (+) and (x - 4) is negative (-), so p(x) is negative (-).",
            "reasoning": [
                "(x - 1)^2 > 0 for all x != 1 because square of real number is non-negative.",
                "For x < 4, (x - 4) < 0.",
                "Product of positive and negative is negative."
            ],
            "check": "Test point x = 2: p(2) = (1)^2 (-2) = -2 < 0.",
            "acceptable_alternatives": [],
            "subpart_answers": [],
            "verification_status": "CHECKED_BY_AUTHOR"
        },
        "oracle": {"no_numeric_claim": "Conceptual sign determination; no numerical oracle required."}
    },
    "research_contribution": "Issue #55 independent Set B construction derived from Q1-Q10 plus cited model-boundary checks.",
    "prerequisite_refs": [],
    "lineage": [],
    "elicitation": {
        "predict": {
            "prompt": "Predict whether a repeated root of multiplicity 2 causes the graph of p(x) to cross the x-axis or touch and turn around.",
            "defensible_answer": "It touches and turns around without changing sign because (x - r)^2 is non-negative on both sides."
        },
        "attempt": {
            "produces": "An interval table showing signs of individual factors and overall product sign.",
            "closure": "RUBRIC",
            "rubric": [
                {"criterion": "Partitions real line correctly at zeros.", "evidence_of": "Domain structuring."},
                {"criterion": "Evaluates factor signs and deduces product parity.", "evidence_of": "Rigorous algebraic calculation."}
            ],
            "accepted": ["Tables that list factor signs and compute product parity algebraically."],
            "rejected": ["Drawing a wavy curve without tabulating factor signs."],
            "task": {
                "prompt": "Construct a sign chart for p(x) = (x + 1)(x - 2)^2 (x - 5) across all real intervals.",
                "givens": [],
                "representation_ref": REP_SIGN_TABLE
            }
        },
        "reconstruct": {
            "route": [
                {"ask": "Where can the polynomial potentially change sign?", "why_this_ask": "Only at real zeros."},
                {"ask": "How do linear factors behave on either side of their root?", "why_this_ask": "They change from negative to positive."},
                {"ask": "How does an even power affect sign changes?", "why_this_ask": "Even powers remain non-negative, preventing sign change."}
            ],
            "differs_from_teaching_path": "Reconstruction works from individual factor properties to overall product rather than declaring the intervals first."
        },
        "boundary_test": {
            "prompt": "What happens to the sign chart if an irreducible quadratic factor like (x^2 + 1) is present?",
            "answer": "Since x^2 + 1 > 0 for all real x, it contributes a positive sign across all intervals without adding any boundary zeros.",
            "confirms": "Learner handles non-linear factors that introduce no real roots."
        }
    },
    "construction_units": [cu_sign_q5, cu_sign_q2, cu_sign_q4],
    "compact_anchor": {
        "prompt": "Interval Sign Charts and Root Multiplicity",
        "result": "Construct a rigorous sign chart for a factored polynomial by partitioning the real line at its zeros and determining interval signs from the parity of negative factors.",
        "representation_ref": REP_SIGN_TABLE
    },
    "extensions": {
        "grade9v3:learner_metadata": {"purpose": "COMPETITION", "learner_profile_ref": "PROFILE-ISS55-POLYNOMIALS-COMPETITION", "provenance": "SIMULATED_OWNER_PRESET"},
        "grade9v3:question_repairs": repairs_sign,
        "grade9v3:lesson_anchors": anchors_sign,
        "grade9v3:component_waivers": {"EQUATIONS": "This unit teaches a qualitative/formal polynomial argument; the inferential act is grounded in root bounds and domain constraints."}
    }
}

# 3. MIC_SUBST: Q10, Q1, Q6, Q9
cu_subst_q10 = make_cu(MIC_SUBST, "Q10", "Solve biquadratic polynomials via substitution u = x^2 while strictly enforcing u >= 0.", ["SUBST-T1", "SUBST-T2", "SUBST-T3", "SUBST-T4"], "SUBST-T4", REP_AUX_DOMAIN, ["POLY-SUBST-1", "POLY-SUBST-2", "POLY-SUBST-3", "POLY-SUBST-4"])
cu_subst_q1 = make_cu(MIC_SUBST, "Q1", "Apply factor theorem to solve for parameter k, then factor completely by grouping.", ["SUBST-T1", "SUBST-T2", "SUBST-T3"], "SUBST-T1", REP_GROUPING, ["POLY-GRP-1", "POLY-GRP-2", "POLY-GRP-3", "POLY-GRP-4"])
cu_subst_q6 = make_cu(MIC_SUBST, "Q6", "Coordinate monic cubic factor model with value condition to determine third root.", ["SUBST-T1", "SUBST-T2", "SUBST-T3"], "SUBST-T3", REP_MONIC, ["POLY-MON-1", "POLY-MON-2", "POLY-MON-3", "POLY-MON-4"])
cu_subst_q9 = make_cu(MIC_SUBST, "Q9", "Analyze parameter family conditions for root existence, degree reduction, and zero polynomial impossibility.", ["SUBST-T1", "SUBST-T2", "SUBST-T3"], "SUBST-T2", REP_PARAM_COEFF, ["POLY-PAR-1", "POLY-PAR-2", "POLY-PAR-3", "POLY-PAR-4"])

repairs_subst = [make_repair(MIC_SUBST, qid, f"CU-{MIC_SUBST}-{qid}") for qid in ("Q10", "Q1", "Q6", "Q9")]
anchors_subst = {f"CU-{MIC_SUBST}-{qid}": make_anchor(qid, f"CU-{MIC_SUBST}-{qid}") for qid in ("Q10", "Q1", "Q6", "Q9")}

mic_subst = {
    **base(MIC_SUBST),
    "title": "Auxiliary Variable Substitution and Real Domain Constraints",
    "bucket_id": BUCKET,
    "primary_capability_ref": CAP_SUBST,
    "intrinsic_badge": "HARD",
    "badge_reason": "Transformations with auxiliary variables must enforce domain restrictions; negative roots in u must be rejected over the real numbers.",
    "entry_assumptions": [
        "Demonstrated quadratic formula and factoring techniques.",
        "Demonstrated properties of real squares."
    ],
    "inferential_jump": "Solve biquadratic polynomials by transforming with u = x^2 while strictly enforcing the real domain condition u >= 0 to reject spurious or non-real roots.",
    "teaching_path": [
        {"id": "SUBST-T1", "role": "DECLARE", "action": "Identify algebraic symmetry or even powers in biquadratic polynomials and introduce u = x^2.", "why_valid": "All powers of x are even, so x^4 = (x^2)^2 and x^2 = u.", "inputs": ["biquadratic polynomial"], "output": "quadratic equation in u"},
        {"id": "SUBST-T2", "role": "TRANSFORM", "action": "State and enforce the essential domain restriction: u >= 0 for all real x.", "why_valid": "The square of any real number is non-negative; negative u has no real square root.", "inputs": ["substitution definition u = x^2"], "output": "admissible domain u >= 0"},
        {"id": "SUBST-T3", "role": "TRANSFORM", "action": "Solve the quadratic equation in u and test each solution against u >= 0.", "why_valid": "Only solutions satisfying u >= 0 can be mapped back to real x via x = +/- sqrt(u).", "inputs": ["roots of quadratic in u"], "output": "filtered set of non-negative u values"},
        {"id": "SUBST-T4", "role": "VERIFY", "action": "Map accepted u to real zeros and expose why unrestricted substitution misleads.", "why_valid": "Each u > 0 gives 2 real roots, u = 0 gives 1 real root, and u < 0 gives 0 real roots.", "inputs": ["accepted u values"], "output": "complete set of real zeros in x"}
    ],
    "relation_refs": [],
    "representation_refs": [REP_AUX_DOMAIN, REP_GROUPING, REP_MONIC, REP_PARAM_COEFF],
    "question_family_refs": [FAM_BIQUAD, FAM_FACTOR, FAM_PARAM],
    "misconceptions": [
        {
            "wrong_idea": "Treating u as an unrestricted real number and claiming negative u yields real zeros, or assuming every root in u produces 2 real roots in x.",
            "diagnostic_prompt": "If a quadratic in u gives u = -4, what is x? Does any real number satisfy x^2 = -4?",
            "repair": "Substitutions inherit the range of the transforming function: for u = x^2 over R, u must be >= 0. Negative roots in u yield zero real roots in x."
        }
    ],
    "exit_task": {
        "prompt": "A biquadratic polynomial transforms into (u + 3)(u - 9) = 0 where u = x^2. What are its real zeros?",
        "source_ref": SRC_OWNER,
        "answer": {
            "kind": "MODEL_RESPONSE",
            "summary": "The root u = -3 is rejected because u >= 0. The root u = 9 gives x^2 = 9 => x = +/- 3. The only real zeros are {-3, 3}.",
            "reasoning": [
                "u = x^2 >= 0 for all real x.",
                "u + 3 = 0 gives u = -3 < 0, which has no real solution for x^2 = -3.",
                "u - 9 = 0 gives u = 9 >= 0, so x^2 = 9 => x = +/- 3."
            ],
            "check": "Substitute x = 3 and x = -3 into the original polynomial: each yields (9+3)(9-9) = 12 * 0 = 0.",
            "acceptable_alternatives": [],
            "subpart_answers": [],
            "verification_status": "CHECKED_BY_AUTHOR"
        },
        "oracle": {"no_numeric_claim": "Conceptual domain filtering proof; no numerical oracle required."}
    },
    "research_contribution": "Issue #55 independent Set B construction derived from Q1-Q10 plus cited model-boundary checks.",
    "prerequisite_refs": [],
    "lineage": [],
    "elicitation": {
        "predict": {
            "prompt": "Predict how many real roots a biquadratic polynomial can have if its transformed quadratic in u has one positive and one negative root.",
            "defensible_answer": "Exactly two real roots, from x = +/- sqrt(u_pos); the negative u root yields no real roots."
        },
        "attempt": {
            "produces": "An algebraic derivation showing substitution, domain restriction u >= 0, root filtering, and real root extraction.",
            "closure": "RUBRIC",
            "rubric": [
                {"criterion": "States domain restriction u >= 0.", "evidence_of": "Domain awareness."},
                {"criterion": "Filters negative u values and solves x = +/- sqrt(u).", "evidence_of": "Correct root mapping."}
            ],
            "accepted": ["Solutions that explicitly state u >= 0 and reject negative values."],
            "rejected": ["Solutions that produce imaginary roots or claim 4 real roots when u has negative values."],
            "task": {
                "prompt": "Solve x^4 - 3x^2 - 4 = 0 over real numbers using substitution.",
                "givens": [],
                "representation_ref": REP_AUX_DOMAIN
            }
        },
        "reconstruct": {
            "route": [
                {"ask": "What substitution transforms the 4th degree equation to a quadratic?", "why_this_ask": "u = x^2 simplifies the degree."},
                {"ask": "What restriction does real x impose on u?", "why_this_ask": "Squares of real numbers cannot be negative."},
                {"ask": "How many real x solutions arise from u > 0, u = 0, and u < 0?", "why_this_ask": "Distinguishes the three preimage cases."}
            ],
            "differs_from_teaching_path": "Reconstruction emphasizes the square root mapping as a filter rather than a mere procedural step."
        },
        "boundary_test": {
            "prompt": "What if both roots in u are negative, such as u = -1 and u = -4?",
            "answer": "The polynomial has no real zeros; the real root set is empty.",
            "confirms": "Learner correctly concludes zero real roots when all auxiliary roots violate the domain constraint."
        }
    },
    "construction_units": [cu_subst_q10, cu_subst_q1, cu_subst_q6, cu_subst_q9],
    "compact_anchor": {
        "prompt": "Auxiliary Variable Substitution and Real Domain Constraints",
        "result": "Solve biquadratic polynomials by transforming with u = x^2 while strictly enforcing the real domain condition u >= 0 to reject spurious or non-real roots.",
        "representation_ref": REP_AUX_DOMAIN
    },
    "extensions": {
        "grade9v3:learner_metadata": {"purpose": "COMPETITION", "learner_profile_ref": "PROFILE-ISS55-POLYNOMIALS-COMPETITION", "provenance": "SIMULATED_OWNER_PRESET"},
        "grade9v3:question_repairs": repairs_subst,
        "grade9v3:lesson_anchors": anchors_subst,
        "grade9v3:component_waivers": {"EQUATIONS": "This unit teaches a qualitative/formal polynomial argument; the inferential act is grounded in root bounds and domain constraints."}
    }
}

microtopics = [mic_ident, mic_sign, mic_subst]

package = {
    "schema_version": "0.2.0",
    "package_id": "EVIDENCE-LIB-MATH-ISS55-POLY",
    "title": "Polynomial Algebra and Degree Constraints — Issue #55 Candidate",
    "version": "0.1.0",
    "status": "CANDIDATE",
    "subject": "Mathematics",
    "scope_summary": "Issue #55 Grade-9 competition-preparation polynomial specimen: polynomial identity, root multiplicity, sign charts, auxiliary variables, and degree cancellation. Owner-supplied benchmark questions remain separate verbatim custody.",
    "curriculum_mappings": [],
    "resources": resources,
    "buckets": [bucket],
    "capabilities": capabilities,
    "microtopics": microtopics,
    "relations": [],
    "representations": representations,
    "question_families": families,
    "questions": [],
    "teaching_routes": [],
    "practice_profiles": [],
    "evidence": [],
    "known_issues": [],
    "extensions": {
        "grade9v3:authoring_specimen": {
            "issue": 55,
            "agent": "B",
            "round": 1,
            "purpose": "COMPETITION",
            "learner_profile_ref": "PROFILE-ISS55-POLYNOMIALS-COMPETITION",
            "qrt_evidence": "evidence/benchmark/ISS55/generated/qrt-review.v1.json",
            "launch_commit": "91719ad8df2bfc06c6a481590d2e24c510c24835",
            "independence": "Independent Set B run; Set A outputs not consulted before freeze"
        }
    },
    "data": [],
}

intake = {
    "status": "READY",
    "intake_digest": "sha256:b1a2b54b267d765e9f8665787f292c78b61c49a5b306987aa00d6e6440d66fd5",
    "inputs": {"questions": [{"id": qid, "label": qid[1:], "text": STEMS[qid]} for qid in STEMS]},
}
bank = owner_bank.new(intake, "iss55-poly")

mic_cap_map = {
    "Q8": CAP_IDENT, "Q3": CAP_IDENT, "Q7": CAP_IDENT,
    "Q5": CAP_SIGN, "Q2": CAP_SIGN, "Q4": CAP_SIGN,
    "Q10": CAP_SUBST, "Q1": CAP_SUBST, "Q6": CAP_SUBST, "Q9": CAP_SUBST
}

for qid, row in zip(STEMS, bank["questions"]):
    evidence = by_qid[qid]
    row["id"] = evidence["stable_id"]
    row["original_identifier"] = qid
    row["primary_capability_ref"] = mic_cap_map[qid]
    row["secondary_capability_refs"] = [evidence["capability_ref"]] if evidence["capability_ref"] != mic_cap_map[qid] else []
    row["family_ref"] = evidence["family_ref"]
    row["conditions"] = []
    row["figure_refs"] = [evidence["representation_ref"]]
    move_rows = []
    for number, (kind, action, why, output) in enumerate(evidence["solution_route"], 1):
        move_rows.append({
            "id": f"{row['id']}-MOVE-{number}",
            "kind": kind,
            "action": action,
            "why_valid": why,
            "inputs": ["supplied benchmark stem and prior move"],
            "output": output
        })
    row["answer"] = {
        "kind": "MODEL_RESPONSE",
        "summary": evidence["verified_answer"],
        "reasoning_route": move_rows,
        "crux_move_ref": move_rows[-1]["id"],
        "check": evidence["independent_check"],
        "verification_status": "INDEPENDENTLY_CHECKED",
    }
    stages = ["KEY_CONCEPT", "REPRESENTATION", "FIRST_MOVE", "FORMAL_MODEL", "CHECKPOINT"]
    kinds = ["CONNECT", "REPRESENT", "CONNECT", "EXECUTE", "EXECUTE"]
    row["scaffolds"] = [
        {
            "text": text,
            "support_kind": kinds[min(i, 4)],
            "reveals": "CONCEPT" if i == 0 else "METHOD",
            "learner_stage": stages[min(i, 4)],
            "supports_move_ref": move_rows[min(i, len(move_rows) - 1)]["id"]
        }
        for i, text in enumerate(evidence["hints"])
    ]
    analysis = row["extensions"].setdefault("grade9v3:analysis", {})
    analysis["learner_question_type"] = "constructed_response"
    analysis["difficulty"] = evidence["difficulty"]
    analysis["common_wrong_route"] = evidence["misconception"]["M1"]
    analysis["expected_time_seconds"] = 240 if evidence["difficulty"]["band"] == "D3" else 150
    analysis["cognitive_demand"] = evidence["demand"]
    analysis["stable_crux_move"] = evidence["Z"]
    analysis["topic"] = "Polynomials in one variable with real coefficients"
    analysis["concept_bucket"] = BUCKET
    row["extensions"]["grade9v3:benchmark_authorship"] = {
        "custody_class": "OWNER_SUPPLIED_RAW_INPUT",
        "drafted_by": "COORDINATING_AGENT",
        "personally_authored_by_owner": False,
        "official_exam_or_pyq": False
    }
    row["extensions"].setdefault("grade9v3:component_waivers", {})["CONDITIONS"] = "The supplied benchmark stem already states its material conditions; no extra condition is added to the verbatim task."
    row["extensions"]["grade9v3:math_spans"] = []
    row.pop("hints", None)
    row.pop("hint_ladder", None)

manifest = {
    "schema": "product-manifest/v1",
    "product_id": "EVIDENCE-MATH-ISS55-POLY-B",
    "subject": "Mathematics",
    "title": "Polynomial Algebra and Degree Constraints — Issue #55 Set B Candidate",
    "home_href": "index.html",
    "question_bank_href": "index.html",
    "package_refs": ["evidence/benchmark/ISS55/generated/package.v1.json"],
    "bank_refs": ["evidence/benchmark/ISS55/generated/owner.bank.json"],
    "output_roles": ["CORE1A", "CORE2"],
    "selection": {
        "microtopics": [MIC_IDENT, MIC_SIGN, MIC_SUBST],
        "core2": [BANK_IDS[f"Q{i}"] for i in range(1, 11)],
        "core2a": [],
        "core2b": []
    },
}

qrt = {
    "schema": "issue55-qrt-authoring-evidence/v1",
    "status": "AUTHORED_NOT_RENDER_VERIFIED",
    "repository": "reallaksh19/Grade9v3.5",
    "issue": 55,
    "agent": "B",
    "round": 1,
    "subject": "Mathematics",
    "grade": 9,
    "topic": "Polynomials in one variable with real coefficients",
    "source_status": "OWNER_SUPPLIED_COORDINATING_AGENT_DRAFT",
    "controlled_inputs": {
        "launch_commit": "91719ad8df2bfc06c6a481590d2e24c510c24835",
        "core_prompt_sha256": "b1a2b54b267d765e9f8665787f292c78b61c49a5b306987aa00d6e6440d66fd5",
        "blueprint_registry": "1.14.0",
        "core1a_blueprint": "BP-CORE1A-CONSTRUCTION@1.7.0",
        "core2_blueprint": "BP-CORE2-SOURCE-QUESTION@1.9.0",
        "question_demand_matrix": "question-demand-matrix/v1@1.0.0"
    },
    "learner_profile": {
        "provenance": "SIMULATED_OWNER_PRESET",
        "demonstrated": [
            "simple factorisation",
            "substitution",
            "introductory factor/remainder theorems",
            "reading a basic value table"
        ],
        "uncertain": [
            "choosing a route across several conditions",
            "repeated factors versus distinct zeros",
            "sign charts",
            "degree-bounded data sufficiency",
            "domain of an auxiliary variable"
        ]
    },
    "hardest_target": {
        "sub_concept": "MIC-MATH-POLY-IDENTITY-DEGREE-BOUND",
        "demand": "JUSTIFY D3",
        "crux": "Difference polynomial d(x) = p(x) - q(x) has 3 zeros, contradicting root bound for non-zero polynomials and forcing d(x) identically zero."
    },
    "matrix_coverage": {
        "APPLY_D3": ["Q1"],
        "EXPLAIN_D3": ["Q2", "Q9"],
        "JUSTIFY_D3": ["Q3", "Q7", "Q8", "Q10"],
        "MODEL_D3": ["Q4"],
        "REPRESENT_D3": ["Q5"],
        "SYNTHESIZE_D3": ["Q6"]
    },
    "items": [
        {
            key: row[key]
            for key in ("question_id", "stable_id", "difficulty", "demand", "qrt_cell", "X", "Y", "Z", "W", "verified_answer", "hints", "misconception", "independent_check")
        }
        for row in LEDGER["items"]
    ],
}


OUT.mkdir(parents=True, exist_ok=True)
(OUT / "package.v1.json").write_text(json.dumps(package, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
(OUT / "owner.bank.json").write_text(json.dumps(bank, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
(OUT / "product.manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
(OUT / "qrt-review.v1.json").write_text(json.dumps(qrt, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(f"wrote {OUT} successfully")
