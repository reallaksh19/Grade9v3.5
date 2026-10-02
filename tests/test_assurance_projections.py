"""The projections of the library (a search index, a set of pages) and the release made of them: each says what it was built from, by digest, and can be checked against it.

The first version of these tools compared a digest of the pages with a different kind of digest, wrote its evidence into the pages it judged, reported a stale index and exited 0,
and digested CRLF checkouts differently from LF ones (so a committed index was stale on every other machine). Each of those is a test here.
"""
from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from Shared.assurance import aggregate, contract
from Shared.assurance.evidence import load_evidence
from Shared.contracts import ContractError
from Shared.tools import build_projection_manifest, build_search_index, drift_detector, release_fingerprint, verify_projection_manifest, verify_search_index

REPO = Path(__file__).resolve().parents[1]


def package(*questions, package_id="p1", **extra):
    return {"package_id": package_id, "subject": "Physics", "questions": list(questions), **extra}


def question(qid, stem="A body of mass 2 kg is pushed by a 12 N force; find its acceleration.", **extra):
    return {"id": qid, "stem": stem, "primary_capability_ref": "CAP-1", **extra}


class Tree(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.lib = self.tmp / "library"
        self.lib.mkdir()
        self.evidence = self.tmp / "evidence"
        self.index, self.manifest = self.tmp / "index.json", self.tmp / "manifest.json"

    def write(self, name, data, newline="\n"):
        (self.lib / name).write_text(json.dumps(data, indent=1).replace("\n", newline), encoding="utf-8", newline="")

    def evidence_records(self):
        return [load_evidence(p) for p in sorted(self.evidence.glob("*.json"))]


class SearchIndex(Tree):
    def build(self):
        return build_search_index.main(["--library-dirs", str(self.lib), "--output-index", str(self.index), "--output-manifest", str(self.manifest)])

    def verify(self, *extra):
        return verify_search_index.main(["--index", str(self.index), "--manifest", str(self.manifest), "--library-dirs", str(self.lib), "--evidence-dir", str(self.evidence), *extra])

    def test_the_index_holds_the_visible_questions_in_a_fixed_order_and_the_manifest_names_the_rest(self):
        self.write("a.json", package(question("Q-3"), question("Q-2", extensions={"search_visibility": "EXCLUDED"}), question("Q-1")))
        self.assertEqual(self.build(), 0)
        manifest = json.loads(self.manifest.read_text())
        self.assertEqual((manifest["canonical_ids"], manifest["excluded_ids"], manifest["record_count"]), (["Q-1", "Q-3"], ["Q-2"], 2))
        self.assertEqual([d["canonical_id"] for d in json.loads(self.index.read_text())], ["Q-1", "Q-3"])

    def test_an_index_that_is_current_complete_and_unaltered_passes_and_the_evidence_is_valid_and_bound_to_the_index(self):
        self.write("a.json", package(question("Q-1")))
        self.build()
        self.assertEqual(self.verify("--enforce"), 0)
        records = self.evidence_records()
        self.assertEqual({r["assurance_type"]: r["outcome"] for r in records}, {"SEARCH_MEMBERSHIP": "PASS", "SEARCH_RETRIEVABILITY": "PASS"})
        self.assertEqual({r["subject"]["kind"] for r in records}, {"PROJECTION"})
        self.assertEqual({r["subject"]["digest"] for r in records}, {contract.digest_file(self.index)})

    def test_a_question_added_to_the_library_after_the_build_is_missing_and_the_index_stale(self):
        self.write("a.json", package(question("Q-1")))
        self.build()
        self.write("b.json", package(question("Q-2"), package_id="p2"))
        self.assertEqual(self.verify("--enforce"), 1)
        codes = {f["code"] for r in self.evidence_records() for f in r["findings"]}
        self.assertEqual(codes, {"MISSING_FROM_INDEX", "STALE_INDEX"})

    def test_a_question_removed_from_the_library_is_a_phantom_in_the_index(self):
        self.write("a.json", package(question("Q-1"), question("Q-2")))
        self.build()
        self.write("a.json", package(question("Q-1")))
        self.assertEqual(self.verify("--enforce"), 1)
        self.assertIn("PHANTOM_IN_INDEX", {f["code"] for r in self.evidence_records() for f in r["findings"]})

    def test_a_stale_index_whose_ids_still_match_is_a_fail_and_exits_nonzero(self):
        """The first version reported INCONCLUSIVE and exited 0: the text in the index was the old text."""
        self.write("a.json", package(question("Q-1")))
        self.build()
        self.write("a.json", package(question("Q-1", stem="A different stem that the index does not hold at all, with different words.")))
        self.assertEqual(self.verify("--enforce"), 1)
        self.assertEqual({f["code"] for r in self.evidence_records() for f in r["findings"]}, {"STALE_INDEX"})
        self.assertEqual(self.verify(), 0, "without --enforce the run reports and does not fail")

    def test_an_index_edited_after_the_build_fails_retrievability(self):
        self.write("a.json", package(question("Q-1")))
        self.build()
        self.index.write_text("[]", encoding="utf-8")
        self.assertEqual(self.verify("--enforce"), 1)
        self.assertEqual({r["assurance_type"]: r["outcome"] for r in self.evidence_records()}["SEARCH_RETRIEVABILITY"], "FAIL")

    def test_a_library_file_that_does_not_parse_stops_the_build_and_the_verification(self):
        self.write("a.json", package(question("Q-1")))
        self.build()
        (self.lib / "broken.json").write_text("{ nope", encoding="utf-8")
        with self.assertRaises(ContractError):
            self.build()
        self.assertEqual(self.verify("--enforce"), 1)

    def test_the_index_is_the_same_on_every_checkout(self):
        """A CRLF working copy of the library digests like the LF one: the committed index was stale on every machine but its author's."""
        self.write("a.json", package(question("Q-1"), question("Q-2")))
        self.build()
        lf_index, lf_manifest = self.index.read_bytes(), json.loads(self.manifest.read_text())
        self.write("a.json", package(question("Q-1"), question("Q-2")), newline="\r\n")
        self.build()
        self.assertEqual(self.index.read_bytes(), lf_index)
        self.assertEqual(json.loads(self.manifest.read_text())["canonical_snapshot_digest"], lf_manifest["canonical_snapshot_digest"])
        self.assertEqual(self.verify("--enforce"), 0)

    def test_the_committed_index_is_current(self):
        libs = [str(REPO / d) for d in ("Physics/library", "Chemistry/library", "Mathematics/library")]
        out = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, out, True)
        argv = ["--index", str(REPO / "public/data/search-index.v1.json"), "--manifest", str(REPO / "public/data/search-index-manifest.v1.json"), "--library-dirs", *libs,
                "--evidence-dir", str(out), "--enforce"]
        self.assertEqual(verify_search_index.main(argv), 0, "rebuild it with Shared/tools/build_search_index.py")


class ProjectionManifest(Tree):
    def setUp(self):
        super().setUp()
        self.pages = self.tmp / "pages"
        self.pages.mkdir()
        self.write("a.json", package(question("Q-PHY-1"), question("Q-PHY-2"), capabilities=[{"id": "CAP-PHY-1"}]))
        (self.pages / "core2.html").write_text("<html><body><section id='Q-PHY-1'>question one</section><p>see CAP-PHY-1 and Q-NOT-A-RECORD</p></body></html>", encoding="utf-8")

    def build(self):
        out = self.tmp / "m.json"
        self.assertEqual(build_projection_manifest.main(["--render-dir", str(self.pages), "--projection-type", "STANDALONE", "--canonical-dir", str(self.lib), "--output", str(out)]), 0)
        return json.loads(out.read_text())

    def verify(self, manifest, *extra):
        path = self.tmp / "m.json"
        path.write_text(json.dumps(manifest))
        return verify_projection_manifest.main(["--manifest", str(path), "--render-dir", str(self.pages), "--canonical-dir", str(self.lib), "--evidence-dir", str(self.evidence), *extra])

    def test_the_manifest_satisfies_its_schema_and_cites_canonical_records_not_file_names(self):
        manifest = self.build()
        self.assertEqual(contract.schema_problems("projection-manifest", manifest), [])
        self.assertEqual(manifest["record_ids"], ["CAP-PHY-1", "Q-PHY-1"], "ids the pages cite that the library holds; Q-NOT-A-RECORD is not one, and core2 is a file")

    def test_a_projection_that_is_what_its_manifest_says_passes(self):
        self.assertEqual(self.verify(self.build(), "--enforce"), 0)
        record = self.evidence_records()[0]
        self.assertEqual((record["assurance_type"], record["outcome"], record["subject"]["id"]), ("PROJECTION_INTEGRITY", "PASS", "pages"))
        self.assertFalse(list(self.pages.glob("*.json")), "no evidence is written into the render directory")

    def test_pages_edited_after_the_manifest_fail(self):
        manifest = self.build()
        (self.pages / "core2.html").write_text("<html><body>edited by hand</body></html>", encoding="utf-8")
        self.assertEqual(self.verify(manifest, "--enforce"), 1)
        self.assertEqual({f["code"] for f in self.evidence_records()[0]["findings"]}, {"ARTIFACT_CHANGED"})

    def test_a_library_that_changed_after_the_projection_was_built_makes_it_stale_even_if_the_pages_did_not(self):
        manifest = self.build()
        self.write("a.json", package(question("Q-PHY-1"), question("Q-PHY-2", stem="A changed stem that the pages were not built from."), capabilities=[{"id": "CAP-PHY-1"}]))
        self.assertEqual(self.verify(manifest, "--enforce"), 1)
        self.assertEqual({f["code"] for f in self.evidence_records()[0]["findings"]}, {"STALE_CANONICAL"})

    def test_an_empty_render_directory_is_an_error_not_a_projection(self):
        shutil.rmtree(self.pages)
        self.pages.mkdir()
        self.assertEqual(build_projection_manifest.main(["--render-dir", str(self.pages), "--projection-type", "WEB", "--canonical-dir", str(self.lib)]), 1)

    def test_evidence_is_refused_inside_the_tree_it_judges(self):
        with self.assertRaises(ValueError):
            verify_projection_manifest.main(["--manifest", str(self.write_manifest()), "--render-dir", str(self.pages), "--evidence-dir", "standalone/evidence-test"])

    def write_manifest(self):
        path = self.tmp / "m.json"
        path.write_text(json.dumps(self.build()))
        return path


class Release(Tree):
    def setUp(self):
        super().setUp()
        self.web = self.tmp / "web"
        self.web.mkdir()
        (self.web / "index.html").write_text("<html>web</html>", encoding="utf-8")
        self.write("a.json", package(question("Q-1", source_refs=["SRC-1"])))
        self.fp_path = self.tmp / "fp.json"

    def fingerprint(self):
        record = release_fingerprint.build_fingerprint("P", [self.lib], self.web)
        contract.write_json(self.fp_path, record)
        return record

    def drift(self, *extra):
        return drift_detector.main(["--accepted-fingerprint", str(self.fp_path), "--canonical-dir", str(self.lib), "--web-dir", str(self.web), "--evidence-dir", str(self.evidence), *extra])

    def test_the_fingerprint_satisfies_its_schema_and_changes_with_each_part(self):
        first = self.fingerprint()
        self.assertEqual(contract.schema_problems("release-fingerprint", first), [])
        self.assertIsNotNone(first["source_set_digest"])
        (self.web / "index.html").write_text("<html>changed</html>", encoding="utf-8")
        self.write("a.json", package(question("Q-1", source_refs=["SRC-1"]), question("Q-2")))
        second = release_fingerprint.build_fingerprint("P", [self.lib], self.web)
        self.assertNotEqual(first["web_projection_digest"], second["web_projection_digest"])
        self.assertNotEqual(first["canonical_snapshot_digest"], second["canonical_snapshot_digest"])

    def test_the_fingerprint_is_the_same_for_a_crlf_checkout(self):
        first = self.fingerprint()
        self.write("a.json", package(question("Q-1", source_refs=["SRC-1"])), newline="\r\n")
        (self.web / "index.html").write_bytes(b"<html>web</html>".replace(b"\n", b"\r\n"))
        self.assertEqual(release_fingerprint.build_fingerprint("P", [self.lib], self.web)["canonical_snapshot_digest"], first["canonical_snapshot_digest"])

    def test_the_assurance_digest_is_the_bundles_own_and_a_broken_bundle_is_refused(self):
        subjects = aggregate.package_subjects([str(self.lib)], Path("/"))
        policies = [{"schema": "canonical-admission-policy/v1", "policy_id": "t", "version": "1", "subject_kind": "CANONICAL_RECORD", "required_pass": ["STRUCTURAL_VALIDITY"],
                     "required_pass_or_na": []}]
        bundle = aggregate.build_bundle("P", subjects, policies, aggregate.evaluate(subjects, policies, {}))
        path = self.tmp / "b.json"
        contract.write_json(path, bundle)
        self.assertEqual(release_fingerprint.build_fingerprint("P", [self.lib], self.web, assurance_bundle=path)["assurance_bundle_digest"], bundle["bundle_digest"])
        contract.write_json(path, {**bundle, "problems": [{"code": "X", "message": "edited"}]})
        with self.assertRaises(ContractError):
            release_fingerprint.build_fingerprint("P", [self.lib], self.web, assurance_bundle=path)

    def test_nothing_drifted_passes(self):
        self.fingerprint()
        self.assertEqual(self.drift("--enforce"), 0)
        self.assertEqual({r["outcome"] for r in self.evidence_records()}, {"PASS"})

    def test_a_library_that_changed_owes_a_rebuild_and_is_not_a_failure(self):
        self.fingerprint()
        self.write("a.json", package(question("Q-1", source_refs=["SRC-1"]), question("Q-2")))
        (self.web / "index.html").write_text("<html>rebuilt</html>", encoding="utf-8")
        self.assertEqual(self.drift("--enforce"), 0)
        self.assertEqual({r["outcome"] for r in self.evidence_records()}, {"INCONCLUSIVE"})

    def test_a_projection_that_changed_while_the_library_did_not_is_unauthorized(self):
        self.fingerprint()
        (self.web / "index.html").write_text("<html>edited by hand</html>", encoding="utf-8")
        self.assertEqual(self.drift("--enforce"), 1)
        record = self.evidence_records()[0]
        self.assertEqual((record["outcome"], record["findings"][0]["code"]), ("FAIL", "UNAUTHORIZED_CHANGE"))


if __name__ == "__main__":
    unittest.main()
