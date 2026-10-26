FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev gcc \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/app /app/app
COPY backend/alembic.ini /app/
COPY backend/migrations /app/migrations

RUN mkdir -p /app/data

EXPOSE $PORT

CMD sh -c "alembic upgrade head || true && uvicorn app.main:app --host 0.0.0.0 --port $PORT"
