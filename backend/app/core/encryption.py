from cryptography.fernet import Fernet
from app.core.config import settings

fernet = Fernet(settings.ENCRYPTION_KEY.encode())

def encrypt_token(token: str) -> str:
    return fernet.encrypt(token.encode()).decode()

def decrypt_token(encrypted: str) -> str:
    return fernet.decrypt(encrypted.encode()).decode()