from agent import Agent
from log import Log
from postgres import Postgres
import sys

class Main:

    def __init__(self, parameters):

        self.log = Log(parameters)
        self.postgres = Postgres(parameters, self.log)
        self.agent = Agent(parameters, self.log, self.postgres)

        # magic_beliefs are for testing only:
        # use it to provide a particular state of mind for Kiko in his awakening
        #{'belief': ['belieftype', 'params']}
        magic_beliefs = {'has_subject': ['percept', '']}
                         # 'input.unknown': ['percept', ''],
                         # 'speech_text': ['percept', "I'm dick also"]}
        self.agent.load_magic_beliefs(magic_beliefs)

    def run(self):

        while not self.agent.sleeping:

            print('>> life loop')
            self.agent.life_loop()
            # try:
            #     self.agent.life_loop()
            # except Exception as error:
            #     self.log.write('ERROR loop: {}'.format(error))


parameters = {
            'server_ip': '192.168.1.18',
            'robot': 'nao',
            'dialogflow_key_file': 'miscellaneous/kikoagent-iajdfl-9d037d057933.json',
            'dialogflow_agent_id': 'kikoagent-iajdfl',
            'postgres_user': 'postgres',
            'postgres_password': 'nao',
            'postgres_host': '127.0.0.1',
            'postgres_port': '5432',
            'postgres_database': 'kikoagent',
            'timeout_listening': 10,
            'experiment_name': 'test',
            'contact_attempts': 3
            }


main = Main(parameters)
main.run()
