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

Create the database tables in a python REPL
```python
from currencyexchange import db, create_app
db.create_all(app=create_app()) # pass the create_app result so Flask-SQLAlchemy gets the configuration.
```

Run the flask app
```shell
flask run
```
# Improvements