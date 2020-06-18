from social_interaction_cloud.abstract_connector import AbstractSICConnector
from xplain import Xplain
from sic import SIC
from find_employee import FindEmployee
from freestyle_poetry import FreestylePoetry
import random
import sys
from time import sleep
from threading import Semaphore


class Agent:

    def __init__(self, parameters, log):

        self.parameters = parameters
        self.log = log
        self.sleeping = False

        self.speaking_semaphore = Semaphore(0)
        self.attention_semaphore = Semaphore(0)
        self.looking_semaphore = Semaphore(0)
        self.listening_semaphore = Semaphore(0)
        self.has_subject_semaphore = Semaphore(0)

        self.xplain = Xplain(parameters)
        self.topics = {}
        self.load_topics()

        self.sic = SIC(self, parameters)

    def life_loop(self):
        self.search_subject()
        self.offer_help()
        self.help()

    def search_subject(self):
        # if it doesnt believe to have a subject, keeps searching for it
        if not(self.xplain.is_belief('has_subject')):
            print('\n> searching subject')
            self.listen_and_look('proactive_subject')
            self.xplain.drop('speech_text')

    def offer_help(self):

        # if a person is believed to be near and there is NOT a current offer of help
        if self.xplain.is_belief('has_subject') and \
                not (self.xplain.is_belief('type_of_help')):
            print('\n> offering help')

            self.drop_perception_of_subject()

            self.say_and_wait(belief_type='type_of_help',
                              say_text=self.get_sentence('general', 'contact_attempt'),
                              unexpected_answer_params=[self.xplain.belief_params('speech_text')],
                              timeout=self.parameters['timeout_listening'])

    def help(self):

        if self.xplain.is_belief('type_of_help'):
            print('\n> trying to help')

            if not (self.xplain.is_belief('helping')):
                self.clear_answer_beliefs()

            if self.xplain.belief_params('type_of_help') == 'find employee':
                FindEmployee(self).act()

            elif self.xplain.belief_params('type_of_help') == 'freestyle poetry':
                FreestylePoetry(self).act()

            # when offer is rejected, agent abandons the subject
            elif self.xplain.belief_params('type_of_help') == 'nothing':
                self.say(self.get_sentence('general', 'rejection_taken'))
                self.xplain.drop('type_of_help')
                self.xplain.drop('has_subject')
                # TODO: rotate_randomly() -/+ 45 90 135 180, or maybe just left and right 61 degres
                # use semaphore, but for now sleep
                sleep(5)

    # say something and wait for a response; includes fallback;
    def say_and_wait(self,
                     belief_type,
                     say_text,
                     no_answer_topic='general',
                     no_answer_subtopic='no_answer',
                     no_answer_params=None,
                     unexpected_answer_topic='general',
                     unexpected_answer_subtopic='unexpected_answer',
                     unexpected_answer_params=None,
                     timeout=None):

        # no answer received
        if self.xplain.is_belief('waiting_answer') and \
                not (self.xplain.is_belief(belief_type)) and \
                not (self.xplain.is_belief('input.unknown')):

            # after X attempts, assumes subject is gone
            attempts = int(self.xplain.belief_params('contact_attempt')[-1])
            if attempts < self.parameters['contact_attempts']:
                self.say(self.get_sentence(no_answer_topic, no_answer_subtopic), no_answer_params)
                self.xplain.increment('contact_attempt', str(attempts+1))
            else:
                self.clear_answer_beliefs()
                self.xplain.drop('has_subject')
                self.say(self.get_sentence('general', 'no_answer_limit'))
                # rotate_for_subject (use same method for subject rejection)

        # answer is unexpected
        if self.xplain.is_belief('input.unknown'):
            self.xplain.drop('contact_attempt')
            self.xplain.adopt('contact_attempt', 'action', '1')
            sentence = self.get_sentence(unexpected_answer_topic, unexpected_answer_subtopic)
            self.say(sentence, unexpected_answer_params)
            self.xplain.drop('input.unknown')
            self.xplain.drop('speech_text')

        # say it for the first time
        if self.xplain.is_belief('has_subject') and not(self.xplain.is_belief('waiting_answer')):
            self.xplain.adopt('contact_attempt', 'action', '1')
            self.say(say_text)
            self.xplain.adopt('waiting_answer', 'action')

        self.listen(belief_type, timeout)

    def say(self, text, params=None, say_animated=True):

        if params is not None:
            text = text.format(*params)

        self.xplain.adopt('speaking', 'action', text)
        if say_animated:
            self.sic.say_animated(text)
        else:
            self.sic.say(text)
        print(text)

        self.speaking_semaphore.acquire()
        self.xplain.drop('speaking')

    def listen(self, context='', timeout=None):
        self.xplain.adopt('listening', 'action')
        self.sic.set_audio_context(context)
        self.sic.start_listening()
        if timeout is not None:
            self.listening_semaphore.acquire(timeout=timeout)
        else:
            self.listening_semaphore.acquire()

        self.sic.stop_listening()
        self.xplain.drop('listening')
        # 1 second additional wait to give dialogflow some time to return a result after closing the audio stream.
        sleep(1)

    def listen_and_look(self, context='', timeout=None):

            self.xplain.adopt('listening', 'action')
            self.sic.set_audio_context(context)
            self.sic.start_listening()
            self.xplain.adopt('looking', 'action')
            self.sic.start_looking()

            if timeout is not None:
                self.has_subject_semaphore.acquire(timeout=timeout)

            else:
                self.has_subject_semaphore.acquire()

            self.sic.stop_listening()
            self.xplain.drop('listening')
            self.sic.stop_looking()
            self.xplain.drop('looking')
            # 1 second additional wait to give dialogflow some time to return a result after closing the audio stream.
            sleep(1)

    def look(self, timeout=None):
        self.xplain.adopt('looking', 'action')
        self.sic.start_looking()
        if timeout is not None:
            self.look_semaphore.acquire(timeout=timeout)
        else:
            self.look_semaphore.acquire()
        self.sic.stop_looking()
        self.xplain.drop('looking')

    def has_subject(self):
        if not self.xplain.is_belief('has_subject'):
            self.xplain.adopt('has_subject', 'percept')
            self.has_subject_semaphore.release()

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

    def clear_answer_beliefs(self):
        self.xplain.drop('waiting_answer')
        self.xplain.drop('speech_text')
        self.xplain.drop('contact_attempt')

    def drop_helping_beliefs(self):
        self.xplain.drop('type_of_help')
        self.xplain.drop('helping')

    def drop_perception_of_subject(self):
        self.xplain.drop('proactive_subject')
        self.xplain.drop('seen_subject')
        self.xplain.drop('subject_touched')

    def load_magic_beliefs(self, magic_beliefs):
        for belief in magic_beliefs:
            self.xplain.adopt(belief, magic_beliefs[belief][0], magic_beliefs[belief][1])

    # says goodbye, drops any active beliefs, stops SIC, and breaks out the life loop
    def dropall_and_sleep(self):
        self.say(self.get_sentence('general', 'sleep_order_taken'))
        self.xplain.adopt('abandon_and_sleep', 'action')
        self.xplain.dropall()
        self.sic.stop()
        self.sleeping = True
        sys.exit()


