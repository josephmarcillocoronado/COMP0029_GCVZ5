from time import time
from typing import Optional, Literal, Callable

from lib.drivers import flags
from lib.gestures import Pose
from lib.modules import Person
from lib.view import View

SIDE = Literal['left', 'right']


class Action:
    def __init__(self, method: Callable = None, args: list = None, flag: str = None):
        self.method = method
        self.args = args
        self.flag = flag

    def __call__(self):
        if self.method:
            self.method(*self.args)


class BodyHeadTurn(Pose):
    def __init__(self, left: Action = None, right: Action = None):
        super().__init__()
        self.left = left
        self.right = right
        self.side: SIDE | None = None
        self.open = {'left': False, 'right': False}
        self.time_opened = time()

    @classmethod
    def from_kwargs(cls, **kwargs) -> 'Pose':
        """
        This pose is used to detect when a person turns their head to the left or right.

        Args:
            left (dict[str, str]): The left action, will have three elements in it: method, args, flag.
                                    method (str): The method of the action.
                                    args (list[str]): The arguments of the action.
                                    flag (str): The flag of the action
            right (dict[str, str]): The right action, will have three elements in it: method, args, flag.
                                    method (str): The method of the action.
                                    args (list[str]): The arguments of the action.
                                    flag (str): The flag of the action.
        """
        left_action = right_action = None

        if left := kwargs.get('left'):
            left_method, left_args = cls._get_method_and_args(**left)
            left_action = Action(method=left_method, args=left_args, flag=left.get('flag'))
        if right := kwargs.get('right'):
            right_method, right_args = cls._get_method_and_args(**right)
            right_action = Action(method=right_method, args=right_args, flag=right.get('flag'))

        return cls(left=left_action, right=right_action)

    def check(self, person: Person) -> bool:
        nose = person.body.get('nose')
        if nose is None:
            return False

        left_ear = person.body.get('left_ear')
        if left_ear is None:
            return False

        right_ear = person.body.get('right_ear')
        if right_ear is None:
            return False

        self.side = None
        # If nose crosses over left ear, register as left turn
        if nose[0] < left_ear[0]:
            self.side = 'left'

        # If nose crosses over right ear, register as right turn
        elif nose[0] > right_ear[0]:
            self.side = 'right'

        if self.side:
            if time() - self.time_opened < 1:
                return False

            self.open[self.side] = not self.open[self.side]
            self.time_opened = time()
            return True

        return False

    def action(self, person: Person, view: Optional[View]) -> None:
        if self.left and self.side == 'left':
            if self.left.flag:
                flags.set(self.left.flag, self.open['left'])
                if self.right and self.right.flag:
                    flags.set(self.right.flag, False)

            self.left()

        if self.right and self.side == 'right':
            if self.right.flag:
                flags.set(self.right.flag, self.open['right'])
                if self.left and self.left.flag:
                    flags.set(self.left.flag, False)

            self.right()
