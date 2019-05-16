from background.adapters import adapter_registry
from background.adapters.db_enumerates import Database

import argparse

parser = argparse.ArgumentParser()

parser.add_argument('-pr', '--provider', type=str, required=True)
parser.add_argument('-db', '--database', type=str, required=True)
parser.add_argument('-host', '--host', type=str, required=True)
parser.add_argument('-p', '--port', type=int, required=True)
parser.add_argument('-u', '--user', type=str, required=True)
parser.add_argument('-psw', '--password', type=str, required=True)
parser.add_argument('-n', '--table_name', type=str, required=True)
parser.add_argument('-n_cols', '--n_cols', type=int, required=True)


if __name__ == '__main__':
    args = parser.parse_args()

    provider = args.provider
    db = args.database
    host = args.host
    port = args.port
    user = args.user
    psw = args.password
    table_name = args.table_name
    n_cols = int(args.n_cols)

    if provider == 'postgresql':
        adapter = adapter_registry[Database(provider)](table_name, None)
    else:
        adapter = adapter_registry[Database(provider)](table_name)

    adapter.connect(host=host,
                    port=port,
                    user=user,
                    password=psw,
                    database=db)
    adapter.create_table(n_cols)
