from agent import Agent
from log import Log
from postgres import Postgres
import time


class Main:

    def __init__(self, parameters):

        self.log = Log(parameters)
        self.postgres = Postgres(parameters, self.log)
        self.agent = Agent(parameters, self.log, self.postgres)

        # !magic_beliefs are for testing only! ###
        # use it to provide a particular state of mind for Kiko in his awakening
        # magic_beliefs = {'has_subject': ['cognition', ''] ...}
        # self.agent.load_magic_beliefs(magic_beliefs)
        # !magic_beliefs are for testing only! ###

    def run(self):

        # wait for tablet to be ready
        time.sleep(7)

        while not self.agent.sleeping:

            try:
                print('>> life loop')
                self.agent.life_loop()
            except Exception as error:
                self.log.write('ERROR loop: {}'.format(error))


parameters = {
            'server_ip': 'localhost',
            'robot': 'nao',
            'dialogflow_key_file': 'miscellaneous/kikoagent-iajdfl-9d037d057933.json',
            'dialogflow_agent_id': 'kikoagent-iajdfl',
            'postgres_user': 'postgres',
            'postgres_password': 'nao',
            'postgres_host': '127.0.0.1',
            'postgres_port': '5432',
            'postgres_database': 'kikoagent',
            'timeout_listening': 10,
            'timeout_watchlook': 15,
            'rejection_tryagain': 3,
            'contact_attempts': 3,
            'experiment_name': 'experiment_1'
            }


main = Main(parameters)
main.run()
