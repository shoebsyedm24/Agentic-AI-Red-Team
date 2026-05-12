FROM python:3.12-slim
WORKDIR /app
RUN mkdir -p /app/chromadb
COPY target-rag/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY shared /shared
COPY target-rag/app.py .
EXPOSE 5001
CMD ["python", "app.py"]
