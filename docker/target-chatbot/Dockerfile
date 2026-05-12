FROM python:3.12-slim
WORKDIR /app
COPY target-chatbot/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY shared /shared
COPY target-chatbot/app.py .
EXPOSE 5000
CMD ["python", "app.py"]
