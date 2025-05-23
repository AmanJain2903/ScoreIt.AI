import pytest
from src.utils import security

pytestmark = pytest.mark.unit

@pytest.fixture
def secure_key_manager():
    return security.SecureKeyManager()

@pytest.fixture 
def model_load():
    return model_load.load_models()

def test_initialization(secure_key_manager):
    assert secure_key_manager._key is not None
    assert secure_key_manager._cipher is not None
    assert secure_key_manager._encryptedKey is None

def test_store_key(secure_key_manager):
    secure_key_manager.store_key("test_key")
    assert secure_key_manager._encryptedKey is not None
    with pytest.raises(ValueError, match="Key cannot be empty."):
        secure_key_manager.store_key("")
    with pytest.raises(ValueError, match="Key must be a string."):
        secure_key_manager.store_key(123)

def test_get_key(secure_key_manager):
    secure_key_manager.store_key("test_key")
    decrypted_key = secure_key_manager.get_key()
    assert decrypted_key == "test_key"
    secure_key_manager._encryptedKey = None
    with pytest.raises(ValueError, match="Failed to decrypt key: "):
        secure_key_manager.get_key()

def test_sanitize_input():
    sanitized_input = security.sanitizeInput("<script>alert('test')</script>", 100)
    assert sanitized_input == "&lt;script&gt;alert(&#x27;test&#x27;)&lt;/script&gt;"
    with pytest.raises(ValueError, match="Input exceeds maximum length of 5 characters."):
        security.sanitizeInput("123456", 5)
    with pytest.raises(ValueError, match="Input exceeds maximum length of 5 characters."):
        security.sanitizeInput(b"123456", 5)
    with pytest.raises(ValueError, match="Input must be a string or bytes."):
        security.sanitizeInput(123, 100)

def test_model_load():
    model_load.load_models()
    assert model_load.model1 is not None
    assert model_load.model2 is not None



