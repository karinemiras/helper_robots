from xplain import Xplain
from postgres import Postgres

parameters = {
            'postgres_user': 'postgres',
            'postgres_password': 'nao',
            'postgres_host': '127.0.0.1',
            'postgres_port': '5432',
            'postgres_database': 'kikoagent',
            }

xplain = Xplain(Postgres(parameters, ''))

print('EXPLANATIONS:\n')
explanations = xplain.get_all_explanations()




