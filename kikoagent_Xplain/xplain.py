# Xplain manages the BDI of the agent.
# Everything the agent knows is a belief.
# Desires and intentions are implicit, while this agent for now only desires and intends to always be helping.
# The agent knows its own deeds, each represented by a belief called 'action'.
# The agent knows beliefs about its environment and itself, represented by beliefs of type 'percept' and 'inference'.


class Xplain:

    def __init__(self, postgres):

        self.postgres = postgres

    # registers active beliefs when an action starts
    def register_beliefs_of_action(self, id_belief):

        cursor = self.postgres.connection.cursor()
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

        self.postgres.connection.commit()
        cursor.close()

    def adopt(self, belief, belieftype, params=''):
        try:
            if not(self.is_belief(belief)):
                cursor = self.postgres.connection.cursor()
                query = """ INSERT INTO beliefs (belief, time_started, active, belieftype, params) 
                                   VALUES (%s, now(), %s,%s, %s) returning id """
                params = (belief, True, belieftype, params)
                cursor.execute(query, params)
                self.postgres.connection.commit()

                if belieftype == 'action':
                    self.register_beliefs_of_action(cursor.fetchone()[0])
                cursor.close()

        except Exception as error:
            self.log.write('\nERROR db adopt: {}'.format(error))

    def drop(self, belief):
        try:
            cursor = self.postgres.connection.cursor()
            query = """ Update beliefs set active = False, time_finished = now() where belief = %s and active = True"""
            cursor.execute(query, (belief,))
            self.postgres.connection.commit()
            cursor.close()
        except Exception as error:
            print('\nERROR db drop: ', error)

    def increment(self, belief, value):
        try:
            cursor = self.postgres.connection.cursor()
            query = """ Update beliefs set params=CONCAT(params,'|',%s) where belief = %s and active = True"""
            cursor.execute(query, (value, belief) )
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
            self.log.write('\nERROR db belieftype_params: {}'.format(error))

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
            self.log.write('\nERROR db is_belief: {}'.format(error))

    def dropall(self):
        try:
            cursor = self.postgres.connection.cursor()
            query = "update beliefs set active=False, time_finished = now() where active = True"
            cursor.execute(query)
            self.postgres.connection.commit()
            cursor.close()
        except Exception as error:
            self.log.write('\nERROR db dropall: {}'.format(error))

    def summary_active_beliefs(self):
        try:
            cursor = self.postgres.connection.cursor()
            query = "select belieftype, belief, params from beliefs where active = True order by belieftype, belief"
            cursor.execute(query)
            records = cursor.fetchall()
            cursor.close()
            for row in records:
                print(row)
        except Exception as error:
            self.log.write('\nERROR db summary_active_beliefs: {}'.format(error))



