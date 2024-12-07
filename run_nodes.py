# Проект "Скрижаль" — Файл: run_nodes.py — Основной скрипт для запуска узлов сети и тестирования
# Версия: 2.1.1
# Примечания: Узлы начинают работу только после успешной аттестации.

import os
import time
import threading
import zmq
import json
from node import Node

def request_attestation(node, context, attestation_endpoint):
    """Функция для отправки запроса на аттестацию узла."""
    print(f"[INFO] Узел {node.node_id} отправляет запрос на аттестацию на адрес {attestation_endpoint}")
    socket = context.socket(zmq.REQ)
    socket.connect(attestation_endpoint)

    if not os.path.exists(node.csr_path):
        print(f"[ERROR] CSR для узла {node.node_id} отсутствует. Пропуск.")
        return False

    with open(node.csr_path, "r", encoding="utf-8") as csr_file:
        csr_data = csr_file.read()

    socket.send_json({"node_id": node.node_id, "action": "attestation_request", "csr": csr_data})

    while not os.path.exists(os.path.join(node.certs_directory, f"{node.node_id}_cert.json")):
        print(f"Ожидание подтверждения от контроллера для узла {node.node_id}...")
        try:
            response = socket.recv_json(flags=zmq.NOBLOCK)
            if response.get("status") == "approved":
                print(f"[INFO] Узел {node.node_id} получил аттестацию.")
                cert_path = os.path.join(node.certs_directory, f"{node.node_id}_cert.json")
                with open(cert_path, "w", encoding="utf-8") as cert_file:
                    cert_file.write(json.dumps(response, ensure_ascii=False, indent=4))
                return True
            elif response.get("status") == "rejected":
                print(f"[INFO] Аттестация узла {node.node_id} отклонена.")
                return False
        except zmq.Again:
            time.sleep(5)
    return True

if __name__ == "__main__":
    context = zmq.Context()

    controller_node_address = os.getenv("CONTROLLER_HOST", "controller_node")
    controller_node_port = os.getenv("CONTROLLER_PORT", "7100")
    attestation_endpoint = f"tcp://{controller_node_address}:{controller_node_port}"

    threads = []

    # Запуск контроллера
    controller_node = Node(group_ids=[1], is_controller=True)
    if request_attestation(controller_node, context, attestation_endpoint):
        controller_thread = threading.Thread(target=controller_node.start)
        threads.append(controller_thread)
        controller_thread.start()
        print(f"[INFO] Контроллер {controller_node.node_id} успешно запущен.")

    # Запуск рядовых узлов
    simple_nodes = []
    for i in range(1, 3):
        simple_node = Node(group_ids=[1])
        if request_attestation(simple_node, context, attestation_endpoint):
            simple_node_thread = threading.Thread(target=simple_node.start)
            threads.append(simple_node_thread)
            simple_node_thread.start()
            simple_nodes.append(simple_node)
            print(f"[INFO] Узел {simple_node.node_id} успешно аттестован и запущен.")

    # Наблюдение за узлами
    while True:
        time.sleep(10)
        for node in simple_nodes:
            print(f"Узел {node.node_id} публикует данные: {node.get_status()}")
