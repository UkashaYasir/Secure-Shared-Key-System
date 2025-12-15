import os
import random
import functools

# GF(2^8) field arithmetic
# Irreducible polynomial: x^8 + x^4 + x^3 + x + 1 (0x11B)
_R = 0x11D
_LOG = [0] * 256
_EXP = [0] * 256

def _init_tables():
    x = 1
    for i in range(255):
        _EXP[i] = x
        _LOG[x] = i
        x <<= 1
        if x & 0x100:
            x ^= _R
    _EXP[255] = _EXP[0] # Cyclic

_init_tables()

def _add(a, b):
    return a ^ b

def _sub(a, b):
    return a ^ b

def _mul(a, b):
    if a == 0 or b == 0:
        return 0
    return _EXP[(_LOG[a] + _LOG[b]) % 255]

def _div(a, b):
    if b == 0:
        raise ZeroDivisionError
    if a == 0:
        return 0
    return _EXP[(_LOG[a] - _LOG[b] + 255) % 255]

class SSSManager:
    """
    Shamir's Secret Sharing over GF(2^8).
    Secrets are bytes. Shares are 'index-hexvalue'.
    """

    @staticmethod
    def _eval_poly(poly, x):
        """Evaluates polynomial at x using Horner's method."""
        y = 0
        for coeff in reversed(poly):
            y = _mul(y, x) ^ coeff
        return y

    @staticmethod
    def _lagrange_interpolate(x, x_s, y_s):
        """
        Computes the value of the polynomial passing through (x_s[i], y_s[i]) at x.
        """
        k = len(x_s)
        y = 0
        for i in range(k):
            # Compute Li(x)
            numerator = 1
            denominator = 1
            for j in range(k):
                if i == j:
                    continue
                numerator = _mul(numerator, _sub(x, x_s[j]))
                denominator = _mul(denominator, _sub(x_s[i], x_s[j]))
            
            term = _mul(y_s[i], _div(numerator, denominator))
            y = _add(y, term)
        return y

    @staticmethod
    def split_secret(secret_bytes: bytes, n: int, k: int) -> list:
        """
        Splits a secret into n shares, k needed to reconstruct.
        """
        if k > n:
            raise ValueError("Threshold (k) cannot be greater than shares (n)")
        if k < 2:
            raise ValueError("Threshold (k) must be at least 2")

        # Create a random polynomial for each byte of the secret
        # poly[0] = secret byte
        # poly[1..k-1] = random coefficients
        
        # We process the secret byte-by-byte (or conceptually so).
        # Actually, let's form k-1 random byte arrays of the same length as secret.
        
        secret_len = len(secret_bytes)
        # Coefficients: a matrix of (k-1) x secret_len
        # plus the constant term which is the secret itself.
        
        # coeffs[i][byte_idx] is the coefficient for x^i at that byte position
        coeffs = [[random.randint(0, 255) for _ in range(secret_len)] for _ in range(k - 1)]
        
        shares = []
        for x in range(1, n + 1):
            # Evaluate polynomial at x for each byte
            share_val = bytearray(secret_len)
            for i in range(secret_len):
                # P(x) = secret + c1*x + c2*x^2 + ...
                val = secret_bytes[i]
                x_pow = x
                for j in range(k - 1):
                    term = _mul(coeffs[j][i], x_pow)
                    val = _add(val, term)
                    x_pow = _mul(x_pow, x)
                share_val[i] = val
            
            # Format: "index-hexdata"
            shares.append(f"{x}-{share_val.hex()}")
            
        return shares

    @staticmethod
    def combine_shares(shares_strings: list) -> bytes:
        """
        Reconstructs the secret from shares.
        """
        if not shares_strings:
            raise ValueError("No shares provided")
            
        # Parse shares
        try:
            points = []
            for s in shares_strings:
                idx_str, data_hex = s.split('-')
                x = int(idx_str)
                y_bytes = bytes.fromhex(data_hex)
                points.append((x, y_bytes))
        except ValueError:
             raise ValueError("Invalid share format")

        k = len(points)
        secret_len = len(points[0][1])
        
        # Validate lengths
        for _, y in points:
            if len(y) != secret_len:
                raise ValueError("Shares have inconsistent lengths")
        
        x_s = [p[0] for p in points]
        y_s_list = [p[1] for p in points]
        
        secret = bytearray(secret_len)
        
        # Interpolate for each byte position at x=0
        for i in range(secret_len):
            y_s = [y[i] for y in y_s_list]
            secret[i] = SSSManager._lagrange_interpolate(0, x_s, y_s)
            
        return bytes(secret)
