import numpy as np


class TellJoke:

    def __init__(self, agent):
        self.agent = agent

    def act(self):

        print('\n> telling joke')
        self.agent.xplain.adopt('helping', 'action', 'freestyle poetry')

        try:
            cursor = self.agent.postgres.connection.cursor()
            # TODO: check if appropriate=True
            query = "select * from jokes order by random() limit 1"
            cursor.execute(query)
            records = cursor.fetchall()
            cursor.close()
            joke = records[0][1]

        except Exception as error:
            self.agent.log.write('\nERROR db get_rhymes: {}'.format(error))

        joke = joke.replace('?', '\\pau=1000\\')
        text = self.agent.get_sentence('tell_joke', 'warn_start') + ' \\pau=1000\\ \\rspd=70\\ ' + joke
        self.agent.say(text)

        self.agent.drop_helping_beliefs()
        self.agent.xplain.drop('type_of_entertainment')
        self.agent.xplain.drop('has_subject')
