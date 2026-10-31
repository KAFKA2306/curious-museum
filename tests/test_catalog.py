"""Static invariants for the source exhibit catalog and its published page."""
import json
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]


class CatalogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads((ROOT / "exhibit_candidates.json").read_text(encoding="utf-8"))
        cls.items = cls.data["items"]

    def test_ids_and_numbers_are_unique(self):
        self.assertEqual(40, len(self.items))
        self.assertEqual(len(self.items), len({r["id"] for r in self.items}))
        self.assertEqual([f"{i:03d}" for i in range(7, 47)], [r["num"] for r in self.items])

    def test_quizzes_and_evidence(self):
        for item in self.items:
            with self.subTest(item=item["id"]):
                self.assertEqual(3, len(item["options"]))
                self.assertIs(type(item["answer"]), int)
                self.assertIn(item["answer"], range(3))
                self.assertTrue(item["source_url"].startswith("https://"))
                self.assertTrue(item["source_name"].strip())
                self.assertTrue(item["status"].strip())
                self.assertTrue(item["fact"].strip())
                self.assertTrue(item["note"].strip())

    def test_batch_and_navigation(self):
        self.assertEqual(25, sum(i["batch"] == "第2回" for i in self.items))
        self.assertIn('href="curation.html"', (ROOT / "index.html").read_text(encoding="utf-8"))
        self.assertIn('href="index.html"', (ROOT / "curation.html").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
