from xplain import Xplain
from sic import SIC
from tablet import Tablet
from find_employee import FindEmployee
from entertainment import Entertainment
from corona_monitor import CoronaMonitor
import random
import sys
import os
from time import sleep
from threading import Semaphore


class Agent:

    def __init__(self, parameters, log, postgres):

        self.parameters = parameters
        self.log = log
        self.postgres = postgres
        self.sleeping = False

        self.speaking_semaphore = Semaphore(0)
        self.looking_semaphore = Semaphore(0)
        self.listening_semaphore = Semaphore(0)
        self.listening_looking_semaphore = Semaphore(0)
        self.current_context = None
        self.try_listen = False

        self.xplain = Xplain(self.postgres)
        self.topics = {}
        self.load_topics()
        CoronaMonitor(self).clean_floor_occupations()
        self.tablet = Tablet(self)

        self.sic = SIC(self, parameters)

    def life_loop(self):

        self.search_subject()

        if not self.xplain.is_belief('disclaimer_visible') and self.xplain.is_belief('has_subject'):

            self.sic.tablet_show(self.tablet.get_body(extras_type='disclaimer'))

            self.say_and_wait(belief_type='disclaimer_visible',
                              say_text=self.get_sentence('general', 'disclaimer_ask'),
                              unexpected_answer_params=[self.xplain.belief_params('speech_text')],
                              timeout=self.parameters['timeout_listening'])

        if self.xplain.is_belief('disclaimer_visible'):

            if self.xplain.belief_params('disclaimer_visible') == 'no' \
                    and not self.xplain.is_belief('disclaimer_given'):

                self.sic.tablet_show(self.tablet.get_body(dialog=''))
                self.say(self.get_sentence('general', 'disclaimer_content'), extra_text=True)

            else:
                CoronaMonitor(self).act()

            self.xplain.adopt('disclaimer_given', 'cognition')

        self.help()

    def search_subject(self):
        # if it doesnt believe to have a subject, keeps searching for it
        if not(self.xplain.is_belief('has_subject')):
            print('\n> searching subject')

            self.listen_and_look('proactive_subject', self.parameters['timeout_watchlook'])
            self.xplain.drop('speech_text')
            self.xplain.drop('input.unknown')

    def offer_help(self, greetings):

            self.tablet.extras_type = None

            if self.xplain.is_belief('type_of_help') and not self.xplain.is_belief('helping'):
                print('\n> offering more help')
                self.tablet.reset_extras()
                self.xplain.drop('type_of_help')
                self.offer_help_flavors(self.get_sentence('general', 'offer_more_help'))

            if not self.xplain.is_belief('type_of_help'):
                print('\n> offering help')
                self.offer_help_flavors(self.get_sentence('general', 'offer_help', greetings))

    def offer_help_flavors(self, say_text):

        self.say_and_wait(belief_type='type_of_help',
                          say_text=say_text,
                          unexpected_answer_params=[self.xplain.belief_params('speech_text')],
                          timeout=self.parameters['timeout_listening'])

    def help(self):

        if self.xplain.is_belief('type_of_help'):
            print('\n> trying to help')

            if self.xplain.belief_params('type_of_help') == 'find employee':
                FindEmployee(self).act()

            elif self.xplain.belief_params('type_of_help') == 'entertainment':
                Entertainment(self).act()

            # when offer is rejected, agent abandons the subject
            elif self.xplain.belief_params('type_of_help') == 'nothing':
                self.say(self.get_sentence('general', 'rejection_taken'))
                self.give_up()

                # wait a bit for subject to leave
                sleep(self.parameters['rejection_tryagain'])

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

        self.try_listen = True

        # no answer received
        if self.xplain.is_belief('waiting_answer') and \
                not (self.xplain.is_belief(belief_type)) and \
                not (self.xplain.is_belief('input.unknown')):

            # after X attempts, assumes subject is gone
            attempts = int(self.xplain.belief_params('contact_attempt')[-1])
            if attempts < self.parameters['contact_attempts']:
                self.say(self.get_sentence(no_answer_topic, no_answer_subtopic, no_answer_params))
                self.xplain.increment('contact_attempt', str(attempts+1))
            else:
                self.say(self.get_sentence('general', 'no_answer_limit'))
                self.try_listen = False
                self.give_up()

        # answer is unexpected
        if self.xplain.is_belief('input.unknown'):
            self.xplain.drop('contact_attempt')
            self.xplain.adopt('contact_attempt', 'action', '1')

            if self.postgres.check_badwords(self.xplain.belief_params('speech_text')):
                sentence = self.get_sentence('general', 'badwords')
            else:
                sentence = self.get_sentence(unexpected_answer_topic, unexpected_answer_subtopic, unexpected_answer_params)

            self.say(sentence)
            self.xplain.drop('input.unknown')
            self.xplain.drop('speech_text')

        # say it for the first time
        if self.xplain.is_belief('has_subject') and not(self.xplain.is_belief('waiting_answer')):
            self.xplain.adopt('contact_attempt', 'action', '1')

            self.current_context = belief_type
            if belief_type in self.xplain.get_intents_entities():
                self.sic.tablet_show(self.tablet.get_body(buttons=self.xplain.get_intents_entities()[belief_type]))

            self.say(say_text)
            if self.try_listen:
                self.xplain.adopt('waiting_answer', 'action')

        if self.try_listen:
            self.listen(belief_type, timeout)

    def say(self, text, say_animated=True, extra_text=False):

        self.xplain.adopt('speaking', 'action', text)
        if not extra_text:
            self.sic.tablet_show(self.tablet.get_body(dialog=text))

        print('Say: ', text)

        if say_animated:
            self.sic.say_animated(text)
        else:
            self.sic.say(text)

        self.speaking_semaphore.acquire()
        self.xplain.drop('speaking')

    def listen(self, context='', timeout=None):
        self.xplain.adopt('listening', 'action')
        self.sic.set_dialogflow_context(context)
        self.sic.start_listening(0)
        print('listenting...')

        if timeout is not None:
            self.listening_semaphore.acquire(timeout=timeout)
        else:
            self.listening_semaphore.acquire()

        self.sic.stop_listening()
        print('stop listenting...')
        self.xplain.drop('listening')
        # 1 second additional wait to give dialogflow some time to return a result after closing the audio stream.
        sleep(1)

    def listen_and_look(self, context='', timeout=None):

            self.xplain.adopt('listening_looking', 'action')

            self.sic.set_dialogflow_context(context)
            self.sic.start_listening(0)
            self.sic.start_looking(0)
            print('listenting and looking...')

            if timeout is not None:
                self.listening_looking_semaphore.acquire(timeout=timeout)
            else:
                self.listening_looking_semaphore.acquire()

            self.sic.stop_listening()
            self.sic.stop_looking()
            print('stoped listenting and looking...')
            self.xplain.drop('listening_looking')

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

        self.xplain.adopt('has_subject', 'cognition')
        if self.xplain.is_belief('listening_looking'):
            self.listening_looking_semaphore.release()

    def load_topics(self):

        topics = os.listdir('topics')

        for topic in topics:
            topic = topic.split('.')[0]
            self.topics[topic] = {}

        for topic in self.topics:
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

    def get_sentence(self, topic, sentence_name, params=None):
        text = random.choice(self.topics[topic][sentence_name])
        if params is not None:
            text = text.format(*params)

        return text

    def clear_answer_beliefs(self):
        self.xplain.drop('waiting_answer')
        self.xplain.drop('speech_text')
        self.xplain.drop('contact_attempt')

    def drop_perception_of_subject(self):
        self.xplain.drop('proactive_subject')
        self.xplain.drop('seen_subject')
        self.xplain.drop('subject_touched')

    def load_magic_beliefs(self, magic_beliefs):
        for belief in magic_beliefs:
            self.xplain.adopt(belief, magic_beliefs[belief][0], magic_beliefs[belief][1])

    # says goodbye, drops any active beliefs, stops SIC, and breaks out the life loop
    def dropall_and_sleep(self):
        self.sic.stop_listening()
        self.sic.say(self.get_sentence('general', 'sleep_order_taken'))
        self.xplain.adopt('abandon_and_sleep', 'action')
        self.xplain.dropall()
        self.sic.stop()
        # TODO: add cleaning of face encodings here
        self.postgres.close()
        self.sleeping = True
        sys.exit()

    def try_get_input_again(self, input_belief):
        self.xplain.drop(input_belief)
        self.xplain.drop('speech_text')
        self.xplain.adopt('input.unknown', 'cognition')
        self.xplain.adopt('waiting_answer', 'action')

    def give_up(self):
        self.sic.tablet_show(self.tablet.resets_screen())
        self.xplain.dropall()
