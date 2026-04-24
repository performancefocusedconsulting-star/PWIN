import sqlite3
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "agent"))

SCHEMA_PATH = Path(__file__).parent.parent / "db" / "schema.sql"


def _mem_db():
    import db_utils
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    db_utils.init_schema(conn, SCHEMA_PATH)
    return conn


class TestSchemaMigration(unittest.TestCase):
    def test_data_source_on_notices(self):
        conn = _mem_db()
        cols = {r[1] for r in conn.execute("PRAGMA table_info(notices)").fetchall()}
        self.assertIn("data_source", cols)

    def test_data_source_on_awards(self):
        conn = _mem_db()
        cols = {r[1] for r in conn.execute("PRAGMA table_info(awards)").fetchall()}
        self.assertIn("data_source", cols)

    def test_data_source_on_buyers(self):
        conn = _mem_db()
        cols = {r[1] for r in conn.execute("PRAGMA table_info(buyers)").fetchall()}
        self.assertIn("data_source", cols)

    def test_data_source_on_suppliers(self):
        conn = _mem_db()
        cols = {r[1] for r in conn.execute("PRAGMA table_info(suppliers)").fetchall()}
        self.assertIn("data_source", cols)

    def test_suitable_for_sme_on_notices(self):
        conn = _mem_db()
        cols = {r[1] for r in conn.execute("PRAGMA table_info(notices)").fetchall()}
        self.assertIn("suitable_for_sme", cols)

    def test_migration_is_idempotent(self):
        conn = _mem_db()
        import db_utils
        db_utils._migrate_schema(conn)  # second call must not raise
        db_utils._migrate_schema(conn)  # third call must not raise


class TestUpsertBuyerRow(unittest.TestCase):
    def test_insert_and_read_back(self):
        import db_utils
        conn = _mem_db()
        db_utils.upsert_buyer_row(conn, {
            "id": "cf-buyer-99",
            "name": "Test Council",
            "postal_code": "TE1 1ST",
            "data_source": "cf",
        })
        conn.commit()
        row = conn.execute("SELECT * FROM buyers WHERE id='cf-buyer-99'").fetchone()
        self.assertEqual(row["name"], "Test Council")
        self.assertEqual(row["data_source"], "cf")
        self.assertEqual(row["postal_code"], "TE1 1ST")

    def test_fts_default_source(self):
        import db_utils
        conn = _mem_db()
        db_utils.upsert_buyer_row(conn, {"id": "fts-b1", "name": "HMRC"})
        conn.commit()
        row = conn.execute("SELECT data_source FROM buyers WHERE id='fts-b1'").fetchone()
        self.assertEqual(row["data_source"], "fts")

    def test_upsert_updates_name(self):
        import db_utils
        conn = _mem_db()
        db_utils.upsert_buyer_row(conn, {"id": "b1", "name": "Old Name", "data_source": "cf"})
        db_utils.upsert_buyer_row(conn, {"id": "b1", "name": "New Name", "data_source": "cf"})
        conn.commit()
        row = conn.execute("SELECT name FROM buyers WHERE id='b1'").fetchone()
        self.assertEqual(row["name"], "New Name")


class TestUpsertSupplierRow(unittest.TestCase):
    def test_insert_with_ch_number(self):
        import db_utils
        conn = _mem_db()
        sid = db_utils.upsert_supplier_row(conn, {
            "id": "cf-sup-abc123",
            "name": "Acme Ltd",
            "companies_house_no": "12345678",
            "data_source": "cf",
        })
        conn.commit()
        row = conn.execute("SELECT * FROM suppliers WHERE id='cf-sup-abc123'").fetchone()
        self.assertEqual(row["companies_house_no"], "12345678")
        self.assertEqual(sid, "cf-sup-abc123")


class TestUpsertNoticeRow(unittest.TestCase):
    def setUp(self):
        import db_utils
        self.conn = _mem_db()
        db_utils.upsert_buyer_row(self.conn, {"id": "b1", "name": "HMRC", "data_source": "fts"})
        self.conn.commit()

    def test_insert_cf_notice(self):
        import db_utils
        db_utils.upsert_notice_row(self.conn, {
            "ocid": "cf-12345",
            "buyer_id": "b1",
            "title": "IT Support",
            "data_source": "cf",
            "suitable_for_sme": 1,
        })
        self.conn.commit()
        row = self.conn.execute("SELECT * FROM notices WHERE ocid='cf-12345'").fetchone()
        self.assertEqual(row["data_source"], "cf")
        self.assertEqual(row["suitable_for_sme"], 1)
        self.assertEqual(row["title"], "IT Support")

    def test_fts_default_source(self):
        import db_utils
        db_utils.upsert_notice_row(self.conn, {"ocid": "ocds-xyz", "buyer_id": "b1"})
        self.conn.commit()
        row = self.conn.execute("SELECT data_source FROM notices WHERE ocid='ocds-xyz'").fetchone()
        self.assertEqual(row["data_source"], "fts")


class TestUpsertAwardRow(unittest.TestCase):
    def setUp(self):
        import db_utils
        self.conn = _mem_db()
        db_utils.upsert_buyer_row(self.conn, {"id": "b1", "name": "HMRC"})
        db_utils.upsert_notice_row(self.conn, {"ocid": "cf-99", "buyer_id": "b1", "data_source": "cf"})
        self.conn.commit()

    def test_insert_cf_award(self):
        import db_utils
        db_utils.upsert_award_row(self.conn, {
            "id": "cf-award-99",
            "ocid": "cf-99",
            "value_amount_gross": 45000.0,
            "data_source": "cf",
        })
        self.conn.commit()
        row = self.conn.execute("SELECT * FROM awards WHERE id='cf-award-99'").fetchone()
        self.assertEqual(row["data_source"], "cf")
        self.assertEqual(row["value_amount_gross"], 45000.0)


class TestLinkAwardSupplier(unittest.TestCase):
    def test_link_is_idempotent(self):
        import db_utils
        conn = _mem_db()
        db_utils.upsert_buyer_row(conn, {"id": "b1", "name": "B"})
        db_utils.upsert_notice_row(conn, {"ocid": "n1", "buyer_id": "b1"})
        db_utils.upsert_award_row(conn, {"id": "a1", "ocid": "n1"})
        db_utils.upsert_supplier_row(conn, {"id": "s1", "name": "S"})
        db_utils.link_award_supplier(conn, "a1", "s1")
        db_utils.link_award_supplier(conn, "a1", "s1")  # second call must not raise
        conn.commit()
        count = conn.execute("SELECT COUNT(*) FROM award_suppliers WHERE award_id='a1'").fetchone()[0]
        self.assertEqual(count, 1)


class TestIngestState(unittest.TestCase):
    def test_get_missing_returns_empty(self):
        import db_utils
        conn = _mem_db()
        self.assertEqual(db_utils.get_ingest_state(conn, "nonexistent"), "")

    def test_set_and_get_roundtrip(self):
        import db_utils
        conn = _mem_db()
        db_utils.set_ingest_state(conn, "cf_last_date", "2026-01-01T00:00:00")
        self.assertEqual(db_utils.get_ingest_state(conn, "cf_last_date"), "2026-01-01T00:00:00")

    def test_overwrite(self):
        import db_utils
        conn = _mem_db()
        db_utils.set_ingest_state(conn, "k", "v1")
        db_utils.set_ingest_state(conn, "k", "v2")
        self.assertEqual(db_utils.get_ingest_state(conn, "k"), "v2")


if __name__ == "__main__":
    unittest.main()
