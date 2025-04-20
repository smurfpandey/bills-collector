"""
Integration tests for Gmail API integration with Celery tasks.
"""
import os
import base64
import json
import pytest
from unittest.mock import patch, MagicMock
from googleapiclient.discovery import build
from googleapiclient.http import HttpMock, RequestMockBuilder

from bills_collector.extensions import db
from bills_collector.models import LinkedAccount, InboxRule, ProcessedEmail, User
from bills_collector.integrations import GoogleClient
from bills_collector.tasks.inbox_tasks import process_gmail_inbox

def read_response(filename):
    """Helper to read mock response files"""
    with open(filename, 'rb') as file:
        return file.read()

@pytest.fixture
def mock_google_client():
    """Returns a mocked GoogleClient"""
    with patch('bills_collector.tasks.inbox_tasks.GoogleClient') as MockGoogleClient:
        mock_client = MockGoogleClient.return_value
        # Setup common mock returns
        mock_client.fetch_inbox_emails.return_value = {
            'messages': [
                {
                    'id': 'test_email_id_1',
                    'threadId': 'thread_1'
                }
            ]
        }
        mock_client.fetch_one_email.return_value = {
            'id': 'test_email_id_1',
            'payload': {
                'parts': [
                    {
                        'mimeType': 'application/pdf',
                        'filename': 'bill.pdf',
                        'body': {'attachmentId': 'test_attachment_id'}
                    }
                ]
            }
        }
        mock_client.get_email_attachment.return_value = {
            'data': base64.b64encode(b'%PDF-test-data').decode('UTF-8')
        }
        mock_client.upload_file_to_drive.return_value = {'id': 'test_drive_file_id'}
        
        yield mock_client

@pytest.fixture
def linked_accounts_setup(app):
    """Create test user and linked accounts"""
    with app.app_context():
        # Create test user
        user = User.query.filter_by(email='somebody@kumar.inc').first()
        
        # Gmail account
        gmail_account = LinkedAccount(
            user_id=user.id,
            account_type='gmail',
            account_id='test_gmail_id',
            access_token='test_access_token',
            refresh_token='test_refresh_token',
            token_json={
                'access_token': 'test_access_token',
                'refresh_token': 'test_refresh_token',
                'expires_at': 1700000000
            },
            expires_at='2023-12-31 23:59:59'
        )
        
        # Drive account for destination
        drive_account = LinkedAccount(
            user_id=user.id,
            account_type='google-drive',
            account_id='test_drive_id',
            access_token='test_drive_token',
            refresh_token='test_drive_refresh',
            token_json={
                'access_token': 'test_drive_token',
                'refresh_token': 'test_drive_refresh',
                'expires_at': 1700000000
            },
            expires_at='2023-12-31 23:59:59'
        )
        
        db.session.add(gmail_account)
        db.session.add(drive_account)
        db.session.commit()
        
        yield {
            'user': user,
            'gmail_account': gmail_account,
            'drive_account': drive_account
        }
        
        # Cleanup
        ProcessedEmail.query.filter_by(account_id=gmail_account.id).delete()
        InboxRule.query.filter_by(account_id=gmail_account.id).delete()
        LinkedAccount.query.filter_by(id=gmail_account.id).delete()
        LinkedAccount.query.filter_by(id=drive_account.id).delete()
        db.session.commit()

@pytest.fixture
def inbox_rule_setup(app, linked_accounts_setup):
    """Create inbox rule for testing"""
    with app.app_context():
        rule = InboxRule(
            user_id=linked_accounts_setup['user'].id,
            account_id=linked_accounts_setup['gmail_account'].id,
            name="Test Rule",
            email_from="bills@company.com",
            email_subject="Monthly Bill",
            attachment_password="test_password",
            destination_folder_id="test_folder_id",
            destination_folder_name="Test Folder",
            destination_account_id=linked_accounts_setup['drive_account'].id
        )
        
        db.session.add(rule)
        db.session.commit()
        
        yield rule
        
        # Cleanup happens in linked_accounts_setup fixture

def test_process_gmail_inbox_standard_mocks(app, inbox_rule_setup, mock_google_client):
    """Test the Gmail API integration with standard mocks"""
    with app.app_context():
        # Create temporary directory for PDF processing
        os.makedirs('tmp', exist_ok=True)
        
        # Run the task
        with patch('bills_collector.tasks.inbox_tasks.get_drive_app') as mock_get_drive:
            mock_get_drive.return_value = mock_google_client
            
            # Mock pikepdf for PDF processing
            with patch('bills_collector.tasks.inbox_tasks.pikepdf.open') as mock_pdf_open:
                mock_pdf = MagicMock()
                mock_pdf_open.return_value = mock_pdf
                
                # Execute the task
                process_gmail_inbox(inbox_rule_setup.account_id)
                
                # Assertions
                mock_google_client.fetch_inbox_emails.assert_called_once()
                mock_google_client.fetch_one_email.assert_called_once_with('test_email_id_1')
                mock_google_client.get_email_attachment.assert_called_once()
                mock_pdf_open.assert_called_once()
                mock_pdf.save.assert_called_once()
                mock_google_client.upload_file_to_drive.assert_called_once()
                
                # Verify email was marked as processed
                processed_email = ProcessedEmail.query.filter_by(
                    email_id='test_email_id_1',
                    account_id=inbox_rule_setup.account_id
                ).first()
                
                assert processed_email is not None

def test_process_gmail_inbox_with_google_mocks(app, inbox_rule_setup):
    """Test the Gmail API integration using Google's mock approach"""
    with app.app_context():
        fixtures_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'fixtures')
        
        # Create mock builder
        mock_builder = RequestMockBuilder({
            'gmail.users.messages.list': (None, read_response(os.path.join(fixtures_dir, 'gmail_messages_list.json'))),
            'gmail.users.messages.get': (None, read_response(os.path.join(fixtures_dir, 'gmail_message_get.json'))),
            'gmail.users.messages.attachments.get': (None, read_response(os.path.join(fixtures_dir, 'gmail_attachment.json'))),
        })
        
        # Create temporary directory for PDF processing
        os.makedirs('tmp', exist_ok=True)
        
        # Patch the GoogleClient to use our mocked service
        with patch('bills_collector.integrations.google_client.build') as mock_build:
            # Create a Gmail service with our mocks
            gmail_service = build('gmail', 'v1', requestBuilder=mock_builder)
            mock_build.return_value = gmail_service
            
            # Patch pikepdf
            with patch('bills_collector.tasks.inbox_tasks.pikepdf.open') as mock_pdf_open:
                mock_pdf = MagicMock()
                mock_pdf_open.return_value = mock_pdf
                
                # Mock the drive upload
                with patch('bills_collector.tasks.inbox_tasks.get_drive_app') as mock_get_drive:
                    mock_drive_client = MagicMock()
                    mock_drive_client.upload_file_to_drive.return_value = {'id': 'test_drive_file_id'}
                    mock_get_drive.return_value = mock_drive_client
                    
                    # Execute the task
                    process_gmail_inbox(inbox_rule_setup.account_id)
                    
                    # Verify email was marked as processed
                    processed_email = ProcessedEmail.query.filter_by(
                        email_id='test_email_id_1',
                        account_id=inbox_rule_setup.account_id
                    ).first()
                    
                    assert processed_email is not None
                    
                    # Verify the drive upload was called
                    mock_drive_client.upload_file_to_drive.assert_called_once()

def test_process_gmail_inbox_skips_processed_emails(app, inbox_rule_setup, mock_google_client):
    """Test that the task skips already processed emails"""
    with app.app_context():
        # Mark the email as already processed
        processed_email = ProcessedEmail(
            email_id='test_email_id_1',
            account_id=inbox_rule_setup.account_id
        )
        db.session.add(processed_email)
        db.session.commit()
        
        # Run the task
        process_gmail_inbox(inbox_rule_setup.account_id)
        
        # Verify that fetch_one_email was not called since email was already processed
        mock_google_client.fetch_one_email.assert_not_called()

def test_process_gmail_inbox_error_handling(app, inbox_rule_setup):
    """Test error handling during email processing"""
    with app.app_context():
        # Create a GoogleClient that raises an exception
        with patch('bills_collector.tasks.inbox_tasks.GoogleClient') as MockGoogleClient:
            mock_client = MockGoogleClient.return_value
            mock_client.fetch_inbox_emails.side_effect = Exception("API Error")
            
            # Execute the task - it should not raise an exception
            process_gmail_inbox(inbox_rule_setup.account_id)
            
            # Verify no emails were processed
            processed_email_count = ProcessedEmail.query.filter_by(
                account_id=inbox_rule_setup.account_id
            ).count()
            
            assert processed_email_count == 0 