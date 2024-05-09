from lib.drivers import mouse, display
from lib.gestures import HandPose
from lib.modules import Side, Person
from lib.view import View
from lib.view.elements.aoi import AOIElement


class HandMouse(HandPose):
    def __init__(self, hand: Side, **kwargs):
        super().__init__(hand=hand, **kwargs)
        self.view_element: AOIElement = AOIElement(x=320, y=240, width=320, height=240)

    @classmethod
    def from_kwargs(cls, **kwargs) -> 'HandPose':
        """
        This pose is used to detect when a person pinches their hand and moves the mouse cursor.
        """
        
        return cls(**kwargs)
    
    
    def check(self, person: Person) -> bool:
        if not person.hands or not person.hands[self.hand]:
            return False

        self.view_element.update_bounds(hand=person.hands[self.hand])
        return person.hands[self.hand].visible

    def action(self, person: Person, view: View) -> None:
        # Calculate the scale factor
        scale_x = display.width / self.view_element.width
        scale_y = display.height / self.view_element.height

        palm_center = person.hands[self.hand].palm_center
        palm_x = palm_center[0] * view.width
        palm_y = palm_center[1] * view.height

        relative_x = (palm_x - self.view_element.x) * scale_x
        relative_y = (palm_y - self.view_element.y) * scale_y

        # Bound the coords to the screen
        screen_x = min(display.width, max(0, relative_x))
        screen_y = min(display.height, max(0, relative_y))

        # Move the mouse
        mouse.move_to(screen_x, screen_y)
