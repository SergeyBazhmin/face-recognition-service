import eventlet
eventlet.monkey_patch()

from server.websocket import socket_io
from server.arg_parser import parser
import server


if __name__ == '__main__':
    args = parser.parse_args()
    server.app.config['JWT_SECRET_KEY'] = args.jwt_secret_key
    socket_io.run(server.app, port=args.server_port, debug=True)
