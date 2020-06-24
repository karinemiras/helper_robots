from freestyle_poetry import FreestylePoetry
from tell_joke import TellJoke
import numpy as np


class Entertainment:

    def __init__(self, agent):
        self.agent = agent

    def act(self):

        print('\n> proposing entertainment')

        if self.agent.xplain.is_belief('type_of_entertainment'):

            if self.agent.xplain.belief_params('type_of_entertainment') == 'poetry':
                FreestylePoetry(self.agent).act()
            if self.agent.xplain.belief_params('type_of_entertainment') == 'joke':
                TellJoke(self.agent).act()
        else:
            self.agent.say_and_wait(belief_type='type_of_entertainment',
                                    say_text=self.agent.get_sentence('entertainment', 'ask_type'),
                                    unexpected_answer_params=[self.agent.xplain.belief_params('speech_text')],
                                    timeout=self.agent.parameters['timeout_listening'])

