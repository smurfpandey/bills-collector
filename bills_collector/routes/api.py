"""Routes for API"""
from datetime import datetime

from flask import Blueprint, jsonify, make_response, request
from flask_login import current_user, login_required

from bills_collector.extensions import db
from bills_collector.integrations import GoogleClient
from bills_collector.models import LinkedAccount, InboxRule
from bills_collector.tasks import inbox_tasks

# Blueprint Configuration
api_bp = Blueprint(
    'api_bp', __name__,
    url_prefix='/api'
)

gdrive_app = None

def custom_error(message, status_code):
    """Method to throw RESTful errors"""
    return make_response(jsonify(message), status_code)

@api_bp.route('/linked_accounts', methods=['GET'])
@login_required
def get_linked_accounts():
    """Get all linked account of this user"""

    accounts = LinkedAccount.query.filter(
        LinkedAccount.user_id == current_user.id
    ).all()

    return jsonify({'linked_accounts': accounts}), 200

@api_bp.route('/linked_accounts/<account_id>', methods=['GET'])
@login_required
def get_linked_account_by_id(account_id):
    """Get all linked account of this user"""

    account = LinkedAccount.query.filter(
        LinkedAccount.user_id == current_user.id,
        LinkedAccount.id == account_id
    ).first()

    if account is None:
        return custom_error("", 404)

    # ensure token is active
    goog_client = GoogleClient(token=account.token_json)

    # fetch token again incase it is refreshed
    account = LinkedAccount.query.filter(
        LinkedAccount.user_id == current_user.id,
        LinkedAccount.id == account_id
    ).first()

    dict_account = {
        'id': account.id,
        'account_type': account.account_type,
        'access_token': account.access_token
    }

    goog_client.close()

    return jsonify(dict_account), 200

@api_bp.route('/linked_accounts/<account_id>/inbox_rules')
@login_required
def get_rules_for_email_account(account_id):
    """Get all Inbox rules for the account"""

    inbox_rules = InboxRule.query.filter(
        InboxRule.account_id == account_id,
        InboxRule.user_id == current_user.id
    ).all()

    return jsonify({'inbox_rules': inbox_rules}), 200

@api_bp.route('/linked_accounts/<account_id>/inbox_rules', methods=['POST'])
@login_required
def create_rule_for_email_account(account_id):
    """Create new Inbox rules for the account"""

    req_data = request.json

    inbox_rule = InboxRule(
        user_id=current_user.id,
        account_id = account_id,
        name = req_data['name'],
        email_from = req_data['email_from'],
        email_subject = req_data['email_subject'],
        attachment_password = req_data['attachment_password'],
        destination_folder_id = req_data['destination_folder_id'],
        destination_folder_name = req_data['destination_folder_name'],
        destination_account_id = req_data['destination_account_id'],
    )

    db.session.add(inbox_rule)
    db.session.commit()

    return jsonify(inbox_rule), 201

@api_bp.route('/linked_accounts/<account_id>/inbox_rules/<rule_id>', methods=['POST'])
@login_required
def update_rule_for_email_account(account_id, rule_id):
    """Update Inbox rules for the account"""

    req_data = request.json

    inbox_rule = InboxRule.query.filter(
        InboxRule.id == rule_id,
        InboxRule.account_id == account_id,
        InboxRule.user_id == current_user.id
    ).first()

    if inbox_rule is None:
        return custom_error("", 404)

    inbox_rule.name = req_data['name']
    inbox_rule.last_update_at = datetime.utcnow()
    inbox_rule.email_from = req_data['email_from']
    inbox_rule.email_subject = req_data['email_subject']
    inbox_rule.attachment_password = req_data['attachment_password']
    inbox_rule.destination_folder_id = req_data['destination_folder_id']
    inbox_rule.destination_folder_name = req_data['destination_folder_name']
    inbox_rule.destination_account_id = req_data['destination_account_id']

    db.session.commit()

    return jsonify(inbox_rule), 200

@api_bp.route('/run_task/', methods=['GET'])
@login_required
def run_task():
    """Manually trigger task"""

    inbox_tasks.check_inbox.delay()

    return make_response('Ok', 200)
