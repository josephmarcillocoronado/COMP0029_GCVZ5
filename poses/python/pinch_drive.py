'''
Author: Michal Bravansky
'''
from time import monotonic

import numpy as np
from lib.modules import Side

from lib.drivers import keyboard
from lib.gestures import Pose
from lib.modules import Person
from lib.view import View
from lib.view.elements.steering_wheel import SteeringWheelElement


class PinchDrive(Pose):
    """
    A class that represents a specific pose for driving.

    Attributes:
        hand (Side): The hand side (left or right).

    Args:
        hand (Side): The hand side (left or right).
        **kwargs: Arbitrary keyword arguments.

    Methods:
        __init__(self, hand: Side, **kwargs): Initializes the PinchDrive instance.
        from_kwargs(cls, **kwargs) -> 'Pose': Class method to create a PinchDrive instance from keyword arguments.
        action(self, person: Person, view: View) -> bool: Performs an action based on the pose.
    """
    def __init__(self, hand: Side, **kwargs):
        """
        Initializes the PinchDrive instance.

        Args:
            hand (Side): The hand side (left or right).
            **kwargs: Arbitrary keyword arguments.
        """
        self.hand = hand
        super().__init__(**kwargs)

    @classmethod
    def from_kwargs(cls, **kwargs) -> 'Pose':
        """
        This pose is used to represents a pose for driving based on pinching with the left and right hands.
        
        Args:
            hand (Literal['left', 'right']): The side of the hand (LEFT or RIGHT).
            method (str): The method of the action.
            args (list[str]): The arguments of the action.
        """
        method, args = cls._get_method_and_args(**kwargs)

        hand = kwargs.get('hand')
        if hand:
            hand = Side[hand.upper()]

        return cls(hand=hand, method=method, args=args)
    

    def action(self, person: Person, view: View) -> bool:
        """
        Performs an action based on the pose. It simulates keyboard presses based on the pinching state of the left and right hands.

        Args:
            person (Person): The person performing the pose.
            view (View): The view in which the pose is performed.
        """
        left_hand = person.hands[0]
        right_hand = person.hands[1]
        left_pinched = left_hand.index_pinched
        right_pinched = right_hand.index_pinched

        keyboard.press("w")

        if left_pinched and not right_pinched:
            keyboard.press("a")
        
        if not left_pinched and right_pinched:
            keyboard.press("d")

    def check(self, person: Person) -> bool:
        """
        Checks if the pose is being performed by the person.

        Args:
            person (Person): The person to check the pose for.
        """
        if not person.hands:
            return False
        
        left_hand = person.hands[0]
        right_hand = person.hands[1]

        if not left_hand or not right_hand:
            return False
        
        left_pinched = left_hand.index_pinched

        right_pinched = right_hand.index_pinched

        return left_pinched or right_pinched