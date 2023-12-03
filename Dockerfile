FROM python:3.11.4-alpine3.18

WORKDIR /app

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY main.py ./

CMD ["python", "./main.py"]