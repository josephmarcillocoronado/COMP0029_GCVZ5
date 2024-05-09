'''
Author: Suhas Hariharan
'''
from lib.gestures import HandPose, RepeatedPose
from lib.drivers import keyboard, mouse
from lib.modules import Side, Person
from collections import deque
from lib.config import config
from lib.view import View

"""
An event that triggers after two consecutive pinches.
Example of using RepeatedPose.
"""
class HandDoublePinchEvent(RepeatedPose, HandPose):
    """
    The HandDoublePinchEvent class inherits from RepeatedPose and HandPose. It represents a double pinch gesture.

    Attributes:
        hand (Side): The hand side (left or right).
    
    Args:
        hand (Side): The hand side (left or right).
        key_hold (bool): Whether the key is held down.
        num_frames (int): The number of frames to check for.
        num_repetitions (int): The number of repetitions to trigger an action.
        **kwargs: Arbitrary keyword arguments.

    Methods:
        __init__(self, hand: Side, **kwargs): Initializes the PinchDrive instance.
        from_kwargs(cls, **kwargs) -> 'Pose': Class method to create a PinchDrive instance from keyword arguments.
        action(self, person: Person, view: View) -> bool: Performs an action based on the pose.
    """
    def __init__(self, hand: Side, key_hold: bool, num_frames: int, num_repetitions: int, **kwargs):
        """
        Initializes the HandDoublePinchEvent instance.

        Args:
            hand (Side): The hand side (left or right).
            key_hold (bool): Whether the key is held down.
            num_frames (int): The number of frames to check for.
            num_repetitions (int): The number of repetitions to trigger an action.
            **kwargs: Arbitrary keyword arguments.

        Methods:
            __init__(self, hand: Side, **kwargs): Initializes the PinchDrive instance.
            from_kwargs(cls, **kwargs) -> 'Pose': Class method to create a PinchDrive instance from keyword arguments.
            action(self, person: Person, view: View) -> bool: Performs an action based on the pose.
        """
        
        RepeatedPose.__init__(self, num_frames=num_frames, num_repetitions=num_repetitions)
        HandPose.__init__(self, hand=hand, **kwargs)
        self._already_pinched = False
        self._key_hold = key_hold

    @classmethod
    def from_kwargs(cls, **kwargs) -> 'HandPose':
        """
        This pose is used to represents a double pinch gesture, which is a specific hand pose.
    
        Args:
            hand (Literal['left', 'right']): The side of the hand (LEFT or RIGHT).
            key_hold (bool): Whether the key is held down.
            num_frames (int): The number of frames to check for.
            num_repetitions (int): The number of repetitions to trigger an action.
        """
        method, args = cls._get_method_and_args(**kwargs)

        hand = kwargs.get('hand')
        if hand:
            hand = Side[hand.upper()]

        key_hold = kwargs.get('key_hold')
        num_frames = kwargs.get('num_frames')
        num_repetitions = kwargs.get('num_repetitions')

        return cls(hand=hand,key_hold =key_hold, num_frames=num_frames, num_repetitions=num_repetitions, method=method, args = args)


    def check(self, person: Person) -> bool:
        """
        This method will return True if the index finger is pinched and if the key is held down.

        Args:
            person (Person): The person to check.

        Returns:
            bool: whether the pose is valid.
        """
        hand = person.hands[self.hand]
        if not hand:
            return False
        
        index_pinched = hand.index_pinched
        
        if index_pinched and self._key_hold:
            return True
        
        if not self._key_hold and index_pinched and not self._already_pinched:
            self._already_pinched = True
            return True
        elif not index_pinched: 
            self._already_pinched = False
        return False
