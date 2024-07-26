"""Routes for user authentication."""
from datetime import datetime, timezone

from flask import redirect, Blueprint, url_for, render_template, request
from flask_login import current_user, login_user, logout_user

from bills_collector.models import User
from bills_collector.extensions import db, login_manager, bcrypt

# Blueprint Configuration
auth_bp = Blueprint(
    'auth_bp', __name__
)

login_manager.login_view = "auth_bp.login"

@login_manager.user_loader
def load_user(user_id):
    """Check if user is logged-in upon page load."""
    if (user_id is not None) and (user_id != 'None'):
        return User.query.get(user_id)
    return None

@auth_bp.route('/login')
def login():
    """Show login page"""

    # Bypass if user is logged in
    if current_user.is_authenticated:
        return redirect(url_for('main_bp.home'))

    return render_template('login.html')

@auth_bp.route('/login', methods=['POST'])
def login_post():
    """Process login request"""

    email = request.form.get('email')
    password = request.form.get('password')
    remember_true = request.form.get('remember')
    remember_session = False
    if remember_true == 'remember_true':
        remember_session = True

    # Bypass if user is logged in
    if current_user.is_authenticated:
        return redirect(url_for('main_bp.home'))

    existing_user = User.query.filter_by(email=email).first()

    if existing_user is None:
        return redirect(url_for('auth_bp.login', msg='Email and Password did not match'))

    does_pass_match = bcrypt.check_password_hash(existing_user.password, password)

    if does_pass_match:
        existing_user.last_login = datetime.now(timezone.utc)
        db.session.commit() # Save changes to database

        login_user(existing_user, remember=remember_session)

        return redirect(url_for('main_bp.home'))
    else:
        return redirect(url_for('auth_bp.login', msg='Email and Password did not match'))



@auth_bp.route('/signup')
def signup(msg=None):
    """Show signup page"""

    # Bypass if user is logged in
    if current_user.is_authenticated:
        return redirect(url_for('main_bp.home'))

    return render_template('signup.html')

@auth_bp.route('/signup', methods=['POST'])
def signup_post():
    """Process signup form data"""

    email = request.form.get('email')
    name = request.form.get('name')
    password = request.form.get('password')

    user = User.query.filter_by(email=email).first()

    if user: # if a user is found, we want to redirect back to signup page so user can try again
        return redirect(url_for('auth_bp.signup', msg='User already exists'))

    # one-way hash the password
    hash_pass = bcrypt.generate_password_hash(password)

    new_user = User(
        email=email,
        name=name,
        password=hash_pass
    )

    # add the new user to the database
    db.session.add(new_user)
    db.session.commit()

    return redirect(url_for('auth_bp.login', msg='User created successfully'))

@auth_bp.route('/logout')
def logout():
    """Logout the currently logged in user"""

    logout_user()
    return redirect(url_for('auth_bp.login'))
