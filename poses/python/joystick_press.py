'''
Author: Michal Bravansky
'''

from lib.gestures import HandPose
from lib.modules import Side, Person
from lib.modules.hands import Hand
from lib.view import View
from lib.drivers import mouse, display
import inspect
import functools

class JoystickButtonPress(HandPose):
    """
    Represents a joystick button press hand pose.

    Args:
        hand (Side): The side of the hand (left or right).
        gesture (dict[str, str], optional): A dictionary mapping gesture methods to expected values. Defaults to None.
        **kwargs: Additional keyword arguments.

    Raises:
        Exception: If any unrecognized gestures are provided.

    Attributes:
        hand (Side): The side of the hand (left or right).
        gesture (dict[str, str]): A dictionary mapping gesture methods to expected values.

    Methods:
        from_kwargs: Create a JoystickButtonPress instance from keyword arguments.
        check: Check if the given person's hand matches the expected gesture.

    """

    def __init__(self, hand: Side, gesture: dict[str, str] = None, **kwargs):
        super().__init__(hand=hand, **kwargs)
        self.hand = hand

        unrecognized_gestures = [gesture for gesture in gesture.keys() if not gesture in self._get_hand_properties()]

        if unrecognized_gestures:
            raise Exception("Gestures not recognized in JoystickButtonPress: " + ", ".join(unrecognized_gestures))
        
        self.gesture = gesture


    def _get_hand_properties(self):
        """
        Get the available gesture methods of the Hand class.

        Returns:
            List[str]: A list of available gesture methods.

        """
        return [name for name, value in inspect.getmembers(Hand)]

    @classmethod
    def from_kwargs(cls, **kwargs) -> 'HandPose':
        """
        This pose is used to represents a joystick button press hand pose.

        Args:
            hand (Literal['left', 'right']): The side of the hand (left or right).
            gesture (dict[str, str], optional): A dictionary mapping gesture methods to expected values. Defaults to None.
        """
        method, args = cls._get_method_and_args(**kwargs)

        hand = kwargs.get('hand').upper()
        if not hand in Side:
            raise ValueError("hand must be a valid Side value")
        
        hand = Side[hand]
        
        gesture = kwargs.get("gesture")

        return cls(method=method, args=args, hand=hand, gesture = gesture)
    
    def check(self, person: Person) -> bool:
        """
        Check if the given person's hand matches the expected gesture.

        Args:
            person (Person): The person to check.

        Returns:
            bool: True if the hand matches the expected gesture, False otherwise.

        """
        if not person.hands or not person.hands[self.hand]:
            return False
        
        hand = person.hands[self.hand]

        for gesture_method, expected_value in self.gesture.items():
            method = getattr(hand, gesture_method)
            if method != expected_value:
                return False
            
        return True