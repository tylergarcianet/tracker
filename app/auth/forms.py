from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, ValidationError
from wtforms.validators import Email, DataRequired, Length, EqualTo, Regexp  # Required is depracated
from ..models import User


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[Email(), DataRequired(), Length(1, 64)])
    password = PasswordField("Password", validators=[DataRequired()])
    remember_me = BooleanField("Keep me logged in")
    submit = SubmitField("Log In")


class RegistrationForm(FlaskForm):
    username = StringField("Username", validators=[
        DataRequired(), Length(1, 64), Regexp("^[A-Za-z][A-Za-z0-9_.]*$", 0,
                                              "Usernames must have only letters, "
                                              "numbers, dots or underscores")])
    email = StringField("Email", validators=[DataRequired(), Length(1, 64), Email()])
    password = PasswordField("Password", validators=[DataRequired(), Length(1, 64),
                                                     EqualTo("password2", message="Passwords must match.")])
    password2 = PasswordField("Confirm password", validators=[DataRequired()])
    submit = SubmitField("Register")

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError("Email already registered.")


class RegistrationForm2(FlaskForm):
    username = StringField("Username", validators=[
        DataRequired(), Length(1, 64), Regexp("^[A-Za-z][A-Za-z0-9_.]*$", 0,
                                              "Usernames must have only letters, "
                                              "numbers, dots or underscores")])
    email = StringField("Email", validators=[DataRequired(), Length(1, 64), Email()])
    password = PasswordField("Password", validators=[DataRequired(), Length(1, 64),
                                                     EqualTo("password2", message="Passwords must match.")])
    password2 = PasswordField("Confirm password", validators=[DataRequired()])
    submit = SubmitField("Register")

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError("Email already registered.")


class InviteForm(FlaskForm):
    # TODO Part for optional invite system
    pass


class ChangePasswordForm(FlaskForm):
    oldpassword = PasswordField("Old Password", validators=[DataRequired()])
    newpassword = PasswordField("New Password", validators=[
        DataRequired(), EqualTo("newpassword2", message="Passwords do not match")])
    newpassword2 = PasswordField("Confirm Password", validators=[DataRequired()])
    submit = SubmitField("Change Password")


class ChangeEmailForm(FlaskForm):
    email = StringField("New Email", validators=[DataRequired(), Length(1, 64), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Change Email")

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError("Email already in use.")


class PasswordResetRequestForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Length(1, 64), Email()])
    submit = SubmitField("Reset Password")


class PasswordResetForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Length(1, 64), Email()])
    password = PasswordField("New Password", validators=[
        DataRequired(), EqualTo("password2", message="Passwords do not match")])
    password2 = PasswordField("Confirm Password", validators=[DataRequired()])
    submit = SubmitField("Reset Password")

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first() is None:
            raise ValidationError("Unknown email address.")
