FROM python:3.9-slim
WORKDIR /app
ENV AZURE_CONNECTION_STRING=os.getenv("AZURE_CONNECTION_STRING")
COPY ../Backend/training_pipeline/ .
COPY requirements.txt .
COPY ../Backend/Serving-Backend/src/DB/ ./DB
RUN pip install -r requirements.txt
CMD ["python", "scripts/train.py"]