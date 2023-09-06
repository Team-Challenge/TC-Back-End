include .env

install:
	. ${VENV}/bin/activate && pip install -r requirements.txt

run:
	${PYTHON} run.py

clean:
	rm -rf __pycache__
	rm -rf ${VENV}

upgrade-migrations:
	. ${VENV}/bin/activate && flask db upgrade

up:
	docker-compose up -d backend

down:
	docker-compose down --remove-orphans
