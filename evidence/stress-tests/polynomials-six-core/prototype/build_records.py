"""Author one NCERT-grounded Polynomials stress package; no golden content copied."""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = "SRC-NCERT-GM9-CH2"
MIC = "MIC-MATH-POLY-DEGREE"
CAP = "CAP-MATH-POLY-DEGREE"
BUCKET = "BUCKET-MATH-POLY-DEGREE"
REP = "REP-MATH-POLY-POWER-CARDS"
REL = "REL-MATH-POLY-DEGREE"
FAM = "FAM-MATH-POLY-DEGREE"
QA = "Q-MATH-POLY-DEGREE-2A"
QB = "Q-MATH-POLY-DEGREE-2B"


def base(id, source=True):
    return dict(id=id, version="0.1.0", status="CANDIDATE", source_refs=[SRC] if source else [], evidence_refs=[], extensions={})


def answer(summary, reasoning, check):
    return dict(kind="MODEL_RESPONSE", summary=summary, reasoning=reasoning, check=check,
                acceptable_alternatives=[], subpart_answers=[], verification_status="CHECKED_BY_AUTHOR")


def step(id, role, action, why, output):
    return dict(id=id, role=role, action=action, why_valid=why, inputs=[], output=output)


resource = dict(base(SRC), title="Ganita Manjari, Grade 9, Part I, Chapter 2",
    origin="WEB", locator="https://ncert.nic.in/textbook/pdf/iemh102.pdf",
    edition="2026 online PDF", section="2.1 Introduction, printed page 18",
    last_checked="2026-09-29", access_status="SECTION_INSPECTED", rights_status="NCERT copyrighted textbook; cited and paraphrased",
    snapshot_ref="evidence/stress-tests/polynomials-six-core/source/iemh102.pdf",
    snapshot_digest="sha256:dbc30792858fa1858d248e4802977cb794b537c1a49f166e2777ea37baf57b02",
    role=["CURRICULUM", "EXPLANATION"], supports_claims=["For a nonzero one-variable polynomial, degree is its highest present exponent; a nonzero constant has degree zero."],
    entry_capabilities=[], depth=["Definition and basic degree examples on printed page 18"],
    selection_reason="Official Class IX chapter directly states the degree rule needed by this microtopic.",
    fallback=[])

bucket = dict(base(BUCKET), title="Degree of a one-variable polynomial", topic="Polynomials",
    intrinsic_badge="MEDIUM", badge_reason="A missing power must be treated as zero coefficient, while a nonzero constant still has degree zero.",
    depth_overlay="FOUNDATION", curriculum_mappings=[], prerequisite_refs=[], primary_representation_ref=REP)
capability = dict(base(CAP), action="Identify the highest nonzero power after combining like terms",
    success_criterion="Name the degree and justify why no higher power remains", prerequisite_refs=[], curriculum_mappings=[],
    external_provider=None, acceptance_status="CANDIDATE")

relation = dict(base(REL), expression="degree(p) = largest n with a_n not equal to 0 for nonzero p(x) = sum a_n x^n",
    meaning="The degree is controlled by the highest power whose coefficient survives after simplification.",
    symbols=[dict(symbol="p", meaning="a nonzero one-variable polynomial", unit_or_domain="polynomial in x"),
             dict(symbol="n", meaning="a whole-number exponent", unit_or_domain="nonnegative integer"),
             dict(symbol="a_n", meaning="coefficient attached to x^n", unit_or_domain="number")],
    conditions=["Combine like powers first.", "At least one coefficient is nonzero; this prototype does not assign a degree to the zero polynomial."],
    derivation=[step("POLY-D1", "DECLARE", "Write the expression as terms grouped by power.", "A power is counted only through its total coefficient.", "One coefficient per power."),
                step("POLY-D2", "VERIFY", "Find the largest power with nonzero coefficient.", "The degree definition selects exactly that power.", "Degree identified.")],
    limits=["The zero polynomial has no highest nonzero power and is outside this rule."],
    checks=["Expand or simplify the expression again and inspect the highest surviving term."], gate_relation_ref="REL-MATH-POLY-DEGREE-STRESS")

representation = dict(base(REP), kind="TABLE_OF_VALUES", purpose="Show powers 0, 1, 2 and 3 as coefficient slots before selecting the highest nonzero one.",
    required_elements=["Power labels", "Coefficients after simplification", "Highest surviving power"], relation_refs=[REL],
    read_order=["Read the power labels.", "Check each combined coefficient.", "Select the rightmost nonzero slot."],
    instance_constraints=["The figure is an unfilled decision frame; numerical coefficients must come from the adjacent task, never from the SVG."],
    accessibility=["Text labels state each exponent and coefficient.", "The caption states which term survives."],
    misleading_alternatives=["Choosing the visually largest coefficient instead of the highest exponent."],
    rendered_asset_refs=["evidence/stress-tests/polynomials-six-core/prototype/power-cards.svg"], scene_instances=[],
    correspondence=[dict(element="Highest surviving power", symbol="degree(p)", in_words="the largest exponent with nonzero coefficient")],
    reveal_stages=[dict(id="VIS-POLY-POWERS", label="Powers", purpose="Show the candidate powers.", visible_elements=["power labels"]),
                   dict(id="VIS-POLY-COEFF", label="Coefficients", purpose="Prompt combination in each slot.", visible_elements=["combine prompts"]),
                   dict(id="VIS-POLY-DEGREE", label="Degree", purpose="Prompt selection of the highest surviving power.", visible_elements=["decision prompt"])])

family = dict(base(FAM), title="Degree after simplification", capability_refs=[CAP],
    solution_structure=["Combine like powers.", "Discard zero-coefficient terms.", "Name the highest surviving exponent."],
    demand_dimensions=dict(model_choice="Decide which expression must be simplified first.", representation_translation="Move between terms and power table.", reasoning_steps="Combine, inspect, justify.", novelty="Cancellation of a visually highest term."),
    safe_variations=["Change coefficients and missing powers."],
    transfer_boundaries=["This prototype classifies nonzero one-variable polynomials only."],
    common_wrong_routes=["Read the first written exponent without simplifying."], item_refs=[QA,QB])

micro = dict(base(MIC), title="Find degree after like terms cancel", bucket_id=BUCKET, primary_capability_ref=CAP,
    intrinsic_badge="MEDIUM", badge_reason="The highest written power can disappear when like terms cancel.",
    entry_assumptions=["Can identify a term's exponent and combine like terms."],
    inferential_jump="Degree belongs to the simplified polynomial, so a written high-power term whose total coefficient is zero does not decide it.",
    teaching_path=[step("POLY-T1", "TRANSFORM", "Combine terms with the same exponent.", "Only like powers share a coefficient.", "3x^3 - 3x^3 + 2x + 5 becomes 2x + 5."),
                   step("POLY-T2", "VERIFY", "Inspect the largest exponent still attached to a nonzero coefficient.", "This is the degree rule on NCERT page 18.", "The degree is 1, not 3.")],
    relation_refs=[REL], representation_refs=[REP], question_family_refs=[FAM],
    misconceptions=[dict(wrong_idea="The largest exponent printed anywhere is always the degree.",
                        diagnostic_prompt="In 3x^3 - 3x^3 + 2x + 5, what remains of the x^3 coefficient?",
                        repair="Combine the x^3 terms first, then inspect the powers that remain.")],
    exit_task=dict(prompt="What is the degree of 4x^2 - 4x^2 + 7? Explain the cancellation.", source_ref=SRC,
                   answer=answer("Degree 0.", ["The x^2 terms cancel.", "The result is the nonzero constant 7, whose degree is 0."], "Simplify first: the result is 7."),
                   oracle=dict(no_numeric_claim="The authored response is a classification argument, checked by substitution of the simplified expression.")),
    research_contribution="Author-created cancellation-first decision based on the NCERT degree definition; pedagogy awaits independent review.",
    prerequisite_refs=[], lineage=[],
    elicitation=dict(predict=dict(prompt="Before simplifying 3x^3 - 3x^3 + 2x + 5, which written power looks largest? Will it decide the degree?", defensible_answer="Power 3 looks largest, but its coefficient cancels; degree is 1."),
        attempt=dict(produces="A simplified expression and a justified degree.", closure="RUBRIC",
                     rubric=[dict(criterion="Combines the x^3 terms to zero.", evidence_of="Does not treat a canceled term as present."), dict(criterion="Names exponent 1 as the highest surviving power.", evidence_of="Applies the definition to the simplified polynomial.")],
                     accepted=["3x^3 - 3x^3 + 2x + 5 = 2x + 5, so degree 1."], rejected=["Degree 3 because x^3 appears in the original writing."],
                     task=dict(prompt="Simplify 3x^3 - 3x^3 + 2x + 5 and decide its degree. State the coefficient that makes your decision.", givens=["The variable is x."], representation_ref=REP)),
        reconstruct=dict(route=[dict(ask="Which terms share exponent 3?", why_this_ask="They must be combined before degree can be read."),
                                dict(ask="What is their combined coefficient?", why_this_ask="Zero removes the apparent high-power term."),
                                dict(ask="Which nonzero power is now highest?", why_this_ask="This directly applies the degree rule.")],
                         differs_from_teaching_path="The learner first commits to an apparent degree, then discovers cancellation through the coefficient."),
        boundary_test=dict(prompt="What is the degree of the constant 9?", answer="Degree 0: it is the nonzero constant 9, which can be written as 9x^0.", confirms="The degree rule includes nonzero constants, not only expressions visibly containing x.")),
    construction_units=[dict(id="CU-POLY-DEGREE", decision="Simplify before naming degree.", step_refs=["POLY-T1","POLY-T2"], representation_ref=REP,
                             reveal_stage_refs=["VIS-POLY-POWERS","VIS-POLY-COEFF","VIS-POLY-DEGREE"], worked_anchor_ref=QA,
                             misconception_indexes=[0], independent_checks=[dict(statement="Expand and combine again; verify every higher exponent has coefficient zero.", check_type="SUBSTITUTION_BACK_CHECK")])],
    compact_anchor=dict(prompt="Degree of 3x^3 - 3x^3 + 2x + 5?", result="The cubic terms cancel; 2x + 5 has degree 1.", representation_ref=REP))


def question(id, stem, summary, reasoning, core, difficulty):
    q=dict(base(id), origin="AUTHORED", origin_ref=SRC, original_identifier=id, stem=stem, subparts=[], options=[],
           conditions=["Treat x as the only variable.", "Simplify before reading degree."], figure_refs=[REP],
           answer=answer(summary, reasoning, "Simplify independently and identify the largest nonzero exponent."),
           primary_capability_ref=CAP, secondary_capability_refs=[], family_ref=FAM, adaptation=None,
           exposure=[dict(core=core, role="PRACTICE" if core=="CORE2A" else "TRANSFER", artifact_ref=None)],
           learner_question_type="constructed_response", difficulty=dict(band=difficulty, score=2 if core=="CORE2A" else 5,
               components=dict(concept_model_selection=1, representation_translation=0, reasoning_chain_length=0 if core=="CORE2A" else 1,
                               algebra_computational_load=1, trap_exception_sensitivity=0 if core=="CORE2A" else 2),
               basis="Authored degree task: cancellation and classification after simplification."))
    return q

qa=question(QA,"Find the degree of 5x^2 + 3x - 5x^2 + 4.","Degree 1.",
            ["The x^2 coefficients add to zero.","The result is 3x + 4, whose highest nonzero power is 1."],"CORE2A","D1")
qa.update(representation_roles=dict(initial_ref=REP, safe_ref=None, bound_ref=REP, stage_refs=["VIS-POLY-POWERS"]),
          failure_signal="Choosing degree 2 means the two x^2 coefficients were not combined.",
          family_exposure=dict(family_ref=FAM, closure="You used cancellation to reveal a linear polynomial."),
          independent_check=dict(statement="Simplify to 3x + 4; its x coefficient is 3, not zero."), repair_ref="POLY-T1",
          hints=[dict(text="First group terms with the same exponent.", reveals="CONCEPT"),
                 dict(text="The x^2 coefficients are 5 and -5.", reveals="METHOD"),
                 dict(text="They cancel; inspect the x term.", reveals="ANSWER")],
          hint_ladder=[dict(order=1,purpose="ORIENT",text="Group equal powers before deciding.",provenance="AUTHORED_HINT"),
                       dict(order=2,purpose="REPRESENT",text="Put both x^2 coefficients in one table slot.",provenance="AUTHORED_HINT"),
                       dict(order=3,purpose="ANSWER",text="The x^2 slot is zero; 3x remains, so degree 1.",provenance="AUTHORED_HINT")])
qb=question(QB,"A coefficient table for p(x) lists power 3: 0, power 2: 0, power 1: 0, power 0: 6. What is the degree of p(x)? Explain your decision from the table.",
            "Degree 0.",
            ["The table represents the nonzero constant polynomial 6.","The only nonzero coefficient is in the power-zero slot, so the degree is 0."],"CORE2B","D2")
qb.update(representation_roles=dict(initial_ref=REP,safe_ref=REP,bound_ref=REP,stage_refs=["VIS-POLY-POWERS"]),
          transfer=dict(dimension="representation_translation", statement="Read the coefficient table rather than simplify a written expression.", builds_on=[QA],
                        invariant="The highest power with a nonzero coefficient decides degree.",
                        novelty=dict(checked_against=[QA],why_new="Earlier practice required combining written like terms; here the learner must translate a sparse coefficient table to a polynomial and recognize a constant.")),
          independent_check=dict(statement="Translate the table to p(x) = 6 and compare with NCERT's nonzero constant example."),repair_ref="POLY-T2",
          hints=[dict(text="Treat each table entry as the coefficient of that power.", reveals="CONCEPT"),dict(text="Check which power has the only nonzero coefficient.",reveals="METHOD"),dict(text="The table represents the constant 6.",reveals="ANSWER")],
          hint_ladder=[dict(order=1,purpose="ORIENT",text="Read the table as coefficients, not as four terms that must all appear.",provenance="AUTHORED_HINT"),
                       dict(order=2,purpose="REPRESENT",text="The coefficient at power 0 is the constant term.",provenance="AUTHORED_HINT"),
                       dict(order=3,purpose="ANSWER",text="Only power 0 has a nonzero coefficient, so degree 0.",provenance="AUTHORED_HINT")])

package=dict(schema_version="0.2.0",package_id="STRESS-LIB-MATH-POLY-DEGREE",title="Polynomials degree stress prototype",version="0.1.0",status="CANDIDATE",subject="Mathematics",
             scope_summary="One microtopic: degree after simplification, including the zero boundary.", curriculum_mappings=[],
             resources=[resource],buckets=[bucket],capabilities=[capability],microtopics=[micro],relations=[relation],representations=[representation],
             question_families=[family],questions=[qa,qb],teaching_routes=[],practice_profiles=[],evidence=[],known_issues=[],extensions={},data=[])
manifest=dict(schema="product-manifest/v1",product_id="STRESS-MATH-POLY-DEGREE",subject="Mathematics",home_href="../index.html",question_bank_href="../index.html",
              package_refs=["evidence/stress-tests/polynomials-six-core/prototype/records.json"],bank_refs=[],
              selection=dict(microtopics=[MIC],core2=[],core2a=[QA],core2b=[QB]))
(HERE/"records.json").write_text(json.dumps(package,indent=2,ensure_ascii=False)+"\n",encoding="utf8")
(HERE/"manifest.json").write_text(json.dumps(manifest,indent=2)+"\n",encoding="utf8")
