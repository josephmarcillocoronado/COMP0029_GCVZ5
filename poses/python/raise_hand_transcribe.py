from lib.gestures import Pose
from lib.drivers import keyboard, mouse, kita_controller
from lib.modules import Side, Person
from collections import deque
from lib.config import config
from lib.view import View

WRIST_ELBOW_X_THRESHOLD = 70

class RaiseHandTranscribe(Pose):
    def __init__(
            self,
            hand: str = "right",
            **kwargs
    ):
        super().__init__(**kwargs)
        hand = Side[hand.upper()]
        self._wrist_landmark = "right_wrist" if hand == Side.RIGHT else "left_wrist"
        self._elbow_landmark = "right_elbow" if hand == Side.RIGHT else "left_elbow"
        self.transcribing = False

    @classmethod
    def from_kwargs(cls, **kwargs) -> 'Pose':
        """
        This pose is used to detect when a person raises their hand and transcribe what they say.

        Args:
            hand (str): The hand to use for the gesture.
            method (str): The method of the action.
            args (list[str]): The arguments of the action.
        """
        method, args = cls._get_method_and_args(**kwargs)
        hand = kwargs.get('hand')

        return cls(method=method, args=args, hand=hand)

    def stop_ongoing_transcription(self):
        if self.transcribing:
            kita_controller.stop_transcription()
            self.transcribing = False

    def check(self, person: Person) -> bool:
        if not person.body or self._wrist_landmark not in person.body or self._elbow_landmark not in person.body:
            self.stop_ongoing_transcription()
            return False    
        

        wrist_x = person.body[self._wrist_landmark][0]
        wrist_y = person.body[self._wrist_landmark][1]

        elbow_x = person.body[self._elbow_landmark][0]
        elbow_y = person.body[self._elbow_landmark][1]

        # check that they are lined up horizontally and that the wrist is above the elbow
        if wrist_y < elbow_y and abs(wrist_x - elbow_x) < WRIST_ELBOW_X_THRESHOLD:
            return True
        self.stop_ongoing_transcription()
        return False


    def action(self, person: Person, view: View) -> None:
        if not self.transcribing:
            self.transcribing = True
            kita_controller.start_transcription()