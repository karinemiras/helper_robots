
class FindEmployee:

    def __init__(self, agent):
        self.agent = agent

    def act(self):

        print('\n> finding employee')

        self.agent.xplain.adopt('helping', 'action', 'help_find_employee')

        self.agent.say_and_wait(fact_type='employee_name',
                                say_text=self.agent.get_sentence('find_employee', 'employee_name'),
                                unexpected_answer_params=[self.agent.xplain.fact_params('speech_text')])

        if self.agent.xplain.is_fact('employee_name'):

            self.agent.clear_answer_facts()

            if self.agent.xplain.fact_params('employee_name') == 'Charlie Brown':
                self.agent.say('Charlie Brown works on the third floor, T345.')
            if self.agent.xplain.fact_params('employee_name') == 'Bob Dylan':
                self.agent.say('Bob Dylan works on the second floor, T240.')
            if self.agent.xplain.fact_params('employee_name') == '':
                self.agent.say('I could not find '+self.agent.xplain.fact_params('speech_text'))

            self.agent.drop_helping_facts()
            self.agent.xplain.drop('employee_name')
            self.agent.xplain.drop('has_subject')


