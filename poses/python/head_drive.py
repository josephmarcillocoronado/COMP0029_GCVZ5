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
from lib.view.elements.face_element import FaceElement

class HeadDrive(Pose):
    """
    A pose representing a driving action based on head movements.

    Args:
        method (str): The method used for driving, either "tilt" or "turn".
        show_face (bool): Whether to show the face element during the driving action.

    Attributes:
        _method (str): The method used for driving.
        view_element (FaceElement): The face element to be shown during the driving action.

    Methods:
        from_kwargs: Create a HeadDrive instance from keyword arguments.
        _get_triggers: Get the left and right triggers based on the driving method.
        action: Perform the driving action based on the person's head movements.
        check: Check if the driving action should continue based on the person's head movements.
    """
    def __init__(self, method: str, show_face: bool):
        self._method = method
        super().__init__()
        if show_face:
            self.view_element = FaceElement(face_colour=(0, 255, 0))

    @classmethod
    def from_kwargs(cls, **kwargs) -> 'Pose':
        """
        This pose is used to represent a driving action based on head movements.

        Args:
            method (str): The method used for driving, either "tilt" or "turn".
            show_face (bool): Whether to show the face element during the driving action.
        """
        method = kwargs.get('method')
        show_face = kwargs.get('show_face')

        if not isinstance(show_face, bool):
            raise ValueError("show_face must be a boolean value")

        return cls(method=method, show_face=show_face)
    
    def _get_triggers(self, person: Person) -> tuple:
        """
        Get the left and right triggers based on the driving method.

        Args:
            person (Person): The person object representing the user.

        Returns:
            tuple: A tuple containing the left and right triggers.
        """
        if self._method == "tilt":
            return (person.head.tilt_left, person.head.tilt_right)
        else:
            return (person.head.turn_left, person.head.turn_right)
    

    def action(self, person: Person, view: View) -> bool:
        """
        Perform the driving action based on the person's head movements.

        Args:
            person (Person): The person object representing the user.
            view (View): The view object representing the user's perspective.

        Returns:
            bool: True if the driving action was performed successfully, False otherwise.
        """
        left_trigger, right_trigger = self._get_triggers(person)

        if not person.head.fish_face:
            keyboard.hold("w")
        else:
            keyboard.release("w")

        if left_trigger:
            keyboard.hold("a")
        else:
            keyboard.release("a")
        
        if right_trigger:
            keyboard.hold("d")
        else:
            keyboard.release("d")

    def check(self, person: Person) -> bool:
        """
        Check if the driving action should continue based on the person's head movements.

        Args:
            person (Person): The person object representing the user.

        Returns:
            bool: True if the driving action should continue, False otherwise.
        """
        if not person.head:
            return False
        
        if self.view_element:
            self.view_element.update_face_elements(person.head)

        left_trigger, right_trigger = self._get_triggers(person)

        if person.head.fish_face and not left_trigger and not right_trigger:
            keyboard.release("w", "a", "d")
            return False

        return True