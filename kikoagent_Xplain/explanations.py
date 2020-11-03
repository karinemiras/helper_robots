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

# use time_ini and time_end to filter time-frame of actions
# example: 2020-11-03 13:50:23.5
time_ini = None
time_end = None

explanations = xplain.get_all_explanations(time_ini, time_end)




