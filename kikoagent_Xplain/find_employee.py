import smtplib


class FindEmployee:

    def __init__(self, agent):
        self.agent = agent

    def act(self):

        print('\n> finding employee')

        records = []
        self.agent.xplain.adopt('helping', 'action', 'find employee')

        if not self.agent.xplain.is_belief('employee_name'):
            self.agent.say_and_wait(belief_type='employee_name',
                                    say_text=self.agent.get_sentence('find_employee', 'ask_name'),
                                    unexpected_answer_topic='find_employee',
                                    timeout=self.agent.parameters['timeout_listening'])

        if self.agent.xplain.is_belief('employee_name') and not self.agent.xplain.is_belief('employee_info_given'):

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

                info = self.make_info(records)
                self.agent.sic.tablet_show(self.agent.tablet.get_body(extras_type='employee', extras_params=records))
                self.agent.say(info)

                self.agent.xplain.adopt('employee_info_given', 'cognition')
                self.agent.xplain.adopt('employee_email', 'cognition', records[0][4])

            else:
                self.agent.say(self.agent.get_sentence('find_employee', 'not_found',
                                                       [self.agent.xplain.belief_params('employee_name')]))
                self.agent.try_get_input_again('employee_name')

        if self.agent.xplain.is_belief('employee_info_given') and not self.agent.xplain.is_belief('visitor_name'):
            self.agent.say_and_wait(belief_type='visitor_name',
                                    say_text=self.agent.get_sentence('find_employee', 'offer_email'),
                                    unexpected_answer_topic='find_employee',
                                    timeout=self.agent.parameters['timeout_listening'])

        if self.agent.xplain.is_belief('visitor_name'):

            if self.agent.xplain.belief_params('visitor_name') in ['no', 'nope', 'not']:
                self.agent.say(self.agent.get_sentence('find_employee', 'ok_no'))
                self.end_help()
            else:

                if not self.agent.xplain.is_belief('correct_name'):
                    self.agent.say_and_wait(belief_type='correct_name',
                                            say_text=self.agent.get_sentence('find_employee', 'check_visitor',
                                                         [self.agent.xplain.belief_params('visitor_name')]),
                                            unexpected_answer_topic='find_employee',
                                            timeout=self.agent.parameters['timeout_listening'])

                else:
                    if self.agent.xplain.belief_params('correct_name') == 'yes':

                        visitor_name = self.agent.xplain.belief_params('visitor_name')
                        visitor_name = visitor_name.replace(' ', '')
                        visitor_name = visitor_name.capitalize()

                        status = self.send_email(self.agent.xplain.belief_params('employee_email'),
                                 self.agent.get_sentence('find_employee', 'email', [visitor_name]))

                        if status:
                            self.agent.say(self.agent.get_sentence('find_employee', 'ok_yes') +
                                           self.agent.get_sentence('find_employee', 'social_distancing'))
                        else:
                            self.agent.say(self.agent.get_sentence('find_employee', 'email_fail'))

                        self.end_help()

                    else:
                        self.agent.try_get_input_again('visitor_name')
                        self.agent.xplain.drop('correct_name')

    def make_info(self, records):

        name = records[0][0]
        location = records[0][2]
        title = records[0][3]
        email = records[0][4]
        telefone = records[0][5]
        group = records[0][6]

        info = ''
        if name is not None:
            info += name

        if title is not None:
            info += ' is a ' + title

        if group is not None:
            info += ' who works in the ' + group + '.'

        if location is not None:
            info += ' \\pau=300\\ You can find this person at the ' + location + '.'

        if email is not None:
            info += ' \\pau=300\\ Or by the e-mail, ' + email + '.'

        if telefone is not None:
            info += ' \\pau=300\\ Or through the telephone, \\readmode=char\\ ' + telefone

        return info

    def end_help(self):
        # ends this particular help
        self.agent.xplain.drop('employee_name')
        self.agent.xplain.drop('visitor_name')
        self.agent.xplain.drop('employee_info_given')
        self.agent.clear_answer_beliefs()
        self.agent.xplain.drop('helping')

    def send_email(self, email_to, email_text):

        try:
            sender_email = "kikorobotsteward@gmail.com"
            password = "kikobabybot"
            subject = 'Visitor coming'
            server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
            server.ehlo()
            server.login(sender_email, password)
            server.sendmail(sender_email, email_to, 'Subject: {}\n\n{}'.format(subject, email_text))
            server.close()

            self.agent.xplain.adopt('send_email', 'action', 'success')

            return True

        except Exception as error:
            self.agent.postgres.log.write('\nERROR db sendemail: {}'.format(error))
            self.agent.xplain.adopt('send_email', 'action', 'fail')

            return False

