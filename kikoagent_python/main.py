from social_interaction_cloud.action import ActionRunner
from social_interaction_cloud.basic_connector import BasicSICConnector
from bdi import *
from threading import Semaphore

class KikoAgent:

    def __init__(self,
                 server_ip,
                 robot,
                 dialogflow_key_file,
                 dialogflow_agent_id):

        self.sic = BasicSICConnector(server_ip,
                                     robot,
                                     dialogflow_key_file,
                                     dialogflow_agent_id)

        self.action_runner = ActionRunner(self.sic)
        self.bdi = BDI()

    def run(self):

        self.sic.start()
        self.action_runner.load_waiting_action('set_language', 'en-US')

        # TODO: add loop breaker
        while True:
            self.main()

        #self.sic.stop()

    def main(self):

        self.search_subject()
        self.offer_help()
        self.help()

    def search_subject(self):

        # if has no subject at sight
        if not(self.bdi.has_bdi_role('has_subject', 'belief')):
            print('\nsearching subject')
            self.semaphore_detect = Semaphore(0)
            self.sic.subscribe_touch_listener('RightBumperPressed', self.subject_detected)
            # use touch instead of vision for a while, because it is very unstable... (maybe light related...)
            # self.action_runner.run_vision_listener('people', self.subject_detected, False)
            self.semaphore_detect.acquire(timeout=5)

    def subject_detected(self):

        self.sic.unsubscribe_touch_listener('RightBumperPressed')
        self.bdi.insert('has_subject', 'belief')
        self.bdi.status_bdi('subject_detected')
        self.semaphore_detect.release()

    def offer_help(self):

        # if there is NOT a current offer of help
        if self.bdi.has_bdi_role('has_subject', 'belief') and \
                not(self.bdi.has_bdi_role('help_on_table', 'belief')):

            print('\noffering help')
            self.action_runner.run_waiting_action('say', 'Hi stranger, do you need any help? '
                                                 'Say employee if you wanna find an employee, '
                                                 'or poetry if you want me to improvise poetry.')
            self.bdi.insert('help_on_table', 'belief')
            self.bdi.status_bdi('offer_help')
            self.action_runner.run_waiting_action('speech_recognition', 'type_of_help', 10,
                                                   additional_callback=self.on_intent)

    def help(self):

        if self.bdi.has_bdi_role('type_of_help', 'belief') and \
                not(self.bdi.has_bdi_role('helping', 'belief')):

            print('\nhelping')
            self.action_runner.run_waiting_action('say', 'this is me helping you, lalalal, lalalal, ohohohoh, i help, i hlep')
            self.bdi.insert('helping', 'belief')

    def on_intent(self, intent_name, *args):

        if intent_name == 'type_of_help' and len(args) > 0:
            print(args[0])

            self.bdi.insert('type_of_help', 'belief', str(args[0]))
            self.bdi.status_bdi('on_intent')
            self.action_runner.run_action('say', 'Ok,'+args[0]+'it is.')

        #if intent_name == 'type_of_help' and len(args) > 0:

example = KikoAgent('192.168.1.19',
                    'nao',
                    'kikoagent-iajdfl-9d037d057933.json',
                    'kikoagent-iajdfl')
example.run()
