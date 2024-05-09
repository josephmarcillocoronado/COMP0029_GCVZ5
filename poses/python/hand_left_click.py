from lib.drivers import mouse
from lib.gestures import HandPose
from lib.modules import Person
from lib.view import View


class HandLeftClick(HandPose):
    @classmethod
    def from_kwargs(cls, **kwargs) -> 'HandPose':

        """
        This pose is used to detect when a person pinches their left hand.
        """
        return cls(**kwargs)
    
    def check(self, person: Person) -> bool:
        if not person.hands or not person.hands[self.hand]:
            return False

        hand = person.hands[self.hand]
        return (
            hand.visible and
            hand.index_pinched
        )

    def action(self, person: Person, view: View) -> None:
        mouse.click("left")
