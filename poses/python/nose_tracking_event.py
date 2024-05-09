"""
Author: Andrzej Szablewski, Alexandros Theofanous, Suhas Hariharan
"""
from lib.drivers import Mouse, Keyboard
from pynput.keyboard import Key
from lib.modules import Side, Person
from collections import deque
from lib.config import config
from lib.view.elements.nose_box import NoseBoxElement
from lib.view.elements.face_element import FaceElement
from lib.view.elements.arrow_overlay_element import ArrowOverlayElement
from lib.view.elements.composite_view_element import CompositeViewElement
from enum import Enum
from lib.gestures.base.head_pose import HeadPose
from lib.view import View
from lib.drivers import flags
from lib.gestures import Pose


# create a nose tracking enum for the different modes and a mode mapping from string to enum
class NoseTrackingMode(Enum):
    ARROW_KEYS_HOLD = 1
    ARROW_KEYS_PRESS = 2
    MOUSE = 3

    @staticmethod
    def from_string(s: str) -> 'NoseTrackingMode':
        return NoseTrackingMode[s.upper()]
    
    

class NoseTrackingEvent(HeadPose):
    _gesture_types = {"nose_movement"}
    _bodypart_types = {"head"}

    def __init__(self, nose_tracking_mode: NoseTrackingMode = NoseTrackingMode.ARROW_KEYS_HOLD, show_face: bool = False, show_arrows: bool = True, reset_nose_box: bool = True, gaming_keys: dict = None):
        super().__init__()
        self.mouse = Mouse()
        self.keyboard = Keyboard()
        self._load_config()
        self._action_hold_state = {
            "up": False,
            "down": False,
            "left": False,
            "right": False
        }
        self._found_nose = False
        self.mode = nose_tracking_mode
        self.reset_nose_box = reset_nose_box

        self._show_face = show_face
        
        self._show_arrows = show_arrows
        
        self.nose_view_element: NoseBoxElement = NoseBoxElement(box_colour=(0, 255, 0), nose_dot_colour=(255, 255, 255), nose_dot_triggered_colour=(0, 255, 255))
        self.nose_view_element.update_nose_box((self._nose_box_percentage_size_x,self._nose_box_percentage_size_y), (self.nose_box_centre_x_percentage, self.nose_box_centre_y_percentage))

        list_of_view_elements = [self.nose_view_element]
        
        if self._show_face:
            self.face_view_element: FaceElement = FaceElement(face_colour=(255, 255, 0))
            list_of_view_elements.append(self.face_view_element)

        if self._show_arrows:
            self.arrow_view_element: ArrowOverlayElement = ArrowOverlayElement(35, (255, 255, 255), (255, 255, 255), self.nose_view_element.true_nose_box_centre)
            list_of_view_elements.append(self.arrow_view_element)

        self.view_element = CompositeViewElement(list_of_view_elements)

        self.gaming_actions = gaming_keys
        for direction in self.gaming_actions:
            gaming_action = self.gaming_actions[direction]
            if type(gaming_action) == dict and "args" in gaming_action["action"]:
                method, args = Pose._get_method_and_args(**gaming_action)
                if gaming_action["action"]["class"] == "keyboard":
                    gaming_action = gaming_action["action"]["args"][0]
                elif gaming_action["action"]["class"] == "mouse" and gaming_action["action"]["method"] == "click":
                    gaming_action = gaming_action["action"]["args"][0] + " click"
                else:
                    gaming_action["action"]["method"] = method
                    gaming_action["action"]["args"] = args
                self.gaming_actions[direction] = gaming_action

    @classmethod
    def from_kwargs(cls, **kwargs) -> 'HeadPose':
        nose_tracking_mode = kwargs.get('nose_tracking_mode')
        reset_nose_box = kwargs.get('reset_nose_box')
        show_face = kwargs.get('show_face')
        show_arrows = kwargs.get('show_arrows')
        gaming_keys = kwargs.get('gaming_keys')
        if nose_tracking_mode:
            nose_tracking_mode = NoseTrackingMode.from_string(nose_tracking_mode)
        return cls(nose_tracking_mode=nose_tracking_mode, show_face=show_face, show_arrows=show_arrows, reset_nose_box=reset_nose_box, gaming_keys=gaming_keys)
    
    def _load_config(self):
        self._scaling_factor_x = config.get("nose_tracking/scaling_factor_x") # used to scale the nose movement vector. higher number = faster movement
        self._scaling_factor_y = config.get("nose_tracking/scaling_factor_y") # used to scale the nose movement vector. higher number = faster movement
        self._nose_box_percentage_size_x = config.get(
            "nose_tracking/nose_box_percentage_size_x")
        self._nose_box_percentage_size_y = config.get(
            "nose_tracking/nose_box_percentage_size_y")
        self.nose_box_centre_x_percentage = config.get(
            "nose_tracking/nose_box_centre_x_percentage")
        self.nose_box_centre_y_percentage = config.get(
            "nose_tracking/nose_box_centre_y_percentage")

    def _update_config(self):
        config.set("nose_tracking/nose_box_centre_x_percentage", self.nose_box_centre_x_percentage)
        config.set("nose_tracking/nose_box_centre_y_percentage", self.nose_box_centre_y_percentage)


    def action(self, person: Person, view: View) -> None:
        head = person.head
        nose_position = head.nose_tip_position

        movement_vector = self._calculate_movement_vector(nose_position)

        if self.mode == NoseTrackingMode.ARROW_KEYS_HOLD:
            self._handle_nose_direction(nose_position, hold=True)
        elif self.mode == NoseTrackingMode.ARROW_KEYS_PRESS:
            self._handle_nose_direction(nose_position, hold=False)
        elif self.mode == NoseTrackingMode.MOUSE:
            self.mouse.move(movement_vector[0], movement_vector[1])

    def _release_key(self, direction, key):
        self.keyboard.key_up(key)
        self._action_hold_state[direction] = False
        self._release_arrow_highlight(direction)

    def _calculate_movement_vector(self, nose_position):
        # Adjust the vector calculation based on nose_box_percentage_size
        vector_x = (nose_position[0] - self.nose_box_centre_x_percentage) * self._scaling_factor_x
        vector_y = (nose_position[1] - self.nose_box_centre_y_percentage) * self._scaling_factor_y
        return (vector_x, vector_y)
    
    def _is_key(self, key):
        return not type(key) == dict and "click" not in key
    
    def _handle_nose_direction(self, nose_position, hold=False):
        # Calculate the thresholds based on the nose_box_percentage_size
        right_threshold = self.nose_box_centre_x_percentage + self._nose_box_percentage_size_x
        left_threshold = self.nose_box_centre_x_percentage - self._nose_box_percentage_size_x
        up_threshold = self.nose_box_centre_y_percentage - self._nose_box_percentage_size_y
        down_threshold = self.nose_box_centre_y_percentage + self._nose_box_percentage_size_y 

        nose_position_x, nose_position_y = nose_position[0], nose_position[1]

        # Right
        if nose_position_x > right_threshold and not self._action_hold_state["right"]:
            self._trigger_action("right", self.gaming_actions["right"], hold)
        elif nose_position_x <= right_threshold and self._action_hold_state["right"]:
            self._release_action("right", self.gaming_actions["right"])

        # Left
        if nose_position_x < left_threshold and not self._action_hold_state["left"]:
            self._trigger_action("left", self.gaming_actions["left"], hold)
        elif nose_position_x >= left_threshold and self._action_hold_state["left"]:
            self._release_action("left", self.gaming_actions["left"])

        # Up
        if nose_position_y < up_threshold and not self._action_hold_state["up"]:
            self._trigger_action("up", self.gaming_actions["up"], hold)
        elif nose_position_y >= up_threshold and self._action_hold_state["up"]:
            self._release_action("up", self.gaming_actions["up"])

        # Down
        if nose_position_y > down_threshold and not self._action_hold_state["down"]:
            self._trigger_action("down", self.gaming_actions["down"], hold)
        elif nose_position_y <= down_threshold and self._action_hold_state["down"]:
            self._release_action("down", self.gaming_actions["down"])
        

    def _trigger_arrow_highlight(self, direction, hold):
        if self._show_arrows:
            self.arrow_view_element.trigger_arrow(direction, hold=hold)

    def _release_arrow_highlight(self, direction):
        if self._show_arrows:
            self.arrow_view_element.untrigger_arrow(direction)

    def _trigger_action(self, direction, action, hold):
        if self._is_key(action):
            self._trigger_key(action, hold)
        elif action == "left click":
            if hold:
                self.mouse.mouse_down("left")
            else:
                self.mouse.click("left")
        elif action == "right click":
            if hold:
                self.mouse.mouse_down("right")
            else:
                self.mouse.click("right")
        elif "method" in action:
            action["method"](*action["args"])
        self._action_hold_state[direction] = True
        self._trigger_arrow_highlight(direction, hold=hold)

    def _release_action(self, direction, action):
        if self._is_key(action):
            self._release_key(direction, action)
        elif action == "left click":
            self.mouse.mouse_up("left")
        elif action == "right click":
            self.mouse.mouse_up("right")
        self._action_hold_state[direction] = False
        self._release_arrow_highlight(direction)
        
    def _trigger_key(self, key, hold):
        if hold:
            self.keyboard.key_down(key)
        else:
            self.keyboard.press(key)

    def _release_all_actions(self):
        for key, action in zip(self._action_hold_state, self.gaming_actions):
            self._release_action(key, action)

    def check(self, person: Person) -> bool:
        if person is None or not person.head:
            return False
        head = person.head
        nose_position = head.nose_tip_position
        self.reset_nose_box = flags.get('reset_nose_box')

        if self.reset_nose_box or not self._found_nose:
            flags.set('reset_nose_box', False)            
            self._butterfly(nose_position)
            self._found_nose = True

        self.nose_view_element.update_nose_point([float(nose_position[0]), float(nose_position[1])])

        if self._show_face:
            self.face_view_element.update_face_elements(head)

        is_within_nose_box = self._is_within_nose_box(nose_position)
        if is_within_nose_box:
            self._release_all_actions()
        return not is_within_nose_box

    def _is_within_nose_box(self, nose_position):
        return abs(nose_position[0] - self.nose_box_centre_x_percentage) <= self._nose_box_percentage_size_x and \
            abs(nose_position[1] - self.nose_box_centre_y_percentage) <= self._nose_box_percentage_size_y
    
    def _butterfly(self, nose_position):
        self.nose_box_centre_x_percentage, self.nose_box_centre_y_percentage = nose_position[0], nose_position[1]
        self.nose_view_element.update_nose_box((self._nose_box_percentage_size_x,self._nose_box_percentage_size_y), (float(nose_position[0]), float(nose_position[1])))
        if self._show_arrows:
            self.arrow_view_element.update_center_point(self.nose_view_element.nose_box_centre)
        self._update_config()