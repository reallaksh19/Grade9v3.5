#!/usr/bin/env python3
"""Core 2 Practice & Question Custody Compiler.

Compiles a structured Core 2 JSON payload into a 100% compliant,
12.7" tablet-ready HTML page following the BP-CORE2-SOURCE-QUESTION@1.5.0 blueprint.
"""

from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path


COGNITIVE_DEMANDS = {
    "MEMORY_RECALL": {"label": "Factual recall", "icon": "🧠"},
    "CONCEPTUAL_EXPLANATION": {"label": "Conceptual explanation", "icon": "💡"},
    "QUANTITATIVE_APPLICATION": {"label": "Quantitative calculation", "icon": "🧮"},
    "MULTISTEP_REASONING": {"label": "Model & multi-step chain", "icon": "⛓️"},
    "REPRESENTATION_TRANSLATION": {"label": "Representation translation", "icon": "📊"},
    "EXPERIMENTAL_REASONING": {"label": "Experimental & data interpretation", "icon": "🔬"},
    "ESTIMATION_LIMITS": {"label": "Estimation & limiting cases", "icon": "⚖️"},
    "PROOF_DERIVATION": {"label": "Proof & formal derivation", "icon": "📐"},
    "CLASSIFICATION_PATTERN": {"label": "Classification & patterns", "icon": "🗂️"},
}


def render_core2(payload: dict, template_html: str) -> str:
    html = template_html

    # Global headers & meta
    subject = payload.get("subject_name", "Mathematics")
    topic_id = payload.get("topic_id", "topic")
    topic_title = payload.get("topic_title", "Topic")

    html = html.replace("{{TOPIC_ID}}", topic_id)
    html = html.replace("{{TOPIC_TITLE}}", topic_title)
    html = html.replace("{{SUBJECT_NAME}}", subject)

    # Active Nav state
    html = html.replace("{{ACTIVE_PHYSICS}}", "active" if subject.lower() == "physics" else "")
    html = html.replace("{{ACTIVE_CHEMISTRY}}", "active" if subject.lower() == "chemistry" else "")
    html = html.replace("{{ACTIVE_MATHEMATICS}}", "active" if subject.lower() == "mathematics" else "")

    # Simulation check
    sim_url = payload.get("simulation_url")
    if sim_url:
        html = re.sub(
            r"\{\{#IF_SIMULATION\}\}(.*?)\{\{/IF_SIMULATION\}\}",
            r"\1",
            html,
            flags=re.DOTALL,
        )
        html = html.replace("{{SIMULATION_URL}}", sim_url)
    else:
        html = re.sub(
            r"\{\{#IF_SIMULATION\}\}.*?\{\{/IF_SIMULATION\}\}",
            "",
            html,
            flags=re.DOTALL,
        )

    # Question Loop
    q_pattern = re.compile(
        r"<!-- \{\{BEGIN_QUESTION\}\} -->(.*?)<!-- \{\{END_QUESTION\}\} -->",
        re.DOTALL,
    )
    m_q = q_pattern.search(html)
    if not m_q:
        return html

    q_item_tpl = m_q.group(1)
    questions_rendered = []

    for q in payload.get("questions", []):
        q_html = q_item_tpl
        qid = q.get("id", "Q1")
        q_html = q_html.replace("{{QUESTION_ID}}", qid)
        q_html = q_html.replace("{{SOURCE_TITLE}}", q.get("source_title", "Question"))
        q_html = q_html.replace("{{PROVENANCE_DESCRIPTION}}", q.get("provenance_description", "Official source preserved"))
        q_html = q_html.replace("{{CONCEPT_NAME}}", q.get("concept_name", ""))
        q_html = q_html.replace("{{DIFFICULTY_BAND}}", q.get("difficulty_band", "D2"))
        q_html = q_html.replace("{{DIFFICULTY_SCORE}}", str(q.get("difficulty_score", 4)))
        q_html = q_html.replace("{{EXPECTED_MINUTES}}", str(q.get("expected_minutes", 3)))
        q_html = q_html.replace("{{QUESTION_TYPE_LABEL}}", q.get("question_type_label", "Standard Problem"))
        q_html = q_html.replace("{{SOURCE_CITATION}}", q.get("source_citation", ""))
        q_html = q_html.replace("{{DIFFICULTY_RATIONALE}}", q.get("difficulty_rationale", ""))

        # Cognitive demand & review template
        demand_key = q.get("cognitive_demand", "MULTISTEP_REASONING")
        demand_info = COGNITIVE_DEMANDS.get(demand_key, {"label": "Model & multi-step chain", "icon": "⛓️"})
        q_html = q_html.replace("{{COGNITIVE_DEMAND_KEY}}", demand_key)
        q_html = q_html.replace("{{COGNITIVE_DEMAND_LABEL}}", demand_info["label"])
        q_html = q_html.replace("{{COGNITIVE_DEMAND_ICON}}", demand_info["icon"])

        review_tpl = q.get("review_template_ref")
        if review_tpl:
            q_html = re.sub(
                r"\{\{#IF_REVIEW_TEMPLATE\}\}(.*?)\{\{/IF_REVIEW_TEMPLATE\}\}",
                r"\1",
                q_html,
                flags=re.DOTALL,
            )
            q_html = q_html.replace("{{REVIEW_TEMPLATE_REF}}", review_tpl)
        else:
            q_html = re.sub(
                r"\{\{#IF_REVIEW_TEMPLATE\}\}.*?\{\{/IF_REVIEW_TEMPLATE\}\}",
                "",
                q_html,
                flags=re.DOTALL,
            )
            q_html = q_html.replace("{{REVIEW_TEMPLATE_REF}}", "")

        # Demand Scaffolding ($X, Y, Z, W$)
        scaffolding = q.get("demand_scaffolding")
        if scaffolding and isinstance(scaffolding, dict):
            q_html = re.sub(
                r"\{\{#IF_DEMAND_SCAFFOLDING\}\}(.*?)\{\{/IF_DEMAND_SCAFFOLDING\}\}",
                r"\1",
                q_html,
                flags=re.DOTALL,
            )
            q_html = q_html.replace("{{SCAFFOLD_X}}", scaffolding.get("x", ""))
            q_html = q_html.replace("{{SCAFFOLD_Y}}", scaffolding.get("y", ""))
            q_html = q_html.replace("{{SCAFFOLD_Z}}", scaffolding.get("z", ""))
            q_html = q_html.replace("{{SCAFFOLD_W}}", scaffolding.get("w", ""))
        else:
            q_html = re.sub(
                r"\{\{#IF_DEMAND_SCAFFOLDING\}\}.*?\{\{/IF_DEMAND_SCAFFOLDING\}\}",
                "",
                q_html,
                flags=re.DOTALL,
            )

        # 5-axis scores
        diff_grid = q.get("difficulty_grid", {})
        q_html = q_html.replace("{{SCORE_MODEL}}", str(diff_grid.get("model", 1)))
        q_html = q_html.replace("{{SCORE_REP}}", str(diff_grid.get("representation", 1)))
        q_html = q_html.replace("{{SCORE_CHAIN}}", str(diff_grid.get("chain", 1)))
        q_html = q_html.replace("{{SCORE_MATH}}", str(diff_grid.get("math", 0)))
        q_html = q_html.replace("{{SCORE_TRAPS}}", str(diff_grid.get("traps", 1)))

        # PDF link check
        pdf_url = q.get("pdf_url")
        if pdf_url:
            q_html = re.sub(
                r"\{\{#IF_PDF_LINK\}\}(.*?)\{\{/IF_PDF_LINK\}\}",
                r"\1",
                q_html,
                flags=re.DOTALL,
            )
            q_html = q_html.replace("{{PDF_URL}}", pdf_url)
        else:
            q_html = re.sub(
                r"\{\{#IF_PDF_LINK\}\}.*?\{\{/IF_PDF_LINK\}\}",
                "",
                q_html,
                flags=re.DOTALL,
            )

        # Stem & Conditions
        q_html = q_html.replace("{{QUESTION_STEM}}", q.get("stem", ""))

        conditions = q.get("conditions", [])
        if conditions:
            q_html = re.sub(
                r"\{\{#IF_CONDITIONS\}\}(.*?)\{\{/IF_CONDITIONS\}\}",
                r"\1",
                q_html,
                flags=re.DOTALL,
            )
            cond_pattern = re.compile(
                r"<!-- \{\{BEGIN_CONDITIONS\}\} -->(.*?)<!-- \{\{END_CONDITIONS\}\} -->",
                re.DOTALL,
            )
            m_cond = cond_pattern.search(q_html)
            if m_cond:
                cond_tpl = m_cond.group(1)
                cond_out = [cond_tpl.replace("{{CONDITION_ITEM}}", c) for c in conditions]
                q_html = cond_pattern.sub(lambda _: "".join(cond_out), q_html)
        else:
            q_html = re.sub(
                r"\{\{#IF_CONDITIONS\}\}.*?\{\{/IF_CONDITIONS\}\}",
                "",
                q_html,
                flags=re.DOTALL,
            )

        # Common wrong route
        q_html = q_html.replace("{{COMMON_WRONG_ROUTE}}", q.get("common_wrong_route", ""))

        # Attempt Box
        resp_type = q.get("response_type", "short_text")
        q_html = q_html.replace("{{RESPONSE_TYPE}}", resp_type)

        attempt_html = ""
        if resp_type in ("single_choice", "multiple_choice"):
            opt_rows = []
            is_multi = resp_type == "multiple_choice"
            input_type = "checkbox" if is_multi else "radio"
            for i, opt in enumerate(q.get("options", [])):
                opt_rows.append(
                    f'<label style="display:flex; align-items:center; gap:10px; padding:10px 14px; background:#fff; border:1px solid #cbd5e1; border-radius:8px; cursor:pointer;">'
                    f'<input data-g9-choice type="{input_type}" name="choice-{qid}" value="{i}">'
                    f'<span>{opt}</span>'
                    f'</label>'
                )
            attempt_html = f'<div style="display:grid; gap:8px; margin:8px 0;">{"".join(opt_rows)}</div>'
        elif resp_type == "free_response":
            attempt_html = f'<label style="font-weight:700; font-size:0.9rem;">Your working steps / explanation:<textarea data-g9-attempt rows="4" placeholder="Enter your working or justification..."></textarea></label>'
        else:
            attempt_html = f'<label style="display:flex; flex-direction:column; gap:6px; font-weight:700; font-size:0.9rem;">Your Answer:<input data-g9-attempt type="text" placeholder="Type your answer here..."></label>'
        
        q_html = q_html.replace("{{ATTEMPT_CONTROLS_HTML}}", attempt_html)

        # SVG Figure
        svg_body = q.get("svg_body")
        if svg_body:
            q_html = re.sub(
                r"\{\{#IF_SVG_FIGURE\}\}(.*?)\{\{/IF_SVG_FIGURE\}\}",
                r"\1",
                q_html,
                flags=re.DOTALL,
            )
            q_html = q_html.replace("{{SVG_FIGURE_BODY}}", svg_body)
            q_html = q_html.replace("{{SVG_FIGURE_CAPTION}}", q.get("svg_caption", ""))
        else:
            q_html = re.sub(
                r"\{\{#IF_SVG_FIGURE\}\}.*?\{\{/IF_SVG_FIGURE\}\}",
                "",
                q_html,
                flags=re.DOTALL,
            )

        # Hint Ladder
        rungs = q.get("hint_ladder", [])
        ghost_pattern = re.compile(
            r"<!-- \{\{BEGIN_GHOST_RUNGS\}\} -->(.*?)<!-- \{\{END_GHOST_RUNGS\}\} -->",
            re.DOTALL,
        )
        m_ghost = ghost_pattern.search(q_html)
        if m_ghost:
            ghost_tpl = m_ghost.group(1)
            ghost_out = []
            for i, r in enumerate(rungs):
                g_str = ghost_tpl.replace("{{RUNG_NO}}", f"H{i}")
                g_str = g_str.replace("{{RUNG_LABEL}}", r.get("label", f"Hint {i+1}"))
                ghost_out.append(g_str)
            q_html = ghost_pattern.sub(lambda _: "".join(ghost_out), q_html)

        payload_pattern = re.compile(
            r"<!-- \{\{BEGIN_RUNG_PAYLOADS\}\} -->(.*?)<!-- \{\{END_RUNG_PAYLOADS\}\} -->",
            re.DOTALL,
        )
        m_payload = payload_pattern.search(q_html)
        if m_payload:
            payload_tpl = m_payload.group(1)
            payload_out = []
            for i, r in enumerate(rungs):
                p_str = payload_tpl.replace("{{RUNG_INDEX}}", str(i + 1))
                p_str = p_str.replace("{{RUNG_NO}}", f"H{i}")
                p_str = p_str.replace("{{RUNG_LABEL}}", r.get("label", f"Hint {i+1}"))
                p_str = p_str.replace("{{RUNG_PROMPT}}", r.get("prompt", ""))
                p_str = p_str.replace("{{RUNG_HINT_TEXT}}", r.get("hint", ""))
                payload_out.append(p_str)
            q_html = payload_pattern.sub(lambda _: "".join(payload_out), q_html)

        # Core 1A review anchor
        q_html = q_html.replace("{{CORE1A_ANCHOR_URL}}", q.get("core1a_anchor_url", "core1a.html"))

        # Solution Moves
        moves = q.get("solution_moves", [])
        moves_pattern = re.compile(
            r"<!-- \{\{BEGIN_SOLUTION_MOVES\}\} -->(.*?)<!-- \{\{END_SOLUTION_MOVES\}\} -->",
            re.DOTALL,
        )
        m_moves = moves_pattern.search(q_html)
        if m_moves:
            move_tpl = m_moves.group(1)
            moves_out = []
            for i, mv in enumerate(moves):
                mv_str = move_tpl.replace("{{MOVE_NUMBER}}", str(i + 1))
                mv_str = mv_str.replace("{{MOVE_STAGE_LABEL}}", mv.get("stage_label", f"Step {i+1}"))
                is_crux = mv.get("is_crux", False)
                mv_str = mv_str.replace("{{IS_CRUX_MOVE}}", str(is_crux).lower())

                if is_crux:
                    mv_str = re.sub(r"\{\{#IF_CRUX\}\}(.*?)\{\{/IF_CRUX\}\}", r"\1", mv_str, flags=re.DOTALL)
                else:
                    mv_str = re.sub(r"\{\{#IF_CRUX\}\}.*?\{\{/IF_CRUX\}\}", "", mv_str, flags=re.DOTALL)

                uses = mv.get("uses")
                if uses:
                    mv_str = re.sub(r"\{\{#IF_USES\}\}(.*?)\{\{/IF_USES\}\}", r"\1", mv_str, flags=re.DOTALL)
                    mv_str = mv_str.replace("{{MOVE_USES}}", uses)
                else:
                    mv_str = re.sub(r"\{\{#IF_USES\}\}.*?\{\{/IF_USES\}\}", "", mv_str, flags=re.DOTALL)

                mv_str = mv_str.replace("{{MOVE_ACTION}}", mv.get("action", ""))
                mv_str = mv_str.replace("{{MOVE_WHY_VALID}}", mv.get("why_valid", ""))
                mv_str = mv_str.replace("{{MOVE_RESULT}}", mv.get("result", ""))
                moves_out.append(mv_str)
            q_html = moves_pattern.sub(lambda _: "".join(moves_out), q_html)

        # Answer & Check
        q_html = q_html.replace("{{ANSWER_SUMMARY}}", q.get("answer_summary", ""))
        q_html = q_html.replace("{{INDEPENDENT_CHECK}}", q.get("independent_check", ""))

        questions_rendered.append(q_html)

    html = q_pattern.sub(lambda _: "".join(questions_rendered), html)
    return html


def main():
    parser = argparse.ArgumentParser(description="Compile Core 2 Practice Page")
    parser.add_argument("--payload", required=True, help="Path to JSON payload file")
    parser.add_argument("--output", required=True, help="Path to destination public HTML file")
    args = parser.parse_args()

    tpl_path = Path(__file__).parent / "core2.template.html"
    with open(tpl_path, "r", encoding="utf-8") as f:
        tpl_html = f.read()

    with open(args.payload, "r", encoding="utf-8") as f:
        payload = json.load(f)

    rendered = render_core2(payload, tpl_html)

    out_public = Path(args.output)
    out_public.parent.mkdir(parents=True, exist_ok=True)
    with open(out_public, "w", encoding="utf-8") as f:
        f.write(rendered)
    print(f"Generated: {out_public}")

    # Mirror to docs/ if under public/
    if "public" in out_public.parts:
        idx = out_public.parts.index("public")
        docs_parts = list(out_public.parts)
        docs_parts[idx] = "docs"
        out_docs = Path(*docs_parts)
        out_docs.parent.mkdir(parents=True, exist_ok=True)
        with open(out_docs, "w", encoding="utf-8") as f:
            f.write(rendered)
        print(f"Mirrored to docs: {out_docs}")


if __name__ == "__main__":
    main()
