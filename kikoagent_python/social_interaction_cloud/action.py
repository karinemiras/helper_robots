import functools
import threading
from social_interaction_cloud.basic_connector import BasicSICConnector


class Action:
    """
    Encapsulation class for BasicSICConnector method calls.

    The BasicSICConnector method call is executed when the perform() method is called. To create a waiting action,
    a threading.Event() object should be provided as lock.
    """

    def __init__(self, action: callable, *args, callback: callable = None, lock: threading.Event() = None):
        """

        :param action: a callable from the BasicSICConnector
        :param args: optional input arguments for the callable
        :param callback: optional callback function that will be triggered when the result
        of the BasicSICConnector action becomes available
        :param lock: optional lock to create a waiting Action.
        """
        self.action = action
        self.callback = callback
        self.lock = lock
        self.args = args

    def perform(self) -> threading.Event():
        """
        Calls the action callable.
        :return: the lock
        """
        self.action(*self.args, callback=self.callback)
        return self.lock


class ActionFactory:
    """
    Factory class that builds Actions, waiting Actions, and listeners for BasicSICConnector vision and touch events.
    """

    def __init__(self, sic: BasicSICConnector):
        """

        :param sic: BasicSICConnector object
        """
        self.sic = sic

    def build_action(self, action_name: str, *args, callback=None, lock: threading.Event() = None):
        """
        Builds an Action object.

        :param action_name: name of targeted BasicSICConnector method
        :param args: input arguments for targeted BasicSICConnector method (except callback function)
        :param callback: optional callback function to register with BasicSICConnector method call
        :param lock: optional threading.Event() to create a waiting action
        :return:
        """
        action = getattr(self.sic, action_name)
        return Action(action, *args, callback=callback, lock=lock)

    def build_waiting_action(self, action_name: str, *args, additional_callback=None):
        """
        Builds an Action object with a lock, called a waiting Action.

        :param action_name: name of targeted BasicSICConnector method
        :param args: input arguments for targeted BasicSICConnector method (except callback function)
        :param additional_callback: optional callback function to register with BasicSICConnector method call that
        will be embedded in the internal waiting callback.
        :return:
        """
        callback, lock = self.__build_waiting_callback(additional_callback)
        return self.build_action(action_name, *args, callback=callback, lock=lock)

    def build_vision_listener(self, vision_type: str, callback=None, continuous=False):
        """
        Builds a special action that registers a vision listener.

        :param vision_type: targeted vision recognition system.
        - 'face' for facial recognition;
        - 'people' for people detection;
        - 'emotion' for emotion detection.
        :param callback: optional callback that is triggered when a vision recognition system result becomes available.
        :param continuous: if True it will trigger the callback for each result and if False it will trigger it only once.
        :return:
        """
        lock = None
        if not continuous:
            callback, lock = self.__build_vision_stopping_callback(vision_type.lower(), callback)
        else:
            if not callback:
                raise ValueError("To build a continuous listener, you need to supply a callback function.")

        if vision_type.lower() == 'face':
            return self.build_action('start_face_recognition', callback=callback, lock=lock)
        elif vision_type.lower() == 'people':
            return self.build_action('start_people_detection', callback=callback, lock=lock)
        elif vision_type.lower() == 'emotion':
            return self.build_action('start_emotion_detection', callback=callback, lock=lock)
        else:
            raise ValueError('vision_type only supports a value of "face", "people", or "emotion"')

    def build_touch_listener(self, touch_event, callback=None, continuous=False):
        """
        Builds a special action that registers a vision listener.

        :param touch_event: touch event the callback function will be registered to.
        :param callback: callback function that will trigger when the targeted touch event becomes available.
        :param continuous: if True it will trigger the callback for each event and if False it will trigger it only once.
        :return:
        """
        lock = None
        if not continuous:
            callback, lock = self.__build_touch_stopping_callback(touch_event, callback)

        return self.build_action('subscribe_touch_listener', touch_event, callback=callback, lock=lock)

    @staticmethod
    def __build_waiting_callback(additional_callback=None):
        """
        Builds a callback function that calls set() on an threading.Event() lock when trigger.
        This is the main mechanism behind a waiting Action.

        :param additional_callback: callback function to be embedded in the waiting callback
        :return:
        """
        lock = threading.Event()

        def callback(*args):
            if additional_callback:
                additional_callback(*args)
            lock.set()

        return callback, lock

    def __build_vision_stopping_callback(self, vision_type, original_callback=None):
        """
        Builds callback function for a single use vision listener.

        :param vision_type:
        :param original_callback:
        :return:
        """
        if vision_type == 'face':
            stop_vision = self.sic.stop_face_recognition
        elif vision_type == 'people':
            stop_vision = self.sic.stop_people_detection
        elif vision_type == 'emotion':
            stop_vision = self.sic.stop_emotion_detection
        else:
            raise ValueError('vision_type only supports a value of "face", "people", or "emotion"')

        def callback(*args):
            if original_callback:
                original_callback(*args)
            stop_vision()

        return self.__build_waiting_callback(callback)

    def __build_touch_stopping_callback(self, touch_event, original_callback=None):
        """
        Builds callback function for a single use touch listener.

        :param touch_event:
        :param original_callback:
        :return:
        """
        stop_listening = functools.partial(self.sic.unsubscribe_touch_listener, touch_event)

        def callback(*args):
            if original_callback:
                original_callback(*args)
            stop_listening()

        return self.__build_waiting_callback(callback)


class ActionRunner:
    """
    Executive class that can be used to either directly run an Action or to preload actions and run them at a
    desired moment.
    """

    def __init__(self, sic: BasicSICConnector):
        """

        :param sic: a BasicSICConnector object
        """
        self.cbsr = sic
        self.action_factory = ActionFactory(sic)
        self.loaded_actions = []

    def load_action(self, action_name: str, *args, callback=None):
        """
        Loads Action. Will be executed when run_loaded_actions() is called

        :param action_name: name of targeted BasicSICConnector method
        :param args: input arguments for targeted BasicSICConnector method (except callback function)
        :param callback: optional callback function to register with BasicSICConnector method call
        :return:
        """
        self.loaded_actions.append(self.action_factory.build_action(action_name, *args, callback=callback))

    def load_waiting_action(self, action_name: str, *args, additional_callback=None):
        """
        Loads waiting Action. Will be executed when run_loaded_actions() is called

        :param action_name: name of targeted BasicSICConnector method
        :param args: input arguments for targeted BasicSICConnector method (except callback function)
        :param additional_callback: optional callback function to register with BasicSICConnector method call that
        will be embedded in the internal waiting callback.
        """
        self.loaded_actions.append(self.action_factory.build_waiting_action(action_name, *args,
                                                                            additional_callback=additional_callback))

    def load_vision_listener(self, vision_type: str, callback, continuous=False):
        """
        Loads vision recognition system listener. Will be executed when run_loaded_actions() is called

        :param vision_type: targeted vision recognition system.
        - 'face' for facial recognition;
        - 'people' for people detection;
        - 'emotion' for emotion detection.
        :param callback: optional callback that is triggered when a vision recognition system result becomes available.
        :param continuous: if True it will trigger the callback for each result and if False it will trigger it only once.
        :return:
        """
        self.loaded_actions.append(self.action_factory.build_vision_listener(vision_type, callback, continuous))

    def load_touch_listener(self, touch_even: str, callback=None, continuous=False):
        """
        Loads touch event listener. Will be executed when run_loaded_actions() is called

        :param touch_event: touch event the callback function will be registered to.
        :param callback: callback function that will trigger when the targeted touch event becomes available.
        :param continuous: if True it will trigger the callback for each event and if False it will trigger it only once.
        :return:
        """
        self.loaded_actions.append(self.action_factory.build_touch_listener(touch_even, callback, continuous))

    def clear(self):
        """
        Clears loaded action

        :return:
        """
        self.loaded_actions = []

    def run_loaded_actions(self, clear: bool = True):
        """
        Call all loaded targeted BasicSICConnector methods. They are all encapsulated in Action objects.
        It will wait until all waiting Actions are finished.

        :param clear: if True it will call clear() and clear all loaded actions.
        :return:
        """
        locks = []
        for action in self.loaded_actions:
            lock = action.perform()
            if lock:
                locks.append(lock)

        if locks:
            condition = threading.Condition()
            self.cbsr.subscribe_condition(condition)
            with condition:
                condition.wait_for(lambda: all([_lock.is_set() for _lock in locks]))
            self.cbsr.unsubscribe_condition(condition)

        if clear:
            self.clear()
        else:
            for lock in locks:
                lock.clear()

    def run_action(self, action_name: str, *args, callback=None):
        """
        Calls targeted BasicSICConnector method.

        :param action_name: name of targeted BasicSICConnector method
        :param args: input arguments for targeted BasicSICConnector method (except callback function)
        :param callback: optional callback function to register with BasicSICConnector method call
        :return:
        """
        action = self.action_factory.build_action(action_name, *args, callback=callback)
        action.perform()

    def run_waiting_action(self, action_name: str, *args, additional_callback=None):
        """
        Calls targeted BasicSICConnector method and waits until it is finished.

        :param action_name: name of targeted BasicSICConnector method
        :param args: input arguments for targeted BasicSICConnector method (except callback function)
        :param additional_callback: optional callback function to register with BasicSICConnector method call that
        will be embedded in the internal waiting callback.
        :return:
        """
        action = self.action_factory.build_waiting_action(action_name, *args, additional_callback=additional_callback)
        lock = action.perform()
        lock.wait()

    def run_vision_listener(self, vision_type: str, callback, continuous=False):
        """
        Registers callback to selected vision recognition system events.

        :param vision_type: targeted vision recognition system.
        - 'face' for facial recognition;
        - 'people' for people detection;
        - 'emotion' for emotion detection.
        :param callback: optional callback that is triggered when a vision recognition system result becomes available.
        :param continuous: if True it will trigger the callback for each result and if False it will trigger it only once.
        :return:
        """
        action = self.action_factory.build_vision_listener(vision_type, callback, continuous)
        lock = action.perform()
        if lock:
            lock.wait()

    def run_touch_listener(self, touch_event: str, callback=None, continuous=False):
        """
        Registers callback to selected touch event.

        :param touch_event: touch event the callback function will be registered to.
        :param callback: callback function that will trigger when the targeted touch event becomes available.
        :param continuous: if True it will trigger the callback for each event and if False it will trigger it only once.
        :return:
        """
        action = self.action_factory.build_touch_listener(touch_event, callback, continuous)
        lock = action.perform()
        if lock:
            lock.wait()
