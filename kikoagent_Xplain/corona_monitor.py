
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

                    if not self.agent.xplain.is_belief('floor'):
                        self.agent.say_and_wait(belief_type='floor',
                                                say_text=self.agent.get_sentence('corona', 'ask_floor_out'),
                                                unexpected_answer_params=[self.agent.xplain.belief_params('speech_text')],
                                                timeout=self.agent.parameters['timeout_listening'])

                    if self.agent.xplain.is_belief('floor'):
                        self.agent.say(self.agent.get_sentence('corona', 'checkout'))
                        # TODO: calculate checkout
                        self.agent.xplain.dropall()

                if self.agent.xplain.belief_params('in_or_out') == 'in':

                    if not self.agent.xplain.is_belief('floor'):
                        self.agent.say_and_wait(belief_type='floor',
                                                say_text=self.agent.get_sentence('corona', 'ask_floor_in'),
                                                unexpected_answer_params=[self.agent.xplain.belief_params('speech_text')],
                                                timeout=self.agent.parameters['timeout_listening'])

                    if self.agent.xplain.is_belief('floor'):

                        if not self.agent.xplain.is_belief('checkin_info'):

                            presence = self.check_occupation()
                            if presence == 0:
                                presence_aux = 'no'
                            else:
                                presence_aux = str(presence)

                            self.agent.say(self.agent.get_sentence('corona', 'inform_occupation', [presence_aux]))
                            # TODO: inform estimation and maybe wait warning
                            self.agent.say(self.agent.get_sentence('corona', 'checkin_reminder'))

                            self.agent.xplain.adopt('checkin_info', 'action')
                            # TODO: calculate checkin

                        if self.agent.xplain.is_belief('checkin_info'):
                            self.agent.offer_help(['By the way, '])

    def check_occupation(self):

        try:
            cursor = self.agent.postgres.connection.cursor()
            query = "select occupation from occupation_building where floor=%s"
            cursor.execute(query, (self.agent.xplain.belief_params('floor'),))
            records = cursor.fetchall()
            cursor.close()
            return records[0][1]

        except Exception as error:
            self.agent.log.write('\nERROR db check_occupation: {}'.format(error))

    def update_occupation(self, in_or_out):

        if in_or_out == 'in':
            new_occupation = self.check_occupation() + 1
        else:
            new_occupation = max(0, self.check_occupation() - 1)

        try:
            cursor = self.agent.postgres.connection.cursor()
            query = "update occupation_building set occupation=%s where floor=%s"
            cursor.execute(query, (self.agent.xplain.belief_params('floor'), new_occupation))
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

