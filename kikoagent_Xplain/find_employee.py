
class FindEmployee:

    def __init__(self, agent):
        self.agent = agent

    def act(self):

        print('\n> finding employee')

        self.agent.xplain.adopt('helping', 'action', 'find employee')

        self.agent.say_and_wait(belief_type='employee_name',
                                say_text=self.agent.get_sentence('find_employee', 'ask_name'),
                                unexpected_answer_params=[self.agent.xplain.belief_params('speech_text')],
                                timeout=self.agent.parameters['timeout_listening'])

        if self.agent.xplain.is_belief('employee_name'):

            if self.agent.xplain.belief_params('employee_name') == 'Charlie Brown':
                self.agent.say('Charlie Brown works on the third floor, T345.')
            if self.agent.xplain.belief_params('employee_name') == 'Bob Dylan':
                self.agent.say('Bob Dylan works on the second floor, T240.')
            if self.agent.xplain.belief_params('employee_name') == '':
                self.agent.say('I could not find '+self.agent.xplain.belief_params('speech_text'))

            self.agent.xplain.dropall()


