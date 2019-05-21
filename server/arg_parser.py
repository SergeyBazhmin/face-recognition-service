import argparse

parser = argparse.ArgumentParser()

parser.add_argument('-jwt',
                    '--jwt_secret_key',
                    help='Jwt secret key',
                    default=False,
                    type=str,
                    required=False)

parser.add_argument('-p',
                    '--server_port',
                    help='Server port',
                    default=5000,
                    type=int,
                    required=False)
