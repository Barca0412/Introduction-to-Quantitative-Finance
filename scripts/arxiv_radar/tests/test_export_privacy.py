"""Publication-boundary privacy checks using synthetic records only."""

import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

import numpy as np
import pyarrow.parquet as pq

from scripts.arxiv_radar import data_store, storage, venue_library
from scripts.arxiv_radar.tests.test_restore import RadarSandbox, make_papers


class ExportPrivacyTests(unittest.TestCase):
    address = "researcher+lab" + "@" + "example.invalid"
    other_address = "reviewer" + "@" + "sub.example.invalid"

    def test_nested_copy_redacts_only_addresses_and_is_idempotent(self):
        source = {
            "nested": [{"contact": f"Institute, Department <{self.address}>; note."}, [self.other_address]],
            "stats": {f"Author {self.address}": {"count": 2}},
            "email_hash": "0123456789abcdef",
            "id": "doi:10.1234/example",
            "abstract": "An unchanged abstract with a matrix product A @ B.",
            "methods": ["llm", "graph"],
            "values": (True, None, 3, 0.25),
        }
        original = copy.deepcopy(source)
        result = data_store._without_plaintext_emails(source)
        self.assertEqual(source, original)
        self.assertEqual(result["nested"][0]["contact"], "Institute, Department <[redacted-email]>; note.")
        self.assertEqual(result["nested"][1], ["[redacted-email]"])
        self.assertEqual(result["stats"], {"Author [redacted-email]": {"count": 2}})
        for field in ("email_hash", "id", "abstract", "methods", "values"):
            self.assertEqual(result[field], original[field])
        self.assertEqual(data_store._without_plaintext_emails(result), result)
        result["nested"][0]["contact"] = "changed copy"
        self.assertEqual(source, original)

    def test_colliding_redacted_stats_keys_fail_without_mutation(self):
        source = {self.address: {"papers": 2}, self.other_address: {"papers": 3}}
        original = copy.deepcopy(source)
        with self.assertRaisesRegex(ValueError, "merge dictionary keys"):
            data_store._without_plaintext_emails(source)
        self.assertEqual(source, original)

    def test_numeric_metrics_and_versions_are_not_email_addresses(self):
        labels = ["mAP@0.5", "Recall@1.0", "Hits@10.0", "NDCG@10.0", "precision@0.50:0.95",
                  "package@1.2.3", "score@release.com1", "score@release.com.5"]
        text = "; ".join(labels)
        source = {"abstract": text, "stats": {label: 0.5 for label in labels}, "nested": [text]}
        self.assertEqual(data_store._without_plaintext_emails(source), source)
        mixed = f"{text}; correspondence <{self.address}>."
        self.assertEqual(data_store._without_plaintext_emails(mixed), f"{text}; correspondence <[redacted-email]>.")

    def test_alphabetic_and_punycode_tlds_still_redact(self):
        for host in ("example.invalid", "123.example.invalid", "sub.example.CO.UK", "example.xn--p1ai"):
            with self.subTest(host=host):
                address = "fixture+lab" + "@" + host
                self.assertEqual(data_store._without_plaintext_emails(f"<{address}>."), "<[redacted-email]>.")

    def test_paper_schema_cleans_legacy_and_nested_fields(self):
        paper = make_papers(1)[0]
        paper.update({
            "affiliation_raw": [f"Institute, Department; {self.address}"],
            "affiliation": self.address,
            "affiliations": [self.other_address],
            "comment": f"Correspondence: {self.address}.",
            "authors": [{"name": "Example Author", "affiliation": f"Lab ({self.address})"}],
            "points_zh": {"problem": f"Contact {self.other_address}", "method": "方法", "result": "结果", "limitation": "局限"},
            "author_ids": [{"openalex": "A123", "orcid": "0000-0000-0000-0001", "email_hash": "0123456789abcdef"}],
            "methods": ["llm"], "finance_domains": ["trading"], "relevance": 3,
        })
        original = copy.deepcopy(paper)
        result = data_store._clean_paper_for_parquet(paper)
        for address in (self.address, self.other_address):
            self.assertNotIn(address, json.dumps(result))
        self.assertEqual(result["affiliation_raw"], ["Institute, Department; [redacted-email]"])
        for field in ("id", "title", "abstract", "categories", "methods", "finance_domains", "relevance", "author_ids"):
            self.assertEqual(result[field], original[field])
        self.assertEqual(paper, original)

    def test_export_sanitizes_every_metadata_artifact_and_preserves_vectors(self):
        with tempfile.TemporaryDirectory() as tmp:
            box = RadarSandbox(Path(tmp))
            papers = make_papers(2)
            papers[0]["comment"] = self.address
            papers[0]["abstract"] = "Report mAP@0.5, Recall@1.0 and Hits@10.0 without changing any metric."
            stats = {"last_updated": "2026-11-15", "nested": [{"contact": self.address}],
                     "author_counts": {self.other_address: 2}, "summary": {"total_papers": 2}}
            library = [venue_library.make_record("icaif", 2026, "fixture", "Machine learning portfolios",
                                                ["Example Author", self.address])]
            library[0]["decision"] = f"Accepted; contact {self.other_address}"
            library_before = copy.deepcopy(library)
            matrix = np.array([[0.25, -0.5, 0.75], [-1.0, 0.5, 0.0]], dtype=np.float32)
            meta = {"model": "test-model", "ids": [p["id"] for p in papers],
                    "text_hashes": ["abc123", "def456"], "theme_queries": {"test": f"Topic {self.address}"}}
            with box.patched(), mock.patch.object(venue_library, "load_all", return_value=library):
                data_store._write_papers_json(papers, "2026-11-15T00:00:00Z")
                storage.write_atomically(box.data / "stats.json", stats)
                data_store.save_local_embeddings(meta, matrix)
                originals = {p: p.read_bytes() for p in box.data.iterdir() if p.is_file()}
                info = data_store.export()
                out = box.data / "export"
                exported_papers = pq.read_table(out / data_store.PAPERS_PARQUET).to_pylist()
                exported_library = pq.read_table(out / data_store.LIBRARY_PARQUET).to_pylist()
                embeddings = pq.read_table(out / data_store.EMBEDDINGS_PARQUET)
                exported_meta = json.loads(embeddings.schema.metadata[data_store.EMBEDDING_METADATA_KEY])
                exported_stats = json.loads((out / "stats.json").read_text())
                public_text = json.dumps([exported_papers, exported_library, exported_meta, exported_stats, info])
                public_text += (out / "README.md").read_text() + (out / data_store.EXPORT_INFO).read_text()
                for address in (self.address, self.other_address):
                    self.assertNotIn(address, public_text)
                self.assertEqual(exported_stats["author_counts"], {"[redacted-email]": 2})
                self.assertEqual(exported_stats["summary"], stats["summary"])
                self.assertEqual(exported_papers[0]["abstract"], papers[0]["abstract"])
                self.assertEqual(exported_library[0]["title_key"], library[0]["title_key"])
                self.assertEqual(exported_library[0]["title"], library[0]["title"])
                self.assertEqual(embeddings.column("id").to_pylist(), meta["ids"])
                self.assertEqual(embeddings.column("text_hash").to_pylist(), meta["text_hashes"])
                np.testing.assert_array_equal(np.array(embeddings.column("vector").to_pylist(), dtype=np.float32), matrix)
                for p, original in originals.items():
                    self.assertEqual(p.read_bytes(), original)
                self.assertEqual(library, library_before)
                for name, expected in info["files"].items():
                    self.assertEqual(data_store._sha256(out / name), expected["sha256"])

    def test_export_removes_stale_optional_files_instead_of_republishing_them(self):
        with tempfile.TemporaryDirectory() as tmp:
            box = RadarSandbox(Path(tmp))
            with box.patched(), mock.patch.object(venue_library, "load_all", return_value=[]):
                data_store._write_papers_json(make_papers(1), "2026-11-15T00:00:00Z")
                out = box.data / "export"
                out.mkdir()
                stale_names = ["stats.json", data_store.LIBRARY_PARQUET, data_store.EMBEDDINGS_PARQUET]
                for name in stale_names:
                    (out / name).write_text(self.address)
                info = data_store.export()
                for name in stale_names:
                    self.assertFalse((out / name).exists())
                    self.assertNotIn(name, info["files"])


if __name__ == "__main__":
    unittest.main()
