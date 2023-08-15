FROM python:3.8-slim-buster

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY . .

RUN python config/create_db.py
RUN flask db upgrade

EXPOSE 8080

CMD [ "gunicorn", "-c" , "config/gunicorn.py", "app:app"]
