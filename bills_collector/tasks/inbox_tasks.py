"""Email Inbox related tasks"""
from datetime import datetime, timedelta
import base64

from celery.utils.log import get_task_logger
import pikepdf
from pydash import filter_
from sqlalchemy import func

from bills_collector.extensions import celery, db
from bills_collector.integrations import GoogleClient
from bills_collector.models import LinkedAccount, InboxRule


logger = get_task_logger(__name__)

@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    """
        Schedule periodic tasks
    """
    # Resubsribe to notifications about to expire
    sender.add_periodic_task(timedelta(hours=12), check_inbox.s(), name='Check for new email in the Inbox every 12hrs')

@celery.task()
def check_inbox():
    """Check for new emails"""

    logger.info('START:: task execution check_inbox')

    # 1. Get all inbox with atleast 1 rule
    inbox_accounts = db.session.query(
        LinkedAccount.id,
        LinkedAccount.account_type,
        func.count(InboxRule.id).label("Rule_Count")
    ).join(
        InboxRule, InboxRule.account_id == LinkedAccount.id
    ).filter(
        LinkedAccount.account_type.in_(['gmail', 'zoho'])
    ).group_by(
        LinkedAccount.id
    ).having(func.count(InboxRule.id) > 0).all()

    # 2. For each Inbox, get all rules
    for account in inbox_accounts:
        logger.info(f"Account: {account.id}, {account.Rule_Count}")

        process_gmail_inbox.delay(account.id)
        # 3. For each rule, check for any new emails in last 24hr

            # 4. For every email, check if it has already been processed
            # 4.1. If not, download and save attachment to destination

@celery.task()
def process_gmail_inbox(inbox_id):
    """Fetch emails as per the rules for this inbox"""

    account = LinkedAccount.query.filter(
        LinkedAccount.id == inbox_id
    ).first()

    inbox_rules = InboxRule.query.filter(
        InboxRule.account_id == inbox_id
    ).all()

    dict_account = {
        'id': account.id,
        'access_token': account.access_token
    }

    google_app = GoogleClient(token=account.token_json)

    for rule in inbox_rules:
        emails = google_app.fetch_inbox_emails(from_address=rule.email_from, subject_text=rule.email_subject)
        if 'messages' in emails:
            for email in emails['messages']:
                email_msg = google_app.fetch_one_email(email['id'])

                payload = email_msg['payload']
                payload_parts = payload.get('parts', [])
                for part in payload_parts:
                    payload_mime = part['mimeType']
                    logger.info(f"Payload Mime: {payload_mime}")

                    if payload_mime == 'application/octet-stream' or payload_mime == 'application/pdf':
                        file_name = part['filename']
                        attachment_id = part['body']['attachmentId']
                        logger.info(f"Attachment: {attachment_id}, {file_name}")
                        if file_name.lower().endswith('.pdf'):
                            attachment = google_app.get_email_attachment(message_id=email['id'], attachment_id=attachment_id)
                            file_data = base64.urlsafe_b64decode(attachment['data'].encode('UTF-8'))
                            file_path = f'tmp/{file_name}'
                            with open(file_path,"wb") as f:
                                f.write(file_data)

                            pdf = pikepdf.open(file_path, password=rule.attachment_password)
                            pdf.save(file_path + "_no_password.pdf")





