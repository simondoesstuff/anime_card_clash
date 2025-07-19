import datetime
from time import sleep
from types import SimpleNamespace
from typing import Iterable, final
from rich import print

from ahk import AHK

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
LEAVE_BATTLE = (0.402, 0.356)
LEAVE_BATTLE_COLOR = "0xFFFFFF"
TELEPORT = SimpleNamespace(button=(0.09, 0.5), ninja=(0.64, 0.36), lobby=(0.64, 0.27))
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


# TODO: general check for failure and do a top level restart & rejoin


def boss_ready():
    hour = datetime.datetime.now().hour
    start = (hour // 3) * 3
    end = start + 2
    return hour >= start and hour < end


@final
class CardClasher:
    def __init__(self) -> None:
        self.ahk = AHK(executable_path="./AutoHotkey/AutoHotkeyU32.exe")
        self.mouse_speed: float = 2.5

    def window(self):
        window = self.ahk.find_window(title="Roblox")

        if not window:
            raise ValueError("Can't find roblox")

        return window

    def mouse_move(
        self, coord: tuple[float, float], speed: float = 1, coord_mode="Window"
    ):
        _, _, width, height = self.window().get_position()
        x = coord[0] * width
        y = coord[1] * height
        self.ahk.mouse_move(x, y, speed=speed * self.mouse_speed, coord_mode=coord_mode)

    def scroll(self, amount: int):
        self.window().activate()
        direction = "wheeldown" if amount > 0 else "wheelup"

        for _ in range(abs(amount)):
            self.ahk.click(button=direction)

    def mouse_right_drag(self, offset: tuple[float, float], speed=1):
        x = offset[0]
        y = offset[1]
        self.ahk.mouse_drag(x, y, button="right", relative=True, coord_mode="Screen")

    def dismiss(self):
        self.click(DISMISS)

    def respawn(self):
        """
        teleport to ninja and back to lobby to reset position
        """
        self.mouse_move(TELEPORT.button)
        self.ahk.click()
        self.mouse_move(TELEPORT.ninja)
        sleep(0.7)
        self.ahk.click()
        self.mouse_move(TELEPORT.button)
        sleep(1.5)
        self.ahk.click()
        self.mouse_move(TELEPORT.lobby)
        sleep(0.7)
        self.ahk.click()
        sleep(1.5)

    def pixel_matches(self, coord: tuple[float, float], color: str):
        _, _, width, height = self.window().get_position()
        x = coord[0] * width
        y = coord[1] * height
        return self.ahk.pixel_get_color(x, y) == color

    def until_pixel(self, coord: tuple[float, float], color: str, throw=False):
        timeout = 10 if not throw else 30
        start_time = datetime.datetime.now()
        i = 0

        while True:
            if datetime.datetime.now() - start_time > datetime.timedelta(
                seconds=timeout
            ):
                if not throw:
                    print(f"Timeout while waiting for {coord} to be {color}")
                    return False
                else:
                    raise TimeoutError(
                        f"Timeout while waiting for {coord} to be {color}"
                    )

            if self.pixel_matches(coord, color):
                return True

            i += 1
            sleep(0.1)

    def keys(
        self,
        keys: Iterable,
        duration: float = 0,
        interval: float = 0,
        simultaneous=False,
    ):
        """
        Presses keys
        @param keys: Iterable of keys to press
        @param duration: Duration to hold each key down
        @param interval: Interval between pressing keys
        @param simultaneous: If True, all keys are pressed at the same time. Interval is used
        between keys down and again, between keys up.
        """

        self.window().activate()

        if simultaneous:
            for key in keys:
                self.ahk.key_down(key)
                sleep(interval)

            sleep(duration - interval)

            for key in keys:
                self.ahk.key_up(key)
                sleep(interval)
        else:
            for key in keys:
                self.ahk.key_down(key)
                sleep(duration)
                self.ahk.key_up(key)
                sleep(interval)

    def key(self, key: str, duration: float = 0):
        """
        Presses a single key for a given duration.
        """
        self.keys([key], duration=duration)

    def click(self, coord: tuple[float, float], and_wait=0.2):
        self.window().activate()
        self.mouse_move(coord)
        if and_wait:
            sleep(and_wait)
        self.ahk.click()
        self.ahk.click()

    def close_menu(self):
        self.window().activate()
        self.keys(["\\", "Right", "Enter", "\\"], interval=0.2)

    def stop_boss(self):
        # def toggle_auto_raid():
        #     self.mouse_move(SETTINGS.button)
        #     self.ahk.click()
        #     sleep(.2)
        #     self.mouse_move(CENTER)
        #     self.scroll(7)
        #     sleep(.5)
        #     self.mouse_move(SETTINGS.raid_restart)
        #     self.ahk.click()
        #     self.mouse_move(SETTINGS.close)
        #     self.ahk.click()

        # toggle_auto_raid()
        sleep(13)
        # toggle_auto_raid()
        # sleep(1)

    def set_tower_delay(self, delay: int):
        """
        Set the delay for the tower battle.
        """
        self.dismiss()
        self.click(SETTINGS.button)
        sleep(0.2)
        self.mouse_move(CENTER)
        self.scroll(7)
        sleep(0.5)
        self.click(SETTINGS.inf)
        self.click(SETTINGS.inf)
        self.keys(str(delay), interval=0.1)
        # manual close with mouse so keyboard nav involved in close_menu doesn't
        # get stuck in the input field
        self.click(SETTINGS.close)
        sleep(2)

    def stop_pots(self):
        self.set_tower_delay(10)
        # click leave battle when it appears
        # wait for battle status
        sleep(1.5)
        self.mouse_move(CENTER)
        sleep(0.1)
        self.until_pixel(BATTLE_STATUS.while_closed, BATTLE_STATUS_COLOR, throw=True)
        self.click(BATTLE_STATUS.while_closed)
        self.until_pixel(LEAVE_BATTLE, LEAVE_BATTLE_COLOR, throw=True)
        self.click(LEAVE_BATTLE)
        sleep(1.5)
        self.set_tower_delay(1)
        sleep(2)

    def set_deck(self, deck: int):
        self.dismiss()
        self.click(DECK.button)
        coord = [DECK.deck1[0] + DECK.offset * (deck - 1), DECK.deck1[1]]
        self.click(coord, and_wait=0.5)
        self.close_menu()
        sleep(0.5)

    def start_boss(self):
        self.window().activate()
        self.set_deck(DECK_SLOTS.boss)
        self.keys("as", 1.1, simultaneous=True)
        self.keys("a", 0.8, simultaneous=True)
        self.keys("s", 1.55, simultaneous=True)
        self.keys("as", 7.35, simultaneous=True)
        self.dismiss()
        sleep(0.5)
        self.ahk.send("e")

    def start_pots(self):
        self.window().activate()
        self.set_deck(DECK_SLOTS.potion)
        self.keys("sd", 1.1, simultaneous=True)
        self.key("d", 4.4)
        sleep(0.5)
        self.click(START_POTS)
        self.close_menu()
        self.key("a", 1)

    def try_close_battle(self):
        """
        Try to close the battle screen if it is open.
        """
        self.window().activate()
        if self.until_pixel(BATTLE_STATUS.while_open, BATTLE_STATUS_COLOR):
            self.close_menu()

    def is_connected(self):
        if not self.pixel_matches(DISCONNECT.left, DISCONNECT.background):
            return True
        if not self.pixel_matches(DISCONNECT.right, DISCONNECT.background):
            return True
        return False

    def clean(self):
        """
        Initialize the environment to be ready for automation
        """
        self.set_tower_delay(1)
        self.toggle_sprint()

    def toggle_sprint(self):
        self.key("Shift", 0.1)

    def main(self):
        print("Hello from [magenta bold]anime-card-clash[/magenta bold]! :)")
        print("[italic]I hope you didn't already press 'shift'[/italic]\n")
        self.clean()

        loop = 0
        mode = None

        while True:
            if not self.is_connected():
                print("[bold red]Disconnected, reconnecting...[/bold red]")
                self.click(DISCONNECT.button)
                sleep(12)
                self.clean()
                mode = None

            next_mode = "boss" if boss_ready() else "pots"

            if mode != next_mode:
                print(f"[bold green]Starting {next_mode}[/bold green]")

                # stop previous

                if mode is not None:
                    print(f"[green bold]Stopping {mode}[/green bold]")

                if mode == "boss":
                    self.stop_boss()
                elif mode == "pots":
                    self.stop_pots()

                self.respawn()

                # start next
                if next_mode == "boss":
                    self.start_boss()
                else:
                    self.start_pots()

                self.try_close_battle()

            if loop % 180 == 0:
                self.dismiss()
                # # this is because we're not sure if the server hop happens unless you press w
                # self.key("Space", duration=0.1)

            mode = next_mode
            loop += 1
            sleep(1)


if __name__ == "__main__":
    sleep(1)
    CardClasher().main()

    cc = CardClasher()
    while True:
        # get pixel color at current
        current_pos = cc.ahk.mouse_position
        color = cc.ahk.pixel_get_color(*current_pos)
        _, _, width, height = cc.window().get_position()
        current_pos = (current_pos[0] / width, current_pos[1] / height)
        print(f"Current position: {current_pos}, Color: {color}")
