from typing import Callable

from lib.gestures import Pose
from lib.modules import Person
from lib.view.elements.base import ViewElement


class Smile(Pose):
    def __init__(
            self,
            name: str,
            method: Callable,
            args: tuple = (),
            view_element: ViewElement = None,
            ignore: str = None
    ):
        super().__init__(name=name, method=method, args=args, view_element=view_element)
        self.triggered = False

    def check(self, person: Person) -> bool:
        if person.head is None:
            self.triggered = False
            return False

        try:
            is_smiling = person.head.smiling
        except KeyError:
            self.triggered = False
            return False
        
        if is_smiling:
            if not self.triggered:
                self.triggered = True
                return True
            else:
                return False
        else:
            self.triggered = False
