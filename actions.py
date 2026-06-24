from enum import IntEnum


class Button(IntEnum):
    UP    = 0
    DOWN  = 1
    LEFT  = 2
    RIGHT = 3
    X     = 4   # Cross
    O     = 5   # Circle
    SQ    = 6   # Square
    TRI   = 7   # Triangle
    L1    = 8
    R1    = 9
    L2    = 10
    R2    = 11


# PS1 → Xbox360 mapping used by capture_client/controller.py
# Cross→A, Circle→B, Square→X, Triangle→Y, L1→LB, R1→RB, L2→LT, R2→RT
PS1_TO_XBOX = {
    Button.X:   "A",
    Button.O:   "B",
    Button.SQ:  "X",
    Button.TRI: "Y",
    Button.L1:  "LB",
    Button.R1:  "RB",
    Button.L2:  "LT",
    Button.R2:  "RT",
    Button.UP:    "DPAD_UP",
    Button.DOWN:  "DPAD_DOWN",
    Button.LEFT:  "DPAD_LEFT",
    Button.RIGHT: "DPAD_RIGHT",
}

# Discrete action set — 18 actions covering the most useful inputs in Bloody Roar 2
ACTIONS: list[tuple[Button, ...]] = [
    (),                          # 0  IDLE
    (Button.UP,),                # 1  JUMP
    (Button.DOWN,),              # 2  CROUCH
    (Button.LEFT,),              # 3  MOVE LEFT
    (Button.RIGHT,),             # 4  MOVE RIGHT
    (Button.X,),                 # 5  LIGHT ATTACK
    (Button.O,),                 # 6  MEDIUM ATTACK
    (Button.SQ,),                # 7  HEAVY ATTACK
    (Button.TRI,),               # 8  BEAST ACTIVATION
    (Button.L1,),                # 9  GUARD
    (Button.R1,),                # 10 GRAB
    (Button.RIGHT, Button.X),    # 11 FORWARD LIGHT
    (Button.RIGHT, Button.O),    # 12 FORWARD MEDIUM
    (Button.DOWN,  Button.X),    # 13 CROUCH LIGHT
    (Button.DOWN,  Button.O),    # 14 CROUCH MEDIUM
    (Button.UP,    Button.X),    # 15 JUMP ATTACK
    (Button.L1,    Button.X),    # 16 GUARD COUNTER
    (Button.L2,    Button.R2),   # 17 BEAST DRIVE
]

N_ACTIONS = len(ACTIONS)  # 18


def action_to_buttons(action_idx: int) -> list[Button]:
    return list(ACTIONS[action_idx])


def action_name(action_idx: int) -> str:
    buttons = ACTIONS[action_idx]
    if not buttons:
        return "IDLE"
    return "+".join(b.name for b in buttons)
