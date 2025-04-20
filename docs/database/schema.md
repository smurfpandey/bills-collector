# Database Schema

## Tables

### Users
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(40) UNIQUE,
    password BYTEA,
    created_at TIMESTAMP,
    last_login TIMESTAMP
);
```
Stores user account information and authentication details.

### Linked Accounts
```sql
CREATE TABLE linked_accounts (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    account_type VARCHAR(50),
    account_id VARCHAR(250),
    access_token VARCHAR(500),
    refresh_token VARCHAR(500),
    token_json JSONB,
    user_profile JSONB,
    expires_at TIMESTAMP,
    last_update_at TIMESTAMP,
    created_at TIMESTAMP
);
```
Manages connections to external services (email/Google Drive).

### Inbox Rules
```sql
CREATE TABLE inbox_rules (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    account_id UUID REFERENCES linked_accounts(id),
    name VARCHAR(150),
    email_from VARCHAR(150),
    email_subject VARCHAR(150),
    attachment_password VARCHAR(50),
    destination_folder_id VARCHAR(150),
    destination_folder_name VARCHAR(150),
    destination_account_id UUID REFERENCES linked_accounts(id),
    last_update_at TIMESTAMP,
    created_at TIMESTAMP
);
```
Defines rules for processing emails and storing attachments.

### Processed Emails
```sql
CREATE TABLE processed_emails (
    id UUID PRIMARY KEY,
    email_id VARCHAR(450),
    account_id UUID REFERENCES linked_accounts(id),
    processed_at TIMESTAMP
);
```
Tracks which emails have been processed to avoid duplicates.

## Relationships
- Users can have multiple Linked Accounts
- Each Linked Account can have multiple Inbox Rules
- Inbox Rules reference both source and destination Linked Accounts
- Processed Emails are linked to their source Linked Account 