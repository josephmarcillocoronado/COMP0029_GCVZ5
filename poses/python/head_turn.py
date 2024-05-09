from collections import deque
from typing import Optional

from lib.config import config
from lib.drivers import flags
from lib.gestures import Pose
from lib.modules import Person
from lib.view import View


LEFT_THRESHOLD = config.get("head/turn_left")
RIGHT_THRESHOLD = config.get("head/turn_right")


class HeadTilt(Pose):
    def __init__(self, left_flag: str, right_flag: str, queue_size: int = 5, confidence: float = 0.7):
        super().__init__()
        self.left_flag = left_flag
        self.right_flag = right_flag
        self._queue = deque(maxlen=queue_size)
        self._confidence = confidence

    @classmethod
    def from_kwargs(cls, **kwargs) -> 'Pose':
        """
        This pose is used to detect when a person turn their head to the left or right.

        Args:
            left_flag (str): The flag to set when the head is tilted to the left.
            right_flag (str): The flag to set when the head is tilted to the right.
        """
        left_flag = kwargs.get('left_flag')
        right_flag = kwargs.get('right_flag')

        return cls(left_flag=left_flag, right_flag=right_flag)

    @staticmethod
    def _get_ratio(person: Person) -> float:
        point_distance_left = person.head.distance_squared("nose-tip", "left-cheek")
        point_distance_right = person.head.distance_squared("nose-tip", "right-cheek")

        return point_distance_left - point_distance_right

    def check(self, person: Person) -> bool:
        if person.head is None:
            return False

        try:
            self._queue.append(self._get_ratio(person))
        except (KeyError, AttributeError):
            return False

        return True

    def action(self, person: Person, view: Optional[View]) -> None:
        left = right = 0
        for angle in self._queue:
            if angle < LEFT_THRESHOLD:
                right += 1
            elif angle > RIGHT_THRESHOLD:
                left += 1

        left /= len(self._queue)
        right /= len(self._queue)

        if left > self._confidence:
            flags.set(self.left_flag, True)
            flags.set(self.right_flag, False)
        elif right > self._confidence:
            flags.set(self.left_flag, False)
            flags.set(self.right_flag, True)
