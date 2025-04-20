# Integration Testing Strategy

## Test Environment Setup

### 1. Test Dependencies
```python
# requirements-test.txt
pytest==7.4.3
pytest-cov==4.1.0
pytest-mock==3.12.0
pytest-asyncio==0.21.1
pytest-env==1.1.1
responses==0.24.1
faker==22.0.0
google-api-python-client==2.108.0  # For Google API mocking
google-auth==2.23.4  # For Google API auth
```

### 2. Test Configuration
```python
# tests/conftest.py
import pytest
import os
from unittest.mock import MagicMock
from googleapiclient.discovery import build
from googleapiclient.http import HttpMock, RequestMockBuilder

from bills_collector.app import create_app
from bills_collector.extensions import db
from bills_collector.models import User, LinkedAccount, InboxRule
from bills_collector.integrations import GoogleClient

def read_response(filename):
    """Helper to read mock response files"""
    with open(filename, 'rb') as file:
        return file.read()

@pytest.fixture
def app():
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def mock_google_client():
    return MagicMock()

@pytest.fixture
def mock_zoho_client():
    return MagicMock()

@pytest.fixture
def gmail_mock_service():
    """Returns a Gmail service with mocked responses"""
    mock = HttpMock('tests/fixtures/gmail_messages_list.json', {'status': '200'})
    return build('gmail', 'v1', http=mock)

@pytest.fixture
def gmail_mock_builder():
    """Returns a RequestMockBuilder for more complex Gmail testing"""
    fixtures_dir = os.path.join(os.path.dirname(__file__), 'fixtures')
    
    mock_builder = RequestMockBuilder({
        'gmail.users.messages.list': (None, read_response(os.path.join(fixtures_dir, 'gmail_messages_list.json'))),
        'gmail.users.messages.get': (None, read_response(os.path.join(fixtures_dir, 'gmail_message_get.json'))),
        'gmail.users.messages.attachments.get': (None, read_response(os.path.join(fixtures_dir, 'gmail_attachment.json'))),
    })
    
    return mock_builder

@pytest.fixture
def google_client_with_mocks(gmail_mock_service):
    """Returns our application client with mocked Google services"""
    client = GoogleClient()
    client.gmail_service = gmail_mock_service
    return client
    
@pytest.fixture
def test_user(app):
    user = User(
        name="Test User",
        email="test@example.com",
        password="hashed_password"
    )
    db.session.add(user)
    db.session.commit()
    return user
```

## Test Categories

### 1. Email Processing Tests

#### Using Standard Mocks
```python
# tests/integration/test_email_processing.py
import pytest
from bills_collector.tasks.inbox_tasks import process_gmail_inbox

def test_email_processing_flow(app, mock_google_client, test_user):
    # Setup test data
    rule = InboxRule(
        user_id=test_user.id,
        name="Test Rule",
        email_from="bills@company.com",
        email_subject="Monthly Bill"
    )
    
    # Mock email data
    mock_google_client.fetch_inbox_emails.return_value = {
        'messages': [
            {
                'id': 'test_email_id',
                'payload': {
                    'parts': [
                        {
                            'mimeType': 'application/pdf',
                            'filename': 'test_bill.pdf',
                            'body': {'attachmentId': 'test_attachment_id'}
                        }
                    ]
                }
            }
        ]
    }
    
    # Execute test
    process_gmail_inbox(rule.id)
    
    # Verify results
    assert mock_google_client.fetch_inbox_emails.called
    assert mock_google_client.get_email_attachment.called
```

#### Using Google API Mocks
```python
# tests/integration/test_gmail_api.py
import pytest
from googleapiclient.discovery import build
from bills_collector.tasks.inbox_tasks import process_gmail_inbox
from bills_collector.integrations import GoogleClient

def test_email_processing_with_google_mocks(app, test_user, gmail_mock_builder):
    # Setup test data
    rule = InboxRule(
        user_id=test_user.id,
        name="Test Rule",
        email_from="bills@company.com",
        email_subject="Monthly Bill"
    )
    db.session.add(rule)
    db.session.commit()
    
    # Build Gmail service with request mock builder
    gmail_service = build('gmail', 'v1', requestBuilder=gmail_mock_builder)
    
    # Patch our GoogleClient to use the mocked service
    with patch('bills_collector.integrations.GoogleClient') as MockGoogleClient:
        mock_client = MockGoogleClient.return_value
        mock_client.gmail_service = gmail_service
        
        # Execute test
        process_gmail_inbox(rule.id)
        
        # Verify the chain of API calls occurred
        # We don't need to verify .called because we're using real API call patterns
        # Instead we verify the end result - was the email marked as processed?
        processed_email = ProcessedEmail.query.filter_by(email_id='test_email_id').first()
        assert processed_email is not None
```

### 2. OAuth Integration Tests
```python
# tests/integration/test_oauth.py
import pytest
from bills_collector.integrations import GoogleClient, ZohoClient

def test_google_oauth_flow(app, client, test_user):
    # Test OAuth initiation
    response = client.get('/auth/google')
    assert response.status_code == 302
    
    # Test OAuth callback
    response = client.get('/auth/google/callback?code=test_code')
    assert response.status_code == 302
    
    # Verify account linking
    linked_account = LinkedAccount.query.filter_by(
        user_id=test_user.id,
        account_type='gmail'
    ).first()
    assert linked_account is not None

def test_token_refresh(app, mock_google_client):
    # Test token refresh flow
    mock_google_client.refresh_token.return_value = {
        'access_token': 'new_token',
        'expires_in': 3600
    }
    
    # Execute refresh
    result = mock_google_client.refresh_token()
    
    # Verify refresh
    assert result['access_token'] == 'new_token'
    assert result['expires_in'] == 3600
```

### 3. PDF Processing Tests
```python
# tests/integration/test_pdf_processing.py
import pytest
from bills_collector.tasks.inbox_tasks import process_pdf_attachment

def test_pdf_processing(app, mock_google_client):
    # Test PDF download and processing
    test_pdf_data = b'%PDF-1.4...'  # Sample PDF data
    mock_google_client.get_email_attachment.return_value = {
        'data': test_pdf_data
    }
    
    # Process PDF
    result = process_pdf_attachment(
        message_id='test_id',
        attachment_id='test_attachment',
        password='test_password'
    )
    
    # Verify processing
    assert result['success'] is True
    assert result['file_path'] is not None
```

### 4. Google Drive Integration Tests
```python
# tests/integration/test_drive_integration.py
import pytest
from bills_collector.integrations import GoogleDriveClient

def test_drive_upload(app, mock_google_client):
    # Test file upload to Drive
    test_file = {
        'path': '/tmp/test.pdf',
        'name': 'test.pdf',
        'mime_type': 'application/pdf'
    }
    
    mock_google_client.upload_file_to_drive.return_value = {
        'id': 'test_file_id',
        'name': 'test.pdf'
    }
    
    # Execute upload
    result = mock_google_client.upload_file_to_drive(
        file_path=test_file['path'],
        file_name=test_file['name'],
        file_mime_type=test_file['mime_type']
    )
    
    # Verify upload
    assert result['id'] == 'test_file_id'
    assert result['name'] == 'test.pdf'
```

### 5. Database Integration Tests
```python
# tests/integration/test_database.py
import pytest
from bills_collector.models import User, LinkedAccount, InboxRule

def test_user_account_creation(app, test_user):
    # Test account linking
    linked_account = LinkedAccount(
        user_id=test_user.id,
        account_type='gmail',
        account_id='test_account_id'
    )
    db.session.add(linked_account)
    db.session.commit()
    
    # Verify linking
    assert linked_account.id is not None
    assert linked_account.user_id == test_user.id

def test_rule_creation(app, test_user):
    # Test rule creation
    rule = InboxRule(
        user_id=test_user.id,
        name="Test Rule",
        email_from="bills@company.com",
        email_subject="Monthly Bill"
    )
    db.session.add(rule)
    db.session.commit()
    
    # Verify rule
    assert rule.id is not None
    assert rule.user_id == test_user.id
```

## Test Data Management

### 1. Mock Response Files
Create these files in `tests/fixtures/`:

```json
# tests/fixtures/gmail_messages_list.json
{
  "messages": [
    {
      "id": "test_email_id_1",
      "threadId": "thread_1"
    },
    {
      "id": "test_email_id_2",
      "threadId": "thread_1"
    }
  ],
  "resultSizeEstimate": 2
}
```

```json
# tests/fixtures/gmail_message_get.json
{
  "id": "test_email_id_1",
  "threadId": "thread_1",
  "labelIds": ["INBOX"],
  "snippet": "Your monthly bill",
  "payload": {
    "mimeType": "multipart/mixed",
    "headers": [
      {"name": "From", "value": "bills@company.com"},
      {"name": "Subject", "value": "Monthly Bill"}
    ],
    "parts": [
      {
        "mimeType": "application/pdf",
        "filename": "test_bill.pdf",
        "body": {"attachmentId": "test_attachment_id"}
      }
    ]
  }
}
```

```json
# tests/fixtures/gmail_attachment.json
{
  "data": "JVBERi0xLjQKJcOkw7zDtsOfCjIgMCBvYmoKPDwvTGVuZ3RoIDMgMCBSL0ZpbHR...truncated...",
  "size": 1024
}
```

### 2. Test Data Helper
```python
# tests/utils/test_data.py
"""Helper functions for creating test data"""

def create_test_rule(user, db_session):
    """Create a test rule for email processing"""
    rule = InboxRule(
        user_id=user.id,
        name="Test Rule",
        email_from="bills@company.com",
        email_subject="Monthly Bill",
        attachment_password="test_password",
        destination_folder_id="test_folder_id",
        destination_folder_name="Test Folder"
    )
    db_session.add(rule)
    db_session.commit()
    return rule

def create_test_linked_account(user, account_type, db_session):
    """Create a test linked account"""
    account = LinkedAccount(
        user_id=user.id,
        account_type=account_type,
        account_id=f"test_{account_type}_id",
        access_token="test_access_token",
        refresh_token="test_refresh_token",
        token_json={
            "access_token": "test_access_token",
            "refresh_token": "test_refresh_token",
            "expires_in": 3600
        }
    )
    db_session.add(account)
    db_session.commit()
    return account
```

## Running Tests

### 1. Test Commands
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=bills_collector

# Run specific test file
pytest tests/integration/test_email_processing.py

# Run with verbose output
pytest -v

# Run only Gmail API tests
pytest tests/integration/test_gmail_api.py
```

### 2. CI/CD Integration
```yaml
# .github/workflows/test.yml
name: Integration Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:13
        env:
          POSTGRES_USER: bills_collector
          POSTGRES_PASSWORD: test_password
          POSTGRES_DB: bills_collector_test
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.8'
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install -r requirements-test.txt
    - name: Run tests
      env:
        DATABASE_URL: postgresql://bills_collector:test_password@localhost:5432/bills_collector_test
      run: |
        pytest --cov=bills_collector
```

## Test Coverage Goals
- Overall coverage: >80%
- Critical paths: 100%
- Error handling: 100%
- Integration points: 100%

## Maintenance

### 1. Regular Updates
- Update test dependencies
- Review and update mocks
- Add tests for new features
- Update existing tests

### 2. Test Data
- Keep mock response files current with API changes
- Update mock responses when API behavior changes
- Maintain test fixtures
- Clean up test artifacts

### 3. Documentation
- Document test setup
- Update test cases
- Maintain test documentation
- Document test patterns 