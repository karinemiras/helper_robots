from social_interaction_cloud.action import ActionRunner
from social_interaction_cloud.basic_connector import BasicSICConnector


class Example:
    """Example that uses speech recognition. Prerequisites are the availability of a dialogflow_key_file,
    a dialogflow_agent_id, and a running Dialogflow service. For help meeting these Prerequisites see
    https://socialrobotics.atlassian.net/wiki/spaces/CBSR/pages/260276225/The+Social+Interaction+Cloud+Manual"""

    def __init__(self, server_ip, robot, dialogflow_key_file, dialogflow_agent_id):
        self.sic = BasicSICConnector(server_ip, robot, dialogflow_key_file, dialogflow_agent_id)
        self.action_runner = ActionRunner(self.sic)

        self.user_model = {}
        self.recognition_manager = {'attempt_success': False,
                                    'attempt_number': 0}

    def run(self):
        self.sic.start()

        self.action_runner.load_waiting_action('set_language', 'en-US')
        self.action_runner.load_waiting_action('wake_up')
        self.action_runner.run_loaded_actions()

        while not self.recognition_manager['attempt_success'] and self.recognition_manager['attempt_number'] < 2:
            self.action_runner.run_waiting_action('say', 'Hi I am Nao. What is your name?')
            self.action_runner.run_waiting_action('speech_recognition', 'answer_name', 3, additional_callback=self.on_intent)
        self.reset_recognition_management()

        if 'name' in self.user_model:
            self.action_runner.run_waiting_action('say', 'Nice to meet you ' + self.user_model['name'])
        else:
            self.action_runner.run_waiting_action('say', 'Nice to meet you')

        self.action_runner.run_waiting_action('rest')
        self.sic.stop()

    def on_intent(self, intent_name, *args):
        if intent_name == 'answer_name' and len(args) > 0:
            self.user_model['name'] = args[0]
            self.recognition_manager['attempt_success'] = True
        elif intent_name == 'fail':
            self.recognition_manager['attempt_number'] += 1

    def reset_recognition_management(self):
        self.recognition_manager.update({'attempt_success': False,
                                         'attempt_number': 0})


example = Example('192.168.1.19',
                  'nao',
                  'silly.json',
                  'answer-name-pgocqj')
example.run()
