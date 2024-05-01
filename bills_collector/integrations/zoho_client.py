"""Client for accessing Zoho Services"""
from datetime import datetime, timezone, timedelta
from uuid import uuid4

from authlib.integrations.requests_client import OAuth2Session
from flask import current_app
from requests.models import PreparedRequest

from bills_collector.extensions import db, oauth
from bills_collector.models import LinkedAccount

class ZohoClient:
    """ Zoho client class"""

    def auth_client(client, client_auth, method, uri, headers, body):
        url = uri
        params = {'client_id':client.app.client_id,'client_secret':client.app.client_secret}
        req = PreparedRequest()
        req.prepare_url(url, params)
        uri = req.url #+ '&' + body
        body = None
        print(uri)
        return uri, headers, body

    def __init__(self, token=None):
        """Contstructor"""
        if token is not None:
            self.app = self.__init_with_token(token)
        else:
            self.app = oauth.register(
                'zoho',
                update_token=self.__update_token,
                authorize_params={'prompt':'consent'},
                #token_endpoint_auth_method=self.auth_client
            )

    def __init_with_token(self, token):
        client_id = current_app.config['ZOHO_CLIENT_ID']
        client_secret = current_app.config['ZOHO_CLIENT_SECRET']
        token_endpoint = current_app.config['ZOHO_ACCESS_TOKEN_URL']

        return OAuth2Session(client_id=client_id,
                             client_secret=client_secret,
                             token_endpoint=token_endpoint,
                             token=token,
                             update_token=self.__update_token)

    def __update_token(name, token, refresh_token=None, access_token=None):
        """Method to update token in db on refresh"""
        if refresh_token:
            item = LinkedAccount.query.filter_by(account_type='zoho', refresh_token=refresh_token).first()
        elif access_token:
            item = LinkedAccount.query.filter_by(account_type='zoho', access_token=access_token).first()
        else:
            return

        if item is None:
            return

        # update token
        item.token_json = token
        item.access_token = token['access_token']
        item.refresh_token = token['refresh_token']
        item.expires_at = datetime.fromtimestamp(token['expires_at'], timezone.utc)
        item.last_update_at = datetime.now(timezone.utc)

        db.session.commit()
        return None

    def close(self):
        """Method to close a oauth2session object"""
        self.app.close()
