from securevault.supabase_client import get_supabase

class SupabaseModels:
    
    @staticmethod
    def create_key_set(n_shares: int, threshold: int, label: str = None) -> dict:
        data = {
            'n_shares': n_shares,
            'threshold': threshold,
            'label': label
        }
        response = get_supabase().table('key_sets').insert(data).execute()
        return response.data[0] if response.data else None

    @staticmethod
    def get_key_set(key_set_id: str) -> dict:
        response = get_supabase().table('key_sets').select('*').eq('id', key_set_id).execute()
        return response.data[0] if response.data else None

    @staticmethod
    def list_key_sets() -> list:
        response = get_supabase().table('key_sets').select('*').order('created_at', desc=True).execute()
        return response.data

    @staticmethod
    def create_file_record(original_filename: str, storage_path: str, nonce: str, auth_tag: str, key_set_id: str) -> dict:
        data = {
            'original_filename': original_filename,
            'storage_path': storage_path,
            'nonce': nonce,
            'auth_tag': auth_tag,
            'key_set_id': key_set_id
        }
        response = get_supabase().table('files').insert(data).execute()
        return response.data[0] if response.data else None
    
    @staticmethod
    def get_file_record(file_id: str) -> dict:
        response = get_supabase().table('files').select('*').eq('id', file_id).execute()
        return response.data[0] if response.data else None
    
    @staticmethod
    def list_files_for_keyset(key_set_id: str) -> list:
        response = get_supabase().table('files').select('*').eq('key_set_id', key_set_id).execute()
        return response.data if response.data else []

    @staticmethod
    def create_reconstruction_session(key_set_id: str, expires_at: str) -> dict:
        data = {
            'key_set_id': key_set_id,
            'expires_at': expires_at,
            'status': 'ACTIVE'
        }
        response = get_supabase().table('reconstruction_sessions').insert(data).execute()
        return response.data[0] if response.data else None
        
    @staticmethod
    def get_active_session(key_set_id: str) -> dict:
        # Simplistic check, real app should check expiry timestamp vs now() in DB or code
        response = get_supabase().table('reconstruction_sessions') \
            .select('*') \
            .eq('key_set_id', key_set_id) \
            .eq('status', 'ACTIVE') \
            .execute()
        # In a real scenario, we might have multiple, we'd pick the latest valid one
        return response.data[0] if response.data else None

    @staticmethod
    def update_session_status(session_id: str, status: str):
        get_supabase().table('reconstruction_sessions').update({'status': status}).eq('id', session_id).execute()
