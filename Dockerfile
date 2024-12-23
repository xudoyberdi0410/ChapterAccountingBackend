FROM python:3.12-slim

# Отключение буферизации вывода
ENV PYTHONUNBUFFERED=1

# Установка рабочего каталога
WORKDIR /app

# Копирование зависимостей и установка
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Установка Gunicorn
RUN pip install gunicorn

# Копирование приложения
COPY . .

# Команда запуска Gunicorn
CMD ["sh", "-c", "alembic upgrade head && gunicorn -b 0.0.0.0:8000 run:app"]