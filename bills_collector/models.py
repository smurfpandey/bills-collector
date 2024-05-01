"""Database models."""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from uuid import uuid4

from flask_login import UserMixin
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.schema import PrimaryKeyConstraint
from sqlalchemy.orm import relationship

from bills_collector.extensions import db

@dataclass
class User(UserMixin, db.Model):
    """User account model."""

    __tablename__ = 'users'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid4, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(40), unique=True, nullable=False)
    password = db.Column(db.LargeBinary(60), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    last_login = db.Column(db.DateTime, default=datetime.now(timezone.utc))

    def __repr__(self):
        return '<User {}>'.format(self.name)

@dataclass
class LinkedAccount(db.Model):
    """Linked account model."""
    id: str
    account_type: str
    user_profile: dict
    expires_at: datetime

    __tablename__ = 'linked_accounts'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid4, nullable=False)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'))
    account_type = db.Column(db.String(50), nullable=False)
    account_id = db.Column(db.String(250), nullable=False)
    access_token = db.Column(db.String(500))
    refresh_token = db.Column(db.String(500))
    token_json = db.Column(JSONB)
    user_profile = db.Column(JSONB)
    expires_at = db.Column(db.DateTime, nullable=False)
    last_update_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))

    #Relationships
    user = relationship('User')

    def __repr__(self):
        return '<Account {}>'.format(self.account_type)

@dataclass
class InboxRule(db.Model):
    """Inbox Rule model"""
    id: str
    account_id: str
    name: str
    email_from: str
    email_subject: str
    attachment_password: str
    destination_folder_id: str
    destination_folder_name: str
    destination_account_id: str

    __tablename__ = 'inbox_rules'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid4, nullable=False)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'))
    account_id = db.Column(UUID(as_uuid=True), db.ForeignKey('linked_accounts.id'))
    name = db.Column(db.String(150), nullable=False)
    email_from = db.Column(db.String(150), nullable=False)
    email_subject = db.Column(db.String(150), nullable=False)
    attachment_password = db.Column(db.String(50), nullable=False)
    destination_folder_id = db.Column(db.String(150))
    destination_folder_name = db.Column(db.String(150))
    destination_account_id = db.Column(UUID(as_uuid=True), db.ForeignKey('linked_accounts.id'))

    last_update_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))

    #Relationships
    user = relationship('User')
    account = relationship('LinkedAccount', foreign_keys=[account_id])
    destination_account = relationship('LinkedAccount', foreign_keys=[destination_account_id])

    def __repr__(self):
        return '<InboxRule {}>'.format(self.id)

@dataclass
class ProcessedEmail(db.Model):
    """Processed Email model"""
    id: str

    __tablename__ = 'processed_emails'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid4, nullable=False)
    email_id = db.Column(db.String(450), nullable=False)
    account_id = db.Column(UUID(as_uuid=True), db.ForeignKey('linked_accounts.id'))
    processed_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))

    account = relationship('LinkedAccount', foreign_keys=[account_id])

    def __repr__(self):
        return '<ProcessedEmail {}>'.format(self.id)
