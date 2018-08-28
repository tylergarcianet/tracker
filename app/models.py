from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from . import login_manager
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app
from datetime import datetime


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Ticket(db.Model):
    __tablename__ = "tickets"
    id = db.Column(db.Integer, primary_key=True)
    tickettitle = db.Column(db.String, index=True)
    ticketrequest = db.Column(db.String, index=True)  # TODO change type from String to Text
    timestamp = db.Column(db.DateTime)  # time the ticket is created
    comments = db.relationship("Comment", backref="ticket", lazy="dynamic")
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))

    is_open = db.Column(db.Boolean, default=True)

    def toggle_open(self):
        if not self.is_open:
            self.is_open = True
        else:
            self.is_open = False

    def __repr__(self):
        return "<TicketNum: %s>" % self.id


class Comment(db.Model):
    __tablename__ = "comments"
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String)  # TODO change type from String to Text
    timestamp = db.Column(db.DateTime)

    ticket_id = db.Column(db.Integer, db.ForeignKey("tickets.id"))
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))

    def __repr__(self):
        return "<Comment %s %r %s>" % (self.id, self.body, self.ticket)


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    email = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean, default=False)
    isadmin = db.Column(db.Boolean, default=False)
    accountcreated = db.Column(db.DateTime, default=datetime.utcnow)
    lastloggedin = db.Column(db.DateTime, default=datetime.utcnow)
    disabled = db.Column(db.Boolean, default=False)
    notifications = db.Column(db.Boolean, default=True)

    tickets = db.relationship("Ticket", backref="user", lazy="dynamic")
    comments = db.relationship("Comment", backref="user", lazy="dynamic")

    def __repr__(self):
        return "<User %r>" % self.email

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.email == current_app.config["TRACKER_ADMIN"]:
            self.isadmin = True

    @property
    def password(self):
        raise AttributeError("password is not a readable attribute")

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config["SECRET_KEY"], expiration)
        return s.dumps({"confirm": self.id})

    def confirm(self, token):
        s = Serializer(current_app.config["SECRET_KEY"])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get("confirm") != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    def generate_reset_token(self, expiration=3600):
        s = Serializer(current_app.config["SECRET_KEY"], expiration)
        return s.dumps({"reset": self.id})

    def generate_email_change_token(self, new_email, expiration=3600):
        s = Serializer(current_app.config["SECRET_KEY"], expiration)
        return s.dumps({"change_email": self.id, "new_email": new_email})

    def change_email(self, token):
        s = Serializer(current_app.config["SECRET_KEY"])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get("change_email") != self.id:
            return False
        new_email = data.get("new_email")
        if new_email is None:
            return False
        if self.query.filter_by(email=new_email).first():
            return False
        self.email = new_email
        db.session.add(self)
        return True

    def reset_password(self, token, new_password):
        s = Serializer(current_app.config["SECRET_KEY"])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get("reset") != self.id:
            return False
        self.password = new_password
        db.session.add(self)
        return True
