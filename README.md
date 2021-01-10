
title: "Account Service Management with Flask (flask_restx/restplus), SQLalchemy, Postgres and Docker. Unit tests with Pytest



To start the Flask app

docker-compose up --build

# In a new terminal
virtualenv .venv
source .venv/bin/activate
pip install -r requirements.txt
# To load env variables
export $(xargs < database.conf)
export FLASK_APP=src/example/app.py
flask run
# Running on http://127.0.0.1:5000

To try the unit tests, change to directory source_code/src/example/tests/test_endpoints.py and run

python3 test_endpoints.py


The Swagger documentation is available on http://localhost:5000/ 

Limitations:
3rd parties API: OpenIBAN
https://openiban.com/ - only validates Bank IBANs for the following countries:
    Belgium
    Germany
    Netherlands
    Luxembourg
    Switzerland
    Austria
    Liechtenstein

