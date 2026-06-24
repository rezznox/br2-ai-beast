from training.actions import N_ACTIONS, action_name, action_to_buttons, Button


def test_action_count():
    assert N_ACTIONS == 18


def test_idle():
    assert action_to_buttons(0) == []
    assert action_name(0) == "IDLE"


def test_combo():
    buttons = action_to_buttons(11)  # FORWARD LIGHT: RIGHT + X
    assert Button.RIGHT in buttons
    assert Button.X in buttons


def test_all_actions_have_names():
    for i in range(N_ACTIONS):
        assert isinstance(action_name(i), str)
        assert len(action_name(i)) > 0
