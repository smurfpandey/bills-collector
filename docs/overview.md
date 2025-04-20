# System Overview

## Application Type
- Flask Web Application with Celery Background Processing
- Automated PDF bill collection from email to Google Drive

## Technology Stack
- **Web Framework**: Flask
- **Background Processing**: Celery
- **Database**: PostgreSQL
- **External APIs**: 
  - Google APIs (Gmail, Drive)
  - Zoho Mail API

## Core Purpose
The Bills Collector is designed to automate the process of collecting PDF bills from email accounts and storing them in Google Drive. It provides:
- Automated email monitoring
- PDF attachment extraction
- Password-protected PDF handling
- Organized storage in Google Drive
- Multi-account support

## Key Features
- Email monitoring (Gmail/Zoho)
- PDF bill collection
- Google Drive integration
- Password-protected PDF support
- Automated scheduling
- Multi-user support
- Rule-based processing 