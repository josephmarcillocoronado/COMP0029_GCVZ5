"""
Ho Shu Han
"""

from lib.drivers import soundplayer
from lib.modules import Side, Person
from lib.view import View
from lib.gestures import Pose
import time
    
class SoundPose(Pose):
    def __init__(self, sound_name: str, hand, **kwargs):
        """
        Initialize a SoundPose object. This pose will play a sound once the user pinches his index finger and thumb.

        Args:
            sound_name (str): The name of the sound to be played.
            hand: The hand side (e.g., 'left' or 'right').
            **kwargs: Additional keyword arguments.

        """
        super().__init__(**kwargs)
        self.sound_name = sound_name
        self.hand = hand


    @classmethod
    def from_kwargs(cls, **kwargs) -> 'Pose':
        """
        This pose will play a sound once the user pinches his index finger and thumb.

        Args:
            hand (Literal['left', 'right']): The side of the hand (LEFT or RIGHT).
            file_name (str): relatative or absolute path to a file which should be played
        """
        sound_name = kwargs.get("sound_name")
        hand = Side[kwargs.get('hand').upper()]
        
        return cls(sound_name=sound_name, hand=hand)
    
    def check(self, person: Person) -> bool:
        """
        Check if the pose is valid for a given person.

        Args:
            person (Person): The person to check the pose against.

        Returns:
            bool: True if the pose is valid, False otherwise.

        """
        hand = person.hands[self.hand]
        
        if not person.hands or not hand:
            return False
        
        return hand.index_pinched

    def action(self, person: Person, view: View) -> None:
        """
        Perform the action associated with the pose.

        Args:
            person (Person): The person performing the pose.
            view (View): The view object.

        """

        soundplayer.play_sound(self.sound_name)
            