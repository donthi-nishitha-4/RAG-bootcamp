FROM python:3.11-slim

# Install system dependencies for psycopg2 and PDF processing
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Set environment variables defaults
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV DB_HOST=db
ENV DB_PORT=5432

# Default command (can be overridden in docker-compose)
CMD ["python", "scripts/run_experiments.py"]
