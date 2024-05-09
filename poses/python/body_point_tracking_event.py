"""
Author: Suhas Hariharan
"""
from lib.drivers import Mouse, Keyboard
from pynput.keyboard import Key
from lib.modules import Side, Person
from lib.config import config
from lib.view.elements.bp_box import BodyPointBoxElement
from lib.view.elements.arrow_overlay_element import ArrowOverlayElement
from lib.view.elements.composite_view_element import CompositeViewElement
from enum import Enum
from lib.gestures.base.head_pose import HeadPose
from lib.view import View
from lib.drivers import flags
from lib.gestures import Pose

# essentially the same as the bp tracking mode but this could diverge
class BPTrackingMode(Enum):
    ARROW_KEYS_HOLD = 1
    ARROW_KEYS_PRESS = 2
    MOUSE = 3

    @staticmethod
    def from_string(s: str) -> 'BPTrackingMode':
        return BPTrackingMode[s.upper()]
    
    

class BodyPointTrackingEvent(Pose):
    _gesture_types = {"bp_movement"}

    def __init__(self, bp_tracking_mode: BPTrackingMode = BPTrackingMode.ARROW_KEYS_HOLD, show_arrows: bool = True, reset_bp_box: bool = True, gaming_keys: dict = None, bp_landmark: str = "right_elbow"):
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
        self._found_bp = False
        self.mode = bp_tracking_mode
        self.bp_landmark = bp_landmark
        self.reset_bp_box = reset_bp_box
        
        self._show_arrows = show_arrows
        
        self.bp_view_element: BodyPointBoxElement = BodyPointBoxElement(box_colour=(0, 255, 0), bp_dot_colour=(255, 255, 255), bp_dot_triggered_colour=(0, 255, 255))
        self.bp_view_element.update_bp_box((self._bp_box_percentage_size_x,self._bp_box_percentage_size_y), (self.bp_box_centre_x_percentage, self.bp_box_centre_y_percentage))

        list_of_view_elements = [self.bp_view_element]
        
        if self._show_arrows:
            self.arrow_view_element: ArrowOverlayElement = ArrowOverlayElement(35, (255, 255, 255), (255, 255, 255), self.bp_view_element.true_bp_box_centre)
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
        bp_tracking_mode = kwargs.get('bp_tracking_mode')
        reset_bp_box = kwargs.get('reset_bp_box')
        show_arrows = kwargs.get('show_arrows')
        gaming_keys = kwargs.get('gaming_keys')
        bp_landmark = kwargs.get('landmark')
        if bp_tracking_mode:
            bp_tracking_mode = BPTrackingMode.from_string(bp_tracking_mode)
        return cls(bp_landmark=bp_landmark, bp_tracking_mode=bp_tracking_mode, show_arrows=show_arrows, reset_bp_box=reset_bp_box, gaming_keys=gaming_keys)
    
    def _load_config(self):
        self._scaling_factor_x = config.get("bp_tracking/scaling_factor_x")
        self._scaling_factor_y = config.get("bp_tracking/scaling_factor_y") 
        self._bp_box_percentage_size_x = config.get(
            "bp_tracking/bp_box_percentage_size_x")
        self._bp_box_percentage_size_y = config.get(
            "bp_tracking/bp_box_percentage_size_y")
        self.bp_box_centre_x_percentage = config.get(
            "bp_tracking/bp_box_centre_x_percentage")
        self.bp_box_centre_y_percentage = config.get(
            "bp_tracking/bp_box_centre_y_percentage")
        self.frame_width = config.get("camera/width")
        self.frame_height = config.get("camera/height")


    def _update_config(self):
        config.set("bp_tracking/bp_box_centre_x_percentage", self.bp_box_centre_x_percentage)
        config.set("bp_tracking/bp_box_centre_y_percentage", self.bp_box_centre_y_percentage)


    def action(self, person: Person, view: View) -> None:
        bp_position = self._get_bp_position(person)

        movement_vector = self._calculate_movement_vector(bp_position)

        if self.mode == BPTrackingMode.ARROW_KEYS_HOLD:
            self._handle_bp_direction(bp_position, hold=True)
        elif self.mode == BPTrackingMode.ARROW_KEYS_PRESS:
            self._handle_bp_direction(bp_position, hold=False)
        elif self.mode == BPTrackingMode.MOUSE:
            self.mouse.move(movement_vector[0], movement_vector[1])

    def _release_key(self, direction, key):
        self.keyboard.key_up(key)
        self._action_hold_state[direction] = False
        self._release_arrow_highlight(direction)

    def _calculate_movement_vector(self, bp_position):
        # Adjust the vector calculation based on bp_box_percentage_size 
        vector_x = (bp_position[0] - self.bp_box_centre_x_percentage) * self._scaling_factor_x
        vector_y = (bp_position[1] - self.bp_box_centre_y_percentage) * self._scaling_factor_y
        return (vector_x, vector_y)
    
    def _is_key(self, key):
        return not type(key) == dict and "click" not in key
    
    def _handle_bp_direction(self, bp_position, hold=False):
        # Calculate the thresholds based on the bp_box_percentage_size
        right_threshold = self.bp_box_centre_x_percentage + self._bp_box_percentage_size_x
        left_threshold = self.bp_box_centre_x_percentage - self._bp_box_percentage_size_x
        up_threshold = self.bp_box_centre_y_percentage - self._bp_box_percentage_size_y
        down_threshold = self.bp_box_centre_y_percentage + self._bp_box_percentage_size_y 

        bp_position_x, bp_position_y = bp_position[0], bp_position[1]
        # Right
        if bp_position_x > right_threshold and not self._action_hold_state["right"]:
            self._trigger_action("right", self.gaming_actions["right"], hold)
        elif bp_position_x <= right_threshold and self._action_hold_state["right"]:
            self._release_action("right", self.gaming_actions["right"])

        # Left
        if bp_position_x < left_threshold and not self._action_hold_state["left"]:
            self._trigger_action("left", self.gaming_actions["left"], hold)
        elif bp_position_x >= left_threshold and self._action_hold_state["left"]:
            self._release_action("left", self.gaming_actions["left"])

        # Up
        if bp_position_y < up_threshold and not self._action_hold_state["up"]:
            self._trigger_action("up", self.gaming_actions["up"], hold)
        elif bp_position_y >= up_threshold and self._action_hold_state["up"]:
            self._release_action("up", self.gaming_actions["up"])

        # Down
        if bp_position_y > down_threshold and not self._action_hold_state["down"]:
            self._trigger_action("down", self.gaming_actions["down"], hold)
        elif bp_position_y <= down_threshold and self._action_hold_state["down"]:
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

    def _get_bp_position(self, person: Person):
        bp_position = person.body.get(self.bp_landmark, None)
        if bp_position is None:
            return None
        # normalise the bp position to the frame size
        bp_position = (bp_position[0] / self.frame_width, bp_position[1] / self.frame_height)
        return bp_position
    
    def check(self, person: Person) -> bool:
        if person is None:
            return False
        bp_position = self._get_bp_position(person)
        if bp_position is None:
            return False
        self.reset_bp_box = flags.get('reset_bp_box')


        if self.reset_bp_box or not self._found_bp:
            flags.set('reset_bp_box', False)            
            self._butterfly(bp_position)
            self._found_bp = True
        
        self.bp_view_element.update_bp_point([float(bp_position[0]), float(bp_position[1])])

        is_within_bp_box = self._is_within_bp_box(bp_position)
        if is_within_bp_box:
            self._release_all_actions()
        return not is_within_bp_box

    def _is_within_bp_box(self, bp_position):
        return abs(bp_position[0] - self.bp_box_centre_x_percentage) <= self._bp_box_percentage_size_x and \
            abs(bp_position[1] - self.bp_box_centre_y_percentage) <= self._bp_box_percentage_size_y
    
    def _butterfly(self, bp_position):
        self.bp_box_centre_x_percentage, self.bp_box_centre_y_percentage = bp_position[0], bp_position[1]
        self.bp_view_element.update_bp_box((self._bp_box_percentage_size_x,self._bp_box_percentage_size_y), (float(bp_position[0]), float(bp_position[1])))
        if self._show_arrows:
            self.arrow_view_element.update_center_point(self.bp_view_element.bp_box_centre)
        self._update_config()