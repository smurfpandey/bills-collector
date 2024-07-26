"""Client for accessing Google Services"""
from datetime import datetime, timezone, timedelta
from uuid import uuid4

from authlib.integrations.requests_client import OAuth2Session
from flask import current_app
import google.oauth2.credentials
import googleapiclient.discovery
from googleapiclient.http import MediaFileUpload
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

    def __init__(self, token=None, account_id=None):
        """Contstructor"""
        if token is not None:
            self.app = self.__init_with_token(token)
            self.app.ensure_active_token(token=self.app.token)
            return
        elif account_id is not None:
            the_app = self.__init_with_account_id(account_id)
            if the_app is not None:
                self.app = the_app
                self.app.ensure_active_token(token=self.app.token)
                return

        # create the default app
        self.app = oauth.register(
            'google',
            server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
            update_token=self.__update_token,
            authorize_params={'prompt':'consent'}
        )

    def __init_with_account_id(self, account_id):
        """Initialize Google client by finding account id in DB"""
        account = LinkedAccount.query.get(account_id)

        if account is None:
            return None

        return self.__init_with_token(account.token_json)

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
        item.last_update_at = datetime.now(timezone.utc)

        db.session.commit()
        return None

    def close(self):
        """Method to close a oauth2session object"""
        self.app.close()

    def __get_google_credentials(self):
        """Creates a google api client"""

        google_provider_cfg = get_google_provider_cfg()
        token_endpoint = google_provider_cfg['token_endpoint']

        google_creds = google.oauth2.credentials.Credentials(
            token=self.app.token['access_token'],
            refresh_token=self.app.token.get('refresh_token'),
            client_id=current_app.config['GOOGLE_CLIENT_ID'],
            client_secret=current_app.config['GOOGLE_CLIENT_SECRET'],
            token_uri=token_endpoint
        )

        return google_creds


    def fetch_inbox_emails(self, from_address, subject_text):
        """Fetch emails from Inbox"""

        api_url = 'https://gmail.googleapis.com/gmail/v1/users/me/messages'
        query_data = {
            'includeSpamTrash': 'false',
            'q': f'has:attachment newer_than:40d in:INBOX from:{from_address} subject:{subject_text}',
            'maxResults': 500
        }

        resp = self.app.get(api_url, params=query_data)

        resp.raise_for_status()

        return resp.json()

    def fetch_one_email(self, message_id):
        """Fetch email from Inbox"""

        api_url = f'https://gmail.googleapis.com/gmail/v1/users/me/messages/{message_id}'

        resp = self.app.get(api_url)

        resp.raise_for_status()

        return resp.json()

    def get_email_attachment(self, message_id, attachment_id):
        """Get Attachment of email"""

        api_url = f'https://gmail.googleapis.com/gmail/v1/users/me/messages/{message_id}/attachments/{attachment_id}'

        resp = self.app.get(api_url)

        resp.raise_for_status()

        return resp.json()

    def upload_file_to_drive(self, file_mime_type, file_path, file_name, drive_folder_id):
        """Upload file to Google Drive"""

        google_creds = self.__get_google_credentials()

        drive_service = googleapiclient.discovery.build("drive", "v3", credentials=google_creds)

        file_metadata = {"name": file_name, "parents": [drive_folder_id]}
        media = MediaFileUpload(
            file_path, mimetype=file_mime_type, resumable=False
        )
        # pylint: disable=maybe-no-member
        file = (
            drive_service.files()
            .create(body=file_metadata, media_body=media, fields="id")
            .execute()
        )

        return file


