# Проект "Скрижаль" — Файл: master_pki_management.py — Скрипт управления PKI мастер-узлом
# Версия: 2.2.0
# Примечания: Добавлена поддержка JSON CSR, автоматизация обработки запросов.

import os
import json
from crypto_utils import load_private_key, save_private_key, save_public_key, generate_key_pair, sign_message

# Директории для управления PKI
PKI_DIR = "./master/pki"
REQUESTS_DIR = os.path.join(PKI_DIR, "requests")
CERTS_DIR = os.path.join(PKI_DIR, "certs")
REJECTED_DIR = os.path.join(PKI_DIR, "rejected")
PRIVATE_DIR = os.path.join(PKI_DIR, "private")
MASTER_KEY_FILE = os.path.join(PRIVATE_DIR, "master_key.pem")
PUBLIC_KEY_FILE = os.path.join(CERTS_DIR, "master_key_public.pem")

# Создание директорий, если их нет
os.makedirs(REQUESTS_DIR, exist_ok=True)
os.makedirs(CERTS_DIR, exist_ok=True)
os.makedirs(REJECTED_DIR, exist_ok=True)
os.makedirs(PRIVATE_DIR, exist_ok=True)

class MasterPKIManager:
    def __init__(self):
        self.private_key, self.public_key = self.load_or_generate_master_key()

    def load_or_generate_master_key(self):
        if os.path.exists(MASTER_KEY_FILE):
            print("[INFO] Загрузка мастер-ключа с диска...")
            private_key = load_private_key(MASTER_KEY_FILE)
            public_key = private_key.public_key()
        else:
            print("[INFO] Генерация нового мастер-ключа...")
            private_key, public_key = generate_key_pair()
            save_private_key(private_key, MASTER_KEY_FILE)
            save_public_key(public_key, PUBLIC_KEY_FILE)
        return private_key, public_key

    def validate_csr(self, csr_data):
        required_fields = {"node_id", "открытый_ключ", "роли", "группы", "выпущен", "истекает"}
        missing_fields = required_fields - set(csr_data.keys())
        if missing_fields:
            return False, f"Отсутствуют обязательные поля: {', '.join(missing_fields)}"
        return True, None

    def process_requests(self, auto_approve=False):
        print("[INFO] Начало обработки запросов на аттестацию...")
        for request_file in os.listdir(REQUESTS_DIR):
            request_path = os.path.join(REQUESTS_DIR, request_file)
            try:
                with open(request_path, "r", encoding="utf-8") as file:
                    csr_data = json.load(file)
                node_id = csr_data.get("node_id")
                if not node_id:
                    print(f"[ERROR] Файл запроса {request_file} не содержит node_id. Пропуск.")
                    continue

                cert_path = os.path.join(CERTS_DIR, f"{node_id}.json")
                if os.path.exists(cert_path):
                    print(f"[DEBUG] Узел {node_id} уже аттестован. Пропуск.")
                    continue

                # Validate CSR
                is_valid, error_message = self.validate_csr(csr_data)
                if not is_valid:
                    print(f"[ERROR] CSR недействителен: {error_message}")
                    rejected_path = os.path.join(REJECTED_DIR, request_file)
                    os.rename(request_path, rejected_path)
                    continue

                # Automatic or manual approval
                if auto_approve or input(f"Подтвердить аттестацию для узла {node_id}? (y/n): ").lower() == "y":
                    # Create and sign certificate
                    certificate = {**csr_data, "status": "approved"}
                    signature = sign_message(self.private_key, json.dumps(certificate).encode("utf-8"))
                    certificate["подпись"] = signature.hex()

                    with open(cert_path, "w", encoding="utf-8") as cert_file:
                        json.dump(certificate, cert_file, ensure_ascii=False, indent=4)
                    print(f"[INFO] Сертификат узла {node_id} успешно сохранен: {cert_path}")
                else:
                    rejected_path = os.path.join(REJECTED_DIR, request_file)
                    os.rename(request_path, rejected_path)
                    print(f"[INFO] Запрос на аттестацию узла {node_id} отклонён.")
                    continue

                # Remove request after successful processing
                os.remove(request_path)
            except Exception as e:
                print(f"[ERROR] Ошибка обработки файла {request_file}: {e}")

if __name__ == "__main__":
    manager = MasterPKIManager()
    manager.process_requests(auto_approve=True)
