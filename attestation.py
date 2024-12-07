# Проект "Скрижаль" — Файл: attestation.py — Модуль для аттестации узлов

import zmq
import json

class AttestationManager:
    def __init__(self, context, attestation_port):
        self.context = context
        self.attestation_port = attestation_port

    def process_attestations(self):
        # Сокет ROUTER для обработки запросов на аттестацию
        socket = self.context.socket(zmq.ROUTER)
        socket.bind(f"tcp://*:{self.attestation_port}")
        print(f"Аттестационный менеджер слушает на порту {self.attestation_port}")
        
        while True:
            try:
                # Получаем сообщение в формате [identity, request]
                message = socket.recv_multipart()
                identity, request = message[0], message[1]
                request_data = json.loads(request.decode('utf-8'))
                print(f"Получен запрос на аттестацию от узла {request_data['node_id']}")
                
                # Формируем ответ
                response_data = {
                    "status": "approved",
                    "node_id": request_data["node_id"]
                }
                response = json.dumps(response_data)
                socket.send_multipart([identity, response.encode('utf-8')])
                print(f"Отправлен ответ на аттестацию узлу {request_data['node_id']}")
            except zmq.error.ZMQError as e:
                print(f"Ошибка при обработке аттестационного запроса: {e}")

