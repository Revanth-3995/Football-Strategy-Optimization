FROM python:3.12-slim

WORKDIR /app

COPY backend/requirements.txt /app/backend/requirements.txt
RUN pip install --no-cache-dir -r /app/backend/requirements.txt

# Copy all python packages
COPY backend /app/backend
COPY services /app/services
COPY analytics /app/analytics
COPY ml_models /app/ml_models
COPY reports /app/reports
COPY database /app/database

# Add current directory to PYTHONPATH so it can find all modules
ENV PYTHONPATH=/app

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
