# Xplain manages the BDI of the agent.
# Everything the agent knows is a belief.
# Desires and intentions are implicit, while this agent for now only desires and intends to always be helping.
# The agent knows its own deeds, each represented by a belief called 'action'.
# The agent knows beliefs about its environment and itself, represented by beliefs of type 'percept' and 'inference'.


class Xplain:

    def __init__(self, postgres):

        self.postgres = postgres
        self.intents_entities = self.get_intents_entities()
        self.dropall()

    def adopt(self, belief, belieftype, params=''):
        try:
            if not(self.is_belief(belief)):
                cursor = self.postgres.connection.cursor()
                query = """ INSERT INTO beliefs (belief, time_started, active, belieftype, params) 
                                   VALUES (%s, now(), %s,%s, %s) returning id """
                params = (belief, True, belieftype, params)
                cursor.execute(query, params)
                self.postgres.connection.commit()

                cursor.close()

        except Exception as error:
            self.postgres.log.write('\nERROR db adopt: {}'.format(error))

    def drop(self, belief):
        try:
            cursor = self.postgres.connection.cursor()

            # because listening_looking is constantly renewed when in search_subject loop, it gets wiped out
            if belief == 'listening_looking':
                query = "Delete from beliefs where belief = %s"
            else:
                query = "Update beliefs set active = False, time_finished = now() where belief = %s and active = True"
            cursor.execute(query, (belief,))
            self.postgres.connection.commit()
            cursor.close()
        except Exception as error:
            print('\nERROR db drop: ', error)

    def increment(self, belief, value):
        try:
            cursor = self.postgres.connection.cursor()
            query = """ Update beliefs set params=CONCAT(params,'|',%s) where belief = %s and active = True"""
            cursor.execute(query, (value, belief))
            self.postgres.connection.commit()
            cursor.close()
        except Exception as error:
            print('\nERROR db increment: ', error)

    # fetches parameters
    def belief_params(self, belief):
        try:
            cursor = self.postgres.connection.cursor()
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
            self.postgres.log.write('\nERROR db belieftype_params: {}'.format(error))

    def is_belief(self, belief):
        try:
            cursor = self.postgres.connection.cursor()
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
            self.postgres.log.write('\nERROR db is_belief: {}'.format(error))

    def dropall(self):
        try:
            cursor = self.postgres.connection.cursor()
            query = "update beliefs set active=False, time_finished = now() where active = True"
            cursor.execute(query)
            self.postgres.connection.commit()
            cursor.close()
        except Exception as error:
            self.postgres.log.write('\nERROR db dropall: {}'.format(error))

    def get_intents_entities(self):
        try:
            intents = {}
            cursor = self.postgres.connection.cursor()
            query = "select belief, entities from beliefs_dictionary where entities IS NOT NULL"
            cursor.execute(query)
            records = cursor.fetchall()
            cursor.close()
            for intent in records:
                intents[intent[0]] = intent[1].split('|')

            return intents
        except Exception as error:
            self.postgres.log.write('\nERROR db get_domain_intents: {}'.format(error))
