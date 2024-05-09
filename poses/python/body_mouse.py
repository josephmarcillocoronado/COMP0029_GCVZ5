from lib.drivers import mouse, display
from lib.gestures import Pose
from lib.modules import Person
from lib.view import View
from lib.view.elements.aoi import AOIElement


class BodyMouse(Pose):
    def __init__(self, landmark: str = None, **kwargs):
        super().__init__(**kwargs)
        self.landmark = landmark or 'right_wrist'
        self.view_element: AOIElement = AOIElement(x=320, y=200, width=280, height=200)

    @classmethod
    def from_kwargs(cls, **kwargs) -> 'Pose':
        """
        This Pose is used to checks if the landmark is detected. If it is, it calculates the scale factor 
        and moves the mouse to the landmark position.
        In default, the landmark is the right wrist.
        
        Args:
            landmark (str): The landmark, should be one of the body part.
        """
        landmark = kwargs.get('landmark')

        return cls(landmark=landmark)

    def check(self, person: Person) -> bool:
        if not person.body:
            return False

        return person.body.get(self.landmark) is not None

    def action(self, person: Person, view: View) -> None:
        # Constants for central box size (e.g., 50% of the view_element size)
        central_box_width_ratio = 0.9
        central_box_height_ratio = 0.9

        # Calculate central box boundaries
        central_box_x1 = self.view_element.x + self.view_element.width * (1 - central_box_width_ratio) / 2
        central_box_y1 = self.view_element.y + self.view_element.height * (1 - central_box_height_ratio) / 2
        central_box_x2 = central_box_x1 + self.view_element.width * central_box_width_ratio
        central_box_y2 = central_box_y1 + self.view_element.height * central_box_height_ratio

        self.view_element.inner_x = int(central_box_x1)
        self.view_element.inner_y = int(central_box_y1)
        self.view_element.inner_width = int(central_box_x2 - central_box_x1)
        self.view_element.inner_height = int(central_box_y2 - central_box_y1)

        # Get landmark coordinates
        landmark = person.body.get(self.landmark)
        landmark_x = landmark[0]
        landmark_y = landmark[1]

        self.view_element.point = (int(landmark_x), int(landmark_y))

        # Calculate scales
        scale_x = display.width / self.view_element.inner_width
        scale_y = display.height / self.view_element.inner_height

        # # Check if landmark is inside central box
        # inside_central_box = (
        #         (central_box_x1 <= landmark_x <= central_box_x2) and
        #         (central_box_y1 <= landmark_y <= central_box_y2)
        # )

        step_size = 15

        # Check if the landmark is inside the central box
        is_inside_x = central_box_x1 <= landmark_x <= central_box_x2
        is_inside_y = central_box_y1 <= landmark_y <= central_box_y2

        if is_inside_x and is_inside_y:
            # Map landmark position to screen coordinates
            screen_x = int((landmark_x - self.view_element.x) * scale_x)
            screen_y = int((landmark_y - self.view_element.y) * scale_y)

            # Move the mouse to the mapped coordinates
            mouse.move_to(screen_x, screen_y)
        else:
            # Move the mouse at a constant pace
            dx = -step_size if landmark_x < central_box_x1 else (step_size if landmark_x > central_box_x2 else 0)
            dy = -step_size if landmark_y < central_box_y1 else (step_size if landmark_y > central_box_y2 else 0)

            mouse.move(dx, dy)
