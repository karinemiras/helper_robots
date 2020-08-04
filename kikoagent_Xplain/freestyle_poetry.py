import numpy as np
import random
import inflect


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

            if len(selected_rhymes) > 0:

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

                    rhymes = syllables1 + syllables2 + syllables3 + syllables4 + syllables5 + \
                             syllables6 + syllables7 + syllables8 + syllables9 + syllables10

                    rhymes = np.array([item.strip() for item in rhymes])
                    rhymes = np.delete(rhymes, np.argwhere(rhymes == word))

                    if len(rhymes) > 0:
                        number_rhymes = min(len(rhymes), number_rhymes)
                        selected_rhymes = np.random.choice(rhymes, number_rhymes, replace=False)

                def sample_word(self, category, subcategory=None):
                    # cursor = self.agent.postgres.connection.cursor()
                    cursor = self.connection.cursor()
                    if subcategory is not None:
                        query = "select word from words where category=%s and subcategory=%s and active=TRUE order by random() limit 1"
                        cursor.execute(query, (category, subcategory))
                    else:
                        query = "select word from words where category=%s and active=TRUE order by random() limit 1"
                        cursor.execute(query, (category,))
                    records = cursor.fetchall()
                    cursor.close()
                    word = records[0][0]
                    return word

                def bob(self):

                    verse = ''

                    to_be_dict = {'I': ['am', 'am not', 'was', 'was not', 'will be', 'will not be'],
                                  'you': ['are', 'are not', 'were', 'were not', 'will be', 'will not be'],
                                  'we': ['are', 'are not', 'were', 'were not', 'will be', 'will not be'],
                                  'they': ['are', 'are not', 'were', 'were not', 'will be', 'will not be'],
                                  'he': ['is', 'is not', 'was', 'was not', 'will be', 'will not be'],
                                  'she': ['is', 'is not', 'was', 'was not', 'will be', 'will not be'],
                                  'it': ['is', 'is not', 'was', 'was not', 'will be', 'will not be'],
                                  'this': ['is', 'is not', 'was', 'was not', 'will be', 'will not be'],
                                  }

                    articles = ['a', 'the']

                    verse_type = random.choice(['personal_quality', 'noun_noun', 'noun_verbs'])
                    to_be = random.choice(range(0, 6))
                    junction = articles + [self.sample_word('pron', 'poss')]

                    print(verse_type + '\n')

                    if verse_type == 'personal_quality':
                        pron = self.sample_word('pron', 'subj_pers')
                        adv = self.sample_word('adv')
                        adj = self.sample_word('adj')

                        molecules = [pron, to_be_dict[pron][to_be], adv, adj]
                        verse = ' '.join(molecules)

                    if verse_type == 'noun_noun':
                        noun1 = self.sample_word('noun')
                        junction1 = random.choice(junction)
                        junction2 = random.choice(junction)
                        adv = self.sample_word('adv') if random.uniform(0, 1) > 0.5 else ''
                        adj = self.sample_word('adj') if random.uniform(0, 1) > 0.5 else ''
                        noun2 = self.sample_word('noun')

                        molecules = [junction1, noun1, to_be_dict['it'][to_be], junction2, adv, adj, noun2]
                        verse = ' '.join(molecules)

                    if verse_type == 'noun_verbs':

                        plu = inflect.engine()

                        junction1 = random.choice(junction)
                        noun = self.sample_word('noun')
                        verb1 = self.sample_word('verb')

                        if random.uniform(0, 1) > 0.5:
                            ending = ' to ' + self.sample_word('verb')
                        else:
                            ending = plu.plural(self.sample_word('noun'))

                        plural = random.choice([True, False])

                        noun = plu.plural(noun) if plural else noun
                        noun = random.choice(articles) + ' ' + noun if not plural else noun
                        verb1 = plu.plural(verb1) if not plural else verb1

                        molecules = [junction1, noun, verb1, ending]
                        verse = ' '.join(molecules)

                    print(verse)


                sentense = '\\rspd=60\\' + word + ', rhymes with '
                for rhyme in selected_rhymes:
                    sentense += rhyme + ', '

                self.agent.say(sentense)

                self.agent.sic.play_audio('audio/aplauses.wav')

                self.agent.xplain.drop('type_of_entertainment')
                self.agent.xplain.drop('given_word')
                self.agent.clear_answer_beliefs()
                self.agent.xplain.drop('helping')

            # found no due rhymes for the word or word in undue:so asks for a second chance
            else:
                self.agent.say(self.agent.get_sentence('freestyle_poetry', 'excuse'))
                self.agent.try_get_input_again('given_word')

