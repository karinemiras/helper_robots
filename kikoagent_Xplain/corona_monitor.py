
class CoronaMonitor:

    def __init__(self, agent):
        self.agent = agent

    def act(self):

        # if a person is believed to be near
        if self.agent.xplain.is_belief('has_subject'):
            print('\n> carrying out corona monitor')

            self.agent.drop_perception_of_subject()

            if not self.agent.xplain.is_belief('in_or_out'):
                self.agent.say_and_wait(belief_type='in_or_out',
                                        say_text=self.agent.get_sentence('corona', 'ask_inout'),
                                        unexpected_answer_params=[self.agent.xplain.belief_params('speech_text')],
                                        timeout=self.agent.parameters['timeout_listening'])

            if self.agent.xplain.is_belief('in_or_out'):

                if self.agent.xplain.belief_params('in_or_out') == 'out':

                    if not self.agent.xplain.is_belief('which_floor'):
                        self.agent.say_and_wait(belief_type='which_floor',
                                                say_text=self.agent.get_sentence('corona', 'ask_floor_out'),
                                                unexpected_answer_params=[self.agent.xplain.belief_params('speech_text')],
                                                timeout=self.agent.parameters['timeout_listening'])

                    if self.agent.xplain.is_belief('which_floor') and not self.agent.xplain.is_belief('which_wing'):
                        self.agent.say_and_wait(belief_type='which_wing',
                                                say_text=self.agent.get_sentence('corona', 'ask_wing_out'),
                                                unexpected_answer_params=[self.agent.xplain.belief_params('speech_text')],
                                                timeout=self.agent.parameters['timeout_listening'])

                    if self.agent.xplain.is_belief('which_floor') and self.agent.xplain.is_belief('which_wing'):
                        self.agent.say(self.agent.get_sentence('corona', 'checkout'))
                        self.update_occupation()
                        self.agent.xplain.dropall()

                if self.agent.xplain.belief_params('in_or_out') == 'in':

                    if not self.agent.xplain.is_belief('which_floor'):
                        self.agent.say_and_wait(belief_type='which_floor',
                                                say_text=self.agent.get_sentence('corona', 'ask_floor_in'),
                                                unexpected_answer_params=[self.agent.xplain.belief_params('speech_text')],
                                                timeout=self.agent.parameters['timeout_listening'])

                    if self.agent.xplain.is_belief('which_floor') and not self.agent.xplain.is_belief('which_wing'):
                        self.agent.say_and_wait(belief_type='which_wing',
                                                say_text=self.agent.get_sentence('corona', 'ask_wing_in'),
                                                unexpected_answer_params=[self.agent.xplain.belief_params('speech_text')],
                                                timeout=self.agent.parameters['timeout_listening'])

                    if self.agent.xplain.is_belief('which_floor') and self.agent.xplain.is_belief('which_wing'):

                        occupation = 0
                        if not self.agent.xplain.is_belief('checkin_info'):

                            occupation = self.check_occupation()
                            if occupation == 0:
                                presence_aux = 'are no people'
                            elif occupation == 1:
                                presence_aux = 'is '+str(occupation)+' person'
                            else:
                                presence_aux = 'are '+str(occupation)+' people'

                            self.agent.say(self.agent.get_sentence('corona', 'inform_occupation', [presence_aux]))

                            if occupation >= self.agent.parameters['corona_max_occupation']:
                                self.agent.say(self.agent.get_sentence('corona', 'wait_advice'))

                            self.agent.say(self.agent.get_sentence('corona', 'checkin_reminder'))
                            self.agent.xplain.adopt('checkin_info', 'action')

                            self.update_occupation()

                        # after giving checkin info, may or my not provide full occupation warning
                        if self.agent.xplain.is_belief('checkin_info'):
                            if occupation < self.agent.parameters['corona_max_occupation']:
                                self.agent.offer_help([self.agent.get_sentence('general', 'offer_help_intro_more')])
                            else:
                                self.agent.offer_help([self.agent.get_sentence('general', 'offer_help_intro_while')])

    def check_occupation(self):
        try:
            cursor = self.agent.postgres.connection.cursor()
            query = "select occupation from occupation_building where floor=%s and wing=%s"
            cursor.execute(query, (self.agent.xplain.belief_params('which_floor'),
                                   self.agent.xplain.belief_params('which_wing')))
            records = cursor.fetchall()
            cursor.close()
            return records[0][0]

        except Exception as error:
            self.agent.log.write('\nERROR db check_occupation: {}'.format(error))

    def update_occupation(self):

        if self.agent.xplain.belief_params('in_or_out') == 'in':
            new_occupation = self.check_occupation() + 1
        else:
            new_occupation = max(0, self.check_occupation() - 1)

        try:
            cursor = self.agent.postgres.connection.cursor()
            query = "update occupation_building set occupation=%s where floor=%s and wing=%s"
            cursor.execute(query, (new_occupation,
                                   self.agent.xplain.belief_params('which_floor'),
                                   self.agent.xplain.belief_params('which_wing')))
            self.agent.postgres.connection.commit()
            cursor.close()

        except Exception as error:
            self.agent.log.write('\nERROR db update_occupation: {}'.format(error))

    def clean_floor_occupations(self):

        try:
            cursor = self.agent.postgres.connection.cursor()
            query = "update occupation_building set occupation=0"
            cursor.execute(query)
            cursor.close()

        except Exception as error:
            self.agent.log.write('\nERROR db clean_floor_occupations: {}'.format(error))

