from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id         = db.Column(db.Integer, primary_key=True)
    username   = db.Column(db.String(80), unique=True, nullable=False)
    email      = db.Column(db.String(120), unique=True, nullable=False)
    password   = db.Column(db.String(256), nullable=False)
    role       = db.Column(db.String(20), default='user')   # 'admin' or 'user'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    tickets = db.relationship('Ticket', backref='owner', lazy=True)

    def set_password(self, raw):
        self.password = generate_password_hash(raw)

    def check_password(self, raw):
        return check_password_hash(self.password, raw)

    @property
    def is_admin(self):
        return self.role == 'admin'


class NetworkDevice(db.Model):
    __tablename__ = 'network_devices'

    id          = db.Column(db.Integer, primary_key=True)
    name        = db.Column(db.String(100), nullable=False)
    host        = db.Column(db.String(255), nullable=False)   # IP or domain
    description = db.Column(db.String(255))
    added_by    = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)

    logs = db.relationship('NetworkLog', backref='device', lazy=True,
                           cascade='all, delete-orphan')


class NetworkLog(db.Model):
    __tablename__ = 'network_logs'

    id          = db.Column(db.Integer, primary_key=True)
    device_id   = db.Column(db.Integer, db.ForeignKey('network_devices.id'),
                            nullable=False)
    status      = db.Column(db.String(10), nullable=False)  # 'UP' or 'DOWN'
    latency_ms  = db.Column(db.Float)                       # None if DOWN
    checked_at  = db.Column(db.DateTime, default=datetime.utcnow)


class Ticket(db.Model):
    __tablename__ = 'tickets'

    id          = db.Column(db.Integer, primary_key=True)
    title       = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    priority    = db.Column(db.String(20), default='Medium')  # Low/Medium/High/Critical
    status      = db.Column(db.String(20), default='Open')    # Open/In Progress/Closed
    device_id   = db.Column(db.Integer, db.ForeignKey('network_devices.id'), nullable=True)
    user_id     = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at  = db.Column(db.DateTime, default=datetime.utcnow,
                            onupdate=datetime.utcnow)

    comments = db.relationship('TicketComment', backref='ticket', lazy=True,
                               cascade='all, delete-orphan')
    device   = db.relationship('NetworkDevice', backref='tickets')


class TicketComment(db.Model):
    __tablename__ = 'ticket_comments'

    id         = db.Column(db.Integer, primary_key=True)
    ticket_id  = db.Column(db.Integer, db.ForeignKey('tickets.id'), nullable=False)
    user_id    = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    comment    = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    author = db.relationship('User', backref='comments')
