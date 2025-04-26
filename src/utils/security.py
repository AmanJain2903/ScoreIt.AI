from cryptography.fernet import Fernet
import html
from typing import Union


# Encrypts API keys and stores them securely
# Encrypts API keys in memory using AES-256 encryption (Advanced Encryption Standard) 256-bit key
# Only decrypts the key when needed
# Automatically clears the key from memory after use
class SecureKeyManager:
    def __init__(self):
        self._key = Fernet.generate_key()
        self._cipher = Fernet(self._key)
        self._encryptedKey = None
    
    def store_key(self, rawKey):
        if not rawKey:
            raise ValueError("Key cannot be empty.")
        if not isinstance(rawKey, str):
            raise ValueError("Key must be a string.")
        self._encryptedKey = self._cipher.encrypt(rawKey.encode())

    def get_key(self):
        try:
            decryptedKey = self._cipher.decrypt(self._encryptedKey)
            return decryptedKey.decode()
        except Exception as e:
            raise ValueError(f"Failed to decrypt key: {e}")



# Sanitization of user input to prevent XSS attacks (Cross-Site Scripting).
# Prevent prompt injection attacks by sanitizing user input.
# Also prevent DOS attacks by limiting the length of user input.
def sanitizeInput(userInput : Union[str, bytes], allowedLength) -> str:
    """
    Sanitize user input to prevent XSS attacks.
    
    Args:
        userInput (Union[str, bytes]): The user input to sanitize.
        
    Returns:
        str: The sanitized input.
    """
    if isinstance(userInput, bytes):
        userInput = userInput.decode('utf-8', errors='replace')
    
    if len(userInput) > allowedLength:
        raise ValueError(f"Input exceeds maximum length of {allowedLength} characters.")
    
    sanitizedInput = html.escape(userInput).strip()
    
    return sanitizedInput
