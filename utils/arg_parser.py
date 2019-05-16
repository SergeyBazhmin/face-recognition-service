import argparse

parser = argparse.ArgumentParser()

parser.add_argument('-jwt',
                    '--use_jwt',
                    help='Enable/Disable json web token usage',
                    default=False,
                    type=bool,
                    required=False)

parser.add_argument('-rh',
                    '--redis_host',
                    help='Redis server host',
                    type=str,
                    required=True)

parser.add_argument('-rp', '--redis_port',
                    help='Redis Server port',
                    type=int,
                    required=True)

parser.add_argument('-rdb',
                    '--redis_db',
                    help='Redis Server database',
                    type=int,
                    required=True)
