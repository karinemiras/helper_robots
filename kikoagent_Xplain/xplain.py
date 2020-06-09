import psycopg2

# Belief Desire and Intentions management
class Xplain:

    def __init__(self, parameters):

        self.user = parameters['postgres_user']
        self.password = parameters['postgres_password']
        self.host = parameters['postgres_host']
        self.port = parameters['postgres_port']
        self.database = parameters['postgres_database']

        self.open()

    def open(self):

        try:
            self.connection = psycopg2.connect(user=self.user,
                                               password=self.password,
                                               host=self.host,
                                               port=self.port,
                                               database=self.database)
        except Exception as error:
            print('\nERROR: ', error)

    def close(self):
        try:
            # closing database connection.
            if self.connection:
                self.connection.close()
                print("PostgreSQL connection is closed")
        except Exception as error:
            print('\nERROR close: ', error)

    def adopt(self, label, ftype, params_ftype=''):
        try:
            if not(self.is_fact(label)):
                cursor = self.connection.cursor()
                query = """ INSERT INTO facts (label, time_started, active, ftype, params) 
                                   VALUES (%s, now(), %s,%s, %s)"""
                params = (label, True, ftype, params_ftype)
                cursor.execute(query, params)
                self.connection.commit()
                cursor.close()
        except Exception as error:
            print('\nERROR adopt: ', error)

    def drop(self, label):
        try:
            cursor = self.connection.cursor()
            query = """ Update facts set active = %s, time_finished = now() where label = %s and active = True"""
            params = (False, label)
            cursor.execute(query, params)
            self.connection.commit()
            cursor.close()
        except Exception as error:
            print('\nERROR drop: ', error)

    def ftype_params(self, label):
        try:
            cursor = self.connection.cursor()
            query = "select params from facts where label = %s and active = %s"
            param = (label, True)
            cursor.execute(query, param)
            records = cursor.fetchall()
            cursor.close()
            if len(records) > 0:
                params = records[0][0].split('|')
                if len(params) > 1:
                    return params
                else:
                    return params[0]
            else:
                return ''
        except Exception as error:
            print('\nERROR ftype_params: ',    error)

    def is_fact(self, label):
        try:
            cursor = self.connection.cursor()
            query = "select * from facts where label = %s and active = %s"
            param = (label, True)
            cursor.execute(query, param)
            records = cursor.fetchall()
            cursor.close()
            if len(records) > 0:
                return True
            else:
                return False
        except Exception as error:
            print('\nERROR is_fact: ', error)

    def summary_facts(self):
        try:
            cursor = self.connection.cursor()
            query = "select ftype, label, params from facts where active = True order by ftype, label"
            cursor.execute(query)
            records = cursor.fetchall()
            cursor.close()
            for row in records:
                print(row)
        except Exception as error:
            print('\nERROR summary_facts: ', error)



