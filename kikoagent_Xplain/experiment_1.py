from agent import Agent
from log import Log
from postgres import Postgres
import time


class Main:

    def __init__(self, parameters):

        self.log = Log(parameters)
        self.postgres = Postgres(parameters, self.log)
        self.agent = Agent(parameters, self.log, self.postgres)

        # magic_beliefs are for testing only:
        # use it to provide a particular state of mind for Kiko in his awakening
        #{'belief': ['belieftype', 'params']}
        magic_beliefs = {'has_subject': ['cogtition', '']
        #                       , 'disclaimer_visible': ['cogtition', 'yes']
        #         , 'disclaimer_given': ['cogtition', '']
        #                       , 'in_or_out': ['cogtition', 'in']
        #                      ,'which_floor': ['cogtition', 'second']
        #                        ,'which_wing': ['cogtition', 'east']
        #          , 'checkin_info': ['cogtition', '']
        #         , 'type_of_help': ['cogtition', 'find employee']
        #     #   , 'employee_name': ['cogtition', 'k a r i n e']
        # , 'helping': ['cogtition', '']
       #      , 'employee_info_given': ['cogtition', '']
      #  , 'visitor_name': ['cogtition', 'an n a']
       #     , 'type_of_entertainment': ['cogtition', 'freestyle']

        # , 'given_word': ['cogtition', 'test']
        }

        self.agent.load_magic_beliefs(magic_beliefs)

    def run(self):

        # wait for tablet to be ready
        time.sleep(7)

        while not self.agent.sleeping:

            print('>> life loop')
            self.agent.life_loop()

            # try:
            #     self.agent.life_loop()
            # except Exception as error:
            #     self.log.write('ERROR loop: {}'.format(error))


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
            'rejection_tryagain': 10,
            'contact_attempts': 3,
            'experiment_name': 'test'
            }


main = Main(parameters)
main.run()
