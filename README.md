# Currency Exchange

# Architecture

# Steps to Run
Requirements
1. python 3.8

Install required python libraries
```shell
pip install requirements.txt
```

Create envrionment variables required to run
```shell
export FLASK_APP=currencyexchange
export FLASK_DEBUG=1
export SECRET_KEY=your_secret_key 
```

Create a migration repository. This will add a migrations folder to your application.
```shell
flask db init
```

Generate an initial migration. The migration script needs to be reviewed and edited, as Alembic currently does not detect every change you make to your models. In particular, Alembic is currently unable to detect table name changes, column name changes, or anonymously named constraints. 
```shell
flask db migrate -m "Initial migration."
```

Apply the migration to the database
```shell
flask db upgrade
```

Each time the database models change repeat the migrate and upgrade commands.


Run the flask app
```shell
flask run
```
# Improvements