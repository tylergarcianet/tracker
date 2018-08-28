from flask import render_template, redirect, request, url_for, flash, g
from flask_login import login_user, login_required, logout_user, current_user
from . import auth
from ..models import User
from .forms import LoginForm, RegistrationForm, ChangePasswordForm,\
    PasswordResetForm, PasswordResetRequestForm, ChangeEmailForm
from .. import db
from ..email import send_email
from datetime import datetime


@auth.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            user.lastloggedin = datetime.utcnow()
            db.session.add(user)
            return redirect(request.args.get("next") or url_for("main.index"))
        flash("Invalid username or password.")
    return render_template("auth/login.html", form=form)


@auth.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.")
    return redirect(url_for("auth.login"))


@auth.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data,
                    email=form.email.data,
                    password=form.password.data)
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        send_email(user.email, "Confirm Your Account",
                   "auth/email/confirm", user=user, token=token)
        flash("A confirmation email has been sent to you by email.")
        return redirect(url_for("main.index"))
    return render_template("auth/register.html", form=form)


@auth.route("/confirm/<token>")
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for("main.index"))
    if current_user.confirm(token):
        flash("You have confirmed your account.")
    else:
        flash("The confirmation link is invalid or has expired.")
    return redirect(url_for("main.index"))


@auth.before_app_request
def before_request():
    if current_user.is_authenticated \
            and not current_user.confirmed \
            and request.endpoint[:5] != "auth.":
        return redirect(url_for("auth.unconfirmed"))


@auth.route("/unconfirmed")
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for("main.index"))
    return render_template("auth/unconfirmed.html")


@auth.route("/confirm")
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_email(current_user.email, "Confirm Your Account",
               "auth/email/confirm", user=current_user, token=token)
    flash("A new confirmation email has been to you by email")
    return redirect(url_for("main.index"))


@auth.route("/account_management", methods=["GET", "POST"])
@login_required
def account_management():
    # This view is currently unused. Replaced by a front-end dropdown menu to individual forms
    changepasswordform = ChangePasswordForm()
    changeemailform = ChangeEmailForm()

    if changepasswordform.validate_on_submit():
        if current_user.verify_password(changepasswordform.oldpassword.data):
            current_user.password = changepasswordform.newpassword.data
            db.session.add(current_user)
            flash("Your password has been updated.")
            return redirect(url_for("main.index"))
        else:
            flash("Invalid Password")

    if changeemailform.validate_on_submit():
        if current_user.verify_password(changeemailform.password.data):
            new_email = changeemailform.email.data
            token = current_user.generate_email_exchange_token(new_email)
            send_email(new_email, "Confirm your email address",
                       "auth/email/change_email",
                       user=current_user, token=token)
        else:
            flash("Invalid email or password.")

    return render_template("auth/accountmanagement.html",
                           changepasswordform=changepasswordform,
                           changeemailform=changeemailform)


@auth.route("/change_password", methods=["GET", "POST"])
@login_required
def change_password():
    changepasswordform = ChangePasswordForm()
    if changepasswordform.validate_on_submit():
        if current_user.verify_password(changepasswordform.oldpassword.data):
            current_user.password = changepasswordform.newpassword.data
            db.session.add(current_user)
            flash("Your password has been updated.")
            return redirect(url_for("main.index"))
        else:
            flash("Invalid Password")

    return render_template("auth/changepassword.html",
                           changepasswordform=changepasswordform)


@auth.route("/change_email", methods=["GET", "POST"])
@login_required
def change_email_request():
    changeemailform = ChangeEmailForm()
    if changeemailform.validate_on_submit():
        if current_user.verify_password(changeemailform.password.data):
            new_email = changeemailform.email.data
            token = current_user.generate_email_exchange_token(new_email)
            send_email(new_email, "Confirm your email address",
                       "auth/email/change_email",
                       user=current_user, token=token)
        else:
            flash("Invalid email or password.")

    return render_template("auth/changeemail.html",
                           changeemailform=changeemailform)


@auth.route("/reset", methods=["GET", "POST"])
def password_reset_request():
    if not current_user.is_anonymous:
        return redirect(url_for("main.index"))
    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            token = user.generate_reset_token()
            send_email(user.email, "Reset Your Password",
                       "auth/email/reset_password",
                       user=user, token=token,
                       next=request.args.get("next"))
        flash("An email with instructions to reset your password has been sent to you.")
        return redirect(url_for("auth.login"))
    return render_template("auth/reset_password.html", form=form)


@auth.route("/invite", methods=["GET", "POST"])
@login_required
def invite():
    """
    TODO: Feature to allow app to open registrations for anyone or use invite-only system.
    :return:
    """
    pass
    return render_template(url_for("main.index"))


@auth.route("/notifications")
def notifications():
    if current_user.notifications:
        current_user.notifications = False
        flash("Email notifications have been disabled")
    else:
        current_user.notifications = True
        flash("Email notifications have been enabled")
    return redirect(url_for("main.index"))


@auth.route("/reset/<token>", methods=["GET", "POST"])
def password_reset(token):
    if not current_user.is_anonymous:
        return redirect(url_for("main.index"))
    form = PasswordResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None:
            return redirect(url_for("main.index"))
        if user.reset_password(token, form.password.data):
            flash("Your password has been updated.")
            return redirect(url_for("auth.login"))
        else:
            return redirect(url_for("main.index"))
    return render_template("auth/reset_password.html", form=form)


@auth.route("/change-email/<token>")
@login_required
def change_email(token):
    if current_user.change_email(token):
        flash("Your email has been updated")
    else:
        flash("Invalid Request")
    return redirect(url_for("main.index"))
