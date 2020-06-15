
class Log:

    def __init__(self, parameters):
        self.parameters = parameters

    def write(self, text):
        print(text)
        with open("experiments/{}/log.txt".format(self.parameters['experiment_name']), "a") as logfile:
            logfile.write(text)

