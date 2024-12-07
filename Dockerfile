# Проект "Скрижаль" — Dockerfile — Подготовка образа для узлов
FROM python:3.11

# Устанавливаем зависимости
RUN apt-get update && apt-get install -y \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Создаем рабочую директорию
WORKDIR /app

# Копируем файлы проекта в контейнер
COPY . /app

# Устанавливаем необходимые Python-пакеты
RUN pip install -r requirements.txt

# Команда по умолчанию для запуска узла
CMD ["python", "run_nodes.py"]

ENV PYTHONPATH "/app"
