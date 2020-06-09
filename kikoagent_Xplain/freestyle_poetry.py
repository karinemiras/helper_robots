from bs4 import BeautifulSoup
import numpy
import requests


class FreestylePoetry:

    def __init__(self, agent):
        self.agent = agent

    def act(self):

        print('\n> freestyling poetry')
        if not (self.agent.xplain.is_fact('helping')):
            self.agent.xplain.adopt('helping', 'action', 'help_poetry')
        self.agent.say_and_wait(fact_type='given_word',
                                say_text=self.agent.get_sentence('freestyle_poetry', 'ask_word'),
                                unexpected_answer_topic='freestyle_poetry')

        if self.agent.xplain.is_fact('given_word'):

            word = self.agent.xplain.ftype_params('given_word')

            response = requests.get(
                'https://www.rhymezone.com/r/rhyme.cgi?Word=' + word + '&typeofrhyme=perfect').text

            soup = BeautifulSoup(response)
            rhymes = []
            for a in soup.find_all('a'):
                if a.get('class') is not None:
                    rhymes.append(a.get_text().replace(u'\xa0', u' '))
            rhymes = numpy.array(rhymes)

            if len(rhymes) > 0:
                sentense = '\\rspd=60\\' + word + ', rhymes with ' \
                           + rhymes[numpy.random.choice(len(rhymes), 1)][0] \
                           + ' \\pau=300\\ ' + rhymes[numpy.random.choice(len(rhymes), 1)][0] \
                           + '\\pau=300\\ and ' + rhymes[numpy.random.choice(len(rhymes), 1)][0] + '.'

                print(sentense)
                self.agent.say(sentense)

                self.agent.drop_basic_beliefs()
                self.agent.xplain.drop('given_word')
            else:
                self.agent.say(self.agent.get_sentence('freestyle_poetry', 'excuse'))
                self.agent.xplain.drop('given_word')
                self.agent.xplain.drop('speech_text')
                self.agent.xplain.adopt('input.unknown', 'percept')
