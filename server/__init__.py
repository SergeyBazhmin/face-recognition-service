from flask_cors import CORS
from flask_jwt_extended import JWTManager
import flask
from common.settings import server_settings
import redis
import datetime

app = flask.Flask(__name__)
app.config['JWT_SECRET_KEY'] = None
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(days=1)
redis_connection = redis.StrictRedis(host=server_settings.redis_configuration.host,
                                     port=server_settings.redis_configuration.port,
                                     db=server_settings.redis_configuration.db)
jwt = JWTManager(app)
CORS(app)

import server.api_resources
import server.error_handlers
