'''
Author: Vayk Mathrani
'''
import numpy as np

from lib.gestures import Pose
from lib.modules import Person, Head
from lib.drivers import mouse, Keyboard
from lib.view import View

class NoseScroll(Pose):
    def __init__(self, sensitivity=1.2, scale_factor=1.0):
        """
        A class to implement nose-based scrolling functionality in a gesture control interface.

        This class inherits from Pose and is designed to use the position of the user's nose
        to control scrolling actions on a computer interface. It tracks the movement of the nose
        and translates this movement into scroll commands, enabling a hands-free interaction method.

        Attributes:
            sensitivity (float): Sensitivity of the nose movement detection. A higher value
            indicates more sensitivity to smaller movements.
            scale_factor (float): Scale factor for determining the scroll amount based on
            nose movement. Adjusts the rate of scrolling.
            previous_nose_position (numpy.ndarray or None): Stores the last recorded position
            of the nose. Used to calculate the movement delta for scrolling.
        Methods:
            __init__: Initializes the NoseScroll object with sensitivity and scale factor.
            from_kwargs: Class method to construct an instance from keyword arguments.
            check: Checks if there has been significant nose movement to trigger a scroll.
            action: Executes the scroll action based on the current nose position.
            calculate_scroll_amount: Calculates the scroll amount based on nose movement.
        """

        super().__init__()
        self.sensitivity = sensitivity
        self.scale_factor = scale_factor
        self.previous_nose_position = None
        self.direction = None
        self.activation = False
    @classmethod
    def from_kwargs(cls, **kwargs) -> 'Pose':
        """
        This pose is used to represents a pose for scrolling based on the movement of the nose.

        Args:
            sensitivity (float): The sensitivity of the gesture, need to be bigger than 0.
            scale_factor (float): Scale factor for determining the scroll amount based on
        """
        sensitivity = kwargs.get('sensitivity', 1.0)
        scale_factor = kwargs.get('scale_factor', 1.0)
        return cls(sensitivity=sensitivity, scale_factor=scale_factor)

    def check(self, person: Person) -> bool:
        """
        Checks if there has been significant nose movement to trigger a scroll.

        Args:
            person (Person): The person object to check nose movement for.
        """

        if not person.head:
            return False

        nose_tip = np.array(person.head['nose-tip'])
        if nose_tip is None or self.previous_nose_position is None:
            self.previous_nose_position = nose_tip
            return False

        movement = nose_tip - self.previous_nose_position
        if np.linalg.norm(movement) > 0:
            self.directionUp = True

        if np.linalg.norm(movement) > (0.05 * self.sensitivity):
            self.previous_nose_position = nose_tip
            return True

        return False

    def action(self, person: Person, view: View) -> None:
        """
        Executes the scroll action based on the nose's position.

        Args:
            person (Person): The person object with the current nose position.
            view (View): The view object used for rendering or feedback.
        """
        nose_tip = person.head['nose-tip']
        scroll_amount = self.calculate_scroll_amount(nose_tip)
        mouse.scroll(0, scroll_amount)

    def calculate_scroll_amount(self, nose_tip):
        """
        Calculates the scroll amount based on the movement of the nose.

        Args:
            nose_tip: The current position of the nose.

        Returns:
            float: The amount to scroll.
        """
        if self.previous_nose_position is None:
            return self.previous_nose_position
        movement_y = nose_tip[1] * self.sensitivity

        if not self.activation and (movement_y) < 0.45 * self.sensitivity:
            self.activation = True
            return movement_y * self.scale_factor 
        if not self.activation and (movement_y) > 0.45 * self.sensitivity:
            self.activation = True
            return -movement_y * self.scale_factor
        self.activation = False
