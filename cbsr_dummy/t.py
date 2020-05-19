import AbstractApplication as Base
from threading import Semaphore
import sys

class SampleApplication(Base.AbstractApplication):
    def __init__(self):
        super(SampleApplication, self).__init__(serverIP='192.168.1.19')

    def main(self):

        self.setLanguage('en-US')

        self.speechLock = Semaphore(0)
        self.say('i am gonna look at you')
        self.speechLock.acquire()
        self.speechLock = Semaphore(0)
        self.say('i')
        self.speechLock.acquire()
        self.speechLock = Semaphore(0)
        self.say('am')
        self.speechLock.acquire()
        self.speechLock = Semaphore(0)
        self.say('gonna')
        self.speechLock.acquire()
        self.speechLock = Semaphore(0)
        self.say('look')
        self.speechLock.acquire()
        self.speechLock = Semaphore(0)
        self.say('at')
        self.speechLock.acquire()
        self.speechLock = Semaphore(0)
        self.say('you')
        self.speechLock.acquire()
         

    def onRobotEvent(self, event):

        if event == 'TextDone':
            self.speechLock.release()


# Run the application
sample = SampleApplication()
sample.main()
sample.stop()
