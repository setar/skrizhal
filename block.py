# Проект "Скрижаль" — Файл: block.py — Класс Block для блоков криптоцепочки

import time
import hashlib
import json

class Block:
    def __init__(self, index, previous_hash, timestamp, node_id, data):
        self.index = index
        self.previous_hash = previous_hash
        self.timestamp = timestamp
        self.node_id = node_id
        self.data = data
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        """
        Вычисляет хеш текущего блока на основе его содержимого.
        """
        block_string = json.dumps(self.__dict__, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    def to_dict(self):
        """
        Преобразует блок в словарь для удобства сериализации.
        """
        return {
            "index": self.index,
            "previous_hash": self.previous_hash,
            "timestamp": self.timestamp,
            "node_id": self.node_id,
            "data": self.data,
            "hash": self.hash
        }
