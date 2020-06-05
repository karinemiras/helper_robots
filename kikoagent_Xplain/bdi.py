import psycopg2
from time import sleep

# Belief Desire and Intentions management
class BDI:

    def __init__(self):

        self.user = 'postgres'
        self.password = 'nao'
        self.host = '127.0.0.1'
        self.port = '5432'
        self.database = 'kikoagent'

        self.open()

    def open(self):

        try:
            self.connection = psycopg2.connect(user=self.user,
                                               password=self.password,
                                               host=self.host,
                                               port=self.port,
                                               database=self.database)
            self.cursor = self.connection.cursor()

        except (Exception, psycopg2.Error) as error:
            print("Error while connecting to PostgreSQL", error)

    def close(self):
        # closing database connection.
        if self.connection:
            self.cursor.close()
            self.connection.close()
            print("PostgreSQL connection is closed")

    def adopt(self, label, role, params_role=''):

        query = """ INSERT INTO bdi (label, datetime, active, role, params) VALUES (%s, now(), %s,%s, %s)"""
        params = (label, True, role, params_role)
        self.cursor.execute(query, params)
        self.connection.commit()

    def drop(self, label, role):

        query = """ Update bdi set active = %s where label = %s and role = %s"""
        params = (False, label, role)
        self.cursor.execute(query, params)
        self.connection.commit()

    def select(self, label, role, active):

        query = "select * from bdi where label = %s and role = %s and active = %s"
        param = (label, role, active)
        self.cursor.execute(query, param)
        records = self.cursor.fetchall()

        return records

    def role_params(self, label, role, active=True):

        query = "select params from bdi where label = %s and role = %s and active = %s"
        param = (label, role, active)
        self.cursor.execute(query, param)
        records = self.cursor.fetchall()
        if len(records) > 0:
            params = records[0][0].split('|')
            if len(params) > 1:
                return params
            else:
                return params[0]
        else:
            return ''

    def has_bdi_role(self, label, role, active=True):

        if len(self.select(label, role, active)) > 0:
            return True
        else:
            return False

    def states_bdi(self, context):

        sleep(0.01)
        query = "select role, label, params from bdi where active = True order by role, label"
        self.cursor.execute(query)
        records = self.cursor.fetchall()

        print('\n', context, ' - current BDI states:')
        for row in records:
            print(row)




