import numpy as np


class FreestylePoetry:

    def __init__(self, agent):
        self.agent = agent

    def act(self):

        number_rhymes = 4
        selected_rhymes = []
        records = []

        print('\n> freestyling poetry')

        self.agent.say_and_wait(belief_type='given_word',
                                say_text=self.agent.get_sentence('freestyle_poetry', 'ask_word'),
                                unexpected_answer_topic='freestyle_poetry',
                                timeout=self.agent.parameters['timeout_listening'])

        if self.agent.xplain.is_belief('given_word'):

            self.agent.clear_answer_beliefs()

            word = self.agent.xplain.belief_params('given_word').strip()

            if not self.agent.postgres.check_badwords(word):
                try:
                    cursor = self.agent.postgres.connection.cursor()
                    query = "select * from rhymes where lower(title) = lower(%s) "
                    cursor.execute(query, (word,))
                    records = cursor.fetchall()
                    cursor.close()

                except Exception as error:
                    self.agent.log.write('\nERROR db get_rhymes: {}'.format(error))

            if len(records) > 0:
                syllables1 = records[0][2].split(',') if records[0][2] is not None else []
                syllables2 = records[0][3].split(',') if records[0][3] is not None else []
                syllables3 = records[0][4].split(',') if records[0][4] is not None else []
                syllables4 = records[0][5].split(',') if records[0][5] is not None else []
                syllables5 = records[0][6].split(',') if records[0][6] is not None else []
                syllables6 = records[0][7].split(',') if records[0][7] is not None else []
                syllables7 = records[0][8].split(',') if records[0][8] is not None else []
                syllables8 = records[0][9].split(',') if records[0][9] is not None else []
                syllables9 = records[0][10].split(',') if records[0][10] is not None else []
                syllables10 = records[0][11].split(',') if records[0][11] is not None else []

                rhymes = syllables1+syllables2+syllables3+syllables4+syllables5 + \
                         syllables6+syllables7+syllables8+syllables9+syllables10

                rhymes = np.array([item.strip() for item in rhymes])
                rhymes = np.delete(rhymes, np.argwhere(rhymes == word))
                # TODO: remove rhymes that are in bad words dic

                if len(rhymes) > 0:
                    number_rhymes = min(len(rhymes), number_rhymes)
                    selected_rhymes = np.random.choice(rhymes, number_rhymes, replace=False)

            if len(selected_rhymes) > 0:
                sentense = '\\rspd=60\\' + word + ', rhymes with '
                for rhyme in selected_rhymes:
                    sentense += rhyme + ', '

                self.agent.say(sentense)

                self.agent.xplain.drop('type_of_entertainment')
                self.agent.xplain.drop('given_word')
                self.agent.clear_answer_beliefs()
                self.agent.xplain.drop('helping')

            # found no due rhymes for the word or word in undue:so asks for a second chance
            else:
                self.agent.say(self.agent.get_sentence('freestyle_poetry', 'excuse'))
                self.agent.try_get_input_again('given_word')

