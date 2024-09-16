import pytest
import random
import os

from flask_login.test_client import FlaskLoginClient

from bills_collector.app import create_app
from bills_collector.extensions import db, bcrypt
from bills_collector.models import User

@pytest.fixture()
def app(default_user_payload):

    os.environ['CONFIG_TYPE'] = 'bills_collector.config.TestingConfig'

    app = create_app()
    app.config.update({
        "TESTING": True,
    })

    # other setup can go here
    app.test_client_class = FlaskLoginClient

    with app.app_context():
        db.create_all()

        pass_hash = bcrypt.generate_password_hash(default_user_payload['password'])
        test_user = User(name=default_user_payload['name'], email=default_user_payload['email'], password=pass_hash)

        db.session.add(test_user)

        # Commit the changes for the users
        db.session.commit()

        yield app

        # Close the database session and drop all tables after the session
        db.session.remove()
        db.drop_all()

@pytest.fixture()
def test_client(app):
    return app.test_client()

@pytest.fixture(scope='function')
def log_in_default_user(test_client, default_user_payload):
    test_client.post('/login',
                     data={'email': default_user_payload['email'], 'password': default_user_payload['password']})

    yield  # this is where the testing happens!

    test_client.get('/logout')


@pytest.fixture()
def runner(app):
    return app.test_cli_runner()

@pytest.fixture
def new_user_payload():
    suffix = random.randint(1, 100)
    return {
        "name": f"John Doe {suffix}",
        "email": f"john_{suffix}@doe.com",
        "password": f"abcqwe_{suffix}"
    }

@pytest.fixture(scope='session')
def default_user_payload():
    return {
        "name": "Somebody Kumar",
        "email": 'somebody@kumar.inc',
        "password": 'someP@ssW0rd'
    }

@pytest.fixture(autouse=True)
def run_before_and_after_tests(test_client):
    """Fixture to execute asserts before and after a test is run"""
    # Setup: fill with any logic you want

    yield # this is where the testing happens

    # Teardown : fill with any logic you want
    #test_client.cookie_jar.clear()
