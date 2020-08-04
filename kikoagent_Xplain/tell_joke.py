import random


class TellJoke:

    def __init__(self, agent):
        self.agent = agent

    def act(self):

        print('\n> telling joke')

        try:
            cursor = self.agent.postgres.connection.cursor()
            query = "select * from jokes where appropriate=True order by random() limit 1"
            cursor.execute(query)
            records = cursor.fetchall()
            cursor.close()
            joke = records[0][1]

        except Exception as error:
            self.agent.log.write('\nERROR db get_rhymes: {}'.format(error))

        joke = joke.replace('?', '? \\pau=800\\ ')
        joke = joke.replace('.', '. \\pau=300\\ ')
        joke = joke.replace('"', ' \\pau=300\\ ')

        text = self.agent.get_sentence('tell_joke', 'warn_start') + ' \\pau=800\\ \\rspd=85\\ ' + joke
        self.agent.say(text)

        type_laugh = random.choice(['1', '2'])

        self.agent.sic.play_audio('audio/laugh{}.wav'.format(type_laugh))

        self.agent.xplain.drop('type_of_entertainment')
        self.agent.clear_answer_beliefs()
        self.agent.xplain.drop('helping')
