# 1. Берем легкий Python 3.10
FROM python:3.10-slim

# 2. Устанавливаем системные библиотеки (нужны для psutil и postgres)
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 3. Создаем рабочую папку
WORKDIR /app

# 4. Копируем список библиотек и устанавливаем их
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Копируем весь наш код внутрь контейнера
COPY . .

# 6. Команда запуска
CMD ["python", "-m", "app.main"]