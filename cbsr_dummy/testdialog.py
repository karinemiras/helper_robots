import AbstractApplication as Base
from threading import Semaphore

class DialogFlowSampleApplication(Base.AbstractApplication):
    def __init__(self):
        super(DialogFlowSampleApplication, self).__init__(serverIP='192.168.1.19')

    def main(self):
        # Set the correct language (and wait for it to be changed)
        self.langLock = Semaphore(0)
        self.setLanguage('en-US')
        self.langLock.acquire()

        # Pass the required Dialogflow parameters (add your Dialogflow parameters)
        #self.setDialogflowKey('silly.json')
        self.setDialogflowKey('kikoagent-iajdfl-9d037d057933.json')
        #self.setDialogflowAgent('answer-name-pgocqj')
        self.setDialogflowAgent('kikoagent-iajdfl')

        # Make the robot ask the question, and wait until it is done speaking
        self.speechLock = Semaphore(0)
        self.sayAnimated('employee or poetry?')
        self.speechLock.acquire()

        # Listen for an answer for at most 5 seconds
        self.type_of_help = None
        self.nameLock = Semaphore(0)
        self.setAudioContext('type_of_help')
        self.startListening()
        self.nameLock.acquire(timeout=10)
        self.stopListening()

        if not self.type_of_help:  # wait one more second after stopListening (if needed)
            self.nameLock.acquire(timeout=1)

        # Respond and wait for that to finish
        if self.type_of_help:
            self.sayAnimated('ok, ' + self.type_of_help + ' it is!')
        else:
            self.sayAnimated('no')
       # self.speechLock.acquire()

        # Display a gesture (replace <gestureID> with your gestureID)
       # self.gestureLock = Semaphore(0)
        #self.doGesture('hands/behavior_1')
        #self.gestureLock.acquire()

    def onRobotEvent(self, event):
        if event == 'LanguageChanged':
            self.langLock.release()
        elif event == 'TextDone':
            self.speechLock.release()
        elif event == 'GestureDone':
           self.gestureLock.release()

    def onAudioIntent(self, *args, intentName):
        print('onAudioIntent', intentName)
        if intentName == 'type_of_help' and len(args) > 0:
            print(intentName)
            self.type_of_help = args[0]
            self.nameLock.release()


# Run the application
sample = DialogFlowSampleApplication()
sample.main()
sample.stop()
