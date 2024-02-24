"""Routes for user account linking."""
from datetime import datetime, timezone

from flask import request, redirect, Blueprint, url_for, session, abort
from flask_login import current_user, login_required


from bills_collector.extensions import db, login_manager, bcrypt
from bills_collector.integrations import GoogleClient, ZohoClient
from bills_collector.models import LinkedAccount

# Blueprint Configuration
connect_bp = Blueprint(
    'connect_bp', __name__
)

google_app = GoogleClient().app
zoho_app = ZohoClient().app

def get_google_scope(connect_type):
    default_scope = ['email', 'openid', 'profile']
    if connect_type == 'google_drive':
        return default_scope + ['https://www.googleapis.com/auth/drive']
    elif connect_type == 'gmail':
        return default_scope + ['https://www.googleapis.com/auth/gmail.readonly']
    else:
        return None

@connect_bp.route('/connect/google')
@login_required
def connect_google():
    """Initiate authentication request with Google"""

    connect_type = request.args.get('type')

    redirect_uri = url_for('connect_bp.callback_google', _external=True)
    connect_scope = get_google_scope(connect_type)

    if connect_scope is None:
        return abort(400)

    connect_scope = ' '.join(connect_scope)

    session['google_connect_type'] = connect_type
    session['google_connect_scope'] = connect_scope

    return google_app.authorize_redirect(
        redirect_uri,
        scope=connect_scope,
        access_type='offline'
    )

@connect_bp.route('/connect/google/callback')
@login_required
def callback_google():
    """Handle callback from Google"""

    connect_type = session['google_connect_type']
    session_scope = session['google_connect_scope']
    token = google_app.authorize_access_token(scope=session_scope)

    user_profile = {
        'name': token['userinfo']['name'],
        'profile_picture': token['userinfo']['picture'],
        'email': token['userinfo']['email'],
    }

    google_account = LinkedAccount(
        account_type=connect_type,
        account_id=token['userinfo']['sub'],
        token_json=token,
        access_token = token['access_token'],
        refresh_token = token['refresh_token'],
        user_profile=user_profile,
        user_id=current_user.id,
        expires_at=datetime.fromtimestamp(token['expires_at'], timezone.utc)
    )

    existing_account = LinkedAccount.query.filter_by(
        account_type=connect_type,
        account_id=token['userinfo']['sub'],
        user_id = current_user.id
    ).first()

    if existing_account is None:
        db.session.add(google_account)
    else:
        existing_account.token_json = token
        existing_account.access_token = token['access_token']
        existing_account.refresh_token = token['refresh_token']
        existing_account.user_profile = user_profile
        existing_account.expires_at = google_account.expires_at
        existing_account.last_update_at = datetime.utcnow()

    db.session.commit()

    return redirect(url_for('main_bp.home'))

@connect_bp.route('/connect/zoho')
@login_required
def connect_zoho():
    """Initiate authentication request with Zoho"""

    redirect_uri = url_for('connect_bp.callback_zoho', _external=True)
    connect_scope = ' '.join([
        'VirtualOffice.folders.READ',
        'VirtualOffice.messages.READ',
        'VirtualOffice.attachments.READ',
        'VirtualOffice.accounts.READ'
    ])

    session['zoho_connect_scope'] = connect_scope

    return zoho_app.authorize_redirect(
        redirect_uri,
        scope=connect_scope,
        access_type='offline'
    )

@connect_bp.route('/connect/zoho/callback')
@login_required
def callback_zoho():
    """Handle callback from Zoho"""

    session_scope = session['zoho_connect_scope']
    token = zoho_app.authorize_access_token(scope=session_scope)

    print(token)

    return token

    zoho_account = LinkedAccount(
        account_type='zoho',
        account_id=token['userinfo']['sub'],
        token_json=token,
        user_profile=user_profile,
        user_id=current_user.id,
        expires_at=datetime.fromtimestamp(token['expires_at'], timezone.utc)
    )
