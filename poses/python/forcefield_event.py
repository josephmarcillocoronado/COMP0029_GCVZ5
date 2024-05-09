'''
Author: Suhas Hariharan
'''
from lib.gestures import HandPose
from lib.drivers import keyboard, mouse
from lib.modules import Side, Person
from collections import deque
from lib.config import config
from lib.view import View


class ForcefieldEvent(HandPose):
    """
    The ForcefieldEvent class inherits from HandPose. It represents a forcefield gesture based on hand depth with level boundaries, triggering different keypresses.

    Attributes:
        _gesture_types (set): A set of gesture types that this class can handle.
        _event_trigger_types (set): A set of event trigger types that this class can handle.
        _bodypart_types (set): A set of body part types that this class can handle.
        _buttons (list): A list of buttons that this class can trigger.
        _num_buttons (int): The number of buttons that this class can trigger.
    Args:
        hand (Side): The hand side (left or right).
        buttons (list[str]): A list of buttons to be triggered.
        depth_buffer_size (int): The size of the depth buffer.
    Methods:
        __init__(self, hand: Side, buttons: list[str], depth_buffer_size: int): Initializes the ForcefieldEvent object.
        from_kwargs(cls, **kwargs) -> 'HandPose': Creates an instance of ForcefieldEvent using keyword arguments.
        _calculate_depth_boundaries(self, depth_start, depth_end, num_buttons): Calculates depth boundaries for the forcefield.
        action(self, person: Person, view: View) -> None: Determines and executes actions based on the current hand depth level.
        check(self, person: Person) -> bool: Checks if the current hand position matches a gesture.
        _get_hand_depth_level(self, hand): Determines the depth level of the hand.
        _normalise_depth(self, hand_depth): Normalizes the depth value of the hand gesture.
        _trigger_button(self, button): Triggers a button action based on the hand gesture.
        _release_button(self, button): Releases a button action based on the hand gesture.
        
    """

    _gesture_types = {"wrist_visible"}
    _event_trigger_types = {
        "key_press",
        "key_release",
        "mouse_left_click",
        "mouse_left_hold",
        "mouse_left_release",
        "mouse_right_click",
        "mouse_right_hold",
        "mouse_right_release",
        "mouse_double_click",
        "key_hold"
    }
    _bodypart_types = {"hand"}


    def __init__(self, hand: Side, buttons: list[str], depth_buffer_size: int):
        """
        Initializes the ForcefieldEvent object.

        Args:
            hand (Side): The hand side (left or right).
            buttons (list[str]): A list of buttons to be triggered.
            depth_buffer_size (int): The size of the depth buffer.
        """
        super().__init__(hand=hand)
        self._buttons = [[value, False] for value in buttons]
        self._num_buttons = len(buttons)

        forcefield_start_depth = config.get("hands/forcefield/forcefields_start")
        forcefield_end_depth = config.get("hands/forcefield/forcefields_end")
        
        self._depth_boundaries = self._calculate_depth_boundaries(forcefield_start_depth, forcefield_end_depth, self._num_buttons)

        self._current_level = 0
        self._triggered_level = 0

        self._depth_buffer = deque(maxlen=depth_buffer_size)

    @classmethod
    def from_kwargs(cls, **kwargs) -> 'HandPose':
        """
        This pose is used to represents a forcefield gesture based on hand depth 
        with level boundaries, triggering different keypresses.


        Args:
            hand (Literal['left', 'right']): The side of the hand (LEFT or RIGHT).
            buttons (list[str]): A list of buttons to be triggered.
            depth_buffer_size (int): The size of the depth buffer, need to be bigger than 0. The default value is 10.
        """
        hand = kwargs.get('hand')
        if hand:
            hand = Side[hand.upper()]
        buttons = kwargs.get('buttons', [])
        depth_buffer_size = kwargs.get('depth_buffer_size', 10)
        return cls(hand=hand, buttons=buttons, depth_buffer_size=depth_buffer_size)

    def _calculate_depth_boundaries(self, depth_start, depth_end, num_buttons):
        """
        Calculates depth boundaries for the forcefield.

        Args:
            depth_start (float): The starting depth value.
            depth_end (float): The ending depth value.
            num_buttons (int): The number of buttons.

        Returns:
            list[float]: A list of depth boundary values.
        """
        boundaries = []
        depth_range = depth_end - depth_start
        depth_level_interval = depth_range / (num_buttons + 1)
        for i in range(1, num_buttons + 1):
            level_boundary = depth_start + i * depth_level_interval
            boundaries.append(level_boundary)
        return boundaries
    
    def action(self, person: Person, view: View) -> None:
        """
        Determines and executes actions based on the current hand depth level.

        Args:
            person (Person): The person object to check the gesture against.
            view (View): The view object used for rendering or feedback.
        """

        hand = person.hands[self.hand]
        self._current_level  = self._get_hand_depth_level(hand)

        if self._current_level > 0:
            for index, button in enumerate(self._buttons):
                level = index + 1
                if level == self._current_level and self._current_level != self._triggered_level:
                    if button[1] is True:
                        self._release_button(button)
                    else:
                        self._trigger_button(button)
                        self._triggered_level = level    
        elif self._current_level == 0:
            for button in self._buttons:
                if button[1] is True:
                    self._release_button(button)
            self._triggered_level = 0


    def check(self, person: Person) -> bool:
        """
        Checks if the current hand position matches a gesture.

        Args:
            person (Person): The person object to check the gesture against.

        Returns:
            bool: True if the gesture is matched, False otherwise.
        """

        hand = person.hands[self.hand]
        if not hand:
            return False
        self._current_level = self._get_hand_depth_level(hand)
        self._depth_buffer.append(self._current_level)
        return self._depth_buffer.count(self._current_level) >= self._depth_buffer.maxlen

    def _get_hand_depth_level(self, hand):
        
        """
        Determines the depth level of the hand.

        Args:
            hand (Hand): The hand object to measure the depth of.

        Returns:
            int: The depth level of the hand.
        """

        depth = hand.pinky_wrist_distance
        depth = self._normalise_depth(depth)
        if depth > self._depth_boundaries[-1]:
            return self._num_buttons
        else:
            for index, boundary in enumerate(self._depth_boundaries):
                if depth < boundary:
                    return index
        return 0

    def _normalise_depth(self, hand_depth):
        """
        Normalizes the depth value of the hand gesture.

        Args:
            hand_depth (float): The depth of the hand.

        Returns:
            float: The normalized depth.
        """
        return hand_depth

    def _trigger_button(self, button):
        """
        Triggers a button action based on the hand gesture.

        Args:
            button (list): The button to be triggered.
        """

        if button[0] == "":
            return
        if button[0].startswith("mouse"):
            _, side, mouse_action = button[0].split("_")
            getattr(mouse, mouse_action)(side)
        else:
            key, key_action = button[0].split("_")
            if key_action == "hold":
                keyboard.hold(key)
            elif key_action == "press":
                keyboard.press(key)
        button[1] = True

    def _release_button(self, button):
        if not button[0]:
            return

        if button[0].startswith("mouse_"):
            _, side, action = button[0].split("_")
            if action == "press":
                getattr(mouse, f"{side}_release")()
        else:
            key, key_action = button[0].split("_")
            keyboard.release(key)
        button[1] = False