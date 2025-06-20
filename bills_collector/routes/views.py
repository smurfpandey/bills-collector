"""Routes for application pages."""

from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user, login_required, logout_user

from bills_collector.models import LinkedAccount, InboxRule

# Blueprint Configuration
main_bp = Blueprint(
    'main_bp', __name__
)

@main_bp.route('/', methods=['GET'])
@login_required
def home():
    """Logged-in User Dashboard."""
    accounts = LinkedAccount.query.filter(
        LinkedAccount.user_id == current_user.id
    ).all()

    return render_template('home.html', current_user=current_user, linked_accounts=accounts)

@main_bp.route('/account/<account_id>/inbox_rules')
@login_required
def account_inbox_rules(account_id):
    """Show inbox rules for a specific account"""
    account = LinkedAccount.query.filter(
        LinkedAccount.id == account_id,
        LinkedAccount.user_id == current_user.id
    ).first_or_404()

    # inbox_rules = InboxRule.query.filter(
    #     InboxRule.account_id == account_id,
    #     InboxRule.user_id == current_user.id
    # ).all()

    #get all linked accounts for the user with type 'google_drive'
    linked_accounts = LinkedAccount.query.filter(
        LinkedAccount.user_id == current_user.id,
        LinkedAccount.account_type == 'google_drive'
    ).all()


    return render_template('inbox_rules.html', account=account, linked_accounts=linked_accounts)
