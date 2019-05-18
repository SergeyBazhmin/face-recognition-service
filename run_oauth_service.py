from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import\
    JWTManager, create_access_token, create_refresh_token, jwt_refresh_token_required, get_jwt_identity
import datetime
from server.enumerates import Errors

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'secret-key'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(seconds=3)
CORS(app)
jwt = JWTManager(app)


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


@app.route('/get-access-token', methods=['POST'])
def get_access_token():
    data = request.json
    print(data)
    host, password = data['user'], data['password']
    if host is None or password is None:
        return jsonify({
            'ok': False,
            'message': Errors.INCONSISTENT_DATA.value
        }, 401)

    access_token = create_access_token(identity=host)
    refresh_token = create_refresh_token(identity=host)

    return jsonify({
        'ok': True,
        'access_token': access_token,
        'refresh_token': refresh_token,
    })


@app.route('/refresh-access-token', methods=['GET'])
@jwt_refresh_token_required
def refresh_access_token():
    current_user = get_jwt_identity()
    access_token = create_access_token(identity=current_user)
    return jsonify({
        'ok': True,
        'access_token': access_token
    })


if __name__ == '__main__':
    app.run(port=5001)
