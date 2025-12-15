import os
from supabase import create_client, Client

# Initialize Supabase client
# Singleton pattern through module-level variable
_supabase: Client = None

def get_supabase() -> Client:
    """
    Returns the initialized Supabase client.
    Initializes it if it hasn't been already.
    """
    global _supabase
    if _supabase is None:
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
        
        if not url or not key:
            raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set in env.")
            
        _supabase = create_client(url, key)
        
    return _supabase
