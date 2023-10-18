include .env

## Local installation commands
install:
	. ${VENV}/bin/activate && pip install -r requirements.txt

run:
	${PYTHON} run.py

clean:
	rm -rf __pycache__
	rm -rf ${VENV}

upgrade-migrations:
	. ${VENV}/bin/activate && flask db upgrade

recreate-db-local:
	rm -f data/app.db && \
	${PYTHON} ./data/create_db.py && \
	make upgrade-migrations && \
	${PYTHON} ./data/create_fixtures.py && \
	echo "DB has been recreated. Migrations & Fixtures have been applied!"

## Docker commmands
build-up:
	docker-compose up --build -d backend
up:
	docker-compose up -d backend

down:
	docker-compose down --remove-orphans

recreate-db-docker:
	docker exec tc-backend bash -c "rm -f data/app.db" && \
	docker exec tc-backend bash -c "python ./data/create_db.py" && \
	docker exec tc-backend bash -c "flask db upgrade" && \
	docker exec tc-backend bash -c "python ./data/create_fixtures.py" && \
	echo "DB has been recreated. Migrations & Fixtures have been applied!"
