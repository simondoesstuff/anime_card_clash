from types import SimpleNamespace

from utils.types import Rect


# TODO: strongly type


CENTER = (0.5, 0.5)
# where to click to dismiss popups
DISMISS = (0.5, 0.99)
SETTINGS = (0.09, 0.6)
SETTINGS = SimpleNamespace(
    button=(0.09, 0.6),
    inf=(0.67, 0.3),
    raid=(0.67, 0.75),
    raid_restart=(0.65, 0.63),
    close=(0.7, 0.16),
)
BATTLE_STATUS = SimpleNamespace(while_closed=(0.345, 0.84), while_open=(0.5, 0.95))
BATTLE_STATUS_COLOR = "0xFFFFFF"
LEAVE_BATTLE = Rect((0.39, 0.34), (0.1, 0.05))
TELEPORT = SimpleNamespace(button=(0.09, 0.5), ninja=(0.64, 0.36), lobby=(0.64, 0.27), menu_text=Rect((.35, .13), (.12, .05)))
START_POTS = (0.54, 0.47)
DECK = SimpleNamespace(button=(0.04, 0.36), deck1=(0.09, 0.78), offset=0.04)
# 1-indexed, only support for top row decks
DECK_SLOTS = SimpleNamespace(
    boss=2,
    potion=1,
)
DISCONNECT = SimpleNamespace(
    left=(0.4, 0.4), right=(0.6, 0.4), button=(0.55, 0.58), background="0x393B3D"
)

