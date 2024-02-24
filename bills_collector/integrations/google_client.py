"""Client for accessing Google Services"""
from datetime import datetime, timezone, timedelta
from uuid import uuid4

from authlib.integrations.requests_client import OAuth2Session
from flask import current_app
import requests

from bills_collector.extensions import db, oauth
from bills_collector.models import LinkedAccount

GOOGLE_DISCOVERY_URL = (
    "https://accounts.google.com/.well-known/openid-configuration"
)

def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()

class GoogleClient:
    """ Google client class"""

    def __init__(self, token=None):
        """Contstructor"""
        if token is not None:
            self.app = self.__init_with_token(token)
        else:
            # Find out what URL to hit for Google login
            # google_provider_cfg = get_google_provider_cfg()
            # authorization_endpoint = google_provider_cfg["authorization_endpoint"]
            self.app = oauth.register(
                'google',
                server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
                update_token=self.__update_token,
                authorize_params={'prompt':'consent'}
            )

    def __init_with_token(self, token):
        client_id = current_app.config['GOOGLE_CLIENT_ID']
        client_secret = current_app.config['GOOGLE_CLIENT_SECRET']

        google_provider_cfg = get_google_provider_cfg()
        token_endpoint = google_provider_cfg['token_endpoint']
        revocation_endpoint = google_provider_cfg['revocation_endpoint']

        return OAuth2Session(client_id=client_id,
                             client_secret=client_secret,
                             token_endpoint=token_endpoint,
                             revocation_endpoint=revocation_endpoint,
                             token=token,
                             update_token=self.__update_token)

    def __update_token(name, token, refresh_token=None, access_token=None):
        """Method to update token in db on refresh"""
        print('token update hua re!!')
        if refresh_token:
            item = LinkedAccount.query.filter_by(refresh_token=refresh_token).first()
        elif access_token:
            item = LinkedAccount.query.filter_by(access_token=access_token).first()
        else:
            return

        if item is None:
            return

        # update token
        item.token_json = token
        item.access_token = token['access_token']
        item.refresh_token = token['refresh_token']
        item.expires_at = datetime.fromtimestamp(token['expires_at'], timezone.utc)
        item.last_update_at = datetime.utcnow()

        db.session.commit()
        return None

    def close(self):
        """Method to close a oauth2session object"""
        self.app.close()
