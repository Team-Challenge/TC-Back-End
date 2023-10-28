FROM python:3.10-slim-buster

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

RUN python data/create_db.py
RUN flask db upgrade
RUN python data/create_fixtures.py

EXPOSE 8080

CMD [ "flask", "run" , "--host", "0.0.0.0", "--port", "8080"]
