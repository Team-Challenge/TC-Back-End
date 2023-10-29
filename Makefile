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
up:
	docker-compose up

build-up:
	docker-compose up --build 

deploy-up:
	docker-compose -f docker-compose-deploy.yaml up -d

deploy-build-up:
	docker-compose -f docker-compose-deploy.yaml up -d --build

down:
	docker-compose down --remove-orphans

recreate-db-docker:
	docker exec tc-backend bash -c "python ./data/create_db.py" && \
	docker exec tc-backend bash -c "flask db upgrade" && \
	docker exec tc-backend bash -c "python ./data/create_fixtures.py" && \
	echo "DB has been recreated!"
