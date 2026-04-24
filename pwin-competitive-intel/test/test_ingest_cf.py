import json
import sqlite3
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).parent.parent / "agent"))
import db_utils

SCHEMA_PATH = Path(__file__).parent.parent / "db" / "schema.sql"


def _mem_db():
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    db_utils.init_schema(conn, SCHEMA_PATH)
    return conn


SAMPLE_TENDER = {
    "id": "2021-123456",
    "title": "IT Support Services",
    "description": "Provision of IT support",
    "publishedDate": "2021-01-15T10:30:00",
    "deadlineDate": "2021-02-15T17:00:00",
    "valueLow": 10000,
    "valueHigh": 50000,
    "noticeType": "Contract Notice",
    "status": "live",
    "isSuitableForSme": True,
    "industryCodes": [{"code": "72250000", "label": "System support services"}],
    "organisation": {
        "id": 9001,
        "name": "Department for Transport",
        "address": {"town": "London", "postcode": "SW1H 0ET"},
    },
    "awardedDate": None,
    "awardedValue": None,
    "suppliers": [],
    "contractStart": None,
    "contractEnd": None,
}

SAMPLE_AWARD = {
    **SAMPLE_TENDER,
    "id": "2021-999999",
    "noticeType": "Contract Award Notice",
    "status": "awarded",
    "awardedDate": "2021-03-01",
    "awardedValue": 45000,
    "suppliers": [
        {
            "supplierName": "Acme Ltd",
            "companiesHouseNumber": "12345678",
            "address": {"postcode": "EC1A 1BB", "town": "London"},
        }
    ],
    "contractStart": "2021-04-01",
    "contractEnd": "2023-03-31",
}


class TestCfHelpers(unittest.TestCase):
    def test_cf_buyer_id_uses_org_id(self):
        import ingest_cf
        self.assertEqual(ingest_cf._cf_buyer_id({"id": 9001, "name": "DfT"}), "cf-buyer-9001")

    def test_cf_buyer_id_falls_back_to_name_hash(self):
        import ingest_cf
        bid = ingest_cf._cf_buyer_id({"name": "Some Council"})
        self.assertTrue(bid.startswith("cf-buyer-"))
        self.assertGreater(len(bid), len("cf-buyer-"))

    def test_cf_supplier_id_is_deterministic(self):
        import ingest_cf
        sup = {"supplierName": "Acme Ltd", "address": {"postcode": "EC1A 1BB"}}
        self.assertEqual(ingest_cf._cf_supplier_id(sup), ingest_cf._cf_supplier_id(sup))
        self.assertTrue(ingest_cf._cf_supplier_id(sup).startswith("cf-sup-"))

    def test_cf_supplier_id_no_postcode(self):
        import ingest_cf
        sid = ingest_cf._cf_supplier_id({"supplierName": "Acme Ltd"})
        self.assertTrue(sid.startswith("cf-sup-"))

    def test_cf_supplier_id_different_names_differ(self):
        import ingest_cf
        s1 = ingest_cf._cf_supplier_id({"supplierName": "Alpha Ltd"})
        s2 = ingest_cf._cf_supplier_id({"supplierName": "Beta Ltd"})
        self.assertNotEqual(s1, s2)

    def test_cf_notice_row_ocid(self):
        import ingest_cf
        row = ingest_cf._cf_notice_row(SAMPLE_TENDER, "cf-buyer-9001")
        self.assertEqual(row["ocid"], "cf-2021-123456")

    def test_cf_notice_row_data_source(self):
        import ingest_cf
        row = ingest_cf._cf_notice_row(SAMPLE_TENDER, "cf-buyer-9001")
        self.assertEqual(row["data_source"], "cf")

    def test_cf_notice_row_suitable_for_sme(self):
        import ingest_cf
        row = ingest_cf._cf_notice_row(SAMPLE_TENDER, "cf-buyer-9001")
        self.assertEqual(row["suitable_for_sme"], 1)

    def test_cf_notice_row_live_status_normalised(self):
        import ingest_cf
        row = ingest_cf._cf_notice_row(SAMPLE_TENDER, "cf-buyer-9001")
        self.assertEqual(row["tender_status"], "active")

    def test_cf_notice_row_awarded_status_normalised(self):
        import ingest_cf
        row = ingest_cf._cf_notice_row(SAMPLE_AWARD, "cf-buyer-9001")
        self.assertEqual(row["tender_status"], "complete")

    def test_cf_award_row_returns_none_for_tender(self):
        import ingest_cf
        self.assertIsNone(ingest_cf._cf_award_row(SAMPLE_TENDER, "cf-2021-123456"))

    def test_cf_award_row_returns_dict_for_award(self):
        import ingest_cf
        result = ingest_cf._cf_award_row(SAMPLE_AWARD, "cf-2021-999999")
        self.assertIsNotNone(result)
        self.assertEqual(result["id"], "cf-award-2021-999999")
        self.assertEqual(result["value_amount"], 45000)
        self.assertEqual(result["data_source"], "cf")
        self.assertEqual(result["contract_start_date"], "2021-04-01")
        self.assertEqual(result["contract_end_date"], "2023-03-31")

    def test_cf_buyer_row_maps_fields(self):
        import ingest_cf
        row = ingest_cf._cf_buyer_row(SAMPLE_TENDER["organisation"])
        self.assertEqual(row["id"], "cf-buyer-9001")
        self.assertEqual(row["name"], "Department for Transport")
        self.assertEqual(row["postal_code"], "SW1H 0ET")
        self.assertEqual(row["locality"], "London")
        self.assertEqual(row["data_source"], "cf")

    def test_cf_supplier_row_maps_fields(self):
        import ingest_cf
        sup = SAMPLE_AWARD["suppliers"][0]
        row = ingest_cf._cf_supplier_row(sup)
        self.assertTrue(row["id"].startswith("cf-sup-"))
        self.assertEqual(row["name"], "Acme Ltd")
        self.assertEqual(row["companies_house_no"], "12345678")
        self.assertEqual(row["postal_code"], "EC1A 1BB")
        self.assertEqual(row["data_source"], "cf")


if __name__ == "__main__":
    unittest.main()
