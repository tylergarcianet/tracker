from datetime import datetime
from . import main
from .. import db
from ..models import Ticket, Comment, User
from .forms import NewTicketForm, NewCommentForm, ToggleDisableForm, ToggleTicketStatusForm
from flask import render_template, redirect, url_for, abort, flash, session,\
    request, current_app, send_from_directory
from flask_login import login_required, current_user
from ..decorators import admin_required
from werkzeug.utils import secure_filename
from ..email import send_email
import os


@main.route("/", methods=["GET", "POST"])
@main.route("/index", methods=["GET", "POST"])
@login_required
def index():
    if "Open" in request.form or "show_open" not in session:
        session["show_open"] = True
    elif "Closed" in request.form:
        session["show_open"] = False

    filter_options = {"is_open": session["show_open"]}
    if not current_user.isadmin:
        filter_options["user"] = current_user

    page = request.args.get("page", 1, type=int)
    tickets = Ticket.query.filter_by(**filter_options).paginate(page, current_app.config["TICKETS_PER_PAGE"], False)

    next_url = url_for("main.index", page=tickets.next_num) if tickets.has_next else None
    prev_url = url_for("main.index", page=tickets.prev_num) if tickets.has_prev else None

    return render_template("index.html",
                           tickets=tickets.items,
                           next_url=next_url, prev_url=prev_url)


@main.route("/ticket/<int:ticketnum>", methods=["GET", "POST"])
@login_required
def ticket(ticketnum):
    t = Ticket.query.get(ticketnum)

    if not current_user.isadmin and not current_user == t.user:
        abort(403)

    new_comment_form = NewCommentForm()
    if new_comment_form.validate_on_submit():
        c = Comment(body=new_comment_form.commentbody.data,
                    timestamp=datetime.utcnow(),
                    ticket=t,
                    user=current_user._get_current_object())
        db.session.add(c)

        if not t.is_open:
            t.is_open = True
        db.session.commit()

        if current_user.isadmin and t.user.notifications:
            user = t.user
            send_email(t.user.email,
                       "Your Ticket Has Been Updated",
                       "auth/email/ticket_update",
                       user=user,
                       ticketnum=ticketnum)

        return redirect(url_for("main.ticket",
                        ticketnum=ticketnum))

    toggle_ticket_status_form = ToggleTicketStatusForm()
    if toggle_ticket_status_form.validate_on_submit() and not current_user.isadmin and t.user != current_user:
        flash("You are not authorized to do that.")
        return redirect(url_for("main.index"))
    elif toggle_ticket_status_form.validate_on_submit():
        t.toggle_open()
        db.session.commit()
        return redirect(url_for("main.ticket", ticketnum=ticketnum))

    # Uploading file
    if request.method == "POST":
        if "file" not in request.files:
            flash("No file part")
            return redirect(request.url)
        file = request.files["file"]
        if file.filename == "":
            flash("No selected file")
            return redirect(request.url)

        def allowed_file(filename):
            return "." in filename and filename.rsplit(".", 1)[1].lower() in current_app.config["ALLOWED_EXTENSIONS"]

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            checkeddir = os.path.join(current_app.config["UPLOAD_FOLDER"], "{0}/".format(ticketnum))
            if not os.path.exists(checkeddir):
                os.makedirs(checkeddir)
            file.save(os.path.join(checkeddir, filename))
            return redirect(url_for("main.ticket", ticketnum=ticketnum))

    checkeddir = os.path.join(current_app.config["UPLOAD_FOLDER"], "{0}/".format(ticketnum))
    if os.path.exists(checkeddir):
        allfiles = os.listdir(checkeddir)
    else:
        allfiles = None

    return render_template("ticket.html",
                           ticket=t,
                           new_comment_form=new_comment_form,
                           ticket_toggle_status_form=toggle_ticket_status_form,
                           allfiles=allfiles)


@main.route("/files/<ticketnum>/<filename>")
@login_required
def uploaded_file(ticketnum, filename):
    return send_from_directory(os.path.join(current_app.config["UPLOAD_FOLDER"], "{0}/".format(ticketnum)),
                               filename)


@main.route("/new_ticket", methods=["GET", "POST"])
@login_required
def new_ticket():
    form = NewTicketForm()
    if form.validate_on_submit():
        t = Ticket(user=current_user._get_current_object(),
                   tickettitle=form.tickettitle.data,
                   ticketrequest=form.ticketrequest.data,
                   timestamp=datetime.utcnow())
        db.session.add(t)
        db.session.commit()
        return redirect(url_for("main.ticket", ticketnum=t.id))
    return render_template("newticket.html",
                           title="Create a New Ticket",
                           form=form)


@main.route("/admin")
@login_required
@admin_required
def admin():
    users = User.query.all()
    return render_template("admin.html",
                           users=users)


@main.route("/admin/<username>", methods=["GET", "POST"])
@login_required
@admin_required
def user(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        abort(404)
    toggle_disable_form = ToggleDisableForm()
    if toggle_disable_form.validate_on_submit():
        if user.id == 1:
            flash("You cannot disable the root user")
            return redirect(url_for("main.user", username=username))
        if user.disabled:
            user.disabled = False
            flash("{0}'s account has been enabled".format(user.username))
        else:
            user.disabled = True
            flash("{0}'s account has been disabled".format(user.username))
        db.session.add(user)
        return redirect(url_for("main.user", username=user.username))
    return render_template("user.html", user=user, toggle_disable_form=toggle_disable_form)
