import sqlite3
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "agent"))

SCHEMA_PATH = Path(__file__).parent.parent / "db" / "schema.sql"


def _mem_db():
    """Open in-memory DB, run schema init from ingest.py (before db_utils exists)."""
    import ingest as ing
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    ing.DB_PATH  # just to import
    orig_path = ing.SCHEMA_PATH
    ing.SCHEMA_PATH = SCHEMA_PATH
    ing.init_schema(conn)
    ing.SCHEMA_PATH = orig_path
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
        import ingest as ing
        ing._migrate_schema(conn)  # second call must not raise
        ing._migrate_schema(conn)  # third call must not raise


if __name__ == "__main__":
    unittest.main()
