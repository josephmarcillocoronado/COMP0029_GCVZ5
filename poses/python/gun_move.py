"""
Author: Dexin Fu
"""
from lib.drivers import mouse
from lib.gestures import HandPose
from lib.modules import Side, Person
from lib.view import View


class GunMoveEvent(HandPose):
    # While the hand is active we update the location of the cursor
    # Each frame the facing_camera gesture is active,
    # the 'move' trigger is called with the coordinates of the palm center
    def __init__(self, hand: Side, multiplier: float):
        super().__init__()
        self.hand = hand
        self.multiplier = multiplier

    def action(self, person: Person, view: View) -> None:
        hand = person.hands[self.hand]
        palm_center_coord = hand.palm_center
        mouse.move_to(palm_center_coord[0] * self.multiplier, palm_center_coord[1] * self.multiplier)

    def check(self, person: Person) -> bool:
        if not person.hands:
            return False

        hand = person.hands[self.hand]
        return (
                hand and hand.thumb_stretched and hand.index_stretched and
                hand.middle_stretched and hand.ring_folded and hand.pinky_folded
        )

    @classmethod
    def from_kwargs(cls, **kwargs) -> 'HandPose':
        """
        This pose is used to moves the cursor based on the palm center of the hand.
        Hand in gun shape is required to activate the gesture.
        The cursor movement is scaled by a multiplier.


        Args:
            hand (Literal['left', 'right']): The side of the hand (LEFT or RIGHT).
            multiplier (float): The multiplier to scale the cursor movement, need to be bigger than 0.
        """
        
        hand = Side[kwargs.get('hand').upper()]
        multiplier = kwargs.get('multiplier')

        return cls(hand=hand, multiplier=multiplier)
