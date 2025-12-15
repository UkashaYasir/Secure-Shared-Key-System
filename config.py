import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration."""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-fallback-key-do-not-use-in-prod'
    SUPABASE_URL = os.environ.get('SUPABASE_URL')
    SUPABASE_KEY = os.environ.get('SUPABASE_SERVICE_ROLE_KEY')
    
    # Session Security
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=15)
    
    # Cryptography settings
    # PBKDF2 iterations - higher is safer but slower. 100,000 is a good baseline.
    KDF_ITERATIONS = 100_000
    KDF_ALGORITHM = 'SHA256'
    KDF_LENGTH = 32  # 32 bytes = 256 bits

    if not SUPABASE_URL or not SUPABASE_KEY:
        print("WARNING: Supabase credentials not found in environment variables.")
