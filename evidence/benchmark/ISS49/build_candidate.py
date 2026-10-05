#!/usr/bin/env python3
from __future__ import annotations
import hashlib, html, json, re, sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO))
from Shared.tools import owner_bank

INPUTS = ROOT / "inputs"
ASSETS = ROOT / "assets"
BASELINE = "91719ad8df2bfc06c6a481590d2e24c510c24835"
CORE_SHA = "c2cca6e6b92997c30d2f3a7eab91577bc8463ec9ce44ca90b9be728f3d1d46b8"
BANK_ID = "iss49-poly-d1"
CAP_TO_MICRO = {
    "CAP-MAT-POLY-STRUCTURE": ("MIC-MAT-POLY-STRUCTURE", "CU-MAT-POLY-STRUCTURE"),
    "CAP-MAT-POLY-OPERATE": ("MIC-MAT-POLY-OPERATE", "CU-MAT-POLY-OPERATE"),
    "CAP-MAT-POLY-MODEL": ("MIC-MAT-POLY-MODEL", "CU-MAT-POLY-MODEL"),
    "CAP-MAT-POLY-CONSTRAINT": ("MIC-MAT-POLY-CONSTRAINT", "CU-MAT-POLY-CONSTRAINT"),
}
TEACH_REP = {
    "CAP-MAT-POLY-STRUCTURE": "REP-MATH-ISS49-STRUCTURE",
    "CAP-MAT-POLY-OPERATE": "REP-MATH-ISS49-OPERATE",
    "CAP-MAT-POLY-MODEL": "REP-MATH-ISS49-MODEL",
    "CAP-MAT-POLY-CONSTRAINT": "REP-MATH-ISS49-CONSTRAINT",
}

def load(path):
    return json.loads(path.read_text(encoding="utf-8"))

def dump(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def score_band(score):
    if score <= 2: return "D1"
    if score <= 5: return "D2"
    if score <= 7: return "D3"
    return "D4"

def math_spans(text):
    out=[]
    seen=set()
    for m in re.finditer(r"\$([^$]+)\$", text):
        literal=m.group(1)
        if literal in seen:
            continue
        seen.add(literal)
        out.append({"target":"stem","literal":literal,"tex":literal,"display":False})
    return out

def answer_obj(spec, qid):
    route=[]
    for i,(kind,action,why,output) in enumerate(spec["moves"],1):
        route.append({
            "id": f"{qid}-MOVE-{i}",
            "kind": kind,
            "action": action,
            "why_valid": why,
            "inputs": [spec.get("summary","") if i == 1 else route[-1]["output"]],
            "output": output,
        })
    crux_idx=int(spec["crux"].split("-")[-1])
    return {
        "kind":"EXACT",
        "summary":spec["summary"],
        "reasoning":[m["output"] for m in route],
        "reasoning_route":route,
        "crux_move_ref":f"{qid}-MOVE-{crux_idx}",
        "check":spec["check"],
        "acceptable_alternatives":[],
        "subpart_answers":[],
        "verification_status":"CHECKED_BY_AUTHOR",
    }

def question_conditions(n):
    if n == 2:
        return ["The variable is x and the coefficient field is the real numbers."]
    if n == 7:
        return ["x ≥ 0."]
    if n == 9:
        return ["The equality claim is over every real x."]
    return []

def qrt_template_id(spec):
    return f"QRT-{spec['demand']}-{spec['band']}"

def build_bank(intake, specs):
    bank=owner_bank.new(intake, BANK_ID)
    by_n={s["n"]:s for s in specs}
    for q in bank["questions"]:
        n=int(q["original_identifier"][1:])
        s=by_n[n]
        qid=q["id"]
        q["primary_capability_ref"]=s["cap"]
        q["family_ref"]=s["fam"]
        q["answer"]=answer_obj(s,qid)
        q["conditions"]=question_conditions(n)
        q["figure_refs"]=[s["figure"]] if s.get("figure") else []
        q["scaffolds"]=[
            {"text":s["scaffolds"][0],"support_kind":"CONNECT","reveals":"CONCEPT","learner_stage":"KEY_CONCEPT","supports_move_ref":f"{qid}-MOVE-1"},
            {"text":s["scaffolds"][1],"support_kind":"CONNECT","reveals":"CONCEPT","learner_stage":"REPRESENTATION","supports_move_ref":q["answer"]["crux_move_ref"]},
            {"text":s["scaffolds"][2],"support_kind":"EXECUTE","reveals":"METHOD","learner_stage":"FIRST_MOVE","supports_move_ref":f"{qid}-MOVE-3"},
        ]
        micro, unit=CAP_TO_MICRO[s["cap"]]
        repair=dict(s["repair"])
        repair.update({
            "question_ref":qid,
            "label":q["original_identifier"],
            "construction_ref":unit,
            "microtopic_ref":micro,
            "status":"CANDIDATE",
            "parent_issue":49,
            "crux_move_ref":q["answer"]["crux_move_ref"],
        })
        difficulty={"band":s["band"],"score":s["score"],"components":s["comp"],
                    "basis":f"{q['original_identifier']} decisive act: {s['moves'][int(s['crux'].split('-')[-1])-1][1]}. Total score {s['score']} -> {s['band']}."}
        ext=q["extensions"]
        ext["grade9v3:analysis"]={
            "learner_question_type":"constructed_response",
            "difficulty":difficulty,
            "common_wrong_route":s["wrong"],
            "expected_time_seconds":s["time"],
            "cognitive_demand":{"primary":s["demand"],"secondary":s["secondary"]},
            "stable_crux_move":s["moves"][int(s["crux"].split("-")[-1])-1][1],
        }
        ext["grade9v3:math_spans"]=math_spans(q["stem"])
        ext["grade9v3:learning_repair"]=repair
        ext["grade9v3:authorship"]={
            "kind":"COORDINATOR_AI_DRAFTED",
            "owner_supplied":True,
            "personally_owner_authored":False,
        }
        ext["grade9v3:qrt_template"]={
            "template_id":qrt_template_id(s),
            "matrix_ref":"Shared/quality/question-demand-matrix.v1.json",
            "status":"CANDIDATE",
        }
        waivers={}
        if not q["conditions"]:
            waivers["CONDITIONS"]="No additional condition is needed beyond the verbatim stem and global one-variable real-coefficient scope."
        if not q["figure_refs"]:
            waivers["REPRESENTATION"]="A separate diagram would be decorative or would duplicate the symbolic object; the question is reviewed through symbolic text and construction support."
        if waivers:
            ext["grade9v3:component_waivers"]=waivers
        if q["figure_refs"]:
            ext["grade9v3:core2_visual_review"]={
                "question_ref":qid,
                "authored_figure_refs":q["figure_refs"],
                "replaces_authored_figure_refs":q["figure_refs"],
                "rationale":"The representation exposes only supplied structure and a blank bridge; the requested coefficient, expansion, model result or parameter remains learner work.",
                "review_status":"AUTHOR_REFERENCE_GROUNDED_REVIEW_NOT_INDEPENDENT_ACCEPTANCE",
            }
    return bank

def common_record(id_, **kwargs):
    row={"id":id_,"version":"0.1.0","status":"CANDIDATE","source_refs":[],"evidence_refs":[],"extensions":{}}
    row.update(kwargs)
    return row

def resource_rows():
    return [
        common_record(
            "SRC-OWNER-ISS49-POLY",
            title="Issue #49 owner-supplied polynomial stress-test questions",
            origin="AUTHORED",
            locator="https://github.com/reallaksh19/Grade9v3.5/issues/49",
            edition="Owner prompt captured 2026-10-05",
            section="Core prompt A — Q1–Q10",
            last_checked="2026-10-05",
            access_status="FULL_ITEM_INSPECTED",
            rights_status="Owner-supplied benchmark text; AI/coordinator authored under Owner request; no official exam or textbook identity claimed.",
            snapshot_ref=None,
            snapshot_digest=None,
            role=["QUESTION_BANK","AUTHOR_CREATED"],
            supports_claims=[],
            entry_capabilities=[],
            depth=["COMPETITION"],
            selection_reason="Exact custody surface for the ten fixed Issue #49 questions.",
            fallback=[],
        ),
        common_record(
            "SRC-NCERT-9-POLYNOMIALS",
            title="NCERT Ganita Manjari Grade 9, Chapter 2: Polynomials",
            origin="WEB",
            locator="https://ncert.nic.in/textbook/pdf/iemh102.pdf",
            edition="Web source checked 2026-10-05",
            section="2.1 Introduction and polynomial examples",
            last_checked="2026-10-05",
            access_status="SECTION_INSPECTED",
            rights_status="Official NCERT source is linked, not republished.",
            snapshot_ref=None,
            snapshot_digest=None,
            role=["CURRICULUM","EXPLANATION"],
            supports_claims=["One-variable polynomial terminology, coefficients, degree, constant polynomials and zero terminology."],
            entry_capabilities=[],
            depth=["FOUNDATION"],
            selection_reason="Official Grade 9 reference supporting the polynomial definitions and terminology used in the teaching.",
            fallback=[],
        ),
    ]

def capabilities():
    rows=[
      ("CAP-MAT-POLY-STRUCTURE","Identify and represent degree, coefficients, missing powers and the polynomial/non-polynomial boundary","Correctly preserves exponent slots, classifies allowed exponents, and reconstructs coefficient representations."),
      ("CAP-MAT-POLY-OPERATE","Evaluate and combine polynomials and use distributive identities for expansion and factorisation","Substitutes with grouping, combines only like powers, exposes all products and verifies factorizations by multiplication."),
      ("CAP-MAT-POLY-MODEL","Choose a polynomial model for a simple geometric quantity and justify identities for all real inputs","Selects the governing relation, preserves units and uses universal algebraic warrants rather than sampled agreement."),
      ("CAP-MAT-POLY-CONSTRAINT","Construct a linear polynomial from a fixed constant and specified zero and establish uniqueness","Represents the one-parameter family, converts the zero into an equation, solves the parameter and checks both constraints."),
    ]
    out=[]
    for id_,action,criterion in rows:
        out.append(common_record(id_,source_refs=["SRC-NCERT-9-POLYNOMIALS"],action=action,success_criterion=criterion,
                                 prerequisite_refs=[],curriculum_mappings=[],external_provider=None,acceptance_status="CANDIDATE"))
    return out

def relations():
    def rel(id_, expression, meaning, symbols, conditions, checks, limits, source=True):
        return common_record(
            id_,
            source_refs=["SRC-NCERT-9-POLYNOMIALS"] if source else [],
            expression=expression,
            meaning=meaning,
            symbols=symbols,
            conditions=conditions,
            derivation=[{
                "id":f"{id_}-DERIVE-1","role":"DECLARE",
                "action":"State the governing definition, identity or geometric relation.",
                "why_valid":"This relation is used only under its stated conditions.",
                "inputs":[expression],"output":meaning
            }],
            limits=limits,
            checks=checks,
            gate_relation_ref=None,
        )
    return [
      rel("REL-MAT-POLY-FORM","p(x)=a_n x^n+...+a_1 x+a_0",
          "A one-variable real-coefficient polynomial is a finite sum whose variable exponents are non-negative integers; missing powers have coefficient zero.",
          [{"symbol":"a_k","meaning":"real coefficient of x^k","unit_or_domain":"real number"},{"symbol":"k","meaning":"exponent index","unit_or_domain":"non-negative integer"}],
          ["Only finitely many coefficients are non-zero.","The highest non-zero exponent is the degree for a non-zero polynomial."],
          ["Reconstruct the expression from its coefficient slots."],
          ["The zero polynomial needs a separate degree convention and is not required by the supplied questions."]),
      rel("REL-MAT-DISTRIBUTIVE","a(b+c)=ab+ac",
          "Multiplication distributes over addition; applying it repeatedly expands polynomial products.",
          [{"symbol":"a,b,c","meaning":"real expressions","unit_or_domain":"real algebraic quantities"}],
          ["Ordinary real-number algebra applies."],
          ["Factor the expanded expression or substitute a simple value."],
          ["The identity preserves equality but does not by itself justify combining unlike powers."]),
      rel("REL-MAT-DIFF-SQUARES","a^2-b^2=(a-b)(a+b)",
          "Conjugate factors expand with cancelling cross terms.",
          [{"symbol":"a,b","meaning":"real expressions","unit_or_domain":"real algebraic quantities"}],
          ["The expression is a difference of two squares."],
          ["Multiply the factors to recover the original difference."],
          ["A sum of squares does not factor by this real identity."]),
      rel("REL-MAT-RECT-AREA","A=L×W",
          "Rectangle area is the product of perpendicular side lengths.",
          [{"symbol":"A","meaning":"area","unit_or_domain":"square length unit"},{"symbol":"L,W","meaning":"side lengths","unit_or_domain":"length"}],
          ["L and W are the rectangle's perpendicular side lengths."],
          ["At a permitted simple input, compare with direct numeric length×width."],
          ["This relation models area, not perimeter or a one-dimensional length."],source=False),
      rel("REL-MAT-POLY-ZERO","r is a zero of p iff p(r)=0",
          "A specified zero is a substitution condition on the polynomial.",
          [{"symbol":"r","meaning":"specified zero","unit_or_domain":"real number"},{"symbol":"p","meaning":"polynomial","unit_or_domain":"real-coefficient polynomial"}],
          ["r is in the polynomial's real input domain."],
          ["Substitute r into the constructed polynomial."],
          ["The relation identifies zeros; uniqueness of a constructed polynomial needs any additional coefficient constraints too."]),
    ]

def svg_for(rep):
    groups=[]
    y=70
    for i,stage in enumerate(rep["stages"]):
        sid=html.escape(stage["id"],quote=True)
        label=html.escape(stage["label"])
        text=html.escape(stage["text"])
        groups.append(f'<g data-g9-stage-id="{sid}"><text x="32" y="48" font-size="24">{label}</text><rect x="32" y="78" width="756" height="170" rx="12" fill="none" stroke="currentColor" stroke-width="3"/><text x="52" y="128" font-size="20">{text}</text><text x="52" y="188" font-size="18">Use the structure shown; the requested result remains learner work.</text></g>')
    return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 820 290" role="img" aria-label="'+html.escape(rep["purpose"],quote=True)+'"><title>'+html.escape(rep["purpose"])+'</title><desc>Three staged algebra-support views. Protected answer content is omitted.</desc><style>text{font-family:Arial,sans-serif;fill:currentColor}</style>'+''.join(groups)+'</svg>'

def build_representations(config):
    out=[]
    ASSETS.mkdir(parents=True,exist_ok=True)
    for rep in config:
        path=ASSETS/rep["file"]
        path.write_text(svg_for(rep),encoding="utf-8")
        ext={}
        match=re.search(r"-Q(\d+)$", rep["id"])
        if match:
            ext["grade9v3:authored_question_ref"]=f"OWN-{BANK_ID.upper()}-{int(match.group(1)):02d}"
        out.append(common_record(
            rep["id"],kind=rep["kind"],purpose=rep["purpose"],extensions=ext,
            required_elements=[s["label"] for s in rep["stages"]],
            relation_refs=[],
            read_order=[s["text"] for s in rep["stages"]],
            instance_constraints=["Pre-attempt stages orient without supplying the requested final result."],
            accessibility=["SVG has an accessible title and description.","All meaning is repeated in text labels."],
            misleading_alternatives=["Printing the protected coefficient, expansion, model result or parameter before learner commitment."],
            rendered_asset_refs=[f"evidence/benchmark/ISS49/assets/{rep['file']}"],
            scene_instances=[],
            reveal_stages=[{"id":s["id"],"label":s["label"],"purpose":s["text"],"visible_elements":[s["label"]]} for s in rep["stages"]],
        ))
    return out

def families(specs):
    defs={
      "FAM-MAT-POLY-STRUCTURE":("Polynomial structure and classification",["CAP-MAT-POLY-STRUCTURE"]),
      "FAM-MAT-POLY-OPERATE":("Polynomial evaluation, combination and identities",["CAP-MAT-POLY-OPERATE"]),
      "FAM-MAT-POLY-MODEL":("Polynomial modelling and identity justification",["CAP-MAT-POLY-MODEL"]),
      "FAM-MAT-POLY-CONSTRAINT":("Polynomial construction from constraints",["CAP-MAT-POLY-CONSTRAINT"]),
    }
    out=[]
    for fid,(title,caps) in defs.items():
        refs=[f"OWN-{BANK_ID.upper()}-{s['n']:02d}" for s in specs if s["fam"]==fid]
        out.append(common_record(fid,title=title,capability_refs=caps,
            solution_structure=["Identify the defining relation or invariant.","Carry out the question-specific transformation.","Verify using an independent reconstruction, substitution or boundary check."],
            demand_dimensions={"model_choice":"Low to connected choice depending on item.","representation_translation":"Symbol, table or geometry translation where the item requires it.","reasoning_steps":"One direct step through a short connected chain.","novelty":"Fresh values and representations preserve the same concept boundary."},
            safe_variations=["Change coefficients, constants or non-zero roots while preserving the concept and stated domain."],
            transfer_boundaries=["Do not introduce calculus, complex-number roots or unbounded degree assumptions."],
            common_wrong_routes=["Use surface pattern matching without preserving exponent, model or domain conditions."],
            item_refs=refs))
    return out

def make_microtopics(concepts, specs, bank):
    by_n={s["n"]:s for s in specs}
    q_by_n={int(q["original_identifier"][1:]):q for q in bank["questions"]}
    out=[]
    for c in concepts:
        unit=CAP_TO_MICRO[c["cap"]][1]
        step_ids=[]
        teaching=[]
        for i,(action,why,output) in enumerate(c["steps"],1):
            sid=f"{unit}-TEACH-{i}"
            step_ids.append(sid)
            teaching.append({"id":sid,"role":"DECLARE" if i==1 else ("VERIFY" if i==len(c["steps"]) else "TRANSFORM"),
                             "action":action,"why_valid":why,"inputs":[] if i==1 else [c["steps"][i-2][2]],"output":output})
        qrefs=[q_by_n[n]["id"] for n in c["questions"]]
        target=q_by_n[c["anchor_q"]]
        repair_rows=[q_by_n[n]["extensions"]["grade9v3:learning_repair"] for n in c["questions"]]
        anchor=c["anchor"]
        anchor_obj={"id":f"ANCHOR-{unit}","stem":anchor["stem"],
                    "answer":{"summary":anchor["summary"],"reasoning":[anchor["summary"]],"check":anchor["check"]},
                    "target_question_ref":target["id"],"target_crux_move_ref":target["answer"]["crux_move_ref"],"construction_ref":unit}
        ext={
          "grade9v3:question_repairs":repair_rows,
          "grade9v3:lesson_anchors":{unit:anchor_obj},
          "grade9v3:component_waivers":{},
        }
        out.append(common_record(
          c["id"],source_refs=["SRC-NCERT-9-POLYNOMIALS"],title=c["title"],bucket_id="BUCKET-MAT-09-POLYNOMIALS",
          primary_capability_ref=c["cap"],intrinsic_badge=c["badge"],badge_reason=c["badge_reason"],
          entry_assumptions=c["assumptions"],inferential_jump=c["jump"],teaching_path=teaching,
          relation_refs=c["relation_ids"],representation_refs=[TEACH_REP[c["cap"]]],question_family_refs=[c["family"]],
          misconceptions=[c["misconception"]],
          exit_task={"prompt":c["exit"]["prompt"],"source_ref":"SRC-OWNER-ISS49-POLY",
                     "answer":{"kind":"MODEL_RESPONSE","summary":c["exit"]["summary"],"reasoning":[c["exit"]["summary"]],"check":c["exit"]["check"],"acceptable_alternatives":[],"subpart_answers":[],"verification_status":"CHECKED_BY_AUTHOR"},
                     "oracle":{"no_numeric_claim":"Authored changed-case recall; not an owner question."}},
          research_contribution=f"Issue #49 concept construction for {', '.join('Q'+str(n) for n in c['questions'])}.",
          prerequisite_refs=[],lineage=[],
          construction_units=[{"id":unit,"decision":c["jump"],"step_refs":step_ids,
             "representation_ref":TEACH_REP[c["cap"]],
             "reveal_stage_refs":[f"{TEACH_REP[c['cap']]}-S1",f"{TEACH_REP[c['cap']]}-S2",f"{TEACH_REP[c['cap']]}-S3"],
             "bank_anchor_ref":target["id"],"crux_question_refs":qrefs,"crux_step_ref":step_ids[1],
             "misconception_indexes":[0],"relation_refs":c["relation_ids"],
             "independent_checks":[
               {"role":"CHECK","statement":c["exit"]["check"]},
               {"role":"APPLY","statement":c["exit"]["prompt"]},
               {"role":"CONNECT","statement":"State which invariant or defining condition made the method valid."},
             ]}],
          extensions=ext
        ))
    return out

def build_package(config, specs, bank):
    reps=build_representations(config["representations"])
    micro=make_microtopics(config["concepts"],specs,bank)
    bucket=common_record("BUCKET-MAT-09-POLYNOMIALS",source_refs=["SRC-NCERT-9-POLYNOMIALS"],
        title="Polynomials in one variable",topic="Polynomials in one variable",
        intrinsic_badge="MEDIUM",badge_reason="The set mixes terminology, representation, symbolic operations, modelling, justification and constraint construction.",
        depth_overlay="FOUNDATION",curriculum_mappings=[],prerequisite_refs=[],
        primary_representation_ref="REP-MATH-ISS49-STRUCTURE")
    return {
      "schema_version":"0.2.0","package_id":"PKG-MAT-ISS49-POLY-D1","title":"Polynomials — Issue #49 candidate",
      "version":"0.1.0","status":"CANDIDATE","subject":"Mathematics",
      "scope_summary":"Grade 9 one-variable real-coefficient polynomials from ten fixed owner-supplied benchmark questions; concept teaching and competition preparation, with no calculus or complex-number prerequisite.",
      "curriculum_mappings":[],"resources":resource_rows(),"buckets":[bucket],"capabilities":capabilities(),
      "microtopics":micro,"relations":relations(),"representations":reps,"question_families":families(specs),
      "questions":[],"teaching_routes":[],"practice_profiles":[],"evidence":[],"known_issues":[],
      "extensions":{"grade9v3:authoring_specimen":{"issue":49,"round":"POLYNOMIAL-STRESS-V1","purpose":"COMPETITION","learner_profile":"SIMULATED_OWNER_PRESET","qrt_evidence":"evidence/benchmark/ISS49/qrt-review.json"}},
      "data":[]
    }

def build_qrt(specs, bank, package):
    matrix=load(REPO/"Shared/quality/question-demand-matrix.v1.json")
    reps={r["id"]:r for r in package["representations"]}
    q_by_n={int(q["original_identifier"][1:]):q for q in bank["questions"]}
    out=[]
    for s in specs:
        q=q_by_n[s["n"]]
        demand=matrix["demands"][s["demand"]]
        targets=demand["targets"]
        band=matrix["band_policies"][s["band"]]
        repair=q["extensions"]["grade9v3:learning_repair"]
        facets={}
        for code,row in matrix["review_asks"].items():
            question=row["question"].format(
                X=targets["X"],Y=targets["Y"],Z=targets["Z"],W=targets["W"],
                band_protected_work=band["protected_work"],visual_job=targets["visual_job"],
                check_job=targets["check_job"],wrong_idea=targets["wrong_idea"],
                replacement_rule=targets["replacement_rule"])
            if code=="H1": evidence=q["scaffolds"][0]["text"]; status="AUTHOR_REVIEW_PASS"
            elif code=="H2": evidence=q["scaffolds"][1]["text"]; status="AUTHOR_REVIEW_PASS"
            elif code=="H3": evidence=q["scaffolds"][2]["text"]; status="AUTHOR_REVIEW_PASS"
            elif code.startswith("S"):
                if q["figure_refs"]:
                    rr=reps[q["figure_refs"][0]]
                    evidence={"representation_ref":rr["id"],"stage_ids":[x["id"] for x in rr["reveal_stages"]]}
                    status="AUTHOR_REVIEW_PASS"
                else:
                    evidence=q["extensions"]["grade9v3:component_waivers"]["REPRESENTATION"]
                    status="WAIVED_WITH_REASON"
            elif code=="P1": evidence={"scaffolds":q["scaffolds"],"protected_work":band["protected_work"]}; status="AUTHOR_REVIEW_PASS"
            elif code=="P2": evidence=repair["construction_ref"]; status="AUTHOR_REVIEW_PASS"
            elif code=="P3": evidence={"reasoning_route":q["answer"]["reasoning_route"],"check":q["answer"]["check"]}; status="AUTHOR_REVIEW_PASS"
            elif code=="M1": evidence={"wrong_idea":repair["wrong_idea"],"probe":repair["probe"]}; status="AUTHOR_REVIEW_PASS"
            elif code=="M2": evidence={"probe":repair["probe"],"pattern":repair["pattern"]}; status="AUTHOR_REVIEW_PASS"
            else: evidence={"rule":repair["rule"],"check":repair["check"],"transfer":repair["transfer"]}; status="AUTHOR_REVIEW_PASS"
            facets[code]={"status":status,"review_question":question,"objective":row["objective"],"authored_evidence":evidence}
        out.append({"question_ref":q["id"],"label":q["original_identifier"],"template_id":qrt_template_id(s),
                    "band":s["band"],"primary_demand":s["demand"],"secondary_demands":s["secondary"],
                    "construction_ref":repair["construction_ref"],"review_independence":"IMPLEMENTATION_COUPLED_NOT_INDEPENDENT",
                    "facets":facets})
    return out

def main():
    core=ROOT/"owner-core-prompt.md"
    if not core.exists():
        raise SystemExit("owner-core-prompt.md missing")
    if sha(core)!=CORE_SHA:
        raise SystemExit(f"owner-core-prompt SHA mismatch: {sha(core)}")
    intake=load(ROOT/"intake.json")
    specs=load(ROOT/"questions-01-05.json")["questions"]+load(ROOT/"questions-06-10.json")["questions"]
    for s in specs:
        if s["score"] != sum(s["comp"].values()) or s["band"] != score_band(s["score"]):
            raise SystemExit(f"difficulty mismatch Q{s['n']}")
    bank=build_bank(intake,specs)
    cfg=load(ROOT/"concepts.json")
    package=build_package(cfg,specs,bank)
    INPUTS.mkdir(parents=True,exist_ok=True)
    dump(INPUTS/"owner.bank.json",bank)
    dump(INPUTS/"package.v1.json",package)
    manifest={
      "schema":"product-manifest/v1","product_id":"EVIDENCE-MAT-ISS49-POLY-D1","subject":"Mathematics",
      "home_href":"index.html","question_bank_href":"index.html",
      "package_refs":["evidence/benchmark/ISS49/inputs/package.v1.json"],
      "bank_refs":["evidence/benchmark/ISS49/inputs/owner.bank.json"],
      "selection":{"microtopics":[c["id"] for c in cfg["concepts"]],
                   "core2":[q["id"] for q in bank["questions"]],"core2a":[],"core2b":[]},
      "output_roles":["CORE1A","CORE2"],"title":"Polynomials — Issue #49 candidate"
    }
    dump(INPUTS/"product.manifest.json",manifest)
    qrt=build_qrt(specs,bank,package)
    dump(ROOT/"qrt-review.json",qrt)
    ledger=[]
    for s,q in zip(specs,bank["questions"]):
        ledger.append({"question_ref":q["id"],"label":q["original_identifier"],"stem":q["stem"],
          "answer_summary":q["answer"]["summary"],"capability_ref":s["cap"],
          "difficulty":{"band":s["band"],"score":s["score"],"components":s["comp"]},
          "cognitive_demand":{"primary":s["demand"],"secondary":s["secondary"]},
          "cohort_comparison":"MATCH_D1_INTENT" if s["band"]=="D1" else "ACTUAL_D2_ABOVE_D1_INTENT",
          "crux_move_ref":q["answer"]["crux_move_ref"],"verification_status":"CHECKED_BY_AUTHOR"})
    dump(ROOT/"question-ledger.json",ledger)
    dump(ROOT/"source-cards.json",[
      {"id":"SRC-OWNER-ISS49-POLY","kind":"OWNER_SUPPLIED","locator":"https://github.com/reallaksh19/Grade9v3.5/issues/49","claims":["Exact Q1-Q10 custody"],"authorship":"AI/coordinator authored under Owner request; not official exam/PYQ or authenticated textbook transcription."},
      {"id":"SRC-NCERT-9-POLYNOMIALS","kind":"OFFICIAL_CURRICULUM_REFERENCE","locator":"https://ncert.nic.in/textbook/pdf/iemh102.pdf","last_checked":"2026-10-05","claims":["One-variable polynomial terminology, coefficients, degree and constant polynomials."],"note":"Official source supports general mathematical definitions; it is not the provenance of the owner benchmark questions."}
    ])
    hardest=next(x for x in ledger if x["label"]=="Q10")
    dump(ROOT/"hardest-target.json",{
      "question_ref":hardest["question_ref"],"label":"Q10","microtopic_ref":"MIC-MAT-POLY-CONSTRAINT",
      "sub_concept":"Constructing a linear polynomial from a fixed constant and specified zero, then proving uniqueness.",
      "primary_demand":"SYNTHESIZE","band":"D2","score":5,
      "learner_relative":{"X":"Coordinate the fixed constant term with the zero condition rather than treating them independently.",
        "Y":"Demonstrated substitution into a familiar linear expression and signed-number operations.",
        "Z":"Represent the family p(x)=ax+2, impose p(1)=0, solve a, then recheck both constraints.",
        "W":"The equation linking the zero condition to the remaining coefficient and the uniqueness conclusion."},
      "diagnostic_hypothesis":"Because interpreting a zero is uncertain in the simulated preset, a learner may preserve the root under arbitrary scaling while overlooking that scaling changes the fixed constant.",
      "interaction":"The Core1A question-specific repair requires a typed prediction and reason before revealing the changed-case pattern for constant 6 and zero 3. No subject-mismatched MODEL_SCOPE_PROBE is enabled."
    })
    dump(ROOT/"custody-receipt.json",{"issue":49,"round":"POLYNOMIAL-STRESS-V1","baseline":BASELINE,
       "owner_core_sha256":sha(core),"expected_owner_core_sha256":CORE_SHA,"question_count":10,
       "wording_policy":"VERBATIM via owner_bank custody hashes","provenance":"OWNER_SUPPLIED custody; AI/coordinator authored benchmark; no official exam identity."})
    print(f"built {len(bank['questions'])} owner questions, {len(package['microtopics'])} microtopics, {len(qrt)} QRT rows")

if __name__=="__main__":
    main()
