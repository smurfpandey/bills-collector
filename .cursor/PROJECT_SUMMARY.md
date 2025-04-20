# Bills Collector - Quick Reference

## Project Overview
Bills Collector automates PDF bill collection from email (Gmail/Zoho) and stores them in Google Drive.

## Key Components
- **Web App**: Flask-based frontend
- **Background Worker**: Celery for automated tasks
- **Database**: PostgreSQL
- **External APIs**: Gmail, Zoho Mail, Google Drive

## Core Workflows
1. **Email Processing** (12-hour intervals)
   - Check inboxes → Match rules → Download PDFs → Store in Drive
2. **Account Management**
   - User auth → Link accounts → Configure rules
3. **Maintenance**
   - Token refresh → Health checks → Cleanup

## Data Model
- `users`: Account info
- `linked_accounts`: OAuth connections
- `inbox_rules`: Email processing rules
- `processed_emails`: Processing history

## Key Files
```
bills_collector/
├── app.py          # Entry point
├── config.py       # Settings
├── models.py       # DB models
├── integrations/   # API clients
├── routes/         # Web endpoints
└── tasks/          # Background jobs
```

## Testing Strategy
- **Test Types**:
  - Integration tests
  - OAuth flow tests
  - PDF processing tests
  - Drive integration tests
  - Database tests
- **Test Environment**:
  - pytest framework
  - Mocked external services
  - Test database
  - CI/CD integration
- **Coverage Goals**:
  - Overall: >80%
  - Critical paths: 100%
  - Error handling: 100%
  - Integration points: 100%

## Documentation Rules
1. **Documentation Location**:
   - Technical docs: `/docs/*`
   - Quick reference: `.cursor/PROJECT_SUMMARY.md`
   - Implementation details: Inline code comments
   - Testing docs: `/docs/testing/*`

2. **Update Triggers**:
   - New feature implementation
   - Workflow changes
   - Schema modifications
   - API integration changes
   - Configuration updates
   - Test updates

3. **What to Update**:
   - This summary file
   - Relevant `/docs` sections
   - Database schema docs
   - API documentation
   - Workflow documentation
   - Test documentation

4. **Documentation Sections**:
   ```
   docs/
   ├── overview.md           # System overview
   ├── database/            # Data structure
   ├── architecture/        # App structure
   ├── workflows/           # Processes
   ├── integrations/        # External APIs
   ├── background/          # Celery tasks
   ├── security/           # Security
   ├── monitoring/         # Monitoring
   ├── configuration/      # Config
   ├── api/                # API docs
   ├── error-handling/     # Errors
   ├── performance/        # Optimization
   ├── maintenance/        # Maintenance
   ├── testing/           # Testing docs
   └── deployment/         # Deployment guides
   ```

## Quick Links
- Full Documentation: [/docs/README.md](/docs/README.md)
- Database Schema: [/docs/database/schema.md](/docs/database/schema.md)
- Workflows: [/docs/workflows/README.md](/docs/workflows/README.md)
- API Reference: [/docs/api/README.md](/docs/api/README.md)
- Testing Guide: [/docs/testing/integration-tests.md](/docs/testing/integration-tests.md)

## Documentation Maintenance Rules
1. **Always**:
   - Update this summary when making significant changes
   - Keep documentation in sync with code
   - Include examples for new features
   - Document error scenarios
   - Update test documentation

2. **Regular Reviews**:
   - Validate documentation accuracy
   - Update outdated information
   - Add missing sections
   - Remove obsolete content
   - Review test coverage

3. **Format**:
   - Use markdown for consistency
   - Include code examples where relevant
   - Keep sections focused and concise
   - Maintain clear hierarchy 