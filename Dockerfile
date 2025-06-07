FROM python:3.13-slim-bookworm

# Встановлення системних залежностей
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Встановлення Poetry
RUN pip install poetry

# Налаштування Poetry
ENV POETRY_NO_INTERACTION=1 \
    POETRY_VENV_IN_PROJECT=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

# Створення робочої директорії
WORKDIR /app

# Копіювання файлів конфігурації Poetry
COPY pyproject.toml poetry.lock* ./

# Встановлення залежностей
RUN poetry install --only=main && rm -rf $POETRY_CACHE_DIR

# Копіювання коду застосунку
COPY . .

# Відкриття порту
EXPOSE 8000

# Запуск застосунку
CMD ["poetry", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]