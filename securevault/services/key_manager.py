from securevault.services import security_utils
from securevault.services import sss_manager
from securevault.services import share_crypto

def generate_and_split_key(n: int, k: int, passwords: list) -> dict:
    """
    Generates a new AES key, splits it into shares, and encrypts each share.
    
    Args:
        n (int): Total shares.
        k (int): Threshold.
        passwords (list): List of N passwords, one for each share.
        
    Returns:
        dict: containing the encrypted shares and metadata.
              Does NOT return the raw AES key.
    """
    if len(passwords) != n:
        raise ValueError("Number of passwords must match number of shares (N).")
        
    # 1. Generate AES Key
    aes_key = security_utils.generate_random_key(32) # 256 bits
    
    # 2. Split Key
    shares = sss_manager.SSSManager.split_secret(aes_key, n, k)
    
    # 3. Encrypt each share
    encrypted_shares = []
    for i, share in enumerate(shares):
        enc_share = share_crypto.encrypt_share(share, passwords[i])
        enc_share['share_index'] = i + 1
        encrypted_shares.append(enc_share)
        
    # We consciously discard 'aes_key' here by not returning it and letting it go out of scope.
    
    return {
        'n': n,
        'k': k,
        'encrypted_shares': encrypted_shares
    }
