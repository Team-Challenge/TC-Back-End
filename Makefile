include .env

UNAME_M := $(shell uname -m)

## Local installation commands
install:
	pip install -r requirements/requirements.txt

run:
	${PYTHON} run.py

clean:
	rm -rf __pycache__

upgrade-migrations:
	flask db upgrade

recreate-db-local:
	rm -f data/app.db && \
	${PYTHON} ./data/create_db.py && \
	make upgrade-migrations && \
	${PYTHON} ./data/create_fixtures.py && \
	echo "DB has been recreated. Migrations & Fixtures have been applied!"

prospector:
	prospector --profile=config/prospector.yaml

## Docker commmands
up:
ifeq ($(UNAME_M),x86_64)
	docker-compose -f docker/docker-compose.yaml up --build
else ifeq ($(UNAME_M),arm64)
	docker-compose -f docker/docker-compose-arm.yaml up --build
else
	echo "$(UNAME_M) is not supported"
endif

down:
ifeq ($(UNAME_M),x86_64)
	docker-compose -f docker/docker-compose.yaml down --remove-orphans
else ifeq ($(UNAME_M),arm64)
	docker-compose -f docker/docker-compose-arm.yaml down --remove-orphans
else
	echo "$(UNAME_M) is not supported"
endif

## Docker commans on deployment server
deploy-up:
	docker-compose -f docker/docker-compose-deploy.yaml up -d

deploy-build-up:
	docker-compose -f docker/docker-compose-deploy.yaml up -d --build

deploy-down:
	docker-compose -f docker/docker-compose-deploy.yaml down --remove-orphans

recreate-db-docker:
	docker exec tc-backend bash -c "python ./data/create_db.py" && \
	docker exec tc-backend bash -c "flask db upgrade" && \
	docker exec tc-backend bash -c "python ./data/create_fixtures.py" && \
	echo "DB has been recreated!"
