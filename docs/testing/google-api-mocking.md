# Google API Mocking Strategy

Based on the official Google API client libraries, we can implement more accurate and maintainable mocks for our Gmail and Drive API integration tests.

## Method 1: HttpMock Approach

This approach is simple and works well for basic API response mocking:

```python
# tests/integration/test_gmail_api.py
import pytest
from googleapiclient.discovery import build
from googleapiclient.http import HttpMock
from bills_collector.integrations import GoogleClient

def test_gmail_fetch_emails_with_http_mock():
    # Create mock response file
    # tests/fixtures/gmail_messages_list.json
    """
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
    """
    
    # Create HttpMock with the mock response file
    mock = HttpMock('tests/fixtures/gmail_messages_list.json', {'status': '200'})
    
    # Build Gmail service with mock
    gmail_service = build('gmail', 'v1', http=mock)
    
    # Use our application's GoogleClient but inject the mocked service
    client = GoogleClient()
    client.gmail_service = gmail_service
    
    # Call the method we want to test
    emails = client.fetch_inbox_emails(from_address="bills@company.com", subject_text="Monthly Bill")
    
    # Verify expected behavior
    assert len(emails['messages']) == 2
    assert emails['messages'][0]['id'] == 'test_email_id_1'
    
    # Optionally verify the request URL was as expected
    assert mock.uri == 'https://gmail.googleapis.com/gmail/v1/users/me/messages?q=from%3Abills%40company.com+subject%3AMonthly+Bill&alt=json'
```

## Method 2: RequestMockBuilder Approach

This approach provides more flexibility for mocking multiple API methods:

```python
# tests/integration/test_gmail_api_with_builder.py
import pytest
import json
import os
from googleapiclient.discovery import build
from googleapiclient.http import RequestMockBuilder
from bills_collector.integrations import GoogleClient

def read_response(filename):
    """Helper to read mock response files"""
    with open(filename, 'rb') as file:
        return file.read()

def test_gmail_workflow_with_request_mock_builder():
    # Setup mocked responses for multiple API methods
    mock_builder = RequestMockBuilder({
        'gmail.users.messages.list': (None, read_response('tests/fixtures/gmail_messages_list.json')),
        'gmail.users.messages.get': (None, read_response('tests/fixtures/gmail_message_get.json')),
        'gmail.users.messages.attachments.get': (None, read_response('tests/fixtures/gmail_attachment.json')),
    })
    
    # Build Gmail service with request mock builder
    gmail_service = build('gmail', 'v1', requestBuilder=mock_builder)
    
    # Create our application's client with the mocked service
    client = GoogleClient()
    client.gmail_service = gmail_service
    
    # Test full workflow
    # 1. First fetch emails
    emails = client.fetch_inbox_emails(from_address="bills@company.com", subject_text="Monthly Bill")
    assert len(emails['messages']) == 2
    
    # 2. Then fetch a specific email
    email_id = emails['messages'][0]['id']
    email = client.fetch_one_email(email_id)
    assert email['id'] == email_id
    
    # 3. Then fetch attachment
    attachment_id = email['payload']['parts'][0]['body']['attachmentId']
    attachment = client.get_email_attachment(message_id=email_id, attachment_id=attachment_id)
    assert 'data' in attachment
```

## Creating Mock Response Files

For effective testing, we should create realistic mock response files based on the actual Gmail API responses:

```python
# script to generate mock response files (tools/generate_mock_responses.py)
import json
import os
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

def create_mock_responses():
    """Generate mock response files from real API calls"""
    # Use test credentials
    credentials = Credentials.from_authorized_user_info(info={
        "token": "test_token",
        # other required credential fields
    })
    
    # Create actual service (for development only)
    service = build('gmail', 'v1', credentials=credentials)
    
    # Example: Get message list
    response = service.users().messages().list(userId='me', q='from:bills@example.com').execute()
    
    # Save as mock file
    os.makedirs('tests/fixtures', exist_ok=True)
    with open('tests/fixtures/gmail_messages_list.json', 'w') as f:
        json.dump(response, f, indent=2)
        
    # Repeat for other API calls you need to mock
    # ...
```

## Integrating with Existing Test Strategy

We can update our existing test framework to use these Google-specific mocks:

```python
# tests/conftest.py - additional fixtures

@pytest.fixture
def gmail_mock_service():
    """Returns a Gmail service with mocked responses"""
    mock = HttpMock('tests/fixtures/gmail_messages_list.json', {'status': '200'})
    return build('gmail', 'v1', http=mock)

@pytest.fixture
def google_client_with_mocks(gmail_mock_service):
    """Returns our application client with mocked Google services"""
    client = GoogleClient()
    client.gmail_service = gmail_mock_service
    return client
```

## Benefits of This Approach

1. **More Accurate Testing**: Mocks exactly match the Gmail API's real behavior
2. **Easier Maintenance**: When API changes, just update the mock files
3. **Better Debugging**: Can inspect what URLs were requested
4. **Comprehensive Testing**: Can test complete workflows with chained API calls
5. **Official Solution**: Uses Google's recommended approach for testing

## References

- [Stack Overflow: How can I mock the results of the Gmail API](https://stackoverflow.com/questions/26847080/how-can-i-mock-the-results-of-the-gmail-api)
- [Google API Client Libraries Documentation](https://developers.google.com/api-client-library) 