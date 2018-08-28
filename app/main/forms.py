from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired


class NewTicketForm(FlaskForm):
    tickettitle = StringField("Enter Ticket Title", validators=[DataRequired()])
    ticketrequest = TextAreaField("Your Request", validators=[DataRequired()])
    submit = SubmitField("Submit")


class NewCommentForm(FlaskForm):
    commentbody = TextAreaField("Enter your comment", validators=[DataRequired()])
    submit = SubmitField("Submit")


class ToggleDisableForm(FlaskForm):
    submit = SubmitField("Disable/Enable")


class ToggleTicketStatusForm(FlaskForm):
    submit = SubmitField("Open/Close Ticket")