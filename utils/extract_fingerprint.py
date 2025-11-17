import re
from utils.constants import sep

def extract_fingerprint(filename: str, fingerprint_length: int = 64) -> str | None:
    """
    Extracts a fingerprint from a filename if it exists after 'separator'.
    
    Args:
        filename: name of the file (e.g., 'video<separator>9f2d5c6e4b3a1e8f7d6c5b4a3f2e1d0c9b8a7f6e5d4c3b2a1f0e9d8c7b6a5f4e.mkv')
        fingerprint_length: expected length of fingerprint in hex characters
        
    Returns:
        The fingerprint string if found, else None
    """
    # Remove file extension
    name_only = filename.rsplit(".", 1)[0]

    # Split on triple underscore
    parts = name_only.split(sep)
    if len(parts) < 2:
        return None  # No separator found

    candidate = parts[-1]

    # Check if it is a valid hex fingerprint of the expected length
    if re.fullmatch(rf"[0-9a-fA-F]{{{fingerprint_length}}}", candidate):
        return candidate

    return None
