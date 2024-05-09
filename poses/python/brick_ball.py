from lib.drivers import mouse
from lib.gestures import Pose
from lib.modules import Side, Person
from lib.view import View

class BrickBall(Pose):

    def __init__(self, hand):
        """
        This method initialises the BrickBall class using the hand parameter.
        Attributes such as hand are also initialised.
        """
        super().__init__()
        self.hand = hand

    @classmethod
    def from_kwargs(cls, **kwargs) -> 'Pose':
        """
        This pose is used to represent the BrickBall pose, which is used to hold 
        left click action once index finger is pinched.

        Args:
            hand (Literal['left', 'right']): The side of the hand (LEFT or RIGHT).
        """
        hand = Side[kwargs.get('hand').upper()]

        return cls(hand=hand)
        
        
    def action(self, person: Person, view: View) -> None:
        """
        This method will perform the action of holding left click action once index finger is pinched.
        Once index finger is released, mouse left click will be released.

        Args:
        person (Person): The person to check.
        view (View): The view to draw on.
        """
        hand = person.hands[self.hand]

        middle_coords = hand['middle_tip']
        mouse.move_to(middle_coords[0]*1000, middle_coords[1]*1000)
        
        if hand.index_pinched:
            mouse.hold("left")
        if not hand.index_pinched:
            mouse.release("left")
    
    def check(self, person: Person) -> bool:
        """
        This method will return True if there are hands, and hand has middle. ring and pinky stretched.
        It will return False otherwise.
        
        Args:
        person (Person): The person to check.

        Returns:
        bool: whether the pose is valid.
        """
        hand = person.hands[self.hand]
        
        if not person.hands or not hand:
            return False
        
        if hand and hand.middle_stretched and hand.ring_stretched and hand.pinky_stretched:
            return True
        
        return False
