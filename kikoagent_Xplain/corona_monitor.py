

class CoronaMonitor:

    def __init__(self, agent):
        self.agent = agent

    def act(self):

        # if a person is believed to be near
        if self.agent.xplain.is_belief('has_subject'):
            print('\n> carrying out corona monitor')

            self.agent.drop_perception_of_subject()
            self.agent.tablet.reset_extras()

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
                        # self.agent.say_and_wait(belief_type='which_wing',
                        #                         say_text=self.agent.get_sentence('corona', 'ask_wing_out'),
                        #                         unexpected_answer_params=[self.agent.xplain.belief_params('speech_text')],
                        #                         timeout=self.agent.parameters['timeout_listening'])
                        # for now, only wing a being used
                        self.agent.xplain.adopt('which_wing', 'cognition','Wing A')

                    if self.agent.xplain.is_belief('which_floor') and self.agent.xplain.is_belief('which_wing'):
                        if not self.agent.xplain.is_belief('bye_checkout'):
                            self.agent.say(self.agent.get_sentence('corona', 'checkout'))
                            self.update_occupation()
                            self.agent.xplain.adopt('bye_checkout', 'action')
                        self.agent.offer_help([self.agent.get_sentence('general', 'offer_help_intro_more')])

                if self.agent.xplain.belief_params('in_or_out') == 'in':

                    if not self.agent.xplain.is_belief('which_floor'):
                        self.agent.say_and_wait(belief_type='which_floor',
                                                say_text=self.agent.get_sentence('corona', 'ask_floor_in'),
                                                unexpected_answer_params=[self.agent.xplain.belief_params('speech_text')],
                                                timeout=self.agent.parameters['timeout_listening'])

                    if self.agent.xplain.is_belief('which_floor') and not self.agent.xplain.is_belief('which_wing'):
                        # self.agent.say_and_wait(belief_type='which_wing',
                        #                         say_text=self.agent.get_sentence('corona', 'ask_wing_in'),
                        #                         unexpected_answer_params=[self.agent.xplain.belief_params('speech_text')],
                        #                         timeout=self.agent.parameters['timeout_listening'])
                        # for now, only wing a being used
                        self.agent.xplain.adopt('which_wing', 'cognition', 'Wing A')

                    if self.agent.xplain.is_belief('which_floor') and self.agent.xplain.is_belief('which_wing'):

                        occupation, occupation_max = self.check_occupation()

                        if not self.agent.xplain.is_belief('occupation_info'):

                            if occupation == 0:
                                presence_aux = 'are no people'
                            elif occupation == 1:
                                presence_aux = 'is '+str(occupation)+' person'
                            else:
                                presence_aux = 'are '+str(occupation)+' people'

                            self.agent.say(self.agent.get_sentence('corona', 'inform_occupation', [presence_aux]))

                            # may or my not provide full occupation warning
                            if occupation >= occupation_max:
                                self.agent.xplain.adopt('max_occupation', 'belief')

                                if not self.agent.xplain.is_belief('wait_or_not'):
                                    self.agent.say_and_wait(belief_type='wait_or_not',
                                                            say_text=self.agent.get_sentence('corona', 'wait_or_not'),
                                                            unexpected_answer_params=[
                                                                self.agent.xplain.belief_params('speech_text')],
                                                            timeout=self.agent.parameters['timeout_listening'])

                            self.agent.xplain.adopt('occupation_info', 'action')

                            if self.agent.xplain.belief_params('wait_or_not') == 'yes':
                                self.update_occupation()

                        # offer help
                        if self.agent.xplain.is_belief('occupation_info'):
                            if occupation < occupation_max:
                                self.agent.offer_help([self.agent.get_sentence('general', 'offer_help_intro_more')])
                            else:
                                self.agent.offer_help([self.agent.get_sentence('general', 'offer_help_intro_while')])

    def check_occupation(self):
        try:
            cursor = self.agent.postgres.connection.cursor()
            query = "select occupation, max_occupation from occupation_building_history" \
                    " where active=True and floor=%s and wing=%s"
            cursor.execute(query, (self.agent.xplain.belief_params('which_floor'),
                                   self.agent.xplain.belief_params('which_wing')))
            records = cursor.fetchall()
            cursor.close()

            return records[0][0], records[0][1]

        except Exception as error:
            self.agent.log.write('\nERROR db check_occupation: {}'.format(error))

    def update_occupation(self):

        if self.agent.xplain.belief_params('in_or_out') == 'in':
            new_occupation, aux = self.check_occupation()
            new_occupation += 1
        else:
            new_occupation, aux = self.check_occupation()
            new_occupation = max(0, new_occupation - 1)

        try:
            cursor = self.agent.postgres.connection.cursor()
            query = "update occupation_building_history set occupation=%s where active=True and floor=%s and wing=%s"
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
            query = "update occupation_building_history set active=False where active=True"
            cursor.execute(query)
            query = "insert into occupation_building_history (datetime, floor, occupation, max_occupation, wing, active) \
                        (select now(), floor, occupation, max_occupation, wing, True   from occupation_building)"
            cursor.execute(query)
            cursor.close()

        except Exception as error:
            self.agent.log.write('\nERROR db clean_floor_occupations: {}'.format(error))

