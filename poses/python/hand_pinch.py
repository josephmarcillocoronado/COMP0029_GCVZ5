'''
Author: Michal Bravansky
'''
from lib.gestures import HandPose
from lib.drivers import keyboard, mouse
from lib.modules import Side, Person
from collections import deque
from lib.config import config
from lib.view import View


class HandPinchEvent(HandPose):

    def __init__(self, hand: Side,key_hold: bool, **kwargs):
        """
        This method initialises the HandPinchEvent class using the hand and key_hold parameter.
        Attributes such as _already_pinched and _key_hold are also initialised.
        """
        super().__init__(hand=hand, **kwargs)
        self._already_pinched = False
        self._key_hold = key_hold

    @classmethod
    def from_kwargs(cls, **kwargs) -> 'HandPose':
        """
        This pose is used to represents a pose for pinching with the left and right hands.

        Args:
            hand (Literal['left', 'right']): The side of the hand (LEFT or RIGHT).
            key_hold (bool): Whether the key is held down.
            args (list[str]): The arguments of the action.
        """
        method, args = cls._get_method_and_args(**kwargs)

        hand = kwargs.get('hand')
        if hand:
            hand = Side[hand.upper()]

        key_hold = kwargs.get('key_hold')

        return cls(hand=hand,key_hold =key_hold, method=method, args = args)


    def check(self, person: Person) -> bool:
        """
        This method will return True if the index finger is pinched and if the key is held down.
        It will return False otherwise.
        
        Args:
        person (Person): The person to check.

        """
        hand = person.hands[self.hand]
        if not hand:
            return False
        
        index_pinched = hand.index_pinched
        
        if index_pinched and self._key_hold:
            return True
        
        if not self._key_hold and index_pinched and not self._already_pinched:
            self._already_pinched = True
            return True
        elif not index_pinched: 
            self._already_pinched = False
        return False
