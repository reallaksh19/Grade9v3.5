#!/usr/bin/env python3
"""Bounded ephemeral acquire/verify source PDFs; log provenance, never source PDF bytes.

Network failures are expected and must be visible, not reclassified as acquired.
The output JSON is a job-local evidence report; no canonical source receipt is created.
"""
from __future__ import annotations

import argparse
import json
import tempfile
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import URLError

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from Shared.tools.source_pipeline import acquire_url, verify_acquisition

QUEUE = REPO / "TEST/imo-research/intake/core2-source-acquisition-handoff.v1.json"


def probe(*, output: Path, queue_path: Path = QUEUE) -> dict:
    queue = json.loads(queue_path.read_text(encoding="utf-8"))
    if queue.get("source_documents") != 4 or queue.get("verified_sha256_documents") != 0:
        raise RuntimeError("expected four pending source documents and zero existing receipts")
    result = {
        "schema":"imo-g9-ephemeral-source-acquisition-probe-v1",
        "scope":"NETWORK_PROBE_EPHEMERAL_ONLY_NO_CORE2_CUSTODY_RECEIPT",
        "executed_at_utc":datetime.now(timezone.utc).isoformat(),
        "sources":[],
        "source_positions":queue["source_positions"],
        "durably_retained_source_snapshots":0,
        "canonical_verified_source_receipts":0,
        "copyright_reproduction_permission":"NOT_GRANTED_BY_DOWNLOAD",
        "full_item_component_custody_verified":False
    }
    for row in queue["source_documents_queue"]:
        source_id = row["source_id"]
        with tempfile.TemporaryDirectory(prefix="imo-g9-source-probe-") as folder:
            pdf = Path(folder) / "source.pdf"
            status = {
                "source_id":source_id,
                "source_url_claim":row["requested_pdf_url"],
                "research_positions":row["position_count_in_68"],
                "outcome":"NOT_ACQUIRED",
                "http_resolved_url":None,
                "media_type":None,
                "byte_length":None,
                "verified_sha256":None,
                "local_byte_verification_passed":False,
                "snapshot_retained_after_run":False,
                "rights_disposition":"NOT_REVIEWED",
                "blocking_reason":None
            }
            try:
                acq=acquire_url(
                    url=row["requested_pdf_url"],subject="TEST",
                    bucket_id="BUCKET-TEST-IMO-G9-SOURCE-CUSTODY-PENDING",
                    resource_ref=source_id,
                    acquired_at=datetime.now(timezone.utc).date().isoformat(),
                    snapshot_output=pdf
                )
                validation=verify_acquisition(acq)
                if not validation["passed"]:
                    status["outcome"]="FAILED_BYTE_VERIFICATION"
                    status["blocking_reason"] = str(validation["findings"])
                else:
                    header=pdf.read_bytes()[:5]
                    if header!=b"%PDF-":
                        status["outcome"]="REJECTED_NOT_PDF_SIGNATURE"
                        status["blocking_reason"]="HTTP content did not start with %PDF-"
                    else:
                        status.update({
                            "outcome":"EPHEMERAL_VERIFIED_PDF_DOWNLOAD",
                            "http_resolved_url":acq["resolved_locator"],
                            "media_type":acq["media_type"],
                            "byte_length":acq["byte_length"],
                            "verified_sha256":acq["sha256"],
                            "local_byte_verification_passed":True
                        })
            except (OSError, TimeoutError, ValueError, URLError) as exc:
                status["outcome"]="NETWORK_OR_CONTENT_BLOCKED"
                status["blocking_reason"]=f"{type(exc).__name__}: {exc}"[:450]
            # Snapshot lives only in TemporaryDirectory; the report never contains PDF bytes.
            print(json.dumps({k:v for k,v in status.items() if k!="source_url_claim"},sort_keys=True))
            result["sources"].append(status)
    result["temporary_verified_downloads"]=sum(
        x["local_byte_verification_passed"] for x in result["sources"]
    )
    result["unavailable_or_invalid"]=4-result["temporary_verified_downloads"]
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args()
    report=probe(output=args.output)
    print(json.dumps({
        "probe_executed":True,
        "sources":len(report["sources"]),
        "temporary_verified":report["temporary_verified_downloads"],
        "network_blocked":report["unavailable_or_invalid"],
        "durable_core2_receipts":0
    },sort_keys=True))


if __name__=="__main__":
    main()
