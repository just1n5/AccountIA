# ================================
# AccountIA Backend - Multi-stage Dockerfile
# ================================

# Base Python image
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    DJANGO_SETTINGS_MODULE=config.settings.development

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
        curl \
        netcat-openbsd \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# ================================
# Development Stage
# ================================
FROM base as development

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Create directories for static and media files
RUN mkdir -p /app/staticfiles /app/media

# Expose port
EXPOSE 8000

# Command for development
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

# ================================
# Production Stage
# ================================
FROM base as production

# Create non-root user
RUN groupadd -r accountia && useradd -r -g accountia accountia

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir gunicorn

# Copy project
COPY . .

# Create directories and set permissions
RUN mkdir -p /app/staticfiles /app/media \
    && chown -R accountia:accountia /app

# Collect static files
RUN python manage.py collectstatic --noinput --clear

# Switch to non-root user
USER accountia

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health/ || exit 1

# Command for production
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "config.wsgi:application"]