from social_interaction_cloud.abstract_connector import AbstractSICConnector
from time import sleep


class SIC(AbstractSICConnector):

    def __init__(self,
                 agent,
                 parameters
                 ):

        super(SIC, self).__init__(parameters['server_ip'])

        self.set_dialogflow_key(parameters['dialogflow_key_file'])
        self.set_dialogflow_agent(parameters['dialogflow_agent_id'])
        self.set_dialogflow_language('en-US')
        self.agent = agent

        self.start()
        self.set_language('en-US')
        sleep(0.1)

    # events processing

    def on_event(self, event):
        print('\n on_robot_event', event)

        if event == 'TextDone':
            self.agent.speaking_semaphore.release()

    def on_person_detected(self):
        print('\n on_person_detected')

        self.agent.xplain.adopt('seen_subject', 'cognition')
        if self.agent.xplain.is_belief('looking'):
            self.agent.looking_semaphore.release()
        self.agent.has_subject()

    # def on_face_recognized(self, identifier):
    #     print('\n on_face_recognized', identifier)

        #self.agent.xplain.adopt('familiar_subject', 'cognition')

    def on_audio_intent(self, detection_result):
        print('\n on_audio_intent',detection_result)

        intent_name = detection_result.intent
        confidence = detection_result.confidence
        speech_text = detection_result.text
        params = ''

        if len(detection_result.parameters) > 0:
            for param in detection_result.parameters:
                print(param, detection_result.parameters[param].string_value)
                params += detection_result.parameters[param].string_value + '|'
            params = params[0:-1]

        self.agent.xplain.adopt(intent_name, 'cognition', params)

        missing_params = False
        # if this intent expects params and the params received are not the expected ones
        if intent_name in self.agent.xplain.get_intents_entities():
            if params not in self.agent.xplain.get_intents_entities()[intent_name]:
                missing_params = True

        self.agent.xplain.drop('speech_text')
        # intents that miss due params or return undue values should be dropped
        if missing_params and intent_name != 'input.unknown':
            self.agent.xplain.drop(intent_name)
            self.agent.xplain.adopt('speech_text', 'cognition', params)

        # updates rhe speech to text with exact content, unless something undue was extracted as param
        else:
            self.agent.xplain.adopt('speech_text', 'cognition', speech_text)

        # due intents
        if intent_name != 'input.unknown':

            self.agent.xplain.drop('contact_attempt')

            # due intents with missing params: force new request of params
            if missing_params:
                self.agent.xplain.adopt('input.unknown', 'cognition')
            else:
                self.agent.xplain.drop('speech_text')
                self.agent.xplain.drop('waiting_answer')

        # magic sentence to stop Kiko safely:
        # Kiko, you have to stop, sleep immediately, and have nice dreams.
        if self.agent.xplain.is_belief('sleep_order'):
            self.agent.dropall_and_sleep()

        if self.agent.xplain.is_belief('proactive_subject'):
            self.agent.has_subject()
        else:
            if self.agent.xplain.is_belief('listening'):
                self.agent.listening_semaphore.release()
            if self.agent.xplain.is_belief('listening_looking'):
                self.agent.listening_looking_semaphore.release()

