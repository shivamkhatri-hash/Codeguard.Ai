import unittest
from app.core.security import hash_password, verify_password, create_jwt_token, decode_jwt_token
from app.services.storage_service import storage_service


class TestAuthAndAdmin(unittest.TestCase):

    def test_password_hashing(self):
        pw = "secretPass123"
        hashed = hash_password(pw)
        self.assertTrue(verify_password(pw, hashed))
        self.assertFalse(verify_password("wrongPass", hashed))

    def test_jwt_tokens(self):
        payload = {"user_id": "usr_123", "email": "test@test.com", "role": "admin"}
        token = create_jwt_token(payload, expires_seconds=3600)
        decoded = decode_jwt_token(token)
        self.assertIsNotNone(decoded)
        self.assertEqual(decoded["user_id"], "usr_123")
        self.assertEqual(decoded["role"], "admin")

    def test_default_users_seeded(self):
        admin = storage_service.get_user_by_email("admin@codeguard.ai")
        self.assertIsNotNone(admin)
        self.assertEqual(admin["role"], "admin")

        dev = storage_service.get_user_by_email("sumit@codeguard.ai")
        self.assertIsNotNone(dev)
        self.assertEqual(dev["role"], "developer")

    def test_admin_stats(self):
        stats = storage_service.get_admin_stats()
        self.assertIn("total_users", stats)
        self.assertIn("severity_breakdown", stats)
        self.assertTrue(stats["total_users"] >= 2)
        print("[OK] Admin Stats Test Passed:", stats["total_users"], "Users,", stats["total_analyses"], "Analyses")


if __name__ == "__main__":
    unittest.main()
