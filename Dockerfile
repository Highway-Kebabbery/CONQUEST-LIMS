FROM python:3-slim

WORKDIR /test-app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

ENV FLASK_APP=flask-app.py

CMD ["python", "chemical_inventory_api_v1.py", "--host=0.0.0.0"]
