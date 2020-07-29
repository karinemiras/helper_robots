
class FindEmployee:

    def __init__(self, agent):
        self.agent = agent

    def act(self):

        print('\n> finding employee')

        self.agent.xplain.adopt('helping', 'action', 'find employee')

        self.agent.say_and_wait(belief_type='employee_name',
                                say_text=self.agent.get_sentence('find_employee', 'ask_name'),
                                unexpected_answer_topic='find_employee',
                                timeout=self.agent.parameters['timeout_listening'])

        if self.agent.xplain.is_belief('employee_name'):
           
            similarity_threshold = 0.4
            try:
                cursor = self.agent.postgres.connection.cursor()
                query = "select * from (SELECT *, similarity(replace(name,' ',''), replace(%s,' ','')) AS sim " \
                        "FROM employees order by sim desc limit 1 ) as f  where sim >= %s"
                cursor.execute(query, (self.agent.xplain.belief_params('employee_name'), similarity_threshold))
                records = cursor.fetchall()
                cursor.close()

            except Exception as error:
                self.agent.log.write('\nERROR db find employee: {}'.format(error))

            if len(records) > 0:

                self.agent.say('I found this person!')
                # give and show info

                self.agent.xplain.drop('employee_name')
                self.agent.clear_answer_beliefs()
                self.agent.xplain.drop('helping')

            else:
                self.agent.say(self.agent.get_sentence('find_employee', 'not_found',
                                                       [self.agent.xplain.belief_params('employee_name')]))
                self.agent.xplain.drop('employee_name')
                self.agent.xplain.drop('speech_text')
                self.agent.xplain.adopt('input.unknown', 'cognition')
                self.agent.xplain.adopt('waiting_answer', 'action')





