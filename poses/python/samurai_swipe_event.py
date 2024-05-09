from lib.drivers import mouse
from lib.gestures import Pose
from lib.modules import Side, Person
from lib.view import View


class SamuraiSwipeEvent(Pose):
    """
    This class represents a SamuraiSwipeEvent, which is a specific pose gesture.

    Attributes:
        dom_hand (str): The dominant hand for the gesture.
        off_hand (str): The off hand for the gesture.
        _sensitivity (int): The sensitivity of the gesture.
        _current_hand (str): The current hand performing the gesture.

    Args:
        dom_hand (str): The dominant hand for the gesture.
        off_hand (str): The off hand for the gesture.
        sensitivity (int): The sensitivity of the gesture.
        **kwargs: Arbitrary keyword arguments.
    
    Methods:
        __init__(self, dom_hand: str, off_hand: str, sensitivity: int, **kwargs): Initializes the SamuraiSwipeEvent instance.
        from_kwargs(cls, **kwargs) -> 'Pose': Class method to create a SamuraiSwipeEvent instance from keyword arguments.
        action(self, person: Person, view: View) -> bool: Performs an action based on the pose.
        check(self, person: Person) -> bool: Checks if the current hand position matches a gesture.
    """
    def __init__(self, dom_hand, off_hand, sensitivity):
        """
        Initializes the SamuraiSwipeEvent.

        Args:
            dom_hand (str): The dominant hand for the gesture.
            off_hand (str): The off hand for the gesture.
            sensitivity (int): The sensitivity of the gesture.
        """
        super().__init__()
        self.dom_hand = dom_hand
        self.off_hand = off_hand
        self._sensitivity = sensitivity
        
        
    def action(self, person: Person, view: View) -> None:
        """
        Performs the action associated with the SamuraiSwipeEvent.

        Args:
            person (Person): The person performing the gesture.
            view (View): The view in which the gesture is being performed.
        """
        hand = person.hands[self._current_hand]

        middle_coords = hand['middle_tip']
        mouse.move_to(middle_coords[0]*1000, middle_coords[1]*1000)
        
        if hand.index_pinched:
            mouse.hold("left", 1)
        else:
            mouse.release("left")
    
    def check(self, person: Person) -> bool:
        """
        Checks if the SamuraiSwipeEvent is being performed.

        Args:
            person (Person): The person to check for the gesture.

        Returns:
            bool: True if the gesture is being performed, False otherwise.
        """
        dom_hand = person.hands[self.dom_hand]
        off_hand = person.hands[self.off_hand]
        
        if not person.hands or (not dom_hand and not off_hand):
            return False
        
        if dom_hand and dom_hand.middle_stretched and dom_hand.ring_stretched and dom_hand.pinky_stretched:
            self._current_hand = self.dom_hand
            return True
        
        if off_hand and off_hand.middle_stretched and off_hand.ring_stretched and off_hand.pinky_stretched:
            self._current_hand = self.off_hand 
            return True
            
        return False

    @classmethod
    def from_kwargs(cls, **kwargs) -> 'Pose':
        """
        This pose is used to represent user's hand is in a position similar to a 
        samurai sword swipe.Class method to create a SamuraiSwipeEvent instance from keyword arguments.

        Args:
            dom_hand (Literal['left' or 'right']): dominant hand side.
            off_hand (Literal['left' or 'right']): off hand side.
            sensitivity (float): The sensitivity of the gesture, need to be bigger than 0.
        """
        
        dom_hand = Side[kwargs.get('dom_hand').upper()]
        off_hand = Side[kwargs.get('off_hand').upper()]
        sensitivity = kwargs.get('sensitivity')

        return cls(dom_hand=dom_hand, off_hand=off_hand, sensitivity=sensitivity)