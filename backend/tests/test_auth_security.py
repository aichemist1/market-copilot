import unittest

from market_copilot.auth.security import hash_password, verify_password


class PasswordHashTests(unittest.TestCase):
    def test_hash_round_trip(self) -> None:
        password_hash = hash_password("correct horse battery staple")

        self.assertTrue(verify_password("correct horse battery staple", password_hash))
        self.assertFalse(verify_password("incorrect", password_hash))


if __name__ == "__main__":
    unittest.main()
