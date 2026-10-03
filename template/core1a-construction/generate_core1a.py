#!/usr/bin/env python3
"""Core 1A Construction Page Compiler.

Transforms a structured Core 1A JSON payload into a 100% compliant, 
12.7" tablet-ready HTML page following the BP-CORE1A-CONSTRUCTION blueprint.
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

CONCEPT_DIFFICULTIES = {
    "EASY": "Easy concept",
    "MEDIUM": "Medium concept",
    "HARD": "Hard concept",
}


def render_core1a(payload: dict, template_html: str) -> str:
    html = template_html

    # Global headers & meta
    subject = payload.get("subject_name", "Mathematics")
    topic_id = payload.get("topic_id", "topic")
    topic_title = payload.get("topic_title", "Topic")
    core1a_sub = payload.get("core1a_subtitle", "Conceptual Construction")

    html = html.replace("{{TOPIC_ID}}", topic_id)
    html = html.replace("{{TOPIC_TITLE}}", topic_title)
    html = html.replace("{{SUBJECT_NAME}}", subject)
    html = html.replace("{{CORE1A_SUBTITLE}}", core1a_sub)

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

    # Conventions Loop
    conv_pattern = re.compile(
        r"<!-- \{\{BEGIN_CONVENTIONS\}\} -->(.*?)<!-- \{\{END_CONVENTIONS\}\} -->",
        re.DOTALL,
    )
    m_conv = conv_pattern.search(html)
    if m_conv:
        conv_item_tpl = m_conv.group(1)
        conv_rendered = []
        for c in payload.get("conventions", []):
            item = conv_item_tpl.replace("{{CONVENTION_NAME}}", c.get("name", ""))
            item = item.replace("{{CONVENTION_RULE}}", c.get("rule", ""))
            conv_rendered.append(item)
        html = conv_pattern.sub(lambda _: "".join(conv_rendered), html)

    # Units Loop
    unit_pattern = re.compile(
        r"<!-- \{\{BEGIN_CONSTRUCTION_UNIT\}\} -->(.*?)<!-- \{\{END_CONSTRUCTION_UNIT\}\} -->",
        re.DOTALL,
    )
    m_unit = unit_pattern.search(html)
    if m_unit:
        unit_item_tpl = m_unit.group(1)
        units_rendered = []

        for u in payload.get("units", []):
            u_html = unit_item_tpl
            u_html = u_html.replace("{{UNIT_ID}}", u.get("unit_id", "U1"))
            u_html = u_html.replace("{{UNIT_NUMBER}}", str(u.get("unit_number", "1")))
            u_html = u_html.replace("{{UNIT_TITLE}}", u.get("unit_title", ""))
            u_html = u_html.replace("{{DIFFICULTY_BAND}}", u.get("difficulty_band", "D2"))
            u_html = u_html.replace("{{BADGE_LABEL}}", u.get("badge_label", "Core Concept"))

            # Concept Difficulty & Cognitive Demand
            c_diff = u.get("concept_difficulty", "MEDIUM").upper()
            c_diff_label = CONCEPT_DIFFICULTIES.get(c_diff, f"{c_diff.capitalize()} concept")
            u_html = u_html.replace("{{CONCEPT_DIFFICULTY}}", c_diff)
            u_html = u_html.replace("{{CONCEPT_DIFFICULTY_LABEL}}", c_diff_label)

            demand_key = u.get("cognitive_demand", "CONCEPTUAL_EXPLANATION")
            demand_info = COGNITIVE_DEMANDS.get(demand_key, {"label": "Conceptual explanation", "icon": "💡"})
            u_html = u_html.replace("{{COGNITIVE_DEMAND_KEY}}", demand_key)
            u_html = u_html.replace("{{COGNITIVE_DEMAND_LABEL}}", demand_info["label"])
            u_html = u_html.replace("{{COGNITIVE_DEMAND_ICON}}", demand_info["icon"])

            review_tpl = u.get("review_template_ref")
            if review_tpl:
                u_html = re.sub(
                    r"\{\{#IF_REVIEW_TEMPLATE\}\}(.*?)\{\{/IF_REVIEW_TEMPLATE\}\}",
                    r"\1",
                    u_html,
                    flags=re.DOTALL,
                )
                u_html = u_html.replace("{{REVIEW_TEMPLATE_REF}}", review_tpl)
            else:
                u_html = re.sub(
                    r"\{\{#IF_REVIEW_TEMPLATE\}\}.*?\{\{/IF_REVIEW_TEMPLATE\}\}",
                    "",
                    u_html,
                    flags=re.DOTALL,
                )
                u_html = u_html.replace("{{REVIEW_TEMPLATE_REF}}", "")

            # Demand Scaffolding ($X, Y, Z, W$)
            scaffolding = u.get("demand_scaffolding")
            if scaffolding and isinstance(scaffolding, dict):
                u_html = re.sub(
                    r"\{\{#IF_DEMAND_SCAFFOLDING\}\}(.*?)\{\{/IF_DEMAND_SCAFFOLDING\}\}",
                    r"\1",
                    u_html,
                    flags=re.DOTALL,
                )
                u_html = u_html.replace("{{SCAFFOLD_X}}", scaffolding.get("x", ""))
                u_html = u_html.replace("{{SCAFFOLD_Y}}", scaffolding.get("y", ""))
                u_html = u_html.replace("{{SCAFFOLD_Z}}", scaffolding.get("z", ""))
                u_html = u_html.replace("{{SCAFFOLD_W}}", scaffolding.get("w", ""))
            else:
                u_html = re.sub(
                    r"\{\{#IF_DEMAND_SCAFFOLDING\}\}.*?\{\{/IF_DEMAND_SCAFFOLDING\}\}",
                    "",
                    u_html,
                    flags=re.DOTALL,
                )

            # Entry Assumptions Loop
            assumptions = u.get("entry_assumptions", [])
            if assumptions:
                u_html = re.sub(
                    r"\{\{#IF_ENTRY_ASSUMPTIONS\}\}(.*?)\{\{/IF_ENTRY_ASSUMPTIONS\}\}",
                    r"\1",
                    u_html,
                    flags=re.DOTALL,
                )
                asmp_pattern = re.compile(
                    r"<!-- \{\{BEGIN_ENTRY_ASSUMPTIONS\}\} -->(.*?)<!-- \{\{END_ENTRY_ASSUMPTIONS\}\} -->",
                    re.DOTALL,
                )
                m_asmp = asmp_pattern.search(u_html)
                if m_asmp:
                    asmp_tpl = m_asmp.group(1)
                    asmp_out = [asmp_tpl.replace("{{ASSUMPTION_ITEM}}", a) for a in assumptions]
                    u_html = asmp_pattern.sub(lambda _: "".join(asmp_out), u_html)
            else:
                u_html = re.sub(
                    r"\{\{#IF_ENTRY_ASSUMPTIONS\}\}.*?\{\{/IF_ENTRY_ASSUMPTIONS\}\}",
                    "",
                    u_html,
                    flags=re.DOTALL,
                )

            u_html = u_html.replace("{{INFERENTIAL_JUMP}}", u.get("inferential_jump", ""))
            u_html = u_html.replace("{{GOVERNING_EQUATION}}", u.get("governing_equation", ""))
            u_html = u_html.replace("{{EQUATION_CONDITIONS}}", u.get("equation_conditions", ""))
            u_html = u_html.replace("{{WORKED_PROBLEM_STEM}}", u.get("worked_problem_stem", ""))
            u_html = u_html.replace("{{WORKED_CONCLUSION}}", u.get("worked_conclusion", ""))
            u_html = u_html.replace("{{STAGE_IDS}}", u.get("stage_ids", "s1 s2 s3"))
            u_html = u_html.replace("{{SVG_CAPTION}}", u.get("svg_caption", ""))
            u_html = u_html.replace("{{SVG_BODY}}", u.get("svg_body", ""))
            u_html = u_html.replace("{{TRAP_WRONG_IDEA}}", u.get("trap_wrong_idea", ""))
            u_html = u_html.replace("{{TRAP_DIAGNOSTIC}}", u.get("trap_diagnostic", ""))
            u_html = u_html.replace("{{TRAP_REPAIR_EXPLANATION}}", u.get("trap_repair_explanation", ""))
            u_html = u_html.replace("{{TRIAD_CHECK_QUESTION}}", u.get("triad_check", ""))
            u_html = u_html.replace("{{TRIAD_APPLY_PROBLEM}}", u.get("triad_apply", ""))
            u_html = u_html.replace("{{TRIAD_CONNECT_FORWARD}}", u.get("triad_connect", ""))

            # Exit Task & Model Answer
            exit_task = u.get("exit_task")
            if exit_task and isinstance(exit_task, dict):
                u_html = re.sub(
                    r"\{\{#IF_EXIT_TASK\}\}(.*?)\{\{/IF_EXIT_TASK\}\}",
                    r"\1",
                    u_html,
                    flags=re.DOTALL,
                )
                u_html = u_html.replace("{{EXIT_TASK_PROMPT}}", exit_task.get("prompt", ""))
                u_html = u_html.replace("{{EXIT_TASK_ANSWER}}", exit_task.get("answer", ""))
                u_html = u_html.replace("{{EXIT_TASK_CHECK}}", exit_task.get("check", ""))
            else:
                u_html = re.sub(
                    r"\{\{#IF_EXIT_TASK\}\}.*?\{\{/IF_EXIT_TASK\}\}",
                    "",
                    u_html,
                    flags=re.DOTALL,
                )

            # Core 2 Practice Links Loop
            practice_links = u.get("core2_practice_links", [])
            if practice_links:
                u_html = re.sub(
                    r"\{\{#IF_CORE2_PRACTICE_LINKS\}\}(.*?)\{\{/IF_CORE2_PRACTICE_LINKS\}\}",
                    r"\1",
                    u_html,
                    flags=re.DOTALL,
                )
                link_pattern = re.compile(
                    r"<!-- \{\{BEGIN_CORE2_PRACTICE_LINKS\}\} -->(.*?)<!-- \{\{END_CORE2_PRACTICE_LINKS\}\} -->",
                    re.DOTALL,
                )
                m_link = link_pattern.search(u_html)
                if m_link:
                    link_tpl = m_link.group(1)
                    link_out = []
                    for pl in practice_links:
                        item = link_tpl.replace("{{PRACTICE_LINK_URL}}", pl.get("url", "#"))
                        item = item.replace("{{PRACTICE_LINK_LABEL}}", pl.get("label", "Practice Problem"))
                        link_out.append(item)
                    u_html = link_pattern.sub(lambda _: "".join(link_out), u_html)
            else:
                u_html = re.sub(
                    r"\{\{#IF_CORE2_PRACTICE_LINKS\}\}.*?\{\{/IF_CORE2_PRACTICE_LINKS\}\}",
                    "",
                    u_html,
                    flags=re.DOTALL,
                )

            # Step cards loop
            step_pattern = re.compile(
                r"<!-- \{\{BEGIN_STEP\}\} -->(.*?)<!-- \{\{END_STEP\}\} -->",
                re.DOTALL,
            )
            m_step = step_pattern.search(u_html)
            if m_step:
                step_tpl = m_step.group(1)
                steps_out = []
                for st in u.get("steps", []):
                    st_str = step_tpl.replace("{{IS_CRUX_STEP}}", str(st.get("is_crux_step", False)).lower())
                    st_str = st_str.replace("{{STEP_ACTION}}", st.get("action", ""))
                    st_str = st_str.replace("{{STEP_WHY_VALID}}", st.get("why_valid", ""))
                    st_str = st_str.replace("{{STEP_STATE_OUTPUT}}", st.get("state_output", ""))
                    steps_out.append(st_str)
                u_html = step_pattern.sub(lambda _: "".join(steps_out), u_html)

            # Worked steps loop
            w_pattern = re.compile(
                r"<!-- \{\{BEGIN_WORKED_STEP\}\} -->(.*?)<!-- \{\{END_WORKED_STEP\}\} -->",
                re.DOTALL,
            )
            m_w = w_pattern.search(u_html)
            if m_w:
                w_tpl = m_w.group(1)
                w_out = []
                for wst in u.get("worked_steps", []):
                    w_out.append(w_tpl.replace("{{WORKED_STEP_TEXT}}", wst))
                u_html = w_pattern.sub(lambda _: "".join(w_out), u_html)

            units_rendered.append(u_html)

        html = unit_pattern.sub(lambda _: "".join(units_rendered), html)

    return html


def main():
    parser = argparse.ArgumentParser(description="Compile Core 1A Construction Page")
    parser.add_argument("--payload", required=True, help="Path to JSON payload file")
    parser.add_argument("--output", required=True, help="Path to destination public HTML file")
    args = parser.parse_args()

    tpl_path = Path(__file__).parent / "core1a.template.html"
    with open(tpl_path, "r", encoding="utf-8") as f:
        tpl_html = f.read()

    with open(args.payload, "r", encoding="utf-8") as f:
        payload = json.load(f)

    rendered = render_core1a(payload, tpl_html)

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
