# Base image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       build-essential \
       libpq-dev \
       nginx \
       curl \
       supervisor \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . /app/

# Collect static files
RUN python manage.py collectstatic --noinput

# Optionally set ownership to www-data (nginx user)
RUN chown -R www-data:www-data /app/sqlite_media /app/static

# Copy nginx config
COPY ./deploy/nginx.conf /etc/nginx/sites-available/default

# Copy supervisor config
COPY ./deploy/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Expose port
EXPOSE 8000

# Start supervisor (runs gunicorn + nginx)
CMD ["/usr/bin/supervisord"]
#docker build -t diginnocent .
#docker run -d -p 80:80 diginnocent
