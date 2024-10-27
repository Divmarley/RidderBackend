# Stage 1: Build stage
FROM python:3.10-slim as builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update -y && apt-get install -y \
    pkg-config \
    python3-dev \
    build-essential \
    default-libmysqlclient-dev \
    --no-install-recommends

# Set work directory
WORKDIR /code

# Install Python dependencies
COPY requirements.txt /code/
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Production stage
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /code

# Copy only the necessary libraries from the builder stage
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy project files
COPY . /code/

# Copy the entrypoint script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Install MySQL client (optional if you need it in production)
RUN apt-get update && apt-get install -y default-mysql-client --no-install-recommends

# Expose the port the app runs on
EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]

# Run the application
# CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
