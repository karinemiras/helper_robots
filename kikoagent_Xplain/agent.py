from social_interaction_cloud.abstract_connector import AbstractSICConnector
from xplain import Xplain
from sic import SIC
from find_employee import FindEmployee
from freestyle_poetry import FreestylePoetry
import random
from threading import Semaphore

class Agent():

    def __init__(self, parameters):

        self.timeout_listing = parameters['timeout_listing']

        self.speaking_semaphore = Semaphore(0)
        self.watching_semaphore = Semaphore(0)
        self.listening_semaphore = Semaphore(0)

        self.xplain = Xplain(parameters)
        self.topics = {}
        self.load_topics()

        self.sic = SIC(self, parameters)

    def life_loop(self):
        self.search_subject()
        self.offer_help()
        self.help()

    def search_subject(self):
        # if it doesnt believe to have a subject, searches for it by looking
        if not(self.xplain.is_fact('has_subject')):
            print('\n> searching subject')
            self.sic.start_looking()
            self.watching_semaphore.acquire()
            self.sic.stop_looking()

    def offer_help(self):

        # if a person is believed to be near and there is NOT a current offer of help
        if self.xplain.is_fact('has_subject') and \
                not (self.xplain.is_fact('type_of_help')):
            print('\n> offering help')

            if not (self.xplain.is_fact('offers_on_table')):
                self.xplain.adopt('offers_on_table', 'action')
            self.say_and_wait(fact_type='type_of_help',
                              say_text=self.get_sentence('general', 'offer_help'),
                              unexpected_answer_params=[self.xplain.ftype_params('speech_text')])

    def help(self):

        if self.xplain.is_fact('type_of_help'):
            print('\n> helping')
            self.xplain.drop('offers_on_table')
            if not (self.xplain.is_fact('helping')):
                self.xplain.drop('waiting_answer')

            if self.xplain.ftype_params('type_of_help') == 'employee':
                FindEmployee(self).act()
            elif self.xplain.ftype_params('type_of_help') == 'poetry':
                FreestylePoetry(self).act()

        # say something and wait for a response; includes fallback;

    def say_and_wait(self,
                     fact_type,
                     say_text,
                     no_answer_topic='general',
                     no_answer_subtopic='no_answer',
                     no_answer_params=None,
                     unexpected_answer_topic='general',
                     unexpected_answer_subtopic='unexpected_answer',
                     unexpected_answer_params=None):

        # no answer received
        if self.xplain.is_fact('waiting_answer') and \
                not (self.xplain.is_fact(fact_type)) and \
                not (self.xplain.is_fact('input.unknown')):
            sentence = self.get_sentence(no_answer_topic, no_answer_subtopic)
            if no_answer_params is not None:
                self.say(sentence.format(*no_answer_params))
            else:
                self.say(sentence)

        # answer is unexpected
        if self.xplain.is_fact('input.unknown'):
            sentence = self.get_sentence(unexpected_answer_topic, unexpected_answer_subtopic)
            if unexpected_answer_params is not None:
                self.say(sentence.format(*unexpected_answer_params))
            else:
                self.say(sentence)

            self.xplain.drop('input.unknown')
            self.xplain.drop('speech_text')

        # say it for the first time
        if not (self.xplain.is_fact('waiting_answer')):
            self.say(say_text)
            self.xplain.adopt('waiting_answer', 'action')

        self.listen(fact_type)

    def say(self, text):
        self.xplain.adopt('speaking', 'action', text)
        self.sic.say(text)
        self.speaking_semaphore.acquire()

    def listen(self, context=''):
        self.sic.set_audio_context(context)
        self.sic.start_listening()
        self.listening_semaphore.acquire(timeout=self.timeout_listing)
        self.sic.stop_listening()

    def has_subject(self, true_or_false):
        if true_or_false:
            self.xplain.adopt('has_subject', 'percept')
            self.watching_semaphore.release()

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

    def drop_basic_beliefs(self):
        self.xplain.drop('has_subject')
        self.xplain.drop('waiting_answer')
        self.xplain.drop('type_of_help')
        self.xplain.drop('helping')
        self.xplain.drop('speech_text')

