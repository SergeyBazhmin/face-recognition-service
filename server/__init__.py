from flask_cors import CORS
from flask_jwt_extended import JWTManager
import flask
import datetime

app = flask.Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'secret-key'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(days=1)
redis_connection = None
jwt = JWTManager(app)
CORS(app)

import server.api_resources
import server.error_handlers
