# BASE PYTHON IMAGE
FROM python:3.9-slim

# PYTHON ENV VARIABLES
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# MAKE NEW DIR IN CONTAINER AND USE IT AS WORKING DIR
RUN mkdir /backend
WORKDIR /backend

# INSTALL SYSTEM DEPENDENCIES
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        gettext \
        postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# COPY AND INSTALL REQUIREMENTS FILE
COPY requirements.txt /backend/
RUN pip install -r requirements.txt

COPY . /backend/