"""Sanity checks for test data handling and fixture isolation."""
import csv
import tempfile
import unittest
from pathlib import Path

from ecommerce_app import fixture
from test_runner import execute_case, load_cases

ROOT = Path(__file__).resolve().parent


class RunnerQualityChecks(unittest.TestCase):
    def test_malformed_json_is_blocked_not_dropped(self):
        rows = load_cases(ROOT / "test_cases.csv")
        row = dict(rows[0])
        row["input_json"] = "{not-json"
        result = execute_case(row)
        self.assertEqual(result["status"], "BLOCKED")
        self.assertEqual(result["test_case_id"], row["test_case_id"])

    def test_duplicate_case_ids_are_rejected(self):
        rows = load_cases(ROOT / "test_cases.csv")[:2]
        rows[1]["test_case_id"] = rows[0]["test_case_id"]
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "duplicates.csv"
            with path.open("w", encoding="utf-8-sig", newline="") as file:
                writer = csv.DictWriter(file, fieldnames=list(rows[0]))
                writer.writeheader()
                writer.writerows(rows)
            with self.assertRaisesRegex(ValueError, "DUPLICATE_TEST_IDS"):
                load_cases(path)

    def test_each_fixture_is_independent(self):
        app1, user1, cart1 = fixture("a1")
        app2, user2, cart2 = fixture("a1")
        app1.catalog.products["A"].stock = 0
        app1.catalog.products["A"].price = app1.catalog.products["A"].price * 2
        user1.used_codes.add("SAVE10")
        self.assertEqual(app2.catalog.products["A"].stock, 20)
        self.assertEqual(str(app2.catalog.products["A"].price), "200000")
        self.assertNotIn("SAVE10", user2.used_codes)
        self.assertIsNot(app1, app2)
        self.assertIsNot(cart1, cart2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
