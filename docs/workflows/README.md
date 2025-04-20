# System Workflows

## Email Processing Workflow

### 1. Periodic Task Execution
- Triggered every 12 hours by Celery scheduler
- Monitors inboxes with active rules
- Processes Gmail and Zoho accounts

### 2. Email Processing Steps
1. **Email Fetching**
   - Query emails matching rules
   - Filter by sender and subject
   - Retrieve email metadata

2. **Duplicate Check**
   - Verify email hasn't been processed
   - Check against processed_emails table
   - Skip if already processed

3. **Attachment Processing**
   - Download PDF attachments
   - Handle password protection
   - Validate PDF format

4. **File Organization**
   - Generate date-based filename (YYYY-MM)
   - Prepare for Google Drive upload
   - Set appropriate metadata

5. **Storage**
   - Upload to specified Google Drive folder
   - Verify upload success
   - Update file permissions

6. **Completion**
   - Mark email as processed
   - Update processing status
   - Log completion

## Account Management Workflow

### 1. User Registration
- Create user account
- Set up authentication
- Initialize user settings

### 2. Account Linking
- Connect email accounts
- Set up Google Drive access
- Configure OAuth tokens

### 3. Rule Configuration
- Define email filters
- Set destination folders
- Configure PDF passwords

## Maintenance Workflow

### 1. Token Management
- Monitor token expiration
- Refresh expired tokens
- Update token storage

### 2. Health Monitoring
- Check system status
- Monitor task execution
- Track error rates

### 3. Cleanup
- Remove temporary files
- Clean up expired sessions
- Archive old records 