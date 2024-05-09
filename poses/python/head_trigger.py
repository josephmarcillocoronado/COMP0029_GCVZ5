from lib.gestures import Pose
import inspect
from lib.modules import Head, Person

class HeadTrigger(Pose):

    def __init__(self, gesture: str, **kwargs):
        """
        This method initialises the HeadTrigger class using the gesture parameter.
        Attributes such as _gesture are also initialised. 
        An error is raised if the gesture is not valid.
        """
        super().__init__(**kwargs)

        if gesture not in self._get_head_properties():
            raise ValueError(f"Gesture type {gesture} is not valid.")
        
        self._gesture = gesture

    @classmethod
    def from_kwargs(cls, **kwargs) -> 'Pose':
        """
        This pose is used to check if a person is performing a specific gesture with their head.

        Args:
            method (str): The method used for driving, either "tilt" or "turn".
            args (list[str]): The arguments of the action, such as "left" or "right".
            gesture (str): The gesture to be checked, such as "tilted_left" or "tilted_right".
        """
        method, args = cls._get_method_and_args(**kwargs)
        
        gesture = kwargs.get("gesture")

        return cls(method=method, args=args, gesture = gesture)

    def _get_head_properties(self) -> list[str]:
        """
        This method will return a list of all the properties of the Head class.

        """
        return [name for name, value in inspect.getmembers(Head)]
    
    
    def check(self, person: Person) -> bool:
        """
        This method will return True if person has a head detected. 
        It will return False otherwise.
        
        Parameters:
        person (Person): The person to check.
        """
        if not person.head:
            return False
            
        return getattr(person.head, self._gesture)