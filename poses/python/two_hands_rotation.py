"""
@author: Mikoto Ando
"""
import math
import random
from lib.gestures import Pose
from lib.modules import Side, Person
from lib.view import View
from lib.drivers import keyboard
from statistics import mean

"""
The two_hand_rotation.py script introduces a mode that enables users to interact with Google Earth using hand gestures, 
specifically by performing rotations and shifts through hand movements. 
This mode is implemented via the RotationEvent class.
"""
class RotationEvent(Pose):

    def __init__(self, hand: Side, **kwargs):
        super().__init__()
        self.hand = hand
        self.right_hand = Side.RIGHT
        self.left_hand = Side.LEFT
        self.rotation_direction = None

    @staticmethod
    def calculate_angle(right_palm_center, left_palm_center):
        """
        Calculates the angle between the palms of both hands relative to the horizontal axis. 
        This angle is used to determine the gesture's direction.
        """
        delta_y = right_palm_center[1] - left_palm_center[1]
        delta_x = right_palm_center[0] - left_palm_center[0]
        angle = math.degrees(math.atan2(delta_y, delta_x)) % 360
        return angle
    
    def ratio_calculator(self,right_palm_center,left_palm_center,default_direction):
        """
        Determines the direction by calculating the angle between the hands. 
        The steeper this angle, the higher the likelihood of initiating an upward rotation.
        """
        angle = self.calculate_angle(right_palm_center, left_palm_center)
        angle = 360 - angle if angle > 270 else angle
        probability_to_choose_up = angle / 90
        if probability_to_choose_up < 0.1:
            self.rotation_direction = default_direction
        elif  probability_to_choose_up > 0.9:
            self.rotation_direction = "down"
        else:
            self.rotation_direction = "down" if random.random() < probability_to_choose_up else default_direction


    def check(self, person: Person) -> bool:

        if not person.hands or not person.hands[self.right_hand] or not person.hands[self.left_hand]:
            return False
        
        right_hand = person.hands[self.right_hand]
        left_hand = person.hands[self.left_hand]
        right_palm_center = person.hands[self.right_hand].palm_center
        left_palm_center = person.hands[self.left_hand].palm_center
        
        angle = self.calculate_angle(right_palm_center, left_palm_center)
        # print("angle",angle)

        right_fingertips_mean = mean([right_hand[f"{finger}_tip"][1] for finger in ["thumb", "index", "middle", "ring", "pinky"]])
        left_fingertips_mean = mean([left_hand[f"{finger}_tip"][1] for finger in ["thumb", "index", "middle", "ring", "pinky"]])

        if right_fingertips_mean > 0.8:
            if not left_hand.palm_facing_camera or left_hand["thumb_tip"][1] < left_hand["pinky_tip"][1]:
                self.rotation_direction = "down"
            elif left_hand.palm_facing_camera or left_hand["thumb_tip"][1] > left_hand["pinky_tip"][1]:
                self.rotation_direction = "up"
            return True
        elif left_fingertips_mean > 0.8:
            if not right_hand.palm_facing_camera or right_hand["thumb_tip"][1] < right_hand["pinky_tip"][1]:
                self.rotation_direction = "down"
            elif right_hand.palm_facing_camera or right_hand["thumb_tip"][1] > right_hand["pinky_tip"][1]:
                self.rotation_direction = "up"
            return True

        # Determine the direction based on the angle
        if left_hand["pinky_tip"][0] > right_hand["thumb_tip"][0] or (left_hand["pinky_tip"][0] > left_hand["thumb_tip"][0] and right_hand["pinky_tip"][0] > right_hand["thumb_tip"][0]):
            self.ratio_calculator(right_palm_center, left_palm_center,"right")
            return True
        elif right_hand["pinky_tip"][0] < left_hand["thumb_tip"][0] or (left_hand["pinky_tip"][0] < left_hand["thumb_tip"][0] and right_hand["pinky_tip"][0] < right_hand["thumb_tip"][0]):
            self.ratio_calculator(right_palm_center, left_palm_center,"left")
            return True
        else:
            if not right_hand.palm_facing_camera and not left_hand.palm_facing_camera:
                # print("not facing")
                if angle > 270:
                    self.rotation_direction = "shift_left"
                else:
                    self.rotation_direction = "shift_right"
                return True
            return False


    def action(self, person: Person, view: View) -> None:
        if self.rotation_direction == "shift_left":
            keyboard.press("shift","left")
        elif self.rotation_direction == "shift_right":
            keyboard.press("shift","right")
        else:
            keyboard.press(self.rotation_direction)

    @classmethod
    def from_kwargs(cls, **kwargs) -> 'Pose':
        return cls( **kwargs)
    