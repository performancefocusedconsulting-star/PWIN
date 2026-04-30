import sys, os, sqlite3, unittest, tempfile
sys.stdout.reconfigure(encoding='utf-8')

# Add agent/ to path so imports work
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

SCHEMA_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'db', 'schema.sql')

class TestSchema(unittest.TestCase):

    def setUp(self):
        self.conn = sqlite3.connect(':memory:')
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys=ON")

    def tearDown(self):
        self.conn.close()

    def _table_exists(self, name):
        row = self.conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?", (name,)
        ).fetchone()
        return row is not None

    def _columns(self, table):
        return {r[1] for r in self.conn.execute(f"PRAGMA table_info({table})").fetchall()}

    def _apply_schema(self):
        with open(SCHEMA_PATH, encoding='utf-8') as f:
            self.conn.executescript(f.read())

    def test_stakeholders_table_exists(self):
        self._apply_schema()
        self.assertTrue(self._table_exists('stakeholders'))
        cols = self._columns('stakeholders')
        self.assertIn('person_id', cols)
        self.assertIn('name_normalised', cols)
        self.assertIn('canonical_buyer_id', cols)
        self.assertIn('scs_band_inferred', cols)

    def test_stakeholder_history_table_exists(self):
        self._apply_schema()
        self.assertTrue(self._table_exists('stakeholder_history'))
        cols = self._columns('stakeholder_history')
        self.assertIn('person_id', cols)
        self.assertIn('snapshot_date', cols)

    def test_pac_witnesses_table_exists(self):
        self._apply_schema()
        self.assertTrue(self._table_exists('pac_witnesses'))
        cols = self._columns('pac_witnesses')
        self.assertIn('witness_id', cols)
        self.assertIn('name_normalised', cols)
        self.assertIn('canonical_buyer_id', cols)


if __name__ == '__main__':
    unittest.main()
