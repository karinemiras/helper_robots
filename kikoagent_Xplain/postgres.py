import psycopg2


class Postgres:

    def __init__(self, parameters, log):

        self.user = parameters['postgres_user']
        self.password = parameters['postgres_password']
        self.host = parameters['postgres_host']
        self.port = parameters['postgres_port']
        self.database = parameters['postgres_database']
        self.log = log
        self.connection = None

        self.open()

    def open(self):

        try:
            self.connection = psycopg2.connect(user=self.user,
                                               password=self.password,
                                               host=self.host,
                                               port=self.port,
                                               database=self.database)
        except Exception as error:
            self.log.write('\nERROR db open: {}'.format(error))

    def close(self):
        try:
            # closing database connection.
            if self.connection:
                self.connection.close()
                print("PostgreSQL connection is closed")
        except Exception as error:
            self.log.write('\nERROR db close: {}'.format(error))

    def check_badwords(self, text):

        text = text.replace("'", "''")
        words = text.split(' ')
        words = ', '.join(["'%s'" % x for x in words])

        try:
            cursor = self.connection.cursor()
            query = "select word from badwords where word in ("+words+")"
            cursor.execute(query)
            records = cursor.fetchall()
            cursor.close()
            if len(records) > 0:
                return True
            else:
                return False
        except Exception as error:
            self.log.write('\nERROR db check_badword: {}'.format(error))

    def query_employee(self, name):

        try:
            records = []
            if name != '':
                cursor = self.connection.cursor()
                query = "select * from (SELECT *, similarity(replace(name,' ',''), replace('"+name+"',' ','')) AS sim " \
                        "FROM employees order by sim desc limit 1 ) as f"
                cursor.execute(query)
                records = cursor.fetchall()
                cursor.close()
            return records

        except Exception as error:
            self.log.write('\nERROR db find employee: {}'.format(error))

