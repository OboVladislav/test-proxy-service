ARG PYTHON_IMAGE=mirror.gcr.io/library/python:3.11-slim
FROM ${PYTHON_IMAGE}

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV UV_LINK_MODE=copy

WORKDIR /app

# Устанавливаем uv
RUN pip install --no-cache-dir uv

# Копируем файлы зависимостей
COPY ./pyproject.toml ./uv.lock ./

# Синхронизируем виртуальное окружение (.venv) без установки самого проекта
RUN uv sync --frozen --no-install-project

ENV PATH="/app/.venv/bin:$PATH"

# Копируем остальной код
COPY . .

# Команда по умолчанию для backend
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]