FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python init_db.py

EXPOSE 8001

CMD ["python", "main.py"]
