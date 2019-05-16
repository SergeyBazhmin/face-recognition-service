from server import jwt
from flask import jsonify
from server.enumerates import Errors


@jwt.unauthorized_loader
def unauthorized_response(_):
    return jsonify({
        'ok': False,
        'message': Errors.JWT_MISSING.value
    }), 401


@jwt.expired_token_loader
def expired_token_response():
    return jsonify({
        'ok': False,
        'message': Errors.JWT_EXPIRED.value
    }), 401


@jwt.invalid_token_loader
def invalid_token_response(_):
    return jsonify({
        'ok': False,
        'message': Errors.JWT_INVALID.value
    }), 401
