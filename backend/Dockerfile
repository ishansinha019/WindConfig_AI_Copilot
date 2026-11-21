FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN pip install --no-cache-dir uv

COPY pyproject.toml alembic.ini ./
RUN uv pip install --system "fastapi[standard]>=0.115.0" "pydantic-settings>=2.5.0" "sqlalchemy>=2.0.35" "alembic>=1.13.3" "psycopg[binary]>=3.2.1" "pytest>=8.3.3" "httpx>=0.27.2"

COPY alembic ./alembic
COPY app ./app
COPY tests ./tests
COPY entrypoint.sh ./entrypoint.sh

RUN chmod +x ./entrypoint.sh

EXPOSE 8000

CMD ["./entrypoint.sh"]
