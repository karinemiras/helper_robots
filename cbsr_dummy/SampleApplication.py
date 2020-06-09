import AbstractApplication as Base
from threading import Semaphore
import sys

class SampleApplication(Base.AbstractApplication):
    def __init__(self):
        super(SampleApplication, self).__init__(serverIP='192.168.1.19')

    def main(self):
        self.sem_setLanguage = Semaphore(0)
        self.setLanguage('en-US')
        self.sem_setLanguage.acquire()
        #\\pau=value\\  msec
        #Insert \\rspd=value\\ in the text. The value between 50 and 400 in %. Default value is 100.
        #Insert \\vct=value\\ in the text. The value is between 50 and 200 in %. Default value is 100.

        # 50 to 150
        self.say(' first second \\pau=1000\\ third  \\pau=3000\\ fourth ')
        sys.exit()
        self.sem_setLanguage = Semaphore(0)
        self.say('i am gonna look at you')
        self.sem_setLanguage.acquire()
        sys.exit()

        self.semaphore_looking = Semaphore(0)
        self.startLooking()
        self.semaphore_looking.acquire(timeout=10)
        self.stopLooking()

    def onRobotEvent(self, event):
        print(event)
        if event == 'LanguageChanged':
            self.sem_setLanguage.release()
        elif event == 'TextDone':
            self.sem_setLanguage.release()

    def onPersonDetected(self):
        self.sayAnimated('i see you')
        self.semaphore_looking.release()



# Run the application
sample = SampleApplication()
sample.main()
sample.stop()
