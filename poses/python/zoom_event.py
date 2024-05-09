import numpy as np
from lib.gestures import Pose
from lib.modules import Side, Person
from lib.view import View
from lib.drivers import mouse
from lib.config import config

class ZoomEvent(Pose):
    """Zooming by holding the index pinch gesture on both hands. Zooming direction and speed according tho the change in the index finger tips distance.

    [trigger types]:
        "zoom": called every frame after frames_for_switch as long as the change in distance since the last frame is above threshold. With arguments (speed) reflecting the change in distance since last frame.
    [bodypart types]:
        "dom_hand" & "off_hand": the  distance (aka speed) is calculated from the distance between the "index_tip"s of these hands
    [gestures types]:
        "index_pinch": the current gesture used
    """
    _event_trigger_types = {"zoom"}
    _gesture_types = {"index_pinch"}
    _bodypart_types = {"dom_hand", "off_hand"}


    def __init__(self, hand: Side):
        super().__init__()

        self.hand = hand
        if hand == Side.LEFT:
            self.dom_hand = Side.LEFT
            self.off_hand = Side.RIGHT
        else:
            self.dom_hand = Side.RIGHT
            self.off_hand = Side.LEFT

        self._n_frames_for_switch = max(2, config.get("hands/zoom/frames_for_switch"))
        self._movement_threshold = config.get("hands/zoom/movement_threshold")
        self._last_hands_dist = config.get("hands/zoom/starting_distance")
        self.frames_held = config.get("hands/zoom/frames_held")

    def action(self, person: Person, view: View) -> None:
        hands_dist = self._get_hands_dist(person.hands[self.dom_hand], person.hands[self.off_hand])
        if self.frames_held >= self._n_frames_for_switch:
            speed = hands_dist - self._last_hands_dist

            if abs(speed) > self._movement_threshold:
                mouse.scroll(speed, speed) # can find a optimum value

        self._last_hands_dist = hands_dist

    @classmethod
    def from_kwargs(cls, **kwargs) -> 'Pose':
        """
        This pose is used to represent zooming by holding the index pinch gesture on both hands.
        Zooming direction and speed according tho the change in the index finger tips distance.

        Args:
            dom_hand (Literal['left' or 'right']): dominant hand side
            off_hand (Literal['left' or 'right']): off hand side
        """

        hand = kwargs.get('hand')
        if hand is None:
            raise ValueError("hand must not be None")
        
        return cls(hand=Side[hand.upper()])
        
    def check(self, person: Person) -> bool:
        if not person.hands or not person.hands[self.dom_hand] or not person.hands[self.off_hand]:
            self.frames_held = 0
            return False

        dom_hand = person.hands[self.dom_hand]
        off_hand = person.hands[self.off_hand]

        if dom_hand.index_pinched and not dom_hand.middle_pinched and not dom_hand.ring_pinched and not dom_hand.pinky_pinched and dom_hand.palm_facing_camera:
            if off_hand.index_pinched and not off_hand.middle_pinched and not off_hand.ring_pinched and not off_hand.pinky_pinched and off_hand.palm_facing_camera:
                self.frames_held += 1
                return True
            
        self.frames_held = 0
        return False 

    def _get_hands_dist(self, dom_hand, off_hand) -> float:

        index_tip1 = dom_hand["index_tip"]
        index_tip2 = off_hand["index_tip"]
        
        fingers_dist = np.sqrt(np.sum((index_tip1 - index_tip2) ** 2))
        tot_palm_height = (dom_hand.distance("middle_base", "wrist") + off_hand.distance("middle_base", "wrist"))
        return fingers_dist * 2 / tot_palm_height