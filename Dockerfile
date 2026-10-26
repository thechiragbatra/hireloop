FROM python:3.12-slim

WORKDIR /app

# Install system dependencies for psycopg2
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY app /app/app
COPY alembic.ini /app/
COPY migrations /app/migrations

EXPOSE 8000

# Run migrations then start server
CMD sh -c "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT"
