from transitions import Machine
from social_interaction_cloud.action import ActionRunner
from social_interaction_cloud.basic_connector import BasicSICConnector


class ExampleRobot(object):
    """Example that shows how to impelement a State Machine with pyTransitions. For more information go to
    https://socialrobotics.atlassian.net/wiki/spaces/CBSR/pages/616398873/Python+Examples#State-Machines-with-PyTransitions"""

    states = ['asleep', 'awake', 'introduced', 'got_acquainted', 'goodbye']

    def __init__(self, sic: BasicSICConnector):
        self.sic = sic
        self.action_runner = ActionRunner(self.sic)
        self.machine = Machine(model=self, states=ExampleRobot.states, initial='asleep')

        self.user_model = {}
        self.recognition_manager = {'attempt_success': False,
                                    'attempt_number': 0}

        # Define transitions
        self.machine.add_transition(trigger='start', source='asleep', dest='awake',
                                    before='wake_up', after='introduce')
        self.machine.add_transition(trigger='introduce', source='awake', dest='introduced',
                                    before='introduction', after='get_name')
        self.machine.add_transition(trigger='get_name', source='introduced', dest='asked_name',
                                    before='ask_name', after='get_acquainted')
        self.machine.add_transition(trigger='get_acquainted', source='asked_name', dest='got_acquainted',
                                    conditions='has_name',
                                    before='get_acquainted_with', after='rest')
        self.machine.add_transition(trigger='get_acquainted', source='asked_name', dest='got_acquainted',
                                    unless='has_name',
                                    before='get_acquainted_without', after='rest')
        self.machine.add_transition(trigger='rest', source='*', dest='asleep',
                                    before='saying_goodbye')

    def wake_up(self):
        self.action_runner.load_waiting_action('set_language', 'en-US')
        self.action_runner.load_waiting_action('wake_up')
        self.action_runner.run_loaded_actions()

    def introduction(self):
        self.action_runner.run_waiting_action('say_animated', 'Hi I am Nao and I am a social robot.')

    def ask_name(self):
        while not self.recognition_manager['attempt_success'] and self.recognition_manager['attempt_number'] < 2:
            self.action_runner.run_waiting_action('say', 'What is your name?')
            self.action_runner.run_waiting_action('speech_recognition', 'answer_name', 3,
                                                  additional_callback=self.on_intent)

    def on_intent(self, intent_name, *args):
        if intent_name == 'answer_name' and len(args) > 0:
            self.user_model['name'] = args[0]
            self.recognition_manager['attempt_success'] = True
        elif intent_name == 'fail':
            self.recognition_manager['attempt_number'] += 1

    def has_name(self):
        return 'name' in self.user_model

    def get_acquainted_with(self):
        self.action_runner.run_waiting_action('say_animated', 'Nice to meet you ' + self.user_model['name'])

    def get_acquainted_without(self):
        self.action_runner.run_waiting_action('say_animated', 'Nice to meet you')

    def saying_goodbye(self):
        self.action_runner.run_waiting_action('say_animated', 'Well this was fun.')
        self.action_runner.run_waiting_action('say_animated', 'I will see you around.')
        self.action_runner.run_waiting_action('rest')


class StateMachineExample(object):

    def __init__(self, server_ip, robot, dialogflow_key_file, dialogflow_agent_id):
        self.sic = BasicSICConnector(server_ip, robot, dialogflow_key_file, dialogflow_agent_id)
        self.sic.start()
        self.robot = ExampleRobot(self.sic)

    def run(self):
        self.robot.start()
        self.sic.stop()


example = StateMachineExample('<SIC IP Address>',
                              'nao',
                              '<dialogflow_key_file.json>',
                              '<dialogflow_agent_id>')
example.run()
