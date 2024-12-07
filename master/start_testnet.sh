#!/bin/bash

# Остановка контейнеров
#docker stop skrizhal_node_0 skrizhal_node_1 skrizhal_node_2 skrizhal_master
docker-compose down

# Запуск контейнеров
docker-compose up --build --detach

# Запуск консоли управления PKI в отдельной сессии screen
screen -dmS pki docker exec -it skrizhal_master python master/master_pki_management.py

# Инструкция для пользователя
echo "Консоль управления PKI запущена в screen с именем 'pki'."
echo "Для подключения выполните: screen -r pki"
echo "Лог узлов будет выведен ниже."
echo "Чтобы остановить логи, используйте Ctrl+C."

# Логи узлов
docker-compose logs -f --no-log-prefix