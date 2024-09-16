"""
This file (test_models.py) contains the unit tests for the models.py file.
"""

from bills_collector.models import User

def test_new_user(new_user_payload):
    """
    GIVEN a User model
    WHEN a new User is created
    THEN check the email, password_hashed, authenticated, and active fields are defined correctly
    """

    new_user = User(
            email=new_user_payload['email'],
            name=new_user_payload['name'],
            password=new_user_payload['password']
        )

    assert new_user.__repr__() == f"<User: {new_user_payload['name']}>"
    assert new_user.email == new_user_payload['email']
