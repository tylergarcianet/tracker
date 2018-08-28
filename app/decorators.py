from functools import wraps
from flask import abort
from flask_login import current_user


def admin_required(f):
    """
    View function decorated with this will return a 404 if
    the logged in user is not an admin according to the
    User model
    :param f:
    :return:
    """
    @wraps(f)
    def decorated_view(*args, **kwargs):
        if current_user.isadmin:
            return f(*args, **kwargs)
        abort(403)
    return decorated_view
