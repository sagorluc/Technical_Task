# Base image
FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system deps
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && apt-get clean

# Copy only requirements first (caches layer)
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Optional: install test requirements (for running tests)
COPY test_requirements.txt /app/
RUN pip install --no-cache-dir -r test_requirements.txt

# Copy project
COPY . /app/

EXPOSE 8000

# Default command
CMD ["gunicorn", "core.wsgi:application", "--bind", "0.0.0.0:8000"]
