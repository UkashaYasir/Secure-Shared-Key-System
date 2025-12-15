from securevault.services import share_crypto, sss_manager
from securevault.models_supabase import SupabaseModels
from securevault.services.audit_logger import AuditLogger
import datetime

# In-memory storage for active reconstructed keys.
# Dict key: session_id, Value: {'key': bytes, 'expires': datetime}
# In a multi-worker production env, this would need a Redis or Memcached with encryption.
# For this demo, process memory is acceptable as per "Hold AES key ONLY in server memory".
_ACTIVE_SESSIONS_MEMORY = {}

class ReconstructionEngine:
    
    @staticmethod
    def reconstruct_key(key_set_id: str, share_files_data: list, passwords: list):
        """
        Attempts to reconstruct the AES key from uploaded shares.
        
        Args:
            key_set_id: ID of the key set.
            share_files_data: List of dicts (parsed JSON from uploaded share files).
            passwords: List of passwords corresponding to the shares.
            
        Returns:
            str: Session ID if successful.
        """
        if len(share_files_data) != len(passwords):
            raise ValueError("Count of shares and passwords must match.")
            
        decrypted_shares = []
        
        try:
            for i, share_data in enumerate(share_files_data):
                # decrypt_share returns the "index-hexdata" string
                s = share_crypto.decrypt_share(share_data, passwords[i])
                decrypted_shares.append(s)
        except Exception as e:
            AuditLogger.log('KEY_RECONSTRUCTION_FAILED', details={'error': str(e), 'key_set_id': key_set_id})
            raise ValueError("Failed to decrypt one or more shares. Check passwords.")

        try:
            # Combine shares
            aes_key = sss_manager.SSSManager.combine_shares(decrypted_shares)
        except Exception as e:
            AuditLogger.log('KEY_RECONSTRUCTION_FAILED', details={'error': 'Combination failed', 'key_set_id': key_set_id})
            raise ValueError("Shares could not be combined. Are they from the same key set?")

        # Create session record in DB
        expiry = datetime.datetime.utcnow() + datetime.timedelta(minutes=15)
        session_record = SupabaseModels.create_reconstruction_session(key_set_id, expiry.isoformat())
        
        # Store key in memory
        _ACTIVE_SESSIONS_MEMORY[session_record['id']] = {
            'key': aes_key,
            'expires': expiry
        }
        
        AuditLogger.log('KEY_RECONSTRUCTED', details={'key_set_id': key_set_id, 'session_id': session_record['id']})
        return session_record['id']

    @staticmethod
    def get_key_for_session(session_id: str) -> bytes:
        session = _ACTIVE_SESSIONS_MEMORY.get(session_id)
        if not session:
            return None
        
        if datetime.datetime.utcnow() > session['expires']:
            # Expired
            del _ACTIVE_SESSIONS_MEMORY[session_id]
            SupabaseModels.update_session_status(session_id, 'EXPIRED')
            return None
            
        return session['key']

    @staticmethod
    def end_session(session_id: str):
        if session_id in _ACTIVE_SESSIONS_MEMORY:
            del _ACTIVE_SESSIONS_MEMORY[session_id]
            SupabaseModels.update_session_status(session_id, 'USED')

    @staticmethod
    def cleanup_expired_sessions():
        # Helper to periodically clean memory
        now = datetime.datetime.utcnow()
        for sid in list(_ACTIVE_SESSIONS_MEMORY.keys()):
            if now > _ACTIVE_SESSIONS_MEMORY[sid]['expires']:
                del _ACTIVE_SESSIONS_MEMORY[sid]
