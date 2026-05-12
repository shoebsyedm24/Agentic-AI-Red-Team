FROM python:3.12-slim
WORKDIR /app
COPY target-multiagent/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY shared /shared
COPY target-multiagent/app.py .
EXPOSE 5003
CMD ["python", "app.py"]
