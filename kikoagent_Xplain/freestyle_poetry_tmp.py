from social_interaction_cloud.abstract_connector import AbstractSICConnector

import sys
from aj import AJ


from social_interaction_cloud.abstract_connector import AbstractSICConnector
from time import sleep


class MyConnector(AbstractSICConnector):
    """This example shows you how to create your won SIC connector by inheriting AbstractSICConnector.
    For more information go to
    https://socialrobotics.atlassian.net/wiki/spaces/CBSR/pages/616398873/Python+Examples#Abstract-SIC-Connector"""
    def __init__(self, server_ip, robot):
        super(MyConnector, self).__init__(server_ip, robot)

    def run(self):
        self.start()
        self.set_language('en-US')

        # \\pau=value\\  msec
        # Insert \\rspd=value\\ in the text. The value between 50 and 400 in %. Default value is 100.
        # Insert \\vct=value\\ in the text. The value is between 50 and 200 in %. Default value is 100.
        # 50 to 150



        song = AJ(_silent_bars_range=[0, 0],
                  _user_solo=False,
                  _tempo_pool={'min': 90, 'mean': 120, 'std': 20, 'max': 150})
        song.times = 4
        song.choices()
        song.tempo = 150
        song.compose()
        song.build_midi()
        song.export_midi('current_song_all')
        #print(song.)


        self.stop()
       # self.say(' first second \\pau=1000\\ third  \\pau=3000\\ fourth ')


# Run the application
my_connector = MyConnector(server_ip='192.168.1.19', robot='nao')
my_connector.run()
