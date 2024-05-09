from lib.gestures import Pose
from lib.modules import Person
from lib.view.elements.hit_trigger import HitTriggerElement


class HitTrigger(Pose):
    
    def __init__(
            self,
            pos: tuple[int, int] = None,
            landmark: str = None,
            radius: int = None,
            skin: str = None,
            default_color: tuple[int, int, int] = None,
            text: str = None,
            dwell: float = None,
            animation: int = None,
            **kwargs
    ):
        super().__init__(**kwargs)
        self.pos = pos or (0, 0)
        self.landmark = landmark or 'left_wrist'
        self.radius = radius or 40
        self.default_color = default_color or (255, 0, 0)
        self.text = text
        self.dwell = dwell or 0.0
        self.animation = animation or 1
        self.view_element: HitTriggerElement = HitTriggerElement(pos=self.pos, radius=self.radius, text=self.text,
                                                                 skin=skin, color=self.default_color, dwell=self.dwell,
                                                                 method=self.method, animation=self.animation)

    @classmethod
    def from_kwargs(cls, **kwargs) -> 'Pose':
        """
        This pose is used to represents a hit trigger action, which is a type of pose that is triggered when a body part is hit.

        Args:
            method (str): The method of the action.
            args (list[str]): The arguments of the action.
            pos (tuple[int, int]): The position of the trigger.
            landmark (str): The landmark, should be one of the body part.
            radius (int): The radius of the trigger.
            color (tuple[int, int, int]): The color of the trigger.
            skin (str): The skin of the trigger, which is the path of the image file.
            text (str): The text to display in the center of the trigger.
            dwell (float): The default dwell time of the trigger.
            animation (int): The animation of the trigger.
        """
        method, args = cls._get_method_and_args(**kwargs)
        pos = kwargs.get('pos')
        landmark = kwargs.get('landmark')
        radius = kwargs.get('radius')
        color = kwargs.get('color')
        skin = kwargs.get('skin')
        text = kwargs.get('text')
        dwell = kwargs.get('dwell')
        animation = kwargs.get('animation')

        return cls(method=method, args=args, pos=pos, landmark=landmark, radius=radius,
                   default_color=color, text=text, skin=skin, dwell=dwell, animation=animation)

    def check(self, person: Person) -> bool:
        if not person.body or (landmark := person.body.get(self.landmark)) is None:
            return False

        return self.view_element.dwell(landmark)
