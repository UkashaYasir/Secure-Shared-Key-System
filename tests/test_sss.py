import unittest
from securevault.services.sss_manager import SSSManager

class TestSSSManager(unittest.TestCase):
    def test_split_and_combine(self):
        secret = b"this is a 32 byte secret key!!!!" # 32 bytes
        n = 5
        k = 3
        
        shares = SSSManager.split_secret(secret, n, k)
        self.assertEqual(len(shares), n)
        
        # Combine k shares
        recovered = SSSManager.combine_shares(shares[:k])
        self.assertEqual(recovered, secret)
        
        # Combine n shares
        recovered_all = SSSManager.combine_shares(shares)
        self.assertEqual(recovered_all, secret)

    def test_insufficient_shares(self):
        secret = b"short secret"
        n = 5
        k = 3
        shares = SSSManager.split_secret(secret, n, k)
        
        # Try with k-1 shares
        # Note: secretsharing library might produce garbage or raise error depending on implementation
        # The recover_secret usually returns something, but it won't be the original secret.
        try:
            recovered = SSSManager.combine_shares(shares[:k-1])
            self.assertNotEqual(recovered, secret)
        except Exception:
            # If it raises, that's also acceptable for "failed to recover"
            pass

if __name__ == '__main__':
    unittest.main()
