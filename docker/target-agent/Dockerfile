FROM python:3.12-slim
RUN apt-get update && apt-get install -y --no-install-recommends bash && rm -rf /var/lib/apt/lists/*
WORKDIR /app
RUN mkdir -p /workspace
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY ../shared /shared
COPY app.py .
EXPOSE 5002
CMD ["python", "app.py"]
