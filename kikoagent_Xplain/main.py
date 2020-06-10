from agent import Agent


class Main:

    def __init__(self, parameters):

        self.agent = Agent(parameters)

    def run(self):

        # TODO: add loop breaker? fidelius, sets all
        #  beleifs false: NAO, you have to sleep immediately, and have nice dreams.
        while True:
            print('>> loop')
            self.agent.life_loop()
            # try:
            #     self.agent.life_loop()
            # except Exception as error:
            #     print('ERROR loop:', error)

        self.agent.sic.stop()


parameters = {
            'server_ip': '192.168.1.19',
            'robot': 'nao',
            'dialogflow_key_file': 'kikoagent-iajdfl-9d037d057933.json',
            'dialogflow_agent_id': 'kikoagent-iajdfl',
            'timeout_listing': 30,
            'postgres_user': 'postgres',
            'postgres_password': 'nao',
            'postgres_host': '127.0.0.1',
            'postgres_port': '5432',
            'postgres_database': 'kikoagent',
            }


main = Main(parameters)
main.run()
