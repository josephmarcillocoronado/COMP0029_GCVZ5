# -*- coding: utf-8 -*-
"""
Created on Wed Dec  6 00:00:03 2023

@author: Sahil
"""
from pynput.mouse import Button, Controller
from lib.drivers import Keyboard
from lib.drivers import display
from lib.drivers import mousePen
from lib.gestures import HandPose
from lib.modules import Side, Person
from lib.view import View
from lib.view.elements.aoi import AOIElement
class HandMouse(HandPose):
    def __init__(self, hand: Side, **kwargs):
        super().__init__(hand=hand)
        self.view_element: AOIElement = AOIElement(x=320, y=240, width=320, height=240, color=(255, 0, 0))
        self.keyboard = Keyboard()
        self.mouse = Controller()
        self.indexPinch = False
        self.middlePinch = False
        self.ringPinch = False
        self.counter = 0
        self.indexCounter = 0

    @classmethod
    def from_kwargs(cls, **kwargs) -> 'HandPose':
        """
        This pose is used to detect when a person pinches their hand and moves the mouse cursor.
        pen is used to draw on the screen
        """
        
        return cls(**kwargs)
    
    def check(self, person: Person) -> bool:
        if not person.hands or not person.hands[self.hand]:
            return False

        if person.hands[self.hand].index_pinched == True:
            print("index")
            self.indexPinch = True
        else:
            self.indexPinch = False
        if person.hands[self.hand].middle_pinched == True:
            print("middle")
            self.middlePinch = True
            self.indexCounter += 1
            if self.indexCounter >= 2:
                self.indexCounter = 0
                self.mouse.press(Button.left)
                self.mouse.release(Button.left)
        else:
            self.middlePinch = False
        if person.hands[self.hand].ring_pinched == True:
            print("ring")
            self.ringPinch = True
            self.keyboard.key_down('p')
        else:
            self.ringPinch = False

        if person.hands[self.hand].pinky_pinched == True:
            print("pinky")
            self.counter += 1
            self.ringPinch = True
            if self.counter >= 15:
                self.counter = 0
                self.keyboard.key_down('e')
        else:
            self.ringPinch = False
        # if person.hands[self.hand].middle_pinched == True:
        #     self.counter += 1
        #     print("Middle pinched")
        #     if self.counter == 5:
        #         self.counter = 0
        self.view_element.update_bounds(hand=person.hands[self.hand])
        # return False
        return person.hands[self.hand].visible
        

    def action(self, person: Person, view: View) -> None:
        # Calculate the scale factor
        scale_x = display.width / self.view_element.width
        scale_y = display.height / self.view_element.height

        hand = person.hands[self.hand]

        palm_center = hand.palm_center
        palm_x = palm_center[0] * view.width
        palm_y = palm_center[1] * view.height

        relative_x = (palm_x - self.view_element.x) * scale_x
        relative_y = (palm_y - self.view_element.y) * scale_y

        # Bound the coords to the screen
        screen_x = min(display.width, max(0, relative_x))
        screen_y = min(display.height, max(0, relative_y))
        # Move the mouse
        # arrZ = []
        # for x in person.hands[self.hand]:
        #     arrZ.append(abs(person.hands[self.hand][x][2]))

        sum_z = sum(abs(coord[2]) for coord in hand.values())

        # print(sum_z, sum(arrZ))
        # print("avg z:", sum(arrZ)/len(arrZ))
        depth = sum_z/len(hand) * 6500
        # print("depth: ", depth)
        # print("coordinates: ", screen_x, " ", screen_y)
        # if self.indexPinch:
        mousePen.move_to(screen_x, screen_y, self.indexPinch, depth)