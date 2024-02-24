"""Routes for application pages."""

from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user, login_required, logout_user

from bills_collector.models import LinkedAccount

# Blueprint Configuration
main_bp = Blueprint(
    'main_bp', __name__
)

@main_bp.route('/', methods=['GET'])
@login_required
def home():
    """Logged-in User Dashboard."""
    accounts = LinkedAccount.query.all()

    return render_template('home.html.j2', current_user=current_user, linked_accounts=accounts)
