from xplain import Xplain
from time import sleep
from os import system

parameters = {
            'postgres_user': 'postgres',
            'postgres_password': 'nao',
            'postgres_host': '127.0.0.1',
            'postgres_port': '5432',
            'postgres_database': 'kikoagent',
            }

xplain = Xplain(parameters)

while True:
    system('clear')
    xplain.summary_facts()
    sleep(1)

