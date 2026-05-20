FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY krasok_bot/ ./krasok_bot/

CMD ["python", "krasok_bot/main.py"]
