FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev gcc \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/app /app/app
COPY alembic.ini /app/
COPY migrations /app/migrations

RUN mkdir -p /app/data

EXPOSE $PORT

CMD sh -c "mkdir -p /app/data && alembic upgrade head || true && uvicorn app.main:app --host 0.0.0.0 --port $PORT"
