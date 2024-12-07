# Проект "Скрижаль" — Файл: crypto_utils.py — Утилиты для криптографии
# Версия: 1.2
# Примечания: Исправлена обработка байтовых данных в функции `sign_data`.

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import utils
from cryptography.hazmat.backends import default_backend

# Функция для генерации пары ключей RSA
def generate_key_pair():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    public_key = private_key.public_key()
    return private_key, public_key

# Функция для подписи данных
def sign_data(private_key, data):
    if not isinstance(data, bytes):  # Проверяем, являются ли данные байтами
        data = data.encode('utf-8')
    signature = private_key.sign(
        data,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    return signature

# Функция для подписи сообщения (обёртка над sign_data)
def sign_message(private_key, data):
    return sign_data(private_key, data)

# Функция для проверки подписи
def verify_signature(public_key, signature, data):
    try:
        public_key.verify(
            signature,
            data.encode('utf-8'),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return True
    except utils.InvalidSignature:
        return False

# Функция для сохранения закрытого ключа в файл
def save_private_key(private_key, filename):
    pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption()
    )
    with open(filename, 'wb') as key_file:
        key_file.write(pem)

# Функция для загрузки закрытого ключа из файла
def load_private_key(filename):
    with open(filename, 'rb') as key_file:
        private_key = serialization.load_pem_private_key(
            key_file.read(),
            password=None,
            backend=default_backend()
        )
    return private_key

# Функция для сохранения публичного ключа в файл
def save_public_key(public_key, filename):
    pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    with open(filename, 'wb') as key_file:
        key_file.write(pem)

# Функция для загрузки публичного ключа из файла
def load_public_key(filename):
    with open(filename, 'rb') as key_file:
        public_key = serialization.load_pem_public_key(
            key_file.read(),
            backend=default_backend()
        )
    return public_key
