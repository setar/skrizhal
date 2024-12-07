# Протокол "Скрижаль" — Модуль для работы с блокчейном

import os
import json
from block import Block
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes

class Blockchain:
    def __init__(self, node_id, data_directory):
        self.node_id = node_id
        self.data_directory = data_directory
        self.blockchain = []  # Локальная копия блоков криптоцепочки
        self.load_blockchain_from_disk()

    def create_block(self, data, private_key):
        # Создание нового блока и добавление его в цепочку
        prev_hash = self.blockchain[-1].signature if self.blockchain else "0"
        new_block = Block(
            block_id=len(self.blockchain) + 1,
            prev_hash=prev_hash,
            data=data,
            creator_id=self.node_id
        )
        new_block.sign_block(private_key)
        self.blockchain.append(new_block)
        self.save_blockchain_to_disk()
        return new_block

    def verify_and_add_block(self, block, public_keys):
        # Проверка подписи блока и добавление его в локальную копию цепочки
        block_data = json.dumps(block.to_dict(), sort_keys=True).encode('utf-8')
        try:
            # Получаем публичный ключ создателя блока
            if block.creator_id in public_keys:
                public_key = public_keys[block.creator_id]
                public_key.verify(
                    bytes.fromhex(block.signature),
                    block_data,
                    padding.PSS(
                        mgf=padding.MGF1(hashes.SHA256()),
                        salt_length=padding.PSS.MAX_LENGTH
                    ),
                    hashes.SHA256()
                )
                self.blockchain.append(block)
                self.save_blockchain_to_disk()
                print(f"Узел {self.node_id} успешно верифицировал и добавил блок {block.block_id}")
            else:
                print(f"Узел {self.node_id}: Неизвестный создатель блока {block.creator_id}, верификация невозможна.")
        except Exception as e:
            print(f"Узел {self.node_id} не смог верифицировать блок {block.block_id}: {e}")

    def save_blockchain_to_disk(self):
        # Сохранение цепочки блоков в локальный каталог
        if not os.path.exists(self.data_directory):
            os.makedirs(self.data_directory)
        with open(os.path.join(self.data_directory, "blockchain.json"), "w") as f:
            json.dump([block.to_dict() for block in self.blockchain], f, indent=4)

    def load_blockchain_from_disk(self):
        # Загрузка цепочки блоков из локального каталога
        if os.path.exists(os.path.join(self.data_directory, "blockchain.json")):
            with open(os.path.join(self.data_directory, "blockchain.json"), "r") as f:
                blocks = json.load(f)
                self.blockchain = [Block.from_dict(block) for block in blocks]
            print(f"Узел {self.node_id} загрузил цепочку блоков из файла. Количество блоков: {len(self.blockchain)}")

