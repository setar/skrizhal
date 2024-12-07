# Проект "Скрижаль" — Файл: node.py — Реализация узла сети
# Версия: 2.5.0
# Примечания: Добавлена генерация CSR и проверка подписанных сертификатов.

import zmq
import os
import json
import time
import threading
from configparser import ConfigParser
from hashlib import sha256
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from datetime import datetime, timedelta

# Версия текущего файла
NODE_VERSION = "2.5.0"

# Загрузка конфигурации
config = ConfigParser()
config.read('config.ini')

# Константы, загружаемые из конфигурационного файла
COMMAND_PORT_BASE = config.getint('Ports', 'command_port_base', fallback=8000)
PUB_PORT_BASE = config.getint('Ports', 'pub_port_base', fallback=9000)
ATTESTATION_PORT = config.getint('Ports', 'attestation_port', fallback=7100)
CONTROLLER_HOST = os.getenv('CONTROLLER_HOST', 'controller_node')

DATA_DIR = "./data"
os.makedirs(DATA_DIR, exist_ok=True)

def hash_id_to_port(base_port, node_id):
    hashed = sha256(node_id.encode('utf-8')).hexdigest()
    return base_port + int(hashed[:6], 16) % 1000

def generate_csr(node_id, roles, groups, validity_years=4):
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public_key = private_key.public_key()

    # Serialize keys
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption()
    )
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    # Generate validity dates
    issued = datetime.now().strftime("%d.%m.%Y %H:%M")
    expires = (datetime.now() + timedelta(days=365 * validity_years)).strftime("%d.%m.%Y %H:%M")

    csr_data = {
        "node_id": node_id,
        "открытый_ключ": public_pem.decode("utf-8"),
        "роли": roles,
        "группы": groups,
        "выпущен": issued,
        "истекает": expires
    }

    return private_pem.decode("utf-8"), json.dumps(csr_data, ensure_ascii=False, indent=4)

class Node:
    def __init__(self, node_id=None, group_ids=None, is_controller=False):
        env_node_id = os.getenv('NODE_ID')
        is_master = env_node_id == "controller_node"

        if is_master:
            print("[INFO] Узел запущен в режиме контроллера")
            self.node_id = "controller_node"
        else:
            self.node_id = node_id or env_node_id
            if not self.node_id:
                raise ValueError("Не удалось определить NODE_ID для узла")

        print(f"[DEBUG] Режим: {'Контроллер' if is_master else 'Обычный узел'}, NODE_ID: {self.node_id}")
        self.group_ids = group_ids if group_ids is not None else []
        self.is_controller = is_controller

        self.command_port = hash_id_to_port(COMMAND_PORT_BASE, self.node_id)
        self.pubsub_port = hash_id_to_port(PUB_PORT_BASE, self.node_id)
        self.attestation_port = ATTESTATION_PORT
        self.controller_address = f"tcp://{CONTROLLER_HOST}:{self.attestation_port}"
        print(f"[DEBUG] Адрес контроллера: {self.controller_address}")

        self.data_directory = os.path.join(DATA_DIR, f"node_{self.node_id}")
        self.certs_directory = os.path.join(self.data_directory, "certs")
        self.private_directory = os.path.join(self.data_directory, "private")
        self.csr_path = os.path.join(self.data_directory, "csr.json")
        os.makedirs(self.data_directory, exist_ok=True)
        os.makedirs(self.certs_directory, exist_ok=True)
        os.makedirs(self.private_directory, exist_ok=True)

        self.context = zmq.Context()

    def start(self):
        print(f"[INFO] Узел {self.node_id} запускается с версией кода: {NODE_VERSION}")

        dealer_socket = self.context.socket(zmq.DEALER)
        dealer_socket.bind(f"tcp://*:{self.command_port}")
        print(f"Узел {self.node_id} слушает команды на порту {self.command_port}")

        pub_socket = self.context.socket(zmq.PUB)
        pub_socket.bind(f"tcp://*:{self.pubsub_port}")
        print(f"Узел {self.node_id} публикует данные на порту {self.pubsub_port}")

        threading.Thread(target=self.process_commands, args=(dealer_socket,)).start()
        threading.Thread(target=self.publish_data, args=(pub_socket,)).start()

        if self.node_id != "controller_node":
            threading.Thread(target=self.request_attestation).start()

    def process_commands(self, dealer_socket):
        print(f"Узел {self.node_id} начал обработку команд...")
        while True:
            try:
                message = dealer_socket.recv_json(flags=zmq.NOBLOCK)
                print(f"Узел {self.node_id} получил команду: {message}")
                dealer_socket.send_json({"status": "success", "node_id": self.node_id})
            except zmq.Again:
                time.sleep(1)

    def publish_data(self, pub_socket):
        print(f"Узел {self.node_id} начал публикацию данных...")
        while True:
            data = {"node_id": self.node_id, "status": "active"}
            pub_socket.send_json(data)
            print(f"Узел {self.node_id} публикует данные: {data}")
            time.sleep(5)

    def request_attestation(self):
        if not os.path.exists(self.csr_path):
            print(f"[INFO] Генерация CSR для узла {self.node_id}...")
            private_key, csr = generate_csr(
                self.node_id, "узел", ",".join(map(str, self.group_ids))
            )
            with open(self.csr_path, "w", encoding="utf-8") as csr_file:
                csr_file.write(csr)
            with open(os.path.join(self.private_directory, "private_key.pem"), "w", encoding="utf-8") as key_file:
                key_file.write(private_key)

        print(f"[DEBUG] Узел {self.node_id} отправляет CSR на аттестацию к контроллеру")
        socket = self.context.socket(zmq.REQ)
        socket.connect(self.controller_address)

        with open(self.csr_path, "r", encoding="utf-8") as csr_file:
            csr_data = json.load(csr_file)
        request = {"node_id": self.node_id, "action": "attestation_request", "csr": csr_data}
        socket.send_json(request)

        while True:
            try:
                if socket.poll(timeout=1000, flags=zmq.POLLIN):
                    response = socket.recv_json(flags=zmq.NOBLOCK)
                    if response.get("status") == "approved":
                        print(f"Узел {self.node_id} получил аттестацию.")
                        signed_csr_path = os.path.join(self.certs_directory, "node_cert.json")
                        with open(signed_csr_path, "w", encoding="utf-8") as cert_file:
                            json.dump(response, cert_file, ensure_ascii=False, indent=4)
                        break
                    elif response.get("status") == "rejected":
                        print(f"Аттестация узла {self.node_id} отклонена.")
                        break
                else:
                    print(f"Ожидание ответа от контроллера для узла {self.node_id}...")
                    time.sleep(5)
            except zmq.ZMQError as e:
                if e.errno == zmq.EAGAIN:
                    print("Сокет не готов к чтению, повторная попытка...")
                else:
                    print(f"Ошибка при чтении сокета: {e}")

if __name__ == "__main__":
    node = Node(node_id="test_node", group_ids=[1], is_controller=False)
    node.start()
