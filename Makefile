include .env

install:
	python3 -m venv $VENV; cd && . ${VENV}/bin/activate && pip install -r requirements.txt

run:
	${PYTHON} run.py

clean:
	rm -rf __pycache__
	rm -rf ${VENV}

upgrade-migrations:
	. ${VENV}/bin/activate && flask db upgrade

