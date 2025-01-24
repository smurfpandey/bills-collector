# bills-collector
A small utility to collect bills (in pdf) from email (gmail/zoho) and store in Google Drive

### Run in production

Application consists of following parts:
- Main Webapp (Flask app)
- Background Worker (Celery app)
- Celery Broker (valkey)
- Main Database (postgres)
