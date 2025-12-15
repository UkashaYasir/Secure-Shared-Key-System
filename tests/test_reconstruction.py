import unittest
from unittest.mock import MagicMock, patch
from securevault.services import reconstruction_engine

class TestReconstruction(unittest.TestCase):
    
    @patch('securevault.services.reconstruction_engine.SupabaseModels')
    @patch('securevault.services.reconstruction_engine.AuditLogger')
    @patch('securevault.services.reconstruction_engine.sss_manager.SSSManager')
    @patch('securevault.services.reconstruction_engine.share_crypto.decrypt_share')
    def test_reconstruct_success(self, mock_decrypt, mock_sss, mock_logger, mock_db):
        # Setup mocks
        mock_decrypt.side_effect = ["share1", "share2", "share3"]
        mock_sss.combine_shares.return_value = b"reconstructed_key_32_bytes______"
        mock_db.create_reconstruction_session.return_value = {'id': 'sess_123'}
        
        engine = reconstruction_engine.ReconstructionEngine()
        
        share_data = [{'d':1}, {'d':2}, {'d':3}]
        passwords = ['p1', 'p2', 'p3']
        key_set_id = 'ks_1'
        
        session_id = engine.reconstruct_key(key_set_id, share_data, passwords)
        
        self.assertEqual(session_id, 'sess_123')
        
        # Verify key is in memory
        key = engine.get_key_for_session('sess_123')
        self.assertEqual(key, b"reconstructed_key_32_bytes______")
        
        # Verify calls
        self.assertEqual(mock_decrypt.call_count, 3)
        mock_sss.combine_shares.assert_called_once()

if __name__ == '__main__':
    unittest.main()
