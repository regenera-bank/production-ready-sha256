import unittest
from regenera_tools.migrations import Migration, validate_migrations, verify_published
from regenera_tools.errors import ValidationError

class MigrationsTest(unittest.TestCase):
    def test_version(self): self.assertEqual(Migration("0001_init.sql", "SELECT 1;").version, 1)
    def test_bad_name(self): self.assertRaises(ValidationError, lambda: Migration("1.sql", "x").version)
    def test_checksum_stable(self): self.assertEqual(Migration("0001_x.sql", "a\r\n").checksum, Migration("0001_x.sql", "a\n").checksum)
    def test_valid(self): self.assertEqual(validate_migrations([Migration("0001_a.sql", "CREATE TABLE a(id int);")]), [])
    def test_duplicate(self): self.assertTrue(validate_migrations([Migration("0001_a.sql", "x"), Migration("0001_b.sql", "y")]))
    def test_gap(self): self.assertTrue(validate_migrations([Migration("0001_a.sql", "x"), Migration("0003_b.sql", "y")]))
    def test_begin(self): self.assertTrue(validate_migrations([Migration("0001_a.sql", "BEGIN; SELECT 1;")]))
    def test_commit(self): self.assertTrue(validate_migrations([Migration("0001_a.sql", "COMMIT;")]))
    def test_destructive(self): self.assertTrue(validate_migrations([Migration("0001_a.sql", "DROP TABLE x;")]))
    def test_destructive_approved(self): self.assertEqual(validate_migrations([Migration("0001_a.sql", "-- regenera: destructive-approved=CHG-1\nDROP TABLE x;")]), [])
    def test_published_same(self):
        migration = Migration("0001_a.sql", "x")
        self.assertEqual(verify_published([migration], {migration.filename: migration.checksum}), [])
    def test_published_changed(self): self.assertTrue(verify_published([Migration("0001_a.sql", "x")], {"0001_a.sql": "0" * 64}))
