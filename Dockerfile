# Stage 1: Builder
FROM python:3.10-slim as builder

# Environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install build dependencies
RUN apt-get update -y && apt-get install -y \
    build-essential \
    python3-dev \
    default-libmysqlclient-dev \
    pkg-config \
    --no-install-recommends \
 && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /code

# Install Python dependencies
COPY requirements.txt /code/
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Production
FROM python:3.10-slim

# Environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=driverapp.settings

# Set work directory
WORKDIR /code

# Install runtime dependencies
RUN apt-get update -y && apt-get install -y \
    netcat-traditional \
    curl \
    default-mysql-client \
    --no-install-recommends \
 && rm -rf /var/lib/apt/lists/*

# Copy Python packages from builder stage
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy project files
COPY . /code/

# Copy and set permissions for entrypoint
COPY entrypoint.sh /code/entrypoint.sh
RUN chmod +x /code/entrypoint.sh

# Create necessary directories
RUN mkdir -p /code/staticfiles /code/media

# Expose Daphne port
EXPOSE 8000

# Entrypoint
ENTRYPOINT ["/code/entrypoint.sh"]
