from typing import Callable

from lib.gestures import Pose
from lib.modules import Person
from lib.view.elements.base import ViewElement

class FishFace(Pose):
    
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
            is_fish_face = person.head.fish_face
        except KeyError:
            self.triggered = False
            return False
        
        if is_fish_face:
            if not self.triggered:
                self.triggered = True
                return True
            else:
                return False
        else:
            self.triggered = False