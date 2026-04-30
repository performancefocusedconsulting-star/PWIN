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


class TestUtils(unittest.TestCase):

    def test_normalise_name_last_first(self):
        from stakeholder_utils import normalise_name
        self.assertEqual(normalise_name('Gallagher, Daniel'), 'Daniel Gallagher')

    def test_normalise_name_with_nickname_and_title(self):
        from stakeholder_utils import normalise_name
        self.assertEqual(normalise_name('Rouse, Deana (Deana), Miss'), 'Deana Rouse')
        self.assertEqual(normalise_name('Berthon, Richard (Richard), Mr'), 'Richard Berthon')

    def test_normalise_name_already_normalised(self):
        from stakeholder_utils import normalise_name
        self.assertEqual(normalise_name('Isabelle Trowler'), 'Isabelle Trowler')
        self.assertEqual(normalise_name('Helen Waite'), 'Helen Waite')

    def test_normalise_name_empty(self):
        from stakeholder_utils import normalise_name
        self.assertEqual(normalise_name(''), '')
        self.assertEqual(normalise_name('  '), '')

    def test_infer_scs_band_permanent_secretary(self):
        from stakeholder_utils import infer_scs_band
        self.assertEqual(infer_scs_band('Permanent Secretary'), 'PermanentSecretary')
        self.assertEqual(infer_scs_band('Second Permanent Secretary'), 'PermanentSecretary')

    def test_infer_scs_band_director_general(self):
        from stakeholder_utils import infer_scs_band
        self.assertEqual(infer_scs_band('Director General and Chief Economic Adviser'), 'DirectorGeneral')
        self.assertEqual(infer_scs_band('Director-General, Strategy'), 'DirectorGeneral')

    def test_infer_scs_band_director(self):
        from stakeholder_utils import infer_scs_band
        self.assertEqual(infer_scs_band('Director - Economics'), 'Director')
        self.assertEqual(infer_scs_band('Director of Finance and Deputy CEO Infrastructure Projects Authority'), 'Director')
        self.assertEqual(infer_scs_band('FCAS Director'), 'Director')

    def test_infer_scs_band_deputy_director_not_director(self):
        from stakeholder_utils import infer_scs_band
        # DeputyDirector must not match as Director
        self.assertEqual(infer_scs_band('Deputy Director, Commercial Policy'), 'DeputyDirector')

    def test_infer_scs_band_unknown(self):
        from stakeholder_utils import infer_scs_band
        self.assertEqual(infer_scs_band('Secretary of State COS-2'), 'Unknown')
        self.assertEqual(infer_scs_band(''), 'Unknown')

    def test_resolve_col_current_format(self):
        from stakeholder_utils import resolve_col
        row = {
            'Name': 'Gallagher, Daniel',
            'Grade (or equivalent)': 'SCS2',
            'Reports to Senior Post': 'CEO',
            'Contact E-mail': 'daniel.gallagher@hmt.gov.uk',
        }
        self.assertEqual(resolve_col(row, 'name'), 'Gallagher, Daniel')
        self.assertEqual(resolve_col(row, 'grade'), 'SCS2')
        self.assertEqual(resolve_col(row, 'reports_to'), 'CEO')

    def test_resolve_col_legacy_format(self):
        from stakeholder_utils import resolve_col
        row = {
            'Name': 'Smith, Jane',
            'Grade': 'SCS1',
            'Reports To Senior Post': 'Head of Unit',
            'Contact Email': 'jane.smith@dfe.gov.uk',
        }
        self.assertEqual(resolve_col(row, 'grade'), 'SCS1')
        self.assertEqual(resolve_col(row, 'reports_to'), 'Head of Unit')

    def test_resolve_col_missing_field_returns_empty(self):
        from stakeholder_utils import resolve_col
        self.assertEqual(resolve_col({}, 'grade'), '')
        self.assertEqual(resolve_col({}, 'reports_to'), '')

    def test_slug(self):
        from stakeholder_utils import slug
        self.assertEqual(slug('Daniel Gallagher'), 'daniel-gallagher')
        self.assertEqual(slug('  Hello  World  '), 'hello-world')

    def test_person_id(self):
        from stakeholder_utils import person_id
        self.assertEqual(person_id('Daniel Gallagher', 'hm-treasury'), 'daniel-gallagher--hm-treasury')


if __name__ == '__main__':
    unittest.main()
