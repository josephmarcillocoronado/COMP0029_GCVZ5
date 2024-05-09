"""
Author: Dexin Fu
"""
from numpy import ndarray

from lib.gestures import Pose
from lib.drivers import keyboard
from lib.modules import Side, Person
from lib.view import View


class MRSwipeEvent(Pose):
    def __init__(self, hand: Side, sensitivity: float, threshold_min: float, threshold_max: float, horizontal: bool):
        super().__init__()
        self.hand = hand
        self._sensitivity = sensitivity
        self._threshold_min = threshold_min
        self._threshold_max = threshold_max
        self._counter = 0
        self._previous_direction = None
        self._horizontal = horizontal

    @classmethod
    def from_kwargs(cls, **kwargs) -> 'Pose':
        """
        This pose is used to detect the swipe gesture and perform the corresponding action.

        Args:
            hand (Literal['left', 'right']): The side of the hand (LEFT or RIGHT).
            sensitivity (int): The sensitivity value, need to be bigger than 0.
            threshold_min (float): The minimum threshold of the gesture, the value should be in range of 0 to 1.
            threshold_max (float): The maximum threshold of the gesture, the value should be in range of 0 to 1.
            horizontal (bool): Whether the swipe in horzontal or not.
        """
        hand = Side[kwargs.get('hand').upper()]
        sensitivity = kwargs.get('sensitivity')
        threshold_min = kwargs.get('threshold_min')
        threshold_max = kwargs.get('threshold_max')
        horizontal = kwargs.get('horizontal')

        return cls(hand=hand, sensitivity=sensitivity, threshold_min=threshold_min,
                   threshold_max=threshold_max, horizontal=horizontal)

    def action(self, person: Person, view: View) -> None:
        hand = person.hands[self.hand]
        middle_tip_coord = hand['middle_tip']
        direction = self._check_hand_pos(middle_tip_coord)
        if direction is None:
            return

        if direction == self._previous_direction and not self._check_is_center(middle_tip_coord):
            self._counter += 1
        else:
            self._counter = 0

        if self._previous_direction != direction:
            keyboard.release(self._previous_direction)
            self._previous_direction = direction
        elif self._counter > self._sensitivity:
            keyboard.press(direction)

    def check(self, person: Person) -> bool:
        if not person.hands:
            return False

        hand = person.hands[self.hand]
        return hand and hand.middle_stretched and hand.index_stretched

    def _check_is_center(self, coord: ndarray) -> bool:
        return (   # type: ignore
                self._threshold_min < coord[0] <= self._threshold_max and
                self._threshold_min < coord[1] <= self._threshold_max
        )

    def _check_hand_pos(self, coords: ndarray) -> str | None:
        if self._horizontal:
            if coords[0] > self._threshold_max:
                return "right"
            elif coords[0] <= self._threshold_min:
                return "left"
        else:
            if coords[1] > self._threshold_max:
                return "down"
            elif coords[1] <= self._threshold_min:
                return "up"
