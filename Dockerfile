FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "main_day3_day4:app", "--host", "0.0.0.0", "--port", "8000"]
EXPOSE 8000