FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY config/ config/
COPY src/ src/
COPY scripts/ scripts/
COPY run_ingestion.py .

CMD ["python", "run_ingestion.py", "--mode", "full"]
