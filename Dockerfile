FROM python:3.10-slim

# Environment variables
## Don't write .pyc to disk
ENV PYTHONDONTWRITEBYTECODE=1
## Send stdout/stderr to terminal logs directly
ENV PYTHONUNBUFFERED=1

WORKDIR /test-app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Expose Flask port
EXPOSE 5000

CMD ["python", "run.py"]
