# Backend service for TeamChallenge Marketplace application

### `Requires Python 3.8 or greater`

## Create virtualenv:
> `python3 -m venv .venv`

## Activate virtual env:
> `source .venv/bin/activate`

## Install dependencies:
> `pip install -r requirements.txt`

## Create `.env`:
> copy `.env_example` as `.env`
>
> set values in `.env`

## Create local database:
> `touch /data/app.db`

## Upgrade DB:
> `flask db upgrade`

## Alternatively use `Makefile` commands

## Git rules
### It is prohibited to push commits directly to the `development` branch.
### Create a Pull Request to merge you branch into the `development`. 
