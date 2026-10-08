#!/usr/bin/env python3
"""Read-only, fail-closed guard for the owner-compiled SOF IMO Grade 9 research seed.

Research candidates are NOT admitted to the existing NCERT/CBSE intake, TEST product
selection, or canonical question bank. A passing check proves structural integrity only.
"""
from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parent / "seed"
STABLE_ID = re.compile(r"SOF-IMO-G09-(?:L1-20\d{2}-\d{2}-[AB]|SAMPLE-20\d{2}-\d{2})-Q\d{3}$")
DIGEST = re.compile(r"sha256:[a-f0-9]{64}$")
VALID_SECTIONS = {None, "LOGICAL_REASONING", "MATHEMATICAL_REASONING", "EVERYDAY_MATHEMATICS", "ACHIEVERS_SECTION"}


class SeedError(ValueError):
    """A source-identity or pre-admission assertion failed."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SeedError(message)


def load_seed(root: Path = ROOT) -> tuple[list[dict], dict, dict]:
    try:
        lines = (root / "questions.jsonl").read_text(encoding="utf-8").splitlines()
        require(lines and all(line.strip() for line in lines), "questions: no blank or missing rows")
        questions = [json.loads(line) for line in lines]
        ledger = json.loads((root / "sources.json").read_text(encoding="utf-8"))
        observations = json.loads((root / "source_observations.json").read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise SeedError(f"unreadable seed: {error}") from error
    require(all(isinstance(q, dict) for q in questions), "questions must be objects")
    require(isinstance(ledger, dict) and isinstance(observations, dict), "invalid ledger shape")
    return questions, ledger, observations


def validate(root: Path = ROOT) -> dict:
    qs, ledger, evidence = load_seed(root)
    require(ledger.get("schema") == "imo-g9-source-ledger-v1", "source ledger schema incompatible")
    require(evidence.get("schema") == "imo-g9-source-observations-v1", "observations schema incompatible")
    sources, aliases = ledger.get("sources"), ledger.get("aliases")
    observations = evidence.get("records")
    require(isinstance(sources, list) and isinstance(aliases, list), "source ledger collections invalid")
    require(isinstance(observations, list), "observations must be a list")
    require(len(qs) == 66 and len(sources) == 4 and len(aliases) == 3, "seed census drift (66/4/3)")
    require((ledger.get("candidate_count"), ledger.get("source_claim_count"),
             ledger.get("alias_count"), ledger.get("core_eligible_count")) == (66, 4, 3, 0),
            "declared source census inconsistent")

    source_map = {}
    for source in sources:
        require(isinstance(source, dict), "source must be an object")
        sid, url = source.get("source_id"), source.get("url")
        require(isinstance(sid, str) and sid and sid not in source_map, "source duplicate/empty ID")
        require(isinstance(url, str) and url.startswith("https://"), f"{sid}: invalid source URL")
        host = urlsplit(url).hostname
        kind = source.get("host_type")
        if kind == "SCHOOL_MIRROR":
            require(host in {"iswkoman.com", "www.iswkoman.com"}, f"{sid}: unsupported mirror")
        elif kind == "ORGANIZER_LANDING_PAGE":
            require(host == "sofworld.org", f"{sid}: unsupported organizer domain")
        else:
            raise SeedError(f"{sid}: unknown host type")
        require(source.get("source_verification_status") == "NOT_VERIFIED", f"{sid}: unproved source promotion")
        require(source.get("rights_status") == "NOT_REVIEWED", f"{sid}: unproved distribution rights")
        require(source.get("answer_key_verified") is False, f"{sid}: unproved official answer key")
        require(source.get("document_sha256") is None, f"{sid}: document digest has no acquisition receipt")
        source_map[sid] = source

    ids, positions, entries = set(), set(), Counter()
    by_id = {}
    for q in qs:
        qid, sid, number, entry = q.get("id"), q.get("source_id_claim"), q.get("original_question_number_claim"), q.get("seed_entry")
        require(isinstance(qid, str) and STABLE_ID.fullmatch(qid), f"invalid stable question ID: {qid}")
        require(qid not in ids, f"duplicate question ID: {qid}")
        require(sid in source_map, f"{qid}: unknown source")
        require(q.get("source_url_claim") == source_map[sid]["url"], f"{qid}: source URL differs from ledger")
        require(isinstance(number, str) and number.isdecimal() and 1 <= int(number) <= 50,
                f"{qid}: unlocated original question")
        require(qid == f"{sid}-Q{int(number):03d}", f"{qid}: ID does not match source position")
        require((sid, number) not in positions, f"{qid}: duplicate source locator")
        require(type(entry) is int and 1 <= entry <= 65, f"{qid}: invalid seed entry")
        require(q.get("exam_section") in VALID_SECTIONS, f"{qid}: invalid exam section")
        require(isinstance(q.get("compiled_topic"), str) and q["compiled_topic"], f"{qid}: missing topic claim")
        require(isinstance(q.get("seed_line"), int) and q["seed_line"] > 0, f"{qid}: missing attachment line")
        require(isinstance(q.get("seed_content_sha256"), str) and DIGEST.fullmatch(q["seed_content_sha256"]),
                f"{qid}: invalid seed digest")
        require(q.get("core_eligible") is False and q.get("source_custody_status") == "NOT_VERIFIED"
                and q.get("answer_status") in {"COMPILATION_WORKED_ANSWER_NOT_INDEPENDENTLY_VERIFIED",
                                                "COMPILATION_CLAIMS_OFFICIAL_KEY_NOT_INDEPENDENTLY_VERIFIED"}
                and q.get("qrt_status") == "NOT_CLASSIFIED" and q.get("rights_status") == "NOT_REVIEWED",
                f"{qid}: unsupported readiness/answer/rights/QRT promotion")
        require(q.get("transcription_status") in {"NOT_VERIFIED", "TEXT_DISPUTED"}, f"{qid}: invalid transcription")
        require(isinstance(q.get("priority_review_flags"), list), f"{qid}: missing review flags")
        ids.add(qid); positions.add((sid, number)); entries[entry] += 1; by_id[qid] = q

    require(set(entries) == set(range(1, 66)), "compilation entries Q1–Q65 must all be represented")
    require({k: v for k, v in entries.items() if v != 1} == {38: 2}, "only original Q38 can split into two")
    split = [q for q in qs if q["seed_entry"] == 38]
    require({(x["seed_subentry"], x["original_question_number_claim"]) for x in split} == {("i", "32"), ("ii", "33")},
            "combined Q38 must keep two distinct printed-source positions")
    require(by_id["SOF-IMO-G09-L1-2024-25-B-Q044"]["exam_section"] == "EVERYDAY_MATHEMATICS",
            "printed Q44 section correction lost")
    require(by_id["SOF-IMO-G09-L1-2025-26-A-Q028"]["transcription_status"] == "TEXT_DISPUTED",
            "printed additive-identity contradiction cannot be cleared")

    alias_pairs = set()
    for alias in aliases:
        require(isinstance(alias, dict), "alias must be object")
        pair = (alias.get("entry_number"), alias.get("alias_of_entry"))
        require(pair not in alias_pairs and pair[1] in entries and pair[0] not in entries and
                alias.get("action") == "KEEP_ALIAS_NOT_QUESTION", "invalid duplicate/alias")
        alias_pairs.add(pair)
    require(alias_pairs == {(66, 29), (67, 27), (68, 30)}, "alias reconciliation drift")

    observation_ids, observed_qids = set(), set()
    for o in observations:
        require(isinstance(o, dict) and isinstance(o.get("id"), str) and o["id"] not in observation_ids,
                "bad/duplicate observation ID")
        observation_ids.add(o["id"])
        require(o.get("source_id") in source_map and o.get("source_url") == source_map[o["source_id"]]["url"],
                "observation source identity mismatch")
        require(type(o.get("pdf_page_index")) is int and o["pdf_page_index"] >= 0,
                "observation missing physical PDF page locator")
        targets = o.get("question_ids", [o.get("question_id")])
        require(isinstance(targets, list) and targets and all(t in by_id for t in targets),
                "observation references missing question")
        for t in targets:
            require(by_id[t]["source_id_claim"] == o["source_id"], "observation question/source mismatch")
        observed_qids.update(targets)
    require("SCAN-2025-26-Q28-SEMANTIC-MISMATCH" in observation_ids and
            "SOF-IMO-G09-L1-2025-26-A-Q028" in observed_qids,
            "Q28 source-text dispute lacks original-scan evidence")
    return {"candidate_questions": len(qs), "unique_source_positions": len(positions),
            "source_claims": len(sources), "aliases": len(aliases),
            "original_compilation_entries": len(entries), "source_observations": len(observations),
            "ready_for_core": 0, "source_verified_questions": 0, "accepted_qrt_cells": 0,
            "result": "STRUCTURALLY_VALID_RESEARCH_SEED_ONLY"}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--seed", type=Path, default=ROOT)
    args = parser.parse_args()
    try:
        result = validate(args.seed)
    except SeedError as error:
        parser.exit(1, f"IMO_SEED_INVALID: {error}\n")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
