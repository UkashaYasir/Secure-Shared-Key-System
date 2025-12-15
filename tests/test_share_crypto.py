import unittest
from securevault.services import share_crypto

class TestShareCrypto(unittest.TestCase):
    def test_encrypt_decrypt_share(self):
        share = "1-abcdef1234567890"
        password = "strongpassword"
        
        # Encrypt
        encrypted = share_crypto.encrypt_share(share, password)
        self.assertIn('ciphertext', encrypted)
        self.assertIn('salt', encrypted)
        self.assertIn('nonce', encrypted)
        
        # Decrypt
        decrypted = share_crypto.decrypt_share(encrypted, password)
        self.assertEqual(decrypted, share)

    def test_wrong_password(self):
        share = "1-abcdef1234567890"
        password = "correct"
        wrong_password = "wrong"
        
        encrypted = share_crypto.encrypt_share(share, password)
        
        with self.assertRaises(ValueError):
            share_crypto.decrypt_share(encrypted, wrong_password)

if __name__ == '__main__':
    unittest.main()
