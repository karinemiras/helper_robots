from social_interaction_cloud.abstract_connector import AbstractSICConnector
from bdi import *

from bs4 import BeautifulSoup
import numpy
import pprint
import random
import requests
import sys
from time import sleep
from threading import Semaphore

class Agent(AbstractSICConnector):

    def __init__(self, server_ip, robot, dialogflow_key_file, dialogflow_agent_id):
        super(Agent, self).__init__(server_ip, robot)

        self.set_dialogflow_key(dialogflow_key_file)
        self.set_dialogflow_agent(dialogflow_agent_id)

        self.speaking_semaphore = Semaphore(0)
        self.watching_semaphore = Semaphore(0)
        self.listening_semaphore = Semaphore(0)

        self.bdi = BDI()
        self.topics = {}

    def run(self):

        self.start()
        self.load_topics()
        self.set_language('en-US')
        sleep(0.1)

        # TODO: add loop breaker? fidelius, sets all beleifs false: NAO, you have to go to sleep immediately, and have nice dreams.
        while True:
            self.main()

        #self.sic.stop()

    def main(self):

        self.search_subject()
        self.offer_help()
        self.help()

    # INI: events processing

    def on_robot_event(self, event):
        print('\n on_robot_event', event)

        if event == 'TextDone':
            self.bdi.drop('speaking', 'belief')
            self.speaking_semaphore.release()

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
            if not (self.bdi.has_bdi_role('has_subject', 'belief')):
                self.bdi.states_bdi('on_robot_event_Touched')
                self.has_subject(True)

    def on_person_detected(self):
        print('\n on_person_detected')
        if not(self.bdi.has_bdi_role('has_subject', 'belief')):
            self.bdi.states_bdi('on_person_detected')
            self.has_subject(True)

    def on_speech_text(self, text):
        print('\n on_speech_text', text)
        if self.bdi.has_bdi_role('speech_text', 'belief'):
            self.bdi.drop('speech_text', 'belief')
        self.bdi.adopt('speech_text', 'belief', text)

    def on_audio_intent(self, *args, intent_name):
        print('\n on_audio_intent', intent_name, args)
        if not(self.bdi.has_bdi_role(intent_name, 'belief')):
            params = ''
            for param in args:
                params += param+'|'
            self.bdi.adopt(intent_name, 'belief', params[0:-1])
        self.bdi.states_bdi('on_audio_intent')
        self.listening_semaphore.release()

    # END: events processing

    def has_subject(self, true_or_false):
        if true_or_false:
            self.bdi.adopt('has_subject', 'belief')
            self.watching_semaphore.release()

    def __say(self, text):
        self.bdi.adopt('speaking', 'belief')
        self.say(text)
        self.speaking_semaphore.acquire()

    def __listen(self, context=''):
        self.set_audio_context(context)
        self.start_listening()
        self.listening_semaphore.acquire(timeout=10)
        self.stop_listening()

    def search_subject(self):
        # if it doesnt believe to have a subject, searches for it by looking
        if not(self.bdi.has_bdi_role('has_subject', 'belief')):
            print('\n> searching subject')
            self.start_looking()
            self.watching_semaphore.acquire()
            self.stop_looking()

    def load_topics(self):
        topics = ['general',
                  'find_employee',
                  'freestyle_poetry']

        for topic in topics:
            self.topics[topic] = {}

        for topic in topics:
            file = open('topics/{}.txt'.format(topic), 'r')
            lines = file.readlines()
            sentence_name = 0
            sentence_variation = 1
            sentence_text = 2
            previous_name = ''
            for line in lines:
                line = line.strip().split('|')
                if line[sentence_name] != previous_name:
                    self.topics[topic][line[sentence_name]] = []
                    previous_name = line[sentence_name]
                self.topics[topic][line[sentence_name]].append(line[sentence_text])
            file.close()

    def get_sentence(self, topic, sentence_name):
        return random.choice(self.topics[topic][sentence_name])

    def offer_help(self):

        # if a person is believed to be near and there is NOT a current offer of help
        if self.bdi.has_bdi_role('has_subject', 'belief') and \
                not(self.bdi.has_bdi_role('type_of_help', 'belief')):
            print('\n> offering help')

            if not(self.bdi.has_bdi_role('offers_on_table', 'belief')):
                self.bdi.adopt('offers_on_table', 'belief')
            self.say_and_wait(answer_belief='type_of_help',
                              say_text=self.get_sentence('general', 'offer_help'),
                              unexpected_answer_params=[self.bdi.role_params('speech_text', 'belief')])

            self.bdi.states_bdi('offer_help')

    # say something and wait for a response; includes fallback;
    def say_and_wait(self,
                     answer_belief, say_text,
                     no_answer_topic='general',
                     no_answer_subtopic='no_answer',
                     no_answer_params=None,
                     unexpected_answer_topic='general',
                     unexpected_answer_subtopic='unexpected_answer',
                     unexpected_answer_params=None):

        # no answer received
        if self.bdi.has_bdi_role('waiting_answer', 'belief') and \
                not(self.bdi.has_bdi_role(answer_belief, 'belief')) and \
                not(self.bdi.has_bdi_role('input.unknown', 'belief')):
            sentence = self.get_sentence(no_answer_topic, no_answer_subtopic)
            if no_answer_params is not None:
                self.__say(sentence.format(*no_answer_params))
            else:
                self.__say(sentence)

        # answer is unexpected
        if self.bdi.has_bdi_role('input.unknown', 'belief'):
            sentence = self.get_sentence(unexpected_answer_topic, unexpected_answer_subtopic)
            if unexpected_answer_params is not None:
                self.__say(sentence.format(*unexpected_answer_params))
            else:
                self.__say(sentence)

            self.bdi.drop('input.unknown', 'belief')
            self.bdi.drop('speech_text', 'belief')

        # say it for the first time
        if not(self.bdi.has_bdi_role('waiting_answer', 'belief')):
            self.__say(say_text)
            self.bdi.adopt('waiting_answer', 'belief')

        self.__listen(answer_belief)

    def help(self):
            
        if self.bdi.has_bdi_role('type_of_help', 'belief'):
            print('\n> helping')
            self.bdi.drop('offers_on_table', 'belief')
            if not(self.bdi.has_bdi_role('helping', 'belief')):
                self.bdi.drop('waiting_answer', 'belief')
            self.bdi.states_bdi('helping')

            if self.bdi.role_params('type_of_help', 'belief') == 'employee':
                self.help_find_employee()
            elif self.bdi.role_params('type_of_help', 'belief') == 'poetry':
                self.help_freestyling_poetry()

    def help_find_employee(self):

        print('\n> finding employee')
        if not(self.bdi.has_bdi_role('helping', 'belief')):
            self.bdi.adopt('helping', 'belief', 'help_find_employee')
        self.say_and_wait(answer_belief='employee_name',
                          say_text=self.get_sentence('find_employee', 'employee_name'),
                          unexpected_answer_params=[self.bdi.role_params('speech_text', 'belief')])
        self.bdi.states_bdi('help_find_employee')

        if self.bdi.has_bdi_role('employee_name', 'belief'):

            if self.bdi.role_params('employee_name', 'belief') == 'Charlie Brown':
                self.__say('Charlie Brown works on the third floor, T345.')
            if self.bdi.role_params('employee_name', 'belief') == 'Bob Dylan':
                self.__say('Bob Dylan works on the second floor, T240.')
            if self.bdi.role_params('employee_name', 'belief') == '':
                self.__say('I could not find '+self.speech_text)

            self.drop_basic_beliefs()
            self.bdi.drop('employee_name', 'belief')
            self.bdi.states_bdi('helped')

    def help_freestyling_poetry(self):

        print('\n> freestyling poetry')
        if not(self.bdi.has_bdi_role('helping', 'belief')):
            self.bdi.adopt('helping', 'belief', 'help_poetry')
        self.say_and_wait(answer_belief='given_word',
                          say_text=self.get_sentence('freestyle_poetry', 'ask_word'),
                          unexpected_answer_topic='freestyle_poetry')
        self.bdi.states_bdi('help_poetry')

        if self.bdi.has_bdi_role('given_word', 'belief'):

            word = self.bdi.role_params('given_word', 'belief')

            response = requests.get(
                'https://www.rhymezone.com/r/rhyme.cgi?Word=' + word + '&typeofrhyme=perfect').text

            soup = BeautifulSoup(response)
            rhymes = []
            for a in soup.find_all('a'):
                if a.get('class') is not None:
                    rhymes.append(a.get_text().replace(u'\xa0', u' '))
            rhymes = numpy.array(rhymes)

            if len(rhymes) > 0:
                sentense = '\\rspd=60\\' + word +', rhymes with '\
                           +rhymes[numpy.random.choice(len(rhymes), 1)][0] \
                           +' \\pau=300\\ '+rhymes[numpy.random.choice(len(rhymes), 1)][0] \
                           +'\\pau=300\\ and '+rhymes[numpy.random.choice(len(rhymes), 1)][0] +'.'

                print(sentense)
                self.__say(sentense)

                self.drop_basic_beliefs()
                self.bdi.drop('given_word', 'belief')
                self.bdi.states_bdi('helped')
            else:
                self.__say('Oh no, I can not rhyme with this word!')
                self.bdi.drop('given_word', 'belief')
                self.bdi.drop('speech_text', 'belief')
                self.bdi.adopt('input.unknown', 'belief')

    def drop_basic_beliefs(self):
        self.bdi.drop('has_subject', 'belief')
        self.bdi.drop('waiting_answer', 'belief')
        self.bdi.drop('type_of_help', 'belief')
        self.bdi.drop('helping', 'belief')
        self.bdi.drop('speech_text', 'belief')


my_connector = Agent(server_ip='192.168.1.19',
                     robot='nao',
                     dialogflow_key_file='kikoagent-iajdfl-9d037d057933.json',
                     dialogflow_agent_id='kikoagent-iajdfl')
my_connector.run()
