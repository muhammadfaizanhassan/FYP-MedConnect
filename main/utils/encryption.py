"""
Encryption utilities for HIPAA-compliant data handling
Uses Fernet (symmetric encryption) for encrypting sensitive patient data
"""
import os
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from django.conf import settings

def derive_key_from_password(password: str, salt: bytes = None) -> bytes:
    """
    Derive a Fernet-compatible key from a password using PBKDF2.
    
    Args:
        password: Password string to derive key from
        salt: Optional salt (defaults to b'medconnect_salt')
        
    Returns:
        Base64-encoded key suitable for Fernet
    """
    if salt is None:
        salt = b'medconnect_salt_2024'  # Fixed salt for consistency
    
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,  # High iteration count for security
    )
    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    return key

# Generate or retrieve encryption key
def get_encryption_key():
    """
    Get or generate encryption key from settings or environment variable.
    In production, this should be stored in environment variables.
    """
    key = getattr(settings, 'ENCRYPTION_KEY', None)
    
    if not key:
        # Try to get from environment variable
        key = os.environ.get('MEDCONNECT_ENCRYPTION_KEY')
    
    if not key:
        # Default to deriving key from "medconnect" password
        key = derive_key_from_password("medconnect")
        # Store in settings for this session
        settings.ENCRYPTION_KEY = key
    else:
        # If key is a simple string (like "medconnect"), derive proper key from it
        if isinstance(key, str) and len(key) < 44:  # Fernet keys are 44 chars when base64
            key = derive_key_from_password(key)
        elif isinstance(key, str):
            # Already a proper base64 key, just encode to bytes
            key = key.encode()
    
    # Ensure key is bytes
    if isinstance(key, bytes):
        return key
    elif isinstance(key, str):
        return key.encode()
    
    return key

def get_cipher():
    """Get Fernet cipher instance for encryption/decryption"""
    key = get_encryption_key()
    return Fernet(key)

def encrypt_data(data):
    """
    Encrypt sensitive data using Fernet symmetric encryption.
    
    Args:
        data: String or bytes to encrypt
        
    Returns:
        Encrypted string (base64 encoded)
    """
    if not data:
        return None
    
    try:
        cipher = get_cipher()
        # Convert to bytes if string
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        encrypted = cipher.encrypt(data)
        # Return base64 encoded string for database storage
        return base64.b64encode(encrypted).decode('utf-8')
    except Exception as e:
        # Log error in production
        print(f"Encryption error: {e}")
        raise

def decrypt_data(encrypted_data):
    """
    Decrypt sensitive data.
    Handles both encrypted and legacy unencrypted data gracefully.
    
    Args:
        encrypted_data: Base64 encoded encrypted string or plain text
        
    Returns:
        Decrypted string or original string if decryption fails (legacy data)
    """
    if not encrypted_data:
        return None
    
    # Check if data looks like encrypted data (base64 encoded Fernet token)
    # Fernet tokens are always base64-encoded and have a specific structure
    try:
        # Try to decode as base64 first
        try:
            decoded = base64.b64decode(encrypted_data.encode('utf-8'), validate=True)
            # If it's valid base64, try to decrypt
            cipher = get_cipher()
            decrypted = cipher.decrypt(decoded)
            return decrypted.decode('utf-8')
        except (ValueError, TypeError):
            # Not valid base64 - likely legacy unencrypted data
            # Silently return original data (no error logging for legacy data)
            return encrypted_data
        except Exception:
            # Decryption failed - likely legacy unencrypted data
            # Silently return original data (no error logging for legacy data)
            return encrypted_data
    except Exception:
        # Any other error - return original data (legacy unencrypted)
        # Silently return original data (no error logging for legacy data)
        return encrypted_data

def hash_sensitive_data(data):
    """
    Hash sensitive data for one-way encryption (e.g., for search/indexing).
    Uses SHA-256 for secure hashing.
    """
    if not data:
        return None
    
    from hashlib import sha256
    if isinstance(data, str):
        data = data.encode('utf-8')
    
    return sha256(data).hexdigest()

