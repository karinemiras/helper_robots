from social_interaction_cloud.abstract_connector import AbstractSICConnector
from xplain import Xplain
from time import sleep


class SIC(AbstractSICConnector):

    def __init__(self,
                 agent,
                 parameters
                 ):

        super(SIC, self).__init__(parameters['server_ip'], parameters['robot'])

        self.set_dialogflow_key(parameters['dialogflow_key_file'])
        self.set_dialogflow_agent(parameters['dialogflow_agent_id'])
        self.agent = agent

        self.start()
        self.set_language('en-US')
        sleep(0.1)

    # events processing

    def on_robot_event(self, event):
        print('\n on_robot_event', event)

        if event == 'TextDone':
            self.agent.speaking_semaphore.release()

        # always listening to touch sensors; uses touch to identify that there is a subject
        touch_sensors = ['RightBumperPressed',
                         'LeftBumperPressed',
                         'BackBumperPressed',
                         'FrontTactilTouched',
                         'MiddleTactilTouched',
                         'RearTactilTouched',
                         'HandRightBackTouched',
                         'HandRightLeftTouched',
                         'HandRightRightTouched',
                         'HandLeftBackTouched',
                         'HandLeftLeftTouched',
                         'HandLeftRightTouched']
        if event in touch_sensors:
            self.agent.has_subject(True)

    def on_person_detected(self):
        print('\n on_person_detected')

        self.agent.has_subject(True)

    def on_speech_text(self, text):
        print('\n on_speech_text', text)

        self.agent.xplain.drop('speech_text')
        self.agent.xplain.adopt('speech_text', 'percept', text)

    def on_audio_intent(self, *args, intent_name):
        print('\n on_audio_intent', intent_name, args)

        params = ''
        for param in args:
            params += param+'|'
        self.agent.xplain.adopt(intent_name, 'percept', params[0:-1])

        self.agent.listening_semaphore.release()

        # magic sentence to stop Kiko safely:
        # Kiko, you have to stop, sleep immediately, and have nice dreams.
        if self.agent.xplain.is_belief('sleep_order'):
            self.agent.dropall_and_sleep()


