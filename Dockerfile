FROM python:3.8-slim-buster

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

RUN mv .env_example .env
RUN echo "SQLALCHEMY_DATABASE_URI=/app/data/app.db" >> /app/.env

RUN python data/create_db.py
RUN flask db upgrade
RUN python data/create_fixtures.py

EXPOSE 8080

CMD [ "gunicorn", "-c" , "config/gunicorn.py", "app:app"]
