FROM python:3.12.11-slim

WORKDIR /app

# Install system dependencies first
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

COPY torch-requirements.txt ./
COPY requirements.txt ./
RUN pip install --upgrade pip && pip install -r torch-requirements.txt && pip install -r requirements.txt \
    && apt-get purge -y build-essential libpq-dev \
    && apt-get autoremove -y \
    && rm -rf /root/.cache

COPY . .

CMD ["python", "app.py"]
