import psycopg2

# Xplain manages the BDI of the agent.
# Everything the agent knows is a belief.
# Desires and intentions are implicit, while this agent for now only desires and intends to always be helping.
# The agent knows its own deeds, each represented by a belief called 'action'.
# The agent knows beliefs about its environment and itself, represented by beliefs of type 'percept' and 'inference'.

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

    # registers active beliefs when an action starts
    def register_beliefs_of_action(self, id_belief):

        cursor = self.connection.cursor()
        query = "select id from beliefs where active = True and id != %s"
        cursor.execute(query, (id_belief, ))
        records = cursor.fetchall()
        query = """ INSERT INTO beliefs_of_action (action_belief_id, active_belief_id) VALUES (%s, %s) """

        if len(records) > 0:
            for belief in records:
                params = (id_belief, belief[0])
                cursor.execute(query, params)
        else:
            # actions taken when there is no beliefs are known
            params = (id_belief, -1)
            cursor.execute(query, params)

        self.connection.commit()
        cursor.close()

    def adopt(self, belief, belieftype, params=''):
        try:
            if not(self.is_belief(belief)):
                cursor = self.connection.cursor()
                query = """ INSERT INTO beliefs (belief, time_started, active, belieftype, params) 
                                   VALUES (%s, now(), %s,%s, %s) returning id """
                params = (belief, True, belieftype, params)
                cursor.execute(query, params)
                self.connection.commit()

                if belieftype == 'action':
                    self.register_beliefs_of_action(cursor.fetchone()[0])
                cursor.close()

        except Exception as error:
            print('\nERROR adopt: ', error)

    def drop(self, belief):
        try:
            cursor = self.connection.cursor()
            query = """ Update beliefs set active = False, time_finished = now() where belief = %s and active = True"""
            cursor.execute(query, (belief,))
            self.connection.commit()
            cursor.close()
        except Exception as error:
            print('\nERROR drop: ', error)

    # fetches parameters
    def belief_params(self, belief):
        try:
            cursor = self.connection.cursor()
            query = "select params from beliefs where belief = %s and active = %s"
            param = (belief, True)
            cursor.execute(query, param)
            records = cursor.fetchall()
            cursor.close()
            if len(records) > 0:
                params = records[0][0].split('|')
                # for multiple parameters
                if len(params) > 1:
                    return params
                # for one or no parameters
                else:
                    return params[0]
            # if belief does not exits, returns empty string
            else:
                return ''
        except Exception as error:
            print('\nERROR belieftype_params: ', error)

    def is_belief(self, belief):
        try:
            cursor = self.connection.cursor()
            query = "select * from beliefs where belief = %s and active = %s"
            param = (belief, True)
            cursor.execute(query, param)
            records = cursor.fetchall()
            cursor.close()
            if len(records) > 0:
                return True
            else:
                return False
        except Exception as error:
            print('\nERROR is_belief: ', error)

    def dropall(self):
        try:
            cursor = self.connection.cursor()
            query = "update beliefs set active=False, time_finished = now() where active = True"
            cursor.execute(query)
            self.connection.commit()
            cursor.close()
        except Exception as error:
            print('\nERROR dropall: ', error)

    def summary_active_beliefs(self):
        try:
            cursor = self.connection.cursor()
            query = "select belieftype, belief, params from beliefs where active = True order by belieftype, belief"
            cursor.execute(query)
            records = cursor.fetchall()
            cursor.close()
            for row in records:
                print(row)
        except Exception as error:
            print('\nERROR summary_active_beliefs: ', error)



