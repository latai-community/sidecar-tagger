"""
Title: Hashing Utilities (Layer 0)
Abstract: Provides memory-safe SHA-256 calculation for file identity verification.
Why: Essential for implementing the "Zero-Cost Identity" check to avoid processing duplicate files.
Dependencies: hashlib
"""
import hashlib
import os

def calculate_sha256(file_path: str, chunk_size: int = 8192) -> str:
    """
    Calculates the SHA-256 hash of a file using stream processing.
    
    Args:
        file_path: Path to the file.
        chunk_size: Size of chunks to read into memory (default 8KB).
        
    Returns:
        str: The hexadecimal SHA-256 hash string.
        
    Raises:
        FileNotFoundError: If file does not exist.
        PermissionError: If file is not readable.
    """
    sha256 = hashlib.sha256()
    
    with open(file_path, "rb") as f:
        while chunk := f.read(chunk_size):
            sha256.update(chunk)
            
    return sha256.hexdigest()

if __name__ == "__main__":
    # Example usage
    import sys
    if len(sys.argv) > 1:
        print(f"Hash: {calculate_sha256(sys.argv[1])}")
