# python 3.12 image
FROM python:3.12-slim

# environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# work directory
WORKDIR /app

# install system dependencies
RUN apt-get update && \
    apt-get install -y build-essential libpq-dev curl && \
    rm -rf /var/lib/apt/lists/*

# copy requirements
COPY requirements.txt .

# install python dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# copy project
COPY . .

# collect static files
RUN python manage.py collectstatic --noinput

# expose port 8000
EXPOSE 8000

# run server
CMD ["gunicorn", "marketlink.wsgi:application", "--bind", "0.0.0.0:8000"]
