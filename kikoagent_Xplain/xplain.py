import psycopg2

# Xplain manages the BDI of the agent.
# Everything the agent knows is a fact, instead of a belief.
# Desires and intentions are implict, while this agent for now only desires and intends to always be helping.
# The agent knows its own deeds, each represented by a fact called 'action'.
# The agent knows facts about its environment and itself, represented by facts of type 'percept' and 'inference'.

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

    # registers active facts when an action starts
    def register_facts_of_action(self, id_fact):

        cursor = self.connection.cursor()
        query = """select id from facts where active = True"""
        cursor.execute(query)
        records = cursor.fetchall()
        for fact in records:
            if id_fact != fact[0]:
                query = """ INSERT INTO facts_of_action (action_fact_id, active_fact_id) VALUES (%s, %s) """
                params = (id_fact, fact[0])
                cursor.execute(query, params)
        self.connection.commit()
        cursor.close()

    def adopt(self, fact, facttype, params_facttype=''):
        try:
            if not(self.is_fact(fact)):
                cursor = self.connection.cursor()
                query = """ INSERT INTO facts (fact, time_started, active, facttype, params) 
                                   VALUES (%s, now(), %s,%s, %s) returning id """
                params = (fact, True, facttype, params_facttype)
                cursor.execute(query, params)
                self.connection.commit()

                if facttype == 'action':
                    self.register_facts_of_action(cursor.fetchone()[0])
                cursor.close()

        except Exception as error:
            print('\nERROR adopt: ', error)

    def drop(self, fact):
        try:
            cursor = self.connection.cursor()
            query = """ Update facts set active = %s, time_finished = now() where fact = %s and active = True"""
            params = (False, fact)
            cursor.execute(query, params)
            self.connection.commit()
            cursor.close()
        except Exception as error:
            print('\nERROR drop: ', error)

    # fetches parameters
    def fact_params(self, fact):
        try:
            cursor = self.connection.cursor()
            query = "select params from facts where fact = %s and active = %s"
            param = (fact, True)
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
            # if fact does not exits, returns empty string
            else:
                return ''
        except Exception as error:
            print('\nERROR facttype_params: ',    error)

    def is_fact(self, fact):
        try:
            cursor = self.connection.cursor()
            query = "select * from facts where fact = %s and active = %s"
            param = (fact, True)
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
            query = "select facttype, fact, params from facts where active = True order by facttype, fact"
            cursor.execute(query)
            records = cursor.fetchall()
            cursor.close()
            for row in records:
                print(row)
        except Exception as error:
            print('\nERROR summary_facts: ', error)



