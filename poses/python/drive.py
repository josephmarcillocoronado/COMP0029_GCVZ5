from abc import ABC, abstractmethod
from time import monotonic
from typing import Callable

import numpy as np

from lib.drivers import keyboard, gamepad
from lib.gestures import Pose
from lib.modules import Person
from lib.view import View
from lib.view.elements.steering_wheel import SteeringWheelElement


landmark_func = Callable[[Person], np.ndarray]


class HandDrive(Pose):
    def __init__(self, get_left: landmark_func, get_right: landmark_func, controller: 'Controller'):
        super().__init__()
        self.get_left = get_left
        self.get_right = get_right
        self.controller = controller
        self.view_element: SteeringWheelElement = SteeringWheelElement()

    @staticmethod
    def get_landmark_func(data: dict, side: str) -> landmark_func:
        if data is None:
            return lambda person: getattr(person.hands, side)['middle_base']  # Default is middle base of hands
        elif data['module'] == 'hands':
            landmark = data['landmark'].split('_', 1)[1]
            return lambda person: getattr(person.hands, side)[landmark]
        else:
            return lambda person: getattr(person, data['module'])[data['landmark']]

    @classmethod
    def from_kwargs(cls, **kwargs) -> 'Pose':
        """
        This pose is used to represents a hand-driven steering wheel in a gesture-based control system.
        It has two modes: gamepad and keyboard.

        Args:
            left (dict[str, str]): The left action, will have two elements in it: module, landmark.
                                    For module, it can be 'hands', 'body', 'face'.
                                    For landmark, it can be 'middle_base', 'wrist', 'elbow', 'nose', etc.
            right (dict[str, str]): The right action, will have two elements in it: module, landmark.
                                    For module, it can be 'hands', 'body', 'face'.
                                    For landmark, it can be 'middle_base', 'wrist', 'elbow', 'nose', etc.
            controller (object): The mode of the action, either in GamepadController mode or KeyboardController mode.
        """
        get_left = cls.get_landmark_func(kwargs.get('left'), 'left')
        get_right = cls.get_landmark_func(kwargs.get('right'), 'right')

        if kwargs.get('mode') in ('gamepad', 'controller', 'joystick'):
            controller = GamepadController()
        else:
            controller = KeyboardController()

        return cls(get_left=get_left, get_right=get_right, controller=controller)

    def check(self, person: Person) -> bool:
        try:
            self.get_left(person)
            self.get_right(person)
        except (KeyError, AttributeError):
            self.controller.release()
            return False

        return True

    @staticmethod
    def calculate_angle(left: np.ndarray, right: np.ndarray) -> float:
        # hand1_pixel = np.array([hand1[0] * width, hand1[1] * height])
        # hand2_pixel = np.array([hand2[0] * width, hand2[1] * height])

        # centre_x = int((hand1_pixel[0] + hand2_pixel[0]) / 2)
        # centre_y = int((hand1_pixel[1] + hand2_pixel[1]) / 2)
        # self.center = (centre_x, centre_y)
        #
        # self.radius = int(np.linalg.norm(hand1_pixel - hand2_pixel) / 2)

        vector = left - right

        angle_radians = np.arctan2(vector[1], vector[0])
        angle_degrees = np.degrees(angle_radians)

        return (angle_degrees + 90) % 360

    def action(self, person: Person, view: View) -> None:
        left = self.get_left(person)
        right = self.get_right(person)

        angle = self.calculate_angle(left=left, right=right)
        self.view_element.angle = angle

        slope = max(min((angle - 270) / 60, 1), -1)  # -1 to 1
        self.controller.action(slope=slope)


class Controller(ABC):
    @abstractmethod
    def action(self, slope: float) -> None:
        pass

    @abstractmethod
    def release(self) -> None:
        pass


class KeyboardController(Controller):
    def __init__(self, sensitivity: float = 0.2):
        self.keys = ("w", "a", "s", "d")
        self.last_held = {key: monotonic() for key in self.keys}
        self.sensitivity = sensitivity

    def hold_key(self, key: str, duration: float) -> None:
        if monotonic() - self.last_held[key] > duration:
            keyboard.hold(key, duration=duration)
            self.last_held[key] = monotonic()

    def action(self, slope: float) -> None:
        keyboard.release("a", "d")
        abs_slope = abs(slope)
        if abs_slope <= self.sensitivity:
            # Drive straight
            keyboard.hold("w")
            return

        keyboard.release("w")

        if slope < 0:
            # Left turn
            keyboard.release("d")
            self.hold_key("a", abs_slope)
        else:
            # Right turn
            keyboard.release("a")
            self.hold_key("d", abs_slope)

    def release(self) -> None:
        keyboard.release(*self.keys)


class GamepadController(Controller):
    def __init__(self, sensitivity: float = 0.5):
        self.sensitivity = sensitivity

    def action(self, slope: float) -> None:
        accel = 0.2
        if abs(slope) <= self.sensitivity:
            accel = 0.45

        gamepad.gamepad.left_joystick_float(x_value_float=slope, y_value_float=0)
        gamepad.gamepad.right_trigger_float(value_float=accel)
        gamepad.gamepad.update()

    def release(self) -> None:
        gamepad.gamepad.reset()
        gamepad.gamepad.update()
