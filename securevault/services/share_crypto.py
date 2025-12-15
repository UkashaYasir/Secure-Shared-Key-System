import json
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from securevault.services import security_utils

def encrypt_share(share: str, password: str) -> dict:
    """
    Encrypts a single share using a key derived from the password.
    
    Args:
        share (str): The share string to encrypt.
        password (str): User provided password.
        
    Returns:
        dict: A dictionary containing the encrypted share and metadata.
    """
    # 1. Generate a fresh salt
    salt = security_utils.generate_salt()
    
    # 2. Derive key from password
    key = security_utils.derive_key(password, salt)
    
    # 3. Encrypt the share using AES-GCM
    aesgcm = AESGCM(key)
    nonce = security_utils.generate_salt(12) # 96-bit nonce for GCM
    
    # Encode share to bytes
    share_bytes = share.encode('utf-8')
    
    ciphertext = aesgcm.encrypt(nonce, share_bytes, None)
    
    # 4. Construct the return dictionary
    return {
        'salt': security_utils.encode_bytes_to_base64(salt),
        'nonce': security_utils.encode_bytes_to_base64(nonce),
        'ciphertext': security_utils.encode_bytes_to_base64(ciphertext),
        'kdf_iterations': 100000, # Hardcoded for now, or fetch from config
        'kdf_algorithm': 'SHA256'
    }

def decrypt_share(encrypted_share_data: dict, password: str) -> str:
    """
    Decrypts a share using the provided password.
    
    Args:
        encrypted_share_data (dict): The dictionary returned by encrypt_share.
        password (str): The password used for encryption.
        
    Returns:
        str: The original share string.
        
    Raises:
        InvalidTag: If decryption fails (wrong password or tampering).
    """
    salt = security_utils.decode_base64_to_bytes(encrypted_share_data['salt'])
    nonce = security_utils.decode_base64_to_bytes(encrypted_share_data['nonce'])
    ciphertext = security_utils.decode_base64_to_bytes(encrypted_share_data['ciphertext'])
    iterations = encrypted_share_data.get('kdf_iterations', 100000)
    
    # Derive the same key
    key = security_utils.derive_key(password, salt, iterations=iterations)
    
    aesgcm = AESGCM(key)
    try:
        plaintext_bytes = aesgcm.decrypt(nonce, ciphertext, None)
        return plaintext_bytes.decode('utf-8')
    except Exception:
        # Re-raise as a generic error or handle specifically
        raise ValueError("Decryption failed. Incorrect password or corrupted data.")
