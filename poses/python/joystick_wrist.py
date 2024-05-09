'''
Author: Michal Bravansky
'''
from lib.gestures import HandPose
from lib.modules import Side, Person
from lib.modules.hands import Hand
from lib.drivers import gamepad
from lib.view import View

class JoystickWrist(HandPose):
    """
    Represents a hand pose for controlling a joystick with wrist movements.

    Attributes:
        MAX_INPUT_RANGE_JOYSTICK (int): The maximum input range for the joystick.
        MAX_INPUT_RANGE_TRIGGER (int): The maximum input range for the trigger.

    Args:
        hand (Side): The side of the hand (LEFT or RIGHT).
        analog_name (str): The name of the analog input.
        switch (str): The switch mode ("on" or "off").
        mode (str): The mode of operation ("default" or "swap").

    Methods:
        from_kwargs(**kwargs): Creates a JoystickWrist instance from keyword arguments.
        action(person, view): Performs the action based on the hand pose.
        _stick_mapper(FB_ratio, LR_ratio, max_input_range_joystick): Maps joystick movements.
        _trigger_mapper(LR_ratio, max_input_range_trigger): Maps trigger movements.
        _get_ratio(hand): Calculates the front-back and left-right ratios.
        _get_palm_front_back_tilt(hand): Calculates the front-back tilt of the palm.
        _get_palm_left_right_tilt(hand): Calculates the left-right tilt of the palm.
        check(person): Checks if the hand pose is valid.
        _set_ratios(): Sets the ratios for joystick and trigger movements.
    """
    MAX_INPUT_RANGE_JOYSTICK = 32767
    MAX_INPUT_RANGE_TRIGGER = 255

    def __init__(self, hand: Side, analog_name:str, switch:str, mode:str):
        super().__init__(hand= hand)
        self._hand = hand
        self._n_frames_for_switch = 10
        self._last_hands_dist = None
        self._analog_name = analog_name
        self._switch = switch
        self._mode = mode
        self.framed_held = 0
        self._set_ratios()

    @classmethod
    def from_kwargs(cls, **kwargs) -> 'HandPose':
        """
        This pose is used to represents a hand pose for controlling a joystick with wrist movements.

        Args:
            hand (Literal['left', 'right']): The side of the hand (LEFT or RIGHT).
            analog_name (str): The name of the analog input.
            switch (str): The switch mode ("on" or "off").
            mode (str): The mode of operation ("default" or "swap")
        """
        hand = kwargs.get('hand')
        if hand:
            hand = Side[hand.upper()]
    
        analog_name = kwargs.get("analog_name")
        switch = kwargs.get("switch")
        mode = kwargs.get("mode")

        return cls(analog_name=analog_name,switch=switch,mode=mode, hand=hand)
    
    def action(self, person:Person, view:View) -> None:
        """
        Performs the action based on the hand pose.

        Args:
            person (Person): The person object containing hand data.
            view (View): The view object for displaying the action.
        """
        hand = person.hands[self._hand]

        FB_ratio, LR_ratio = self._get_ratio(hand)
                
        if self._analog_name == "sticks":
            if self._switch == "on":
                # threshould tan(5)=0.0875 to ignore randon rotation
                if abs(FB_ratio) > 0.0875 or abs(LR_ratio) > 0.0875:
                    self._stick_mapper(FB_ratio, LR_ratio, self.MAX_INPUT_RANGE_JOYSTICK)

        else:                   
            if self._switch == "on":
                # threshould tan(8.5)=0.15 to ignore randon rotation
                if abs(LR_ratio) > 0.15:
                    self._trigger_mapper(LR_ratio, self.MAX_INPUT_RANGE_TRIGGER)


    def _stick_mapper(self, FB_ratio, LR_ratio, max_input_range_joystick):
        """
        Maps joystick movements based on the front-back and left-right ratios.

        Args:
            FB_ratio (float): The front-back ratio.
            LR_ratio (float): The left-right ratio.
            max_input_range_joystick (int): The maximum input range for the joystick.
        """
        if FB_ratio > 0: # hand move forward
            FB_ratio = FB_ratio/self.ratio_stick_forward*max_input_range_joystick
            if FB_ratio > max_input_range_joystick: FB_ratio = max_input_range_joystick
        else: # hand move backward
            FB_ratio = FB_ratio/self.ratio_stick_backward*max_input_range_joystick
            if FB_ratio < -max_input_range_joystick: FB_ratio = -max_input_range_joystick
        if LR_ratio > 0: # hand move left
            LR_ratio = LR_ratio/self.ratio_stick_left*max_input_range_joystick
            if LR_ratio > max_input_range_joystick: LR_ratio = max_input_range_joystick
        else: # hand move right
            LR_ratio = LR_ratio/self.ratio_stick_right*max_input_range_joystick
            if LR_ratio < -max_input_range_joystick: LR_ratio = -max_input_range_joystick
        # input only accept int value
        FB_ratio = round(FB_ratio)
        LR_ratio = round(LR_ratio)
        
        if self._hand == Side.LEFT:
            gamepad.joystick_left_move(-LR_ratio, FB_ratio)
        else:
            gamepad.joystick_right_move(-LR_ratio, FB_ratio)

    def _trigger_mapper(self, LR_ratio, max_input_range_trigger):
        """
        Maps trigger movements based on the left-right ratio.

        Args:
            LR_ratio (float): The left-right ratio.
            max_input_range_trigger (int): The maximum input range for the trigger.
        """
        T = LR_ratio
        if self._mode == "default":
            if T > 0: # hand move left - press left trigger
                T = T/self.ratio_trigger_outwards*max_input_range_trigger
                if T > max_input_range_trigger: T = max_input_range_trigger
                # input only accept int value
                T = round(T)
                gamepad.joystick_left_trigger(T)
                gamepad.joystick_right_trigger(0)
            else: # hand move right - press right trigger
                T = T/self.ratio_trigger_inwards*max_input_range_trigger
                if T < -max_input_range_trigger: T = -max_input_range_trigger
                T = round(T)
                gamepad.joystick_left_trigger(0)
                gamepad.joystick_right_trigger(-T)
        else: # swap mode
            if T > 0: # hand move left - press right trigger
                T = T/self.ratio_trigger_inwards*max_input_range_trigger
                if T > max_input_range_trigger: T = max_input_range_trigger
                T = round(T)
                gamepad.joystick_left_trigger(0)
                gamepad.joystick_right_trigger(T)
            else: # hand move right - press left tribyaygger
                T = T/self.ratio_trigger_outwards*max_input_range_trigger
                if T < -max_input_range_trigger: T = -max_input_range_trigger
                T = round(T)
                gamepad.joystick_left_trigger(-T)
                gamepad.joystick_right_trigger(0)

    def _get_ratio(self, hand:Hand) -> float:
        """
        Calculates the front-back and left-right ratios based on hand data.

        Args:
            hand (Hand): The hand object containing joint positions.

        Returns:
            float: The front-back and left-right ratios.
        """
        FB_ratio = self._get_palm_front_back_tilt(hand)  
        LR_ratio = self._get_palm_left_right_tilt(hand)
        return FB_ratio, LR_ratio
    
    def _get_palm_front_back_tilt(self, hand:Hand):
        """
        Calculates the front-back tilt of the palm based on hand data.

        Args:
            hand (Hand): The hand object containing joint positions.

        Returns:
            float: The front-back tilt ratio.
        """
        dy = hand["middle_base"][1] - hand["wrist"][1]
        dz = hand["middle_base"][2] - hand["wrist"][2]
        return dz / dy
    
    def _get_palm_left_right_tilt(self, hand: Hand):
        """
        Calculates the left-right tilt of the palm based on hand data.

        Args:
            hand (Hand): The hand object containing joint positions.

        Returns:
            float: The left-right tilt ratio.
        """
        dy = hand["middle_base"][1] - hand["wrist"][1]
        dx = hand["middle_base"][0] - hand["wrist"][0]
        return dx / dy
    
    def check(self, person: Person) -> bool:
        """
        Checks if the hand pose is valid.

        Args:
            person (Person): The person object containing hand data.

        Returns:
            bool: True if the hand pose is valid, False otherwise.
        """
        if person.hands and person.hands[self._hand]:

            hand = person.hands[self._hand]

            held = hand.thumb_stretched and hand.index_stretched and hand.middle_stretched and hand.ring_stretched and hand.pinky_stretched
            self.framed_held += 1

            if held and self.framed_held > self._n_frames_for_switch:
                return True
            
            return False
        
        self.framed_held = 0
        return False 

    def _set_ratios(self) -> None:
        """
        Sets the ratios for joystick and trigger movements.
        """
        self.ratio_stick_left = 0.7
        self.ratio_stick_right = 0.57
        self.ratio_stick_forward = 0.65
        self.ratio_stick_backward = 0.35
        self.ratio_trigger_outwards = 0.3
        self.ratio_trigger_inwards = 0.6

