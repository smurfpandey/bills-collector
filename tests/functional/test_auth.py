"""
This file (test_auth.py) contains the functional tests for the `auth` blueprint.

These tests use GETs and POSTs to different URLs to check for the proper behavior
of the `auth` blueprint.
"""
import bills_collector.routes.auth
from bills_collector.extensions import bcrypt
from bills_collector.models import User


def test_login_page(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/login' page is requested (GET)
    THEN check the response is valid
    """
    response = test_client.get('/login')
    assert response.status_code == 200
    assert b'Sign in to your account' in response.data
    assert b'Your email' in response.data
    assert b'Password' in response.data

def test_login_page_already_logged_in(test_client, log_in_default_user):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/login' page is requested (GET)
    THEN check the response is valid
    """
    response = test_client.get('/login', follow_redirects=True)
    assert response.status_code == 200
    assert response.request.path == '/'
    assert b'Somebody Kumar' in response.data
    assert b'Connected Accounts' in response.data
    assert b'Sign in to your account' not in response.data

def test_signup_page(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/signup' page is requested (GET)
    THEN check the response is valid
    """
    response = test_client.get('/signup')
    assert response.status_code == 200
    assert b'Create your account' in response.data
    assert b'Your name' in response.data
    assert b'Your email' in response.data
    assert b'Password' in response.data
    assert b'Create Account' in response.data

def test_signup_page_already_logged_in(test_client, log_in_default_user):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/signup' page is requested (GET)
    THEN check the response is valid
    """
    response = test_client.get('/signup', follow_redirects=True)

    assert response.status_code == 200
    assert response.request.path == '/'
    assert b'Somebody Kumar' in response.data
    assert b'Connected Accounts' in response.data
    assert b'Create your account' not in response.data

def test_valid_login_without_remember(test_client, default_user_payload, mocker):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/login' page is posted to (POST)
    THEN check the response is valid
    """

    login_spy = mocker.spy(bills_collector.routes.auth, 'login_user')

    response = test_client.post('/login',
                                data=dict(email=default_user_payload['email'], password=default_user_payload['password']),
                                follow_redirects=True)

    existing_user = User.query.filter_by(email=default_user_payload['email']).first()
    login_spy.assert_called_once_with(existing_user, remember=False)

    assert response.status_code == 200
    assert response.request.path == '/'
    assert default_user_payload['name'].encode() in response.data
    assert b'Connected Accounts' in response.data
    assert b'Sign in to your account' not in response.data

def test_valid_login_with_remember(test_client, default_user_payload, mocker):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/login' page is posted to with remember flag (POST)
    THEN check the response is valid
    """

    login_spy = mocker.spy(bills_collector.routes.auth, 'login_user')

    response = test_client.post('/login',
                                data=dict(email=default_user_payload['email'], password=default_user_payload['password'],
                                           remember='remember_true'),
                                follow_redirects=True)

    assert response.status_code == 200
    assert response.request.path == '/'

    # check for remember cookie in the cookie jar
    # cookies = response.headers.getlist('Set-Cookie')
    # print(cookies)
    # remember_cookie = next(
    #     (cookie for cookie in cookies if 'remember_token' in cookie),
    #     None
    # )
    # assert remember_cookie is not None
    existing_user = User.query.filter_by(email=default_user_payload['email']).first()

    login_spy.assert_called_once_with(existing_user, remember=True)

    assert default_user_payload['name'].encode() in response.data
    assert b'Connected Accounts' in response.data
    assert b'Sign in to your account' not in response.data

def test_invalid_login_wrong_email(test_client, default_user_payload, mocker):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/login' page is posted to with wrong email (POST)
    THEN check the response is valid
    """

    login_spy = mocker.spy(bills_collector.routes.auth, 'login_user')
    check_hash_spy = mocker.spy(bcrypt, 'check_password_hash')

    response = test_client.post('/login',
                                data=dict(email='invalid_user@somewhere.com', password=default_user_payload['password']),
                                follow_redirects=True)

    assert check_hash_spy.call_count == 0
    assert login_spy.call_count == 0

    assert response.request.path == '/login'
    # assert b'Email and Password did not match' in response.data

def test_invalid_login_wrong_password(test_client, default_user_payload, mocker):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/login' page is posted to with wrong password (POST)
    THEN check the response is valid
    """

    login_spy = mocker.spy(bills_collector.routes.auth, 'login_user')
    check_hash_spy = mocker.spy(bcrypt, 'check_password_hash')

    response = test_client.post('/login',
                                data=dict(email=default_user_payload['email'], password='wrong_password'),
                                follow_redirects=True)

    assert check_hash_spy.call_count == 1
    assert login_spy.call_count == 0

    assert response.request.path == '/login'

def test_login_with_existing_session(test_client, default_user_payload, mocker, log_in_default_user):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/login' page is posted to with wrong password (POST)
    THEN check the response is valid
    """

    login_spy = mocker.spy(bills_collector.routes.auth, 'login_user')
    check_hash_spy = mocker.spy(bcrypt, 'check_password_hash')

    response = test_client.post('/login',
                                data=dict(email=default_user_payload['email'], password='wrong_password'),
                                follow_redirects=True)

    assert check_hash_spy.call_count == 0
    assert login_spy.call_count == 0

    assert response.request.path == '/'

def test_signup_existing_user(test_client, default_user_payload, mocker):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/login' page is posted to with wrong password (POST)
    THEN check the response is valid
    """

    gen_hash_spy = mocker.spy(bcrypt, 'generate_password_hash')

    response = test_client.post('/signup',
                                data=dict(email=default_user_payload['email'], name=default_user_payload['name'], password=default_user_payload['password']),
                                follow_redirects=True)

    assert response.request.path == '/signup'
    assert gen_hash_spy.call_count == 0

def test_valid_signup(test_client, new_user_payload, mocker):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/login' page is posted to with wrong password (POST)
    THEN check the response is valid
    """

    gen_hash_spy = mocker.spy(bcrypt, 'generate_password_hash')

    response = test_client.post('/signup',
                                data=dict(email=new_user_payload['email'], name=new_user_payload['name'], password=new_user_payload['password']),
                                follow_redirects=True)

    assert response.request.path == '/login'
    gen_hash_spy.assert_called_once_with(new_user_payload['password'])


    new_user = User.query.filter_by(email=new_user_payload['email']).first()

    assert new_user is not None
    assert new_user.id is not None

    # Asset new this user can login
    login_spy = mocker.spy(bills_collector.routes.auth, 'login_user')

    response = test_client.post('/login',
                                data=dict(email=new_user_payload['email'], password=new_user_payload['password']),
                                follow_redirects=True)

    assert response.status_code == 200
    assert response.request.path == '/'
    login_spy.assert_called_once_with(new_user, remember=False)

    assert new_user_payload['name'].encode() in response.data
    assert b'Connected Accounts' in response.data
    assert b'Sign in to your account' not in response.data
