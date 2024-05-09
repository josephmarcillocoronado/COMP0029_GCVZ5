'''
Author: Michal Bravansky
'''
from time import monotonic

import numpy as np
from lib.modules import Side

from lib.drivers import keyboard, mouse
from lib.gestures import Pose
from lib.modules import Person
from lib.view import View
from lib.view.elements.face_element import FaceElement

class HeadSuikaController(Pose):
    """This pose is used to operate the game Suika with head movements.

    Args:
        method (str): The method used to detect triggers. Can be "tilt" or "turn".
        show_face (bool): Flag indicating whether to show the face element.

    Attributes:
        _method (str): The method used to detect triggers.
        view_element (FaceElement): The face element to be shown.

    """

    def __init__(self, method, show_face: True):
        self._method = method
        super().__init__()
        if show_face:
            self.view_element = FaceElement(face_colour=(0, 255, 0))

    @classmethod
    def from_kwargs(cls, **kwargs) -> 'Pose':
        """
        This pose is used to operate the game Suika with head movements.

        Args:
            method (str): The method used to detect triggers. Can be "tilt" or "turn".
            show_face (bool): Flag indicating whether to show the face element.
        """
        method = kwargs.get('method')
        show_face = kwargs.get('show_face')

        if not isinstance(show_face, bool):
            raise ValueError("show_face must be a boolean value")

        return cls(method=method, show_face=show_face)
    
    def _get_triggers(self, person: Person) -> tuple:
        """Get the triggers based on the method.

        Args:
            person (Person): The person object containing head information.

        Returns:
            tuple: A tuple of triggers based on the method.

        """
        if self._method == "tilt":
            return (person.head.tilt_left, person.head.tilt_right)
        else:
            return (person.head.turn_left, person.head.turn_right)
    

    def action(self, person: Person, view: View) -> bool:
        """Perform the action based on the detected triggers.

        Args:
            person (Person): The person object containing head information.
            view (View): The view object for displaying the action.

        Returns:
            bool: True if the action is performed successfully, False otherwise.

        """
        left_trigger, right_trigger = self._get_triggers(person)

        if person.head.fish_face and not self._mouse_click:
            mouse.click("left")
            self._mouse_click = True
        elif not person.head.fish_face:
            self._mouse_click = False
        
        if left_trigger:
            mouse.move(-10, 0)
        
        if right_trigger:
            mouse.move(10, 0)

    def check(self, person: Person) -> bool:
        """Check if the pose is valid based on the detected triggers.

        Args:
            person (Person): The person object containing head information.

        Returns:
            bool: True if the pose is valid, False otherwise.

        """
        if not person.head:
            return False
        
        if self.view_element:
            self.view_element.update_face_elements(person.head)

        left_trigger, right_trigger = self._get_triggers(person)

        if not person.head.fish_face and not left_trigger and not right_trigger:
            self._mouse_click = False
            return False

        return True