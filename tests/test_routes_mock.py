
import unittest
from unittest.mock import patch, MagicMock
import io
import sys

# Mock imports that might fail if environment is bad, but we need them for functionality
try:
    from securevault import create_app
    from securevault.routes import bp
except ImportError:
    pass

class TestEncryptFileMock(unittest.TestCase):
    def setUp(self):
        # Create a dummy app if import failed? No, we need the real app structure.
        # Assuming we can fix the import error by installing deps.
        import securevault
        self.app = securevault.create_app()
        self.app.config['TESTING'] = True
        self.app.config['SECRET_KEY'] = 'dev'
        self.client = self.app.test_client()

    @patch('securevault.routes.get_supabase')
    @patch('securevault.routes.SupabaseModels')
    @patch('securevault.routes.audit_logger.AuditLogger')
    @patch('securevault.routes.file_crypto')
    @patch('securevault.services.sss_manager')
    @patch('securevault.services.share_crypto')
    def test_encrypt_file_upload_flow(self, mock_share_crypto, mock_sss, mock_file_crypto, mock_audit, mock_models, mock_get_supabase):
        # Setup Mocks
        mock_file_crypto.encrypt_file.return_value = {
            'ciphertext': b'encrypted_content',
            'nonce': 'nonce',
            'auth_tag': 'tag'
        }
        
        mock_sss.SSSManager.split_secret.return_value = [b'share1', b'share2', b'share3']
        
        def encrypt_share_side_effect(share, pwd):
            return {'data': 'encrypted_share'}
        mock_share_crypto.encrypt_share.side_effect = encrypt_share_side_effect
        
        # Mock Supabase
        mock_key_set = {'id': 'key_set_123', 'label': 'test'}
        mock_models.create_key_set.return_value = mock_key_set
        
        mock_storage = MagicMock()
        mock_bucket = MagicMock()
        mock_get_supabase.return_value.storage.from_.return_value = mock_bucket
        
        # Execute
        data = {
            'file': (io.BytesIO(b'original content'), 'test.txt'),
            'n_shares': '3',
            'threshold': '2',
            'password': 'pass',
            'key_set_id': 'new'
        }
        
        response = self.client.post('/encrypt-file', data=data, content_type='multipart/form-data')
        
        # Verify
        self.assertEqual(response.status_code, 200)
        # Check if download is triggered (checking headers or content)
        self.assertIn('secure_shares_test.txt.json', response.headers.get('Content-Disposition'))
        
        # KEY VERIFICATION: Check if upload was called with a file-like object (BytesIO)
        mock_bucket.upload.assert_called_once()
        call_args = mock_bucket.upload.call_args[1] # kwargs
        self.assertIn('file', call_args)
        uploaded_file = call_args['file']
        self.assertIsInstance(uploaded_file, io.BytesIO, "Upload should receive a BytesIO object")
        self.assertEqual(uploaded_file.getvalue(), b'encrypted_content')

if __name__ == '__main__':
    unittest.main()
