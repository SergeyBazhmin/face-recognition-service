import eventlet
eventlet.monkey_patch()

from server.settings import server_settings, RedisConfiguration
from server.websocket import socket_io
import server
from utils.arg_parser import parser
import redis


if __name__ == '__main__':
    args = parser.parse_args()
    server_settings.use_oauth = args.use_jwt
    server_settings.redis = RedisConfiguration(args.redis_host, args.redis_port, args.redis_db)
    server.redis_connection = redis.StrictRedis(host=args.redis_host, port=args.redis_port, db=args.redis_db)
    socket_io.run(server.app, port=args.server_port)
