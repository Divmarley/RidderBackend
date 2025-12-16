# Stage 1: Builder
FROM python:3.10-slim as builder

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update -y && apt-get install -y \
    build-essential \
    python3-dev \
    default-libmysqlclient-dev \
    pkg-config \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /code

COPY requirements.txt /code/
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Production
FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=driverapp.settings

WORKDIR /code

RUN apt-get update -y && apt-get install -y \
    netcat-traditional \
    curl \
    default-mysql-client \
    gettext \
 && rm -rf /var/lib/apt/lists/*


RUN apt-get update \
    && apt-get install -y gettext \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

COPY . /code/

COPY entrypoint.sh /code/entrypoint.sh
RUN chmod +x /code/entrypoint.sh

RUN mkdir -p /code/staticfiles /code/media

EXPOSE 8000

ENTRYPOINT ["/code/entrypoint.sh"]
