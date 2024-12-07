#!/bin/bash
# Проект "Скрижаль" — Файл: make_env.sh — Скрипт для подготовки окружения
# Скрипт для подготовки окружения для запуска протокола "Скрижаль" на основе Linux дистрибутива RedOS (DNF-based)

# Обновление системы и установка необходимых пакетов
sudo dnf update -y

# Установка ZeroMQ и необходимых библиотек для Python
sudo dnf install -y zeromq zeromq-devel

# Установка Python и менеджера пакетов pip
sudo dnf install -y python3 python3-pip

# Установка дополнительных библиотек для работы с криптографией и ZeroMQ
pip3 install pyzmq cryptography

# Установка других полезных утилит для отладки и мониторинга
sudo dnf install -y git vim net-tools

# Установка Docker и Docker Compose
# Установка Docker
sudo dnf install -y dnf-plugins-core
sudo dnf config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
sudo dnf install -y docker-ce docker-ce-cli containerd.io

# Запуск и включение Docker
sudo systemctl enable --now docker

# Установка Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Проверка установки Docker и Docker Compose
docker --version
docker-compose --version

# Клонирование репозитория или создание директории для проекта "Скрижаль"
mkdir -p ~/skrizhal_environment
cd ~/skrizhal_environment

# Создание виртуального окружения Python (опционально)
python3 -m venv venv
source venv/bin/activate

# Установка библиотек в виртуальное окружение
pip install pyzmq cryptography

# Сообщение о завершении установки
echo "Подготовка окружения для проекта Скрижаль завершена."
echo "Нужно добавить пользователя в группу docker `sudo usermod -aG docker s.taranenko` "