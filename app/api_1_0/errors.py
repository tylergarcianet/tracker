from flask import jsonify


def forbidden(message):
    response = jsonify({"error": "Forbidden", "message": message})
    response.status_code = 403
    return response
