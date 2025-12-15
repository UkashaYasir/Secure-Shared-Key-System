import json
from datetime import datetime

def format_operation(op_code):
    """Converts operation codes to human-readable text."""
    mapping = {
        'KEY_GENERATION': 'Key Generation',
        'FILE_ENCRYPTED': 'File Encrypted',
        'FILE_DECRYPTED': 'File Decrypted',
        'KEY_RECONSTRUCTED': 'Key Reconstructed',
        'KEY_RECONSTRUCTION_FAILED': 'Key Reconstruction Failed',
        'KEY_RECONSTRUCTION': 'Key Reconstruction', # In case of slight variations
        'SHARE_GENERATION': 'Share Generation'
    }
    return mapping.get(op_code, op_code.replace('_', ' ').title())

def operation_color(op_code):
    """Maps operation codes to Bootstrap colors."""
    colors = {
        'KEY_GENERATION': 'success',
        'FILE_ENCRYPTED': 'primary',
        'FILE_DECRYPTED': 'info',
        'KEY_RECONSTRUCTED': 'warning',
        'KEY_RECONSTRUCTION_FAILED': 'danger',
        'SHARE_GENERATION': 'secondary'
    }
    return colors.get(op_code, 'secondary')

def operation_icon(op_code):
    """Maps operation codes to FontAwesome icons."""
    icons = {
        'KEY_GENERATION': 'fa-key',
        'FILE_ENCRYPTED': 'fa-lock',
        'FILE_DECRYPTED': 'fa-unlock',
        'KEY_RECONSTRUCTED': 'fa-puzzle-piece',
        'KEY_RECONSTRUCTION_FAILED': 'fa-exclamation-triangle',
        'SHARE_GENERATION': 'fa-share-alt'
    }
    return icons.get(op_code, 'fa-circle-info')

def format_details(details):
    """Formats the details dictionary into a readable string."""
    if not details:
        return ''
    if isinstance(details, str):
        return details
    
    # If it's a simple dict, we can try to make it look nicer
    # e.g. "File ID: ..., Key Set ID: ..."
    try:
        # If it's a dict, join key-value pairs
        if isinstance(details, dict):
            parts = []
            for k, v in details.items():
                human_key = k.replace('_', ' ').title()
                parts.append(f"<b>{human_key}:</b> {v}")
            return ", ".join(parts)
        
        return json.dumps(details, indent=2)
    except:
        return str(details)

def format_datetime(value, fmt="%Y-%m-%d %H:%M:%S"):
    """Formats ISO datetime string to specific format."""
    if not value:
        return "-"
    try:
        # Handle Supabase/Postgres timestamp format
        # e.g. 2025-12-08T07:56:37.956276+00:00
        # dateutil parser is more robust but let's try standard library first
        dt = datetime.fromisoformat(value)
        return dt.strftime(fmt)
    except Exception:
        return value
