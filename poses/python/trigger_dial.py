from typing import Optional

from lib.drivers import flags
from lib.gestures import Pose
from lib.modules import Person
from lib.view import View
from lib.view.elements.trigger_dial import TriggerDialElement

class TriggerDial(Pose):
    _instances: list[str] = []

    def __init__(
            self,
            dial_name: str,
            elements: dict[str, dict[str]],
            base_offset: int = None,
            element_offset: float = None,
            dwell: float = None,
            landmark: str = None,
            anchor: str = None,
            text: str = None
    ):
        super().__init__()
        self.name = dial_name
        self.landmark = landmark or 'right_wrist'
        self.anchor = anchor or 'right_shoulder'
        self.text = text

        base_offset = base_offset or 0
        element_offset = element_offset or 0.5
        dwell = dwell or 1.0
        self.view_element: TriggerDialElement = TriggerDialElement(base_offset=base_offset, elements=elements,
                                                                   factor=-1, dwell=dwell, text=self.text,
                                                                   element_offset=element_offset)
        self._instances.append(dial_name)

    @classmethod
    def from_kwargs(cls, **kwargs) -> 'Pose':
        """
        This pose is used to create a trigger dial that can be used to select a specific action.

    
        Args:
            dial_name (str): The name of the dial.
            base_offset (float): The offset for dial. 0 = half-circle, 1 = full circle.
            element_offset (float): The element offset, determines how much the distance affects the angle step.
            landmark (str): The landmark, should be one of the body part.
            anchor (str): The anchor, should be one of the body part that connect with landmark.
            text (str): The text to display in the center of the dial.
            elements (dict[str, dict[str]]): The dictionary that contains multiple element dictionaries that can be selected. 
                        Each element contains:  skin(str): the skin of the element, which is the path of the image file
                                                action (dict[str, str]: the action to be performed when the element is triggered)
                                                        class (str): the class of the action
                                                        method (str): the method of the action
                                                        args (list[str]): the arguments of the action
            dwell (float): The default dwell time of the dial elements.
        """
        dial_name = kwargs.get('dial_name')
        base_offset = kwargs.get('base_offset')
        element_offset = kwargs.get('element_offset')
        landmark = kwargs.get('landmark')
        anchor = kwargs.get('anchor')
        text = kwargs.get('text')
        elements = kwargs.get('elements')
        dwell = kwargs.get('dwell')

        return cls(base_offset=base_offset, element_offset=element_offset, text=text, anchor=anchor,
                   landmark=landmark, elements=elements, dial_name=dial_name, dwell=dwell)

    def check(self, person: Person) -> bool:
        landmark = person.body.get(self.landmark)
        anchor = person.body.get(self.anchor)
        self.view_element.visible = False
        if not any(flags.get(flag) for flag in self._instances):
            flags.set("joystick", True)
            return False

        if not flags.get(self.name):
            return False

        self.view_element.visible = True
        if not person.body or landmark is None or anchor is None:
            return False

        self.view_element.update_values(anchor, landmark)

        flags.set("joystick", False)
        return True

    def action(self, person: Person, view: Optional[View]) -> None:
        for hit_trigger in self.view_element:
            hit_trigger.action()
