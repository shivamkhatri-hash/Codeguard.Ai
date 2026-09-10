import unittest
from app.services.mongodb_storage_service import MongoDBStorageService


class TestMongoDBAtlas(unittest.TestCase):

    def setUp(self):
        self.service = MongoDBStorageService()

    def test_mongodb_connection_and_seeding(self):
        admin = self.service.get_user_by_email("admin@codeguard.ai")
        self.assertIsNotNone(admin)
        self.assertEqual(admin["role"], "admin")
        print("[OK] MongoDB Atlas Admin Account Verified:", admin["email"])

    def test_save_and_retrieve_analysis(self):
        test_id = self.service.generate_id()
        self.service.save_analysis(
            analysis_id=test_id,
            filename="0209.py",
            status="completed",
            language="python",
            code="cursor.execute('SELECT * FROM users')",
            syntax_valid=True,
            findings=[{"line": 1, "severity": "High", "title": "SQL Injection"}]
        )

        retrieved = self.service.get_analysis(test_id)
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved["filename"], "0209.py")
        self.assertEqual(len(retrieved["findings"]), 1)
        print("[OK] MongoDB Atlas Analysis Saved & Retrieved Successfully! ID:", test_id)

        # Cleanup
        self.service.delete_analysis(test_id)


if __name__ == "__main__":
    unittest.main()
