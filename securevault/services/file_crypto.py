from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from securevault.services import security_utils

def encrypt_file(file_bytes: bytes, key: bytes) -> dict:
    """
    Encrypts a file using AES-GCM with the provided key.
    
    Args:
        file_bytes (bytes): The raw content of the file.
        key (bytes): The AES-256 key.
        
    Returns:
        dict: A dictionary with 'ciphertext', 'nonce', and 'auth_tag' (implicitly in ciphertext for GCM).
              However, for storage, we might want to separate them or keep them together.
              Standard GCM encrypt() returns concatenation of ciphertext + tag.
              We will split them for clarity in storage if needed, or just keep as blob.
              The prompt asked to store nonce and auth_tag separately in DB.
    """
    aesgcm = AESGCM(key)
    nonce = security_utils.generate_salt(12)
    
    # AESGCM.encrypt appends the auth tag to the end of the ciphertext
    encrypted_data = aesgcm.encrypt(nonce, file_bytes, None)
    
    # Extract ciphertext and tag
    # The tag is the last 16 bytes
    tag = encrypted_data[-16:]
    ciphertext = encrypted_data[:-16]
    
    return {
        'nonce': security_utils.encode_bytes_to_base64(nonce),
        'ciphertext': ciphertext, # Keep as bytes for storage upload
        'auth_tag': security_utils.encode_bytes_to_base64(tag)
    }

def decrypt_file(ciphertext: bytes, key: bytes, nonce_b64: str, auth_tag_b64: str) -> bytes:
    """
    Decrypts a file.
    
    Args:
        ciphertext (bytes): The raw encrypted bytes (excluding tag).
        key (bytes): The AES key.
        nonce_b64 (str): Base64 encoded nonce.
        auth_tag_b64 (str): Base64 encoded auth tag.
        
    Returns:
        bytes: The decrypted file content.
    """
    nonce = security_utils.decode_base64_to_bytes(nonce_b64)
    tag = security_utils.decode_base64_to_bytes(auth_tag_b64)
    
    # Reconstruct the full 'data' expected by AESGCM.decrypt (ciphertext + tag)
    encrypted_data = ciphertext + tag
    
    aesgcm = AESGCM(key)
    return aesgcm.decrypt(nonce, encrypted_data, None)
