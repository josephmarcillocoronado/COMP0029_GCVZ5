import math

from lib.drivers import keyboard, flags
from lib.gestures import Pose
from lib.modules import Person
from lib.view import View
from lib.view.elements.joystick_circle import JoystickCircle


class Joystick(Pose):
    def __init__(
            self,
            keys: dict[str, str],
            pos: tuple[int, int] = None,
            landmark: str = None,
            color: tuple[int, int, int] = None,
            skin: str = None,
            **kwargs
    ):
        super().__init__(**kwargs)
        self.pos = pos or (100, 250)
        self.landmark = landmark or 'left_wrist'
        self.color = color or (0, 255, 0)
        self.skin = skin or 'common/joystick'
        self.view_element: JoystickCircle = JoystickCircle(self.skin, *self.pos)

        self.state = 0
        self.keys = keys
        flags.set("joystick", True)

    @classmethod
    def from_kwargs(cls, **kwargs) -> 'Pose':
        """
        This pose is used to represents a joystick that can be controlled by a person's body.

        Args:
            method (str): The method of the action.
            args (list[str]): The arguments of the action.
            keys (dict[str, str]): The keys to use for the joystick.
            pos (tuple[int, int]): The position of the joystick.
            landmark (str): The landmark to use for the joystick.
            color (tuple[int, int, int]): The color of the joystick.
            skin (str): The skin of the joystick.
        """
        method, args = cls._get_method_and_args(**kwargs)
        pos = kwargs.get('pos')
        landmark = kwargs.get('landmark')
        color = kwargs.get('color')
        skin = kwargs.get('skin')

        keys = {
            'up': kwargs.get('up', 'w'),
            'down': kwargs.get('down', 's'),
            'left': kwargs.get('left', 'a'),
            'right': kwargs.get('right', 'd')
        }

        return cls(method=method, args=args, keys=keys, pos=pos, landmark=landmark, color=color, skin=skin)

    def check(self, person: Person) -> bool:
        self.view_element.visible = False
        landmark = None
        if person.body:
            landmark = person.body.get(self.landmark)

        if not person.body or landmark is None or not flags.get("joystick"):
            keyboard.release(*self.keys)
            self.view_element.point = self.view_element.center
            self.view_element.visible = flags.get("joystick")
            return False

        self.view_element.update_bounds(landmark=landmark)
        self.view_element.visible = True

        # Make sure point is outside the box, which is effectively the deadzone
        if landmark in self.view_element:
            keyboard.release(*self.keys.values())
            return False

        return True

    def action(self, person: Person, view: View) -> None:
        # Divide the joystick into 8 sectors
        # 0 1 2
        # 7   3
        # 6 5 4

        # Calculate which quadrant the point is in by calculating the angle of the line from the center to the point
        # and dividing by 45
        x, y = self.view_element.point
        x -= self.view_element.x + self.view_element.width // 2
        y -= self.view_element.y + self.view_element.height // 2

        angle = math.atan2(y, x)
        angle = math.degrees(angle)
        self.view_element.angle = angle
        offset = 22.5  # Needed because the angle is offset for some reason
        angle += 180 - offset
        sector = int(angle / 45)

        # If the point is in the deadzone, don't do anything
        if sector == 8:
            return

        # If the point is going in the same direction as before, don't do anything
        if sector == self.state:
            return

        self.state = sector

        hold = set()

        if sector == 0:
            hold.add(self.keys['up'])
            hold.add(self.keys['left'])
        elif sector == 1:
            hold.add(self.keys['up'])
        elif sector == 2:
            hold.add(self.keys['up'])
            hold.add(self.keys['right'])
        elif sector == 3:
            hold.add(self.keys['right'])
        elif sector == 4:
            hold.add(self.keys['down'])
            hold.add(self.keys['right'])
        elif sector == 5:
            hold.add(self.keys['down'])
        elif sector == 6:
            hold.add(self.keys['down'])
            hold.add(self.keys['left'])
        elif sector == 7:
            hold.add(self.keys['left'])

        keyboard.release(*(key for key in self.keys.values() if key not in hold))
        keyboard.hold(*hold)
