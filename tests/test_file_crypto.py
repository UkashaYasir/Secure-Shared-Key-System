import unittest
import os
from securevault.services import file_crypto

class TestFileCrypto(unittest.TestCase):
    def test_encrypt_decrypt_file(self):
        original_data = os.urandom(1024) # 1KB random data
        key = os.urandom(32)
        
        # Encrypt
        enc_result = file_crypto.encrypt_file(original_data, key)
        self.assertIn('ciphertext', enc_result)
        self.assertIn('nonce', enc_result)
        self.assertIn('auth_tag', enc_result)
        
        # Decrypt
        decrypted_data = file_crypto.decrypt_file(
            enc_result['ciphertext'], 
            key, 
            enc_result['nonce'], 
            enc_result['auth_tag']
        )
        
        self.assertEqual(decrypted_data, original_data)

    def test_tampered_ciphertext(self):
        original_data = b"hello world"
        key = os.urandom(32)
        
        enc_result = file_crypto.encrypt_file(original_data, key)
        
        # Tamper with ciphertext
        tampered_ciphertext = bytearray(enc_result['ciphertext'])
        tampered_ciphertext[0] ^= 0xFF # Flip bits
        
        with self.assertRaises(Exception): # AESGCM raises invalid tag generic exception
            file_crypto.decrypt_file(
                bytes(tampered_ciphertext), 
                key, 
                enc_result['nonce'], 
                enc_result['auth_tag']
            )

if __name__ == '__main__':
    unittest.main()
