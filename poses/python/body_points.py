'''
Author: Ho Shu Han
'''
import numpy as np
from lib.gestures import Pose
from lib.drivers import keyboard
from lib.modules import Person
from lib.view import View
from lib.drivers import mouse
import numpy as np
import math


class BodyPoint(Pose):
    """
    This class performs an action when the distance between specified body points (head, hands, body) exceeds a specified threshold.

    Attributes:
    - point1 (str): The name of the first body point.
    - point2 (str): The name of the second body point.
    - threshold (float): The threshold distance for checking the distance between the two points.
    - point1_actual (dict): The actual coordinates of the first body point.
    - point2_actual (dict): The actual coordinates of the second body point.
    - distance (float): The calculated distance between the two points.

    Methods:
    - from_kwargs(**kwargs): Creates a BodyPoint instance from keyword arguments.
    - set_point_actual(person, point): Sets the actual coordinates of a body point based on the person and point name.
    - _get_hands_dist(dom_hand, off_hand): Calculates the distance between two hands.
    - _get_hand_body_dist(hand, body): Calculates the distance between a hand and the body.
    - _get_hand_head_dist(hand, head): Calculates the distance between a hand and the head.
    - _get_body_head_dist(body, head): Calculates the distance between the body and the head.
    - check(person): Checks if the distance between the two points exceeds the threshold.

    Inherits from the Pose class.
    """
    def __init__(self, point1, point2, threshold_distance, interval_angle, **kwargs):
        super().__init__(**kwargs)

        self.point1 = point1
        self.point2 = point2
        self.point1_actual = None
        self.point2_actual = None

        self.threshold_distance = threshold_distance
        self.interval_angle = interval_angle
        self.distance = 0
        self.angle = 0

    @classmethod
    def from_kwargs(cls, **kwargs) -> 'Pose': 
        """
        This pose is used to performs an action when the distance between specified 
        body points (head, hands, body) exceeds a specified threshold.

        Args:
            point1 (str): The name of the first body point.
            point2 (str): The name of the second body point.
            threshold_distance (float): The threshold distance for checking the distance 
                                        between the two points, it should be in range of 0 to 1.
            interval_angle (list[int, int]): The interval angle for checking the angle 
                                        between the two points, it should be in range of 0 to 360.
            method (str): The method of the action.
            args (list[str]): The arguments of the action.
        """
        point1 = kwargs.get('point1')
        point2 = kwargs.get('point2')
        threshold_distance = kwargs.get('threshold_distance')
        interval_angle = kwargs.get('interval_angle')
        method, args = cls._get_method_and_args(**kwargs)
        
        return cls(method=method, args=args, point1=point1, point2=point2, threshold_distance=threshold_distance, interval_angle=interval_angle)   

    def set_point_actual(self, person, point):
        """
        Sets the actual coordinates of a body point based on the person and point name.

        Args:
        - person (Person): The person object containing the body points.
        - point (str): The name of the body point.

        Returns:
        - dict or None: The actual coordinates of the body point, or None if the point is not found.
        """
        if "body" in point:
            if not person.body:
                return False
            return person.body

        elif "hand" in point:
            if "left" in point: 
                if not person.hands.left:
                    return False
                return person.hands.left

            elif "right" in point:
                if not person.hands.right:
                    return False
                return person.hands.right

        elif "head" in point:
            if not person.head:
                return False
            return person.head
        return None
    
    def _get_hands_dist(self, dom_hand, off_hand) -> float:
        """
        Calculates the distance between two hands.

        Args:
        - dom_hand (dict): The dominant hand coordinates.
        - off_hand (dict): The non-dominant hand coordinates.

        Returns:
        - float: The distance between the two hands.
        """
        index_tip1 = dom_hand["index_tip"]
        index_tip2 = off_hand["index_tip"]
        
        fingers_dist = np.sqrt(np.sum((index_tip1 - index_tip2) ** 2))
        tot_palm_height = (dom_hand.distance("middle_base", "wrist") + off_hand.distance("middle_base", "wrist"))
        angle_radians = abs(np.arctan2(index_tip2[1] - index_tip1[1], index_tip2[0] - index_tip1[0]))
        
        # print(angle_radians)
        return angle_radians, fingers_dist * 2 / tot_palm_height

    def _get_hand_body_dist(self, hand, body) -> float:
        """
        Calculates the distance between a hand and the body.
        Angle calculations - 0: South, 90: East, 180: North, 270: West

        Args:
        - hand (dict): The hand coordinates.
        - body (dict): The body coordinates.

        Returns:
        - float: The distance between the hand and the body.
        """
        middle_hand = hand.palm_center
        middle_body = (body["right_shoulder"] + body["left_shoulder"])/2000
        
        distance = np.sqrt(np.sum((np.array(middle_hand) - np.array(middle_body))**2))

        angle_radians = np.arctan2(middle_hand[0] - middle_body[0], middle_hand[1] - middle_body[1])
        
        return angle_radians, distance
                            
    def _get_hand_head_dist(self, hand, head) -> float:
        """
        Calculates the distance between a hand and the head.
        Angle calculations - 0: East, 90: North, 180: West, 270: South

        Args:
        - hand (dict): The hand coordinates.
        - head (dict): The head coordinates.

        Returns:
        - float: The distance between the hand and the head.
        """    
        middle_hand = hand.palm_center
        middle_head = head["nose-tip"]

        distance = np.linalg.norm(middle_hand - middle_head)
        angle_radians = abs(np.arctan2(middle_hand[1] - middle_head[1], middle_hand[0] - middle_head[0]))
        
        return angle_radians, distance
    
    def _get_body_head_dist(self, body, head) -> float:
        """
        Calculates the distance between the body and the head.

        Args:
        - body (dict): The body coordinates.
        - head (dict): The head coordinates.

        Returns:
        - float: The distance between the body and the head.
        """    
        middle_head = head["nose-tip"]
        middle_body = (body["left_shoulder"] + body["right_shoulder"])/2

        distance = np.linalg.norm(middle_head - middle_body)
        angle_radians = abs(np.arctan2(middle_head[1] - middle_body[1], middle_head[0] - middle_body[0]))
        
        return angle_radians, distance
    
    def check(self, person: Person) -> bool:
        """
        Checks if the distance between the two points exceeds the threshold.

        Args:
        - person (Person): The person object containing the body points.

        Returns:
        - bool: True if the distance exceeds the threshold, False otherwise.
        """
        self.point1_actual = self.set_point_actual(person, self.point1)
        self.point2_actual = self.set_point_actual(person, self.point2)

        if not self.point1_actual or not self.point2_actual:
            return False

        if "hand" in self.point1 and "hand" in self.point2:
            self.angle, self.distance = self._get_hands_dist(self.point1_actual, self.point2_actual)

        elif ("hand" in self.point1 and "body" in self.point2) or ("body" in self.point1 and "hand" in self.point2):
            if "hand" in self.point1:
                self.angle, self.distance = self._get_hand_body_dist(self.point1_actual, self.point2_actual)
            else:
                self.angle, self.distance = self._get_hand_body_dist(self.point2_actual, self.point1_actual)

        elif ("hand" in self.point1 and "head" in self.point2) or ("head" in self.point1 and "hand" in self.point2):
            if "hand" in self.point1:
                self.angle, self.distance = self._get_hand_head_dist(self.point1_actual, self.point2_actual)
            else:
                self.angle, self.distance = self._get_hand_head_dist(self.point2_actual, self.point1_actual)

        elif ("body" in self.point1 and "head" in self.point2) or ("head" in self.point1 and "body" in self.point2):
            if "body" in self.point1:
                self.angle, self.distance = self._get_body_head_dist(self.point1_actual, self.point2_actual)
            else:
                self.angle, self.distance = self._get_body_head_dist(self.point2_actual, self.point1_actual)

        if self.distance > self.threshold_distance and self.angle >= math.radians(self.interval_angle[0]) and self.angle <= math.radians(self.interval_angle[1]):
            return True                                 
        else:                             
            return False
        