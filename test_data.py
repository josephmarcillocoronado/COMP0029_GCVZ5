TEST_DATA = [
    # Commands and modes
    ("Play Minecraft with my right hand", {"entities": [(0, 4, "COMMAND"), (5, 14, "MODE"), (23, 28, "ORIENTATION"), (29, 33, "LANDMARK")]}),
    ("Activate Mario using left click", {"entities": [(0, 8, "COMMAND"), (9, 14, "MODE"), (21, 31, "ACTION")]}),
    ("Start Rocket League and jump up", {"entities": [(0, 5, "COMMAND"), (6, 19, "MODE"), (24, 31, "ACTION")]}),

    # Actions and poses
    ("Perform a three fingers pinch to open the door", {"entities": [(9, 24, "POSE"), (28, 39, "ACTION")]}),
    ("Use the mouse while holding a left elbow", {"entities": [(8, 13, "POSE"), (25, 30, "ORIENTATION"), (31, 37, "LANDMARK")]}),
    ("Rotate with your right wrist to point forward", {"entities": [(0, 6, "ACTION"), (17, 22, "ORIENTATION"), (23, 28, "LANDMARK")]}),

    # Combining modes and landmarks
    ("Switch to joystick mode with both hands", {"entities": [(0, 6, "COMMAND"), (10, 23, "MODE"), (29, 33, "LANDMARK")]}),
    ("Play Rocket League in mouse mode", {"entities": [(0, 4, "COMMAND"), (5, 18, "MODE"), (22, 27, "POSE")]}),
    ("Attach left click to my right wrist", {"entities": [(0, 6, "COMMAND"), (7, 17, "ACTION"), (24, 29, "ORIENTATION"), (30, 35, "LANDMARK")]}),

    # Edge cases
    ("", {"entities": []}),
    ("Press the trigger button to shoot", {"entities": [(0, 5, "COMMAND"), (9, 24, "ACTION"), (28, 33, "ACTION")]}),
    ("Pass the ball using left click", {"entities": [(0, 14, "ACTION"), (22, 32, "ACTION")]}),
]
