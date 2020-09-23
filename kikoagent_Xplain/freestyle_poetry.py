from time import sleep
import random
import inflect


class FreestylePoetry:

    def __init__(self, agent):
        self.agent = agent
        
    def act(self):

        records = []

        print('\n> freestyling poetry')

        self.agent.sic.tablet_show(self.agent.tablet.get_body(buttons=['anything']))
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

                    if word == 'anything':
                        query = "select word, category from words_rhymes where  " \
                                " category in ('adv', 'adj', 'noun', 'verb') order by random() limit 1"
                    else:
                        query = "select word, category from words_rhymes where lower(word) = lower(%s) " \
                                "and category in ('adv', 'adj', 'noun', 'verb') order by random() limit 1"

                    cursor.execute(query, (word,))
                    records = cursor.fetchall()
                    cursor.close()
                except Exception as error:
                    self.agent.log.write('\nERROR db check suggested word: {}'.format(error))

                # if suggested word exists in the dictionary
                if len(records) > 0:

                    verses = []
                    # fist verse uses word from user
                    ending, verse = self.write_verse(suggested_word=records[0][0], suggested_word_category=records[0][1])
                    self.format_verse(verse, verses)
                    ending, verse = self.write_verse(rhyming=True, rhyming_word=ending)
                    self.format_verse(verse, verses)
                    ending, verse = self.write_verse()
                    self.format_verse(verse, verses)
                    ending, verse = self.write_verse(rhyming=True, rhyming_word=ending)
                    self.format_verse(verse, verses)

                    poem = ' \\pau=800\\ \\rspd=100\\ '
                    for verse in verses:
                        poem += verse + '. \\pau=300\\ '

                    self.agent.say(self.agent.get_sentence('freestyle_poetry', 'ready', [word]))

                    self.agent.sic.tablet_show(
                        self.agent.tablet.get_body(extras_type='poetry', extras_params=['not_think', verses]))

                    self.agent.say(poem, extra_text=True)

                    self.agent.sic.play_audio('audio/aplauses.wav')
                    self.agent.sic.tablet_show(
                        self.agent.tablet.get_body(extras_type='poetry', extras_params=['think', verses]))

                    sleep(5)

                    self.agent.xplain.drop('type_of_entertainment')
                    self.agent.xplain.drop('given_word')
                    self.agent.clear_answer_beliefs()
                    self.agent.xplain.drop('helping')

                # found no due rhymes for the word or word in undue:so asks for a second chance
                else:
                    self.agent.say(self.agent.get_sentence('freestyle_poetry', 'excuse', [word]))
                    self.agent.try_get_input_again('given_word')

            else:
                self.agent.say(self.agent.get_sentence('general', 'badwords'))
                self.agent.try_get_input_again('given_word')

    def format_verse(self, verse, verses):
        verse = verse.capitalize() + '.'
        verses.append(verse)

    def sample_word(self, category, subcategory=None):
        cursor = self.agent.postgres.connection.cursor()
        if subcategory is not None:
            query = "select word from words_rhymes where " \
                    "category=%s and subcategory=%s and active=TRUE order by random() limit 1"
            cursor.execute(query, (category, subcategory))
        else:
            query = "select word from words_rhymes where category=%s and active=TRUE order by random() limit 1"
            cursor.execute(query, (category,))
        records = cursor.fetchall()
        cursor.close()
        word = records[0][0]
        return word

    def write_verse(self, suggested_word='', suggested_word_category=None, rhyming=False, rhyming_word=''):

        verse_type = ''
        ending = ''
        verse = ''
        rhyme_word = ''
        adv = ''
        adj = ''

        articles = ['the'] #'a'
        
        to_be_dict = {'I': ['am', 'am not', 'was', 'was not', 'will be', 'will not be'],
                      'you': ['are', 'are not', 'were', 'were not', 'will be', 'will not be'],
                      'we': ['are', 'are not', 'were', 'were not', 'will be', 'will not be'],
                      'they': ['are', 'are not', 'were', 'were not', 'will be', 'will not be'],
                      'he': ['is', 'is not', 'was', 'was not', 'will be', 'will not be'],
                      'she': ['is', 'is not', 'was', 'was not', 'will be', 'will not be'],
                      'it': ['is', 'is not', 'was', 'was not', 'will be', 'will not be'],
                      'this': ['is', 'is not', 'was', 'was not', 'will be', 'will not be'],
                      }

        if rhyming:
            try:

                cursor = self.agent.postgres.connection.cursor()
                query = "select syllable1,syllables2,syllables3,syllables4,syllables5, \
                         syllables6,syllables7,syllables8,syllables9,syllables10 " \
                        "from words_rhymes where lower(title) = lower(%s) limit 1"
                cursor.execute(query, (rhyming_word,))
                records = cursor.fetchall()

                if len(records) > 0:
                    syllables1 = records[0][0].split(',') if records[0][0] is not None else []
                    syllables2 = records[0][1].split(',') if records[0][1] is not None else []
                    syllables3 = records[0][2].split(',') if records[0][2] is not None else []
                    syllables4 = records[0][3].split(',') if records[0][3] is not None else []
                    syllables5 = records[0][4].split(',') if records[0][4] is not None else []
                    syllables6 = records[0][5].split(',') if records[0][5] is not None else []
                    syllables7 = records[0][6].split(',') if records[0][6] is not None else []
                    syllables8 = records[0][7].split(',') if records[0][7] is not None else []
                    syllables9 = records[0][8].split(',') if records[0][8] is not None else []
                    syllables10 = records[0][9].split(',') if records[0][9] is not None else []

                    rhymes = syllables1 + syllables2 + syllables3 + syllables4 + syllables5 + \
                             syllables6 + syllables7 + syllables8 + syllables9 + syllables10
                    rhymes = str([x.strip(' ').replace("'", "''") for x in rhymes]).strip("[]")
                    rhymes = rhymes.replace('"', "'")

                    query = "select word,category from words_rhymes where word !='"+rhyming_word + \
                            "' and word in("+rhymes+") order by random() limit 1"
                    cursor.execute(query)
                    records = cursor.fetchall()

                    # if there are rhymes for that word
                    if len(records) > 0:
                        rhyme_word = records[0][0]
                        rhyme_category = records[0][1]
                        verse_type = 'subject_{}'.format(rhyme_category)
                    else:
                        rhyming = False
                else:
                    rhyming = False

                cursor.close()

            except Exception as error:
                self.agent.log.write('\nERROR db get_rhymes: {}'.format(error))
        else:
            if suggested_word_category is not None:
                verse_type = 'subject_{}'.format(suggested_word_category)

        # if it is not rhyming or using a user's word, any category (sentence structure) is ok
        if verse_type == '':
            verse_type = random.choice(['subject_adj', 'subject_noun', 'subject_adv', 'subject_verb'])

        to_be = random.choice(range(0, 6))
        junctions = articles + [self.sample_word('pron', 'poss')]
        plu = inflect.engine()

        # uses a subject personal pronoun as subject
        if random.uniform(0, 1) > 0.9:
            subject = self.sample_word('pron', 'subj_pers')
            to_be_ = to_be_dict[subject][to_be]
        # a noun as subject
        else:
            ref = random.choice(junctions)
            subject = ref + ' ' + self.sample_word('noun')
            to_be_ = to_be_dict['it'][to_be]

        if verse_type == 'subject_adj':

            if random.uniform(0, 1) > 0.5:
                adv = self.sample_word('adv')

            if rhyming:
                adj = rhyme_word
            elif suggested_word_category is not None:
                adj = suggested_word
            else:
                adj = self.sample_word('adj')

            molecules = [subject, to_be_, adv, adj]
            verse = ' '.join(molecules)
            ending = adj

        if verse_type == 'subject_noun':

            junction = random.choice(junctions)

            if random.uniform(0, 1) > 0.5:
                adj = self.sample_word('adj')
                if random.uniform(0, 1) > 0.5:
                    adv = self.sample_word('adv')

            if rhyming:
                noun = rhyme_word
            elif suggested_word_category is not None:
                noun = suggested_word
            else:
                noun = self.sample_word('noun')

            molecules = [subject, to_be_, junction, adv, adj, noun]
            verse = ' '.join(molecules)
            ending = noun

        if verse_type == 'subject_adv':

            junction = random.choice(junctions)
            noun = self.sample_word('noun')
            verb = self.sample_word('verb')

            if rhyming:
                adv = rhyme_word
            elif suggested_word_category is not None:
                adv = suggested_word
            else:
                adv = self.sample_word('adv')

            plural = random.choice([True, False])

            noun = plu.plural(noun) if plural else noun
            noun = junction + ' ' + noun if not plural else noun
            verb = plu.plural(verb) if not plural else verb

            molecules = [noun, verb, adv]
            verse = ' '.join(molecules)
            ending = adv

        if verse_type == 'subject_verb':

            junction = random.choice(junctions)
            noun = self.sample_word('noun')

            if suggested_word_category is not None:
                verb = suggested_word
            else:
                verb = self.sample_word('verb')

            if not rhyming:
                ending = self.sample_word('noun')
                ending_local = junction + ' ' + ending
            else:
                ending = rhyme_word
                ending_local = 'to ' + ending

            plural = random.choice([True, False])

            noun = plu.plural(noun) if plural else noun
            noun = junction + ' ' + noun if not plural else noun
            verb = plu.plural(verb) if not plural else verb

            molecules = [noun, verb, ending_local]
            verse = ' '.join(molecules)

        print(verse_type)
        return ending, verse




