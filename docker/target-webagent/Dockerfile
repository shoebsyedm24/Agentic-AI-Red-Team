FROM python:3.12-slim
WORKDIR /app
COPY target-webagent/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY shared /shared
COPY target-webagent/app.py .
EXPOSE 5004
CMD ["python", "app.py"]
