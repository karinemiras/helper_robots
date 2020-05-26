import functools
import threading
from enum import Enum
from queue import Queue
from social_interaction_cloud.abstract_connector import AbstractSICConnector, RobotType


class BasicNaoPosture(Enum):
    STAND = 'Stand'
    STANDINIT = 'StandInit'
    STANDZERO = 'StandZero'
    CROUCH = 'Crouch'
    SIT = 'Sit'
    SITONCHAIR = 'SitOnChair'
    SITRELAX = 'SitRelax'
    LYINGBELLY = 'LyingBelly'
    LYINGBACK = 'LyingBack'
    UNKNOWN = 'Unknown'  # this is not a valid posture


class BasicPepperPosture(Enum):
    STAND = 'Stand'
    STANDINIT = 'StandInit'
    STANDZERO = 'StandZero'
    CROUCH = 'Crouch'
    UNKNOWN = 'Unknown'  # this is not a valid posture


class BasicSICConnector(AbstractSICConnector):
    """
    Basic implementation of AbstractSICConnector. It serves a connector to the Social Interaction Cloud.
    The base mechanism is that a callback function can be registered for each robot action. When the action returns a
    result (e.g. a ActionDone event) the callback is called once and removed. Only for touch and vision events a
    persistent callback can be registered.

    """

    def __init__(self, server_ip: str, robot: RobotType, dialogflow_key_file=None, dialogflow_agent_id=None):
        """

        :param server_ip: IP address of Social Interaction Cloud server
        :param robot: robot type. Currently supported are 'nao' or 'pepper'
        :param dialogflow_key_file: path to Google's Dialogflow key file
        :param dialogflow_agent_id: ID number of Dialogflow agent to be used (project ID)
        """
        super(BasicSICConnector, self).__init__(server_ip=server_ip, robot=robot)

        self.robot = robot
        self.robot_state = {'posture': BasicNaoPosture.UNKNOWN if self.robot == RobotType.NAO else BasicPepperPosture.UNKNOWN}

        if dialogflow_key_file and dialogflow_agent_id:
            self.set_dialogflow_key(dialogflow_key_file)
            self.set_dialogflow_agent(dialogflow_agent_id)

        self.__listeners = {}
        self.__conditions = []
        self.__vision_listeners = {}
        self.__touch_listeners = {}

    ###########################
    # Event handlers          #
    ###########################

    def on_robot_event(self, event):
        self.__notify_listeners(event)
        self.__notify_touch_listeners(event)

    def on_posture_changed(self, posture: str):
        self.__notify_listeners('onPostureChanged', posture)
        if self.robot == RobotType.NAO:
            self.robot_state['posture'] = BasicNaoPosture[posture.upper()]
        else:
            self.robot_state['posture'] = BasicPepperPosture[posture.upper()]

    def on_audio_language(self, language_key):
        self.__notify_listeners('onAudioLanguage', language_key)

    def on_audio_intent(self, *args, intent_name):
        self.__notify_listeners('onAudioIntent', intent_name, *args)

    def on_new_audio_file(self, audio_file):
        self.__notify_listeners('onNewAudioFile', audio_file)

    def on_speech_text(self, text):
        self.__notify_listeners('onSpeechText', text)

    def on_new_picture_file(self, picture_file):
        if not self.__vision_listeners:
            self.stop_looking()
        self.__notify_listeners('onNewPictureFile', picture_file)

    def on_person_detected(self):
        self.__notify_vision_listeners('onPersonDetected')

    def on_face_recognized(self, identifier):
        self.__notify_vision_listeners('onFaceRecognized', identifier)

    def on_emotion_detected(self, emotion):
        self.__notify_vision_listeners('onEmotionDetected', emotion)

    ###########################
    # Speech Recognition      #
    ###########################

    def speech_recognition(self, context: str, max_duration: int, callback=None):
        """
        Initiate a speech recognition attempt using Google's Dialogflow using a context.
        For more information on contexts see: https://cloud.google.com/dialogflow/docs/contexts-overview

        The robot will stream audio for at most max_duraction seconds to Dialogflow to recognize something.
        The result (or a 'fail') is returned via the callback function.

        :param context: Google's Dialogflow context label (str)
        :param max_duration: maximum time to listen in seconds (int)
        :param callback: callback function that will be called when a result (or fail) becomes available
        :return:
        """
        enhanced_callback, lock = self.__build_speech_recording_callback(callback)
        self.__register_listener('onAudioIntent', enhanced_callback)
        threading.Thread(target=self.__recognizing, args=(context, lock, max_duration)).start()

    def record_audio(self, duration, callback=None):
        """
        Records audio for a number of duration seconds. The location of the audio is returned via the callback function.

        :param duration: number of second of audio that will be recorded.
        :param callback: callback function that will be called when the audio is recorded.
        :return:
        """
        enhanced_callback, lock = self.__build_speech_recording_callback(callback)
        self.__register_listener('onNewAudioFile', enhanced_callback)
        threading.Thread(target=self.__recording, args=(lock, duration)).start()

    def __recognizing(self, context, lock, max_duration):
        self.set_audio_context(context)
        self.start_listening()
        lock.wait(timeout=max_duration)
        self.stop_listening()
        if not lock.is_set():
            success = lock.wait(1)  # 1 second additional wait to give dialogflow some time to return
            # a result after closing the audio stream.
            if not success:
                self.__notify_listeners('onAudioIntent', 'fail')

    def __recording(self, lock, max_duration):
        self.set_record_audio(True)
        self.start_listening()
        lock.wait(timeout=max_duration)
        self.stop_listening()
        self.set_record_audio(False)

    @staticmethod
    def __build_speech_recording_callback(embedded_callback=None):
        lock = threading.Event()

        def callback(*args):
            if embedded_callback:
                embedded_callback(*args)
            lock.set()

        return callback, lock

    ###########################
    # Vision                  #
    ###########################

    def take_picture(self, callback=None):
        """
        Take a picture. Location of the stored picture is returned via callback.

        :param callback:
        :return:
        """
        if not self.__vision_listeners:
            self.start_looking()
        self.__register_listener("onNewPictureFile", callback)
        super(BasicSICConnector, self).take_picture()

    def start_face_recognition(self, callback):
        """
        Start face recognition. Each time a face is detected, the callback function is called with the recognition result.

        :param callback:
        :return:
        """
        self.__start_vision_recognition("onFaceRecognized", callback)

    def stop_face_recognition(self):
        """
        Stop face recognition.

        :return:
        """
        self.__stop_vision_recognition("onFaceRecognized")

    def start_people_detection(self, callback):
        """
        Start people detection. Each time a person is detected, the callback function is called.

        :param callback:
        :return:
        """
        self.__start_vision_recognition("onPersonDetected", callback)

    def stop_people_detection(self):
        """
        Stop people detection.

        :return:
        """
        self.__stop_vision_recognition("onPersonDetected")

    def start_emotion_detection(self, callback):
        """
        Start emotion detection. Each time an emotion becomes available the callback function is called with the emotion.

        :param callback:
        :return:
        """
        print("start emotion detection")
        self.__start_vision_recognition("onEmotionDetected", callback)

    def stop_emotion_detection(self):
        """
        Stop emotion detection.

        :return:
        """
        self.__stop_vision_recognition("onEmotionDetected")

    def __start_vision_recognition(self, event, callback):
        if not self.__vision_listeners:
            self.start_looking()
        self.__register_vision_listener(event, callback)

    def __stop_vision_recognition(self, event):
        self.__unregister_vision_listener(event)
        if not self.__vision_listeners:
            self.stop_looking()

    ###########################
    # Touch                   #
    ###########################

    def subscribe_touch_listener(self, touch_event, callback):
        """
        Subscribe a touch listener. The callback function will be called each time the touch_event becomes available.

        :param touch_event:
        :param callback:
        :return:
        """
        self.__touch_listeners[touch_event] = callback

    def unsubscribe_touch_listener(self, touch_event):
        """
        Unsubscribe touch listener.

        :param touch_event:
        :return:
        """
        del self.__touch_listeners[touch_event]

    ###########################
    # Robot actions           #
    ###########################

    def set_language(self, language_key: str, callback=None):
        if callback:
            self.__register_listener('LanguageChanged', callback)
        super(BasicSICConnector, self).set_language(language_key)

    def set_idle(self, callback=None):
        if callback:
            self.__register_listener("SetIdle", callback)
        super(BasicSICConnector, self).set_idle()

    def set_non_idle(self, callback=None):
        if callback:
            self.__register_listener("SetNonIdle", callback)
        super(BasicSICConnector, self).set_non_idle()

    def say(self, text: str, callback=None):
        if callback:
            self.__register_listener('TextDone', callback)
        super(BasicSICConnector, self).say(text)

    def say_animated(self, text: str, callback=None):
        if callback:
            self.__register_listener('TextDone', callback)
        super(BasicSICConnector, self).say_animated(text)

    def do_gesture(self, gesture: str, callback=None):
        if callback:
            self.__register_listener('GestureDone', callback)
        super(BasicSICConnector, self).do_gesture(gesture)

    def play_audio(self, audio_file: str, callback=None):
        if callback:
            self.__register_listener('PlayAudioDone', callback)
        super(BasicSICConnector, self).play_audio(audio_file)

    def set_eye_color(self, color: str, callback=None):
        if callback:
            self.__register_listener('EyeColourDone', callback)
        super(BasicSICConnector, self).set_eye_color(color)

    def turn_left(self, callback=None):
        if callback:
            self.__register_listener('TurnDone', callback)
        super(BasicSICConnector, self).turn_left()

    def turn_right(self, callback=None):
        if callback:
            self.__register_listener('TurnDone', callback)
        super(BasicSICConnector, self).turn_right()

    def wake_up(self, callback=None):
        if callback:
            self.__register_listener('WakeUpDone', callback)
        super(BasicSICConnector, self).wake_up()

    def rest(self, callback=None):
        if callback:
            self.__register_listener('RestDone', callback)
        super(BasicSICConnector, self).rest()

    def set_breathing(self, enable: bool, callback=None):
        if callback:
            if enable:
                self.__register_listener('BreathingEnabled', callback)
            else:
                self.__register_listener('BreathingDisabled', callback)
        super(BasicSICConnector, self).set_breathing(enable)

    def go_to_posture(self, posture: Enum, speed: float = 1.0, callback=None):
        if callback:
            self.__register_listener('GoToPostureDone', functools.partial(self.__posture_callback,
                                                                          target_posture=posture,
                                                                          embedded_callback=callback))
        super(BasicSICConnector, self).go_to_posture(posture.value, speed)

    def __posture_callback(self, target_posture, embedded_callback):
        if self.robot_state['posture'] == target_posture:  # if posture was successfully reached
            embedded_callback(True)  # call the listener to signal a success
        else:  # if the posture was not reached
            embedded_callback(False)  # call the listener to signal a failure

    ###########################
    # Robot action Listeners  #
    ###########################

    def subscribe_condition(self, condition: threading.Condition):
        """
        Subscribe a threading.Condition object that will be notified each time a registered callback is called.

        :param condition: threading.Condition object that will be notified
        :return:
        """
        self.__conditions.append(condition)

    def unsubscribe_condition(self, condition: threading.Condition):
        """
        Unsubscribe the threading.Condition object.

        :param condition: threading.Condition object to unsubscribe
        :return:
        """
        if condition in self.__conditions:
            self.__conditions.remove(condition)

    def __notify_conditions(self):
        for condition in self.__conditions:
            with condition:
                condition.notify()

    def __register_listener(self, event, callback):
        if event in self.__listeners:
            self.__listeners[event].put(callback)
        else:
            queue = Queue()
            queue.put(callback)
            self.__listeners[event] = queue

    def __register_vision_listener(self, event, callback):
        self.__vision_listeners[event] = callback

    def __unregister_vision_listener(self, event):
        del self.__vision_listeners[event]

    def __notify_listeners(self, event, *args):
        # If there is a listener for the event
        if event in self.__listeners and not self.__listeners[event].empty():
            # only the the first one will be notified
            listener = self.__listeners[event].get()
            # notify the listener
            listener(*args)
            self.__notify_conditions()

    def __notify_vision_listeners(self, event, *args):
        if event in self.__vision_listeners:
            listener = self.__vision_listeners[event]
            listener(*args)
            self.__notify_conditions()

    def __notify_touch_listeners(self, event, *args):
        if event in self.__touch_listeners:
            listener = self.__touch_listeners[event]
            listener(*args)
            self.__notify_conditions()

    ###########################
    # Management              #
    ###########################

    def start(self):
        self.__clear_listeners()
        super(BasicSICConnector, self).start()

    def stop(self):
        self.__clear_listeners()
        super(BasicSICConnector, self).stop()

    def __clear_listeners(self):
        self.__listeners = {}
        self.__conditions = []
        self.__vision_listeners = {}
        self.__touch_listeners = {}
