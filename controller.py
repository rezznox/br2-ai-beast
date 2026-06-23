"""Virtual Xbox360 controller via vgamepad (ViGEm bus driver required on Windows).

DuckStation's XInput backend picks up the virtual pad automatically. Map PS1 buttons
to Xbox360 equivalents: Cross→A, Circle→B, Square→X, Triangle→Y, L1→LB, R1→RB,
L2→LT(analog), R2→RT(analog), D-pad→DPAD buttons.

Install ViGEmBus driver from: https://github.com/nefarius/ViGEmBus/releases
"""

from __future__ import annotations

import vgamepad as vg

# Matches Button enum values from src/actions.py (int indices 0–11)
_BUTTON_MAP: dict[int, object] = {
    0: "DPAD_UP",
    1: "DPAD_DOWN",
    2: "DPAD_LEFT",
    3: "DPAD_RIGHT",
    4: vg.XUSB_BUTTON.XUSB_GAMEPAD_A,           # Cross
    5: vg.XUSB_BUTTON.XUSB_GAMEPAD_B,           # Circle
    6: vg.XUSB_BUTTON.XUSB_GAMEPAD_X,           # Square
    7: vg.XUSB_BUTTON.XUSB_GAMEPAD_Y,           # Triangle
    8: vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_SHOULDER,   # L1
    9: vg.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_SHOULDER,  # R1
    10: None,  # L2 — analog trigger, handled separately
    11: None,  # R2 — analog trigger, handled separately
}

_DPAD_BUTTONS = {
    "DPAD_UP":    vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_UP,
    "DPAD_DOWN":  vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_DOWN,
    "DPAD_LEFT":  vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_LEFT,
    "DPAD_RIGHT": vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_RIGHT,
}

TRIGGER_MAX = 255


class VirtualController:
    def __init__(self, mock: bool) -> None:
        self._mock = mock
        self._pad = vg.VX360Gamepad()

    def press(self, button_values: list[int]) -> None:
        """Press a set of buttons (by Button enum int values) and release all others."""
        if self._mock:
            return
        self._pad.reset()

        for val in button_values:
            mapped = _BUTTON_MAP.get(val)
            if isinstance(mapped, str) and mapped in _DPAD_BUTTONS:
                self._pad.press_button(_DPAD_BUTTONS[mapped])
            elif mapped is not None:
                self._pad.press_button(mapped)
            elif val == 10:  # L2
                self._pad.left_trigger(value=TRIGGER_MAX)
            elif val == 11:  # R2
                self._pad.right_trigger(value=TRIGGER_MAX)

        self._pad.update()

    def release_all(self) -> None:
        if self._mock:
            return
        self._pad.reset()
        self._pad.update()
