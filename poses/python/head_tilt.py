import math
from collections import deque
from typing import Optional, Callable

from lib.config import config
from lib.drivers import flags
from lib.gestures import Pose
from lib.modules import Person
from lib.view import View

LEFT_THRESHOLD = config.get("head/tilt_left")
RIGHT_THRESHOLD = config.get("head/tilt_right")

""""""
class HeadTilt(Pose):
    def __init__(
            self,
            left_flag: str = None,
            right_flag: str = None,
            queue_size: int = 5,
            confidence: float = 0.7,
            left_method: Callable = None,
            left_args: tuple = None,
            right_method: Callable = None,
            right_args: tuple = None
    ):
        super().__init__()
        self.left_flag = left_flag
        self.right_flag = right_flag
        self.left_method = left_method
        self.left_args = left_args
        self.right_method = right_method
        self.right_args = right_args
        self._queue = deque(maxlen=queue_size)
        self._confidence = confidence

    @classmethod
    def from_kwargs(cls, **kwargs) -> 'Pose':
        """
        This pose is used to detect when a person tilts their head to the left or right.

        Args:
            left_flag (str): The flag to set when the head is tilted to the left.
            right_flag (str): The flag to set when the head is tilted to the right.
        """
        left_flag = kwargs.get('left_flag')
        right_flag = kwargs.get('right_flag')

        if left := kwargs.get('left'):
            _d = {"action": left}
            left_method, left_args = cls._get_method_and_args(**_d)
        else:
            left_method = None
            left_args = None

        if right := kwargs.get('right'):
            _d = {"action": right}
            right_method, right_args = cls._get_method_and_args(**_d)
        else:
            right_method = None
            right_args = None

        return cls(left_flag=left_flag, right_flag=right_flag, left_method=left_method,
                   left_args=left_args, right_method=right_method, right_args=right_args)

    @staticmethod
    def _get_angle(person: Person) -> float:
        height_vector = person.head["temple-centre"] - person.head["chin-centre"]
        return math.atan2(height_vector[1], height_vector[0]) + math.pi / 2

    def check(self, person: Person) -> bool:
        if person.head is None:
            return False

        try:
            self._queue.append(self._get_angle(person))
        except KeyError:
            return False

        return True

    def action(self, person: Person, view: Optional[View]) -> None:
        left = right = 0
        for angle in self._queue:
            if angle < LEFT_THRESHOLD:
                left += 1
            elif angle > RIGHT_THRESHOLD:
                right += 1

        left /= len(self._queue)
        right /= len(self._queue)

        if left > self._confidence:
            if self.left_method:
                self.left_method(*self.left_args)
            if self.left_flag:
                flags.set(self.left_flag, True)
            if self.right_flag:
                flags.set(self.right_flag, False)
        elif right > self._confidence:
            if self.right_method:
                self.right_method(*self.right_args)
            if self.left_flag:
                flags.set(self.left_flag, False)
            if self.right_flag:
                flags.set(self.right_flag, True)
