from social_interaction_cloud.abstract_connector import AbstractSICConnector
from time import sleep
from bdi import *
from threading import Semaphore
import sys
import requests
from bs4 import BeautifulSoup
import numpy

class Agent(AbstractSICConnector):

    def __init__(self, server_ip, robot, dialogflow_key_file, dialogflow_agent_id):
        super(Agent, self).__init__(server_ip, robot)

        self.set_dialogflow_key(dialogflow_key_file)
        self.set_dialogflow_agent(dialogflow_agent_id)

        self.speech_text = ''

        self.speaking_semaphore = Semaphore(0)
        self.watching_semaphore = Semaphore(0)
        self.listening_semaphore = Semaphore(0)

        self.bdi = BDI()

    def run(self):

        self.start()

        self.set_language('en-US')
        sleep(0.1)

        # TODO: add loop breaker
        while True:
            self.main()

        #self.sic.stop()

    def main(self):

        self.search_subject()
        self.offer_help()
        self.help()

    def on_robot_event(self, event):
        print('event', event)
        if event == 'TextDone':
            self.bdi.drop('speaking', 'belief')
            self.bdi.states_bdi('on_robot_event_TextDone')
            self.speaking_semaphore.release()

        # TODO or any other touch
        if event == 'RightBumperPressed':
            if not (self.bdi.has_bdi_role('has_subject', 'belief')):
                self.bdi.adopt('has_subject', 'belief')
                self.bdi.states_bdi('on_person_detected')
                self.watching_semaphore.release()

    def on_person_detected(self):
        if not(self.bdi.has_bdi_role('has_subject', 'belief')):
            self.bdi.adopt('has_subject', 'belief')
            self.bdi.states_bdi('on_person_detected')
            self.watching_semaphore.release()

    def on_speech_text(self, text):
        print('on_speech_text', text)
        self.speech_text = text

    def on_audio_intent(self, *args, intent_name):
        print('on_audio_intent', intent_name)

        print(args)
        if len(args) > 0:
            temp = args[0]
        else:
            temp = ''

        self.bdi.adopt(intent_name, 'belief', str(temp))
        self.bdi.states_bdi('on_audio_intent')
        self.listening_semaphore.release()

    def __say(self, text):
        self.bdi.adopt('speaking', 'belief')
        self.say(text)
        self.speaking_semaphore.acquire()

    def __listen(self, context=''):
        self.speech_text = ''
        self.set_audio_context(context)
        self.start_listening()
        self.listening_semaphore.acquire(timeout=10)
        self.stop_listening()

    def search_subject(self):
        # if has no subject at sight
        if not(self.bdi.has_bdi_role('has_subject', 'belief')):
            print('\nsearching subject')
            self.start_looking()
            self.watching_semaphore.acquire(timeout=10)
            self.stop_looking()

    def offer_help(self):

        # if there is NOT a current offer of help
        if self.bdi.has_bdi_role('has_subject', 'belief') and not(self.bdi.has_bdi_role('type_of_help', 'belief')) :

            print('\noffering help')

            ### make this part reusable ###
            if not(self.bdi.has_bdi_role('offer_help_on_table', 'belief')):
                self.__say('Hi, do you need any help? Say employee if you wanna find an employee, or poetry if you want me to improvise poetry.')

            if self.bdi.has_bdi_role('offer_help_on_table', 'belief') and  \
               not(self.bdi.has_bdi_role('type_of_help', 'belief')) and \
               not(self.bdi.has_bdi_role('input.unknown', 'belief')):
                self.__say('Did you say anything? I did not understand you.')

            if self.bdi.has_bdi_role('input.unknown', 'belief'):
                self.bdi.drop('input.unknown', 'belief')
                self.__say("Can you please reformulate, I don't know what you mean by " + self.speech_text)



            if not(self.bdi.has_bdi_role('offer_help_on_table', 'belief')):
                self.bdi.adopt('offer_help_on_table', 'belief')

            self.bdi.states_bdi('offer_help')
            self.__listen('type_of_help')

    def help(self):
            
        if self.bdi.has_bdi_role('type_of_help', 'belief'): #and \
              #  not(self.bdi.has_bdi_role('helping', 'belief')):

            print('\nhelping')
            #self.bdi.adopt('helping', 'belief')

            if self.bdi.role_params('type_of_help', 'belief') == 'employee':
                self.help_find_employee()

            elif self.bdi.role_params('type_of_help', 'belief') == 'poetry':
                self.help_poetry()

    def help_find_employee(self):

        ### make this part reusable ###
        if not (self.bdi.has_bdi_role('waiting_response', 'belief')):
            self.__say('What is the name of the employee?')

        if self.bdi.has_bdi_role('waiting_response', 'belief') and \
                not (self.bdi.has_bdi_role('employee_name', 'belief')) and \
                not (self.bdi.has_bdi_role('input.unknown', 'belief')):
            self.__say('Can you please repeat? I did not hear you.')

        if self.bdi.has_bdi_role('input.unknown', 'belief'):
            self.bdi.drop('input.unknown', 'belief')
            self.__say("Can you please reformulate, I don't know what you mean by " + self.speech_text)

        if not(self.bdi.has_bdi_role('waiting_response', 'belief')):
            self.bdi.adopt('waiting_response', 'belief', 'offer_help')

        self.bdi.states_bdi('help_find_employee')
        self.__listen('employee_name')
        ###

        if self.bdi.has_bdi_role('employee_name', 'belief'):

            if self.bdi.role_params('employee_name', 'belief') == 'Charlie Brown':
                self.__say('Charlie Brown works on the third floor, T345.')

            if self.bdi.role_params('employee_name', 'belief') == 'Bob Dylan':
                self.__say('Bob Dylan works on the second floor, T240.')

            if self.bdi.role_params('employee_name', 'belief') == '':
                self.__say('I could not find '+self.speech_text)
            else:

                print('passosususususususus')
                # when helping is accomplished, drop idle bdi roles
                self.bdi.drop('has_subject', 'belief')
                self.bdi.drop('waiting_response', 'belief')
                self.bdi.drop('type_of_help', 'belief')
                self.bdi.drop('offer_help_on_table', 'belief')

                #self.bdi.drop('helping', 'belief')
                self.bdi.states_bdi('helped')

    def help_poetry(self):
        ### make this part reusable ###
        if not (self.bdi.has_bdi_role('waiting_response', 'belief')):
            self.__say('Give me a word!')

        if self.bdi.has_bdi_role('waiting_response', 'belief') and \
                not (self.bdi.has_bdi_role('given_word', 'belief')) and \
                not (self.bdi.has_bdi_role('input.unknown', 'belief')):
            self.__say('Can you please repeat? I did not hear you.')

        if self.bdi.has_bdi_role('input.unknown', 'belief'):
            self.bdi.drop('input.unknown', 'belief')
            self.__say("Can you please reformulate, I don't know what you mean by " + self.speech_text)

        if not (self.bdi.has_bdi_role('waiting_response', 'belief')):
            self.bdi.adopt('waiting_response', 'belief', 'offer_help')

        self.bdi.states_bdi('help_poetry')
        self.__listen('given_word')
        ###

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

                # when helping is accomplished, drop idle bdi roles
                self.bdi.drop('has_subject', 'belief')
                self.bdi.drop('waiting_response', 'belief')
                self.bdi.drop('type_of_help', 'belief')
                self.bdi.drop('given_word', 'belief')
                self.bdi.drop('offer_help_on_table', 'belief')
                # self.bdi.drop('helping', 'belief')
                self.bdi.states_bdi('helped')
            else:
                self.bdi.drop('given_word', 'belief')

my_connector = Agent(server_ip='192.168.1.19',
                     robot='nao',
                     dialogflow_key_file='kikoagent-iajdfl-9d037d057933.json',
                     dialogflow_agent_id='kikoagent-iajdfl')
my_connector.run()
