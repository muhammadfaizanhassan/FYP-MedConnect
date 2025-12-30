"""
Custom encrypted fields for Django models
"""
from django.db import models
from django.core.exceptions import ValidationError
from main.utils.encryption import encrypt_data, decrypt_data

class EncryptedTextField(models.TextField):
    """
    Encrypted text field for storing sensitive data
    Automatically encrypts on save and decrypts on retrieval
    """
    def from_db_value(self, value, expression, connection):
        """Decrypt when reading from database"""
        if value is None:
            return value
        # decrypt_data handles legacy unencrypted data gracefully
        return decrypt_data(value)
    
    def to_python(self, value):
        """Convert to Python string"""
        if isinstance(value, str) or value is None:
            return value
        return str(value)
    
    def get_prep_value(self, value):
        """Encrypt before saving to database"""
        if value is None:
            return value
        if isinstance(value, str) and value.strip():
            # Check if already encrypted - if decryption works and returns different value, it's encrypted
            try:
                decrypted = decrypt_data(value)
                # If decryption returns same value, it wasn't encrypted
                if decrypted != value:
                    return value  # Already encrypted, don't encrypt again
            except:
                pass
            return encrypt_data(value)
        return value

class EncryptedCharField(models.CharField):
    """
    Encrypted char field for storing sensitive data
    Automatically encrypts on save and decrypts on retrieval
    """
    def from_db_value(self, value, expression, connection):
        """Decrypt when reading from database"""
        if value is None:
            return value
        # decrypt_data handles legacy unencrypted data gracefully
        return decrypt_data(value)
    
    def to_python(self, value):
        """Convert to Python string"""
        if isinstance(value, str) or value is None:
            return value
        return str(value)
    
    def get_prep_value(self, value):
        """Encrypt before saving to database"""
        if value is None:
            return value
        if isinstance(value, str) and value.strip():
            # Check if already encrypted (starts with base64-like pattern)
            # If it looks encrypted, don't encrypt again
            try:
                # Try to decrypt it - if it works, it's already encrypted
                from main.utils.encryption import decrypt_data
                decrypted = decrypt_data(value)
                # If decryption returns same value, it wasn't encrypted
                if decrypted != value:
                    return value  # Already encrypted
            except:
                pass
            return encrypt_data(value)
        return value

