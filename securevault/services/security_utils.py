import os
import base64
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend

def generate_salt(length=16):
    """Generates a random salt of specified length."""
    return os.urandom(length)

def derive_key(password: str, salt: bytes, iterations=100_000, length=32) -> bytes:
    """
    Derives a secure key from a password using PBKDF2-HMAC-SHA256.
    
    Args:
        password (str): The user's password.
        salt (bytes): A random salt.
        iterations (int): Number of iterations for PBKDF2.
        length (int): Desired key length in bytes (32 for AES-256).
        
    Returns:
        bytes: The derived key.
    """
    if isinstance(password, str):
        password = password.encode('utf-8')
        
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=length,
        salt=salt,
        iterations=iterations,
        backend=default_backend()
    )
    return kdf.derive(password)

def generate_random_key(length=32) -> bytes:
    """Generates a cryptographically strong random key."""
    return os.urandom(length)

def encode_bytes_to_base64(data: bytes) -> str:
    """Encodes bytes to a base64 string."""
    return base64.b64encode(data).decode('utf-8')

def decode_base64_to_bytes(data: str) -> bytes:
    """Decodes a base64 string to bytes."""
    return base64.b64decode(data)
