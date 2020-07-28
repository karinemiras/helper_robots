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
        magic_beliefs = {'has_subject': ['cogtition', '']
      #                    , 'in_or_out': ['cogtition', 'in']
      #                  ,'which_floor': ['cogtition', 'second']
      #                    ,'which_wing': ['cogtition', 'east']
      # #      , 'checkin_info': ['cogtition', '']
        #     , 'type_of_help': ['cogtition', 'entertainment']
        #     , 'type_of_entertainment': ['cogtition', 'poetry']
        #     , 'waiting_answer': ['cogtition', '']
        #     , 'contact_attempt': ['cogtition', '1']

                         }

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
            'timeout_watchlook': 15,
            'experiment_name': 'test',
            'contact_attempts': 3,
            'corona_max_occupation': 2,
            'wait_to_approach_again': 3
            }


main = Main(parameters)
main.run()
