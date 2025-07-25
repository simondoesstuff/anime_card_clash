import datetime
import webbrowser
from time import sleep, time
from typing import final
from PIL import Image
import numpy as np

from body import (
    roblox,
    click,
    key,
    keys,
    mouse_move,
    pixel_matches,
    scroll,
    until_pixel,
    until_text,
)

from config import (
    BATTLE_STATUS,
    BATTLE_STATUS_COLOR,
    CENTER,
    DECK,
    DECK_SLOTS,
    DISCONNECT,
    DISMISS,
    JOIN_LINK,
    LEAVE_BATTLE,
    SETTINGS,
    START_POTS,
    TELEPORT,
)
from ocr import fetch_screen, read_text
from utils.logging import tprint
from utils.types import Rect

# TODO: general check for failure and do a top level restart & rejoin


def boss_ready():
    hour = datetime.datetime.now().hour
    start = (hour // 3) * 3
    end = start + 2
    return hour >= start and hour < end


@final
class CardClasher:
    def __init__(self):
        # TODO: possible to remove this state?
        self._is_sprinting = False

    def dismiss(self):
        roblox()
        click(DISMISS)

    def respawn(self, key=1):
        """
        teleport to another location and back to lobby to reset position
        @param key: specifies the key of the alternate location (it always does lobby)
        """
        roblox()
        click(TELEPORT.button)

        if not until_text(TELEPORT.menu_text, "teleport"):
            tprint("[red bold]Couldn't open the teleport menu[/red bold]")
            return

        lobby = TELEPORT.lobby
        keyed_item = (lobby[0], lobby[1] + TELEPORT.offset * key)

        click(keyed_item)
        sleep(1.5)
        click(TELEPORT.button)

        if not until_text(TELEPORT.menu_text, "teleport"):
            tprint("[red bold]Couldn't open the teleport menu[/red bold]")
            return

        click(lobby)
        sleep(3)

    def close_menu(self):
        roblox()
        keys(["\\", "Right", "Enter", "\\"], interval=0.3)

    def stop_boss(self):
        roblox()

        # def toggle_auto_raid():
        #     mouse_move(SETTINGS.button)
        #     click()
        #     sleep(0.2)
        #     mouse_move(CENTER)
        #     scroll(7)
        #     sleep(0.5)
        #     mouse_move(SETTINGS.raid_restart)
        #     click(double=False)
        #     mouse_move(SETTINGS.close)
        #     click()

        # toggle_auto_raid()
        sleep(13)
        # toggle_auto_raid()
        # sleep(1)

    def set_tower_delay(self, delay: int):
        """
        Set the delay for the tower battle.
        """
        roblox()
        self.dismiss()
        click(SETTINGS.button)
        sleep(0.2)
        mouse_move(CENTER)
        scroll(7)
        sleep(0.5)
        click(SETTINGS.inf)
        click(SETTINGS.inf)
        keys(str(delay), interval=0.1)
        # manual close with mouse so keyboard nav involved in close_menu doesn't
        # get stuck in the input field
        click(SETTINGS.close)

    def stop_pots(self):
        roblox()
        self.set_tower_delay(10)
        # body.click leave battle when it appears
        # wait for battle status
        sleep(1.5)

        try:
            if not until_pixel(BATTLE_STATUS.while_closed, BATTLE_STATUS_COLOR):
                tprint('[bold red]Can\'t find the "open battle" button[/bold red]')
                return

            click(BATTLE_STATUS.while_closed)

            if not until_text(LEAVE_BATTLE, "continue later", timeout=30):
                tprint('[bold red]Can\'t find the "leave battle" button[/bold red]')
                return

            click(LEAVE_BATTLE.pos)
        finally:
            click(BATTLE_STATUS.while_open)  # no harm clicking it while not in battle
            sleep(1.5)
            self.set_tower_delay(1)
            sleep(2)

    def set_deck(self, deck: int):
        roblox()
        self.dismiss()
        click(DECK.button, and_wait=0.5)
        coord = (DECK.deck1[0] + DECK.offset * (deck - 1), DECK.deck1[1])
        click(coord, and_wait=0.5)
        self.close_menu()
        sleep(0.5)

    def start_boss(self):
        roblox()
        self.respawn()
        self.set_deck(DECK_SLOTS.boss)
        keys("as", 1.1, simultaneous=True)
        keys("a", 0.8, simultaneous=True)
        keys("s", 1.53, simultaneous=True)
        keys("as", 7.35, simultaneous=True)
        # to put the boss in better view
        keys("sd", 0.2, simultaneous=True)
        self.dismiss()
        sleep(0.5)
        keys("eeeeeee", interval=0.3)

    def start_pots(self):
        roblox()
        self.respawn(key=3)
        self.set_deck(DECK_SLOTS.potion)
        keys("sd", 1.1, simultaneous=True)
        key("d", 4.4)
        sleep(0.5)
        click(START_POTS)
        self.close_menu()
        key("a", 1)

    def try_close_battle(self, instant: bool = False):
        """
        Try to close the battle screen if it is open.
        """
        roblox()

        if until_pixel(
            BATTLE_STATUS.while_open,
            BATTLE_STATUS_COLOR,
            timeout=15 if not instant else 1,
        ):
            self.close_menu()
        else:
            tprint(
                "[yellow]Tried (and [bold red]failed[/bold red]) to close the battle screen, but it wasn't open or something [bold]GG[/bold][/yellow]"
            )

    def is_connected(self):
        if not pixel_matches(DISCONNECT.left, DISCONNECT.background):
            return True
        if not pixel_matches(DISCONNECT.right, DISCONNECT.background):
            return True
        return False

    def clean(self):
        """
        Initialize the environment to be ready for automation
        """
        self.__init__()
        roblox()
        self.set_tower_delay(1)
        key("i", 1.5)
        key("o", 1.5)
        self.set_sprint(True)

    def align_cam(self):
        key("i", 1.5)
        key("o", 0.3)
        # attempt to put the target at this position
        target_pos = np.array([0.5, 0.1])
        # the amnt of time per screen distance during a step.
        # measured for the horizontal, computed for the vertical with aspect ratio
        step_ratio = 0.82
        # filters for the PLAY text
        color = (40, 169, 255)
        tolerance = 0.1 * 255

        for _ in range(4):
            img = fetch_screen(Rect((0, 0), (1, 1)))
            # filter for pixels within tolerance of the target color
            mask = np.all(np.abs(img[:, :] - color) <= tolerance, axis=2)
            # convert back into an image form
            img = (mask * 255).astype(np.uint8)
            # get the centroid, average of the bounding box
            reads = read_text(img)
            # reads = list(filter(lambda x: x[0].strip().upper() == "PLAY", reads))

            if len(reads) == 0:
                raise RuntimeError(
                    "Make sure the PLAY area's text is entirely in view."
                )

            read = reads[0]
            center = np.array(read[1]).sum(axis=0) / 4
            # normalize for window shape
            _, _, win_width, win_height = roblox(activate=False)
            center /= np.array([win_width, win_height])
            # adjust based on the diff
            diff = target_pos - center
            # convert delta into time
            aspect_ratio = win_height / win_width
            diff *= np.array([step_ratio, step_ratio * aspect_ratio])

            # execute adjustment
            if diff[0] > 0:
                key("left", abs(diff[0]))
            else:
                key("right", abs(diff[0]))
            # TODO: adjust the pitch
        key("o", 1.5)

    def set_sprint(self, sprint: bool):
        roblox()

        if self._is_sprinting == sprint:
            return

        key("Shift", 0.3)
        self._is_sprinting = sprint

    def rejoin(self):
        try:
            webbrowser.open(JOIN_LINK)
            tprint(f"Attempting to join server: {JOIN_LINK}")
        except webbrowser.Error as e:
            tprint(f"[bold red]An error occurred: {e}[/bold red]")
            raise e

    def afk_loop(self):
        """
        AFK loop that only handles disconnections and rejoining,
        without automatically starting boss or pots battles.
        """
        tprint("Starting [cyan bold]AFK loop[/cyan bold] - no auto battles will start")
        tprint("[italic]Only monitoring connection and rejoining if needed[/italic]\n")
        self.clean()

        loop = 0
        time_since_success = time()

        while True:
            if not self.is_connected():
                tprint("[bold red]Disconnected, reconnecting...[/bold red]")
                click(DISCONNECT.button)
                sleep(12)
                self.clean()

            if loop % 45 == 0:
                self.dismiss()

            # TODO: make this a config option
            if pixel_matches(
                (0.7859375, 0.053703703703703705), "0xFFFFFF"
            ) or pixel_matches((0.9713541666666666, 0.040740740740740744), "0xFFFFFF"):
                tprint(
                    "[bold red]UI Nav mode detected stuck on, toggling off...[/bold red]"
                )
                key("\\")

            if pixel_matches(BATTLE_STATUS.while_closed, BATTLE_STATUS_COLOR):
                time_since_success = time()
            elif pixel_matches(BATTLE_STATUS.while_open, BATTLE_STATUS_COLOR):
                tprint(
                    "[bold red]Battle status is detected stuck "
                    + "open, will try to close[/bold red]"
                )
                self.try_close_battle(instant=True)
                key("\\")

            if time() - time_since_success >= 300:
                tprint(
                    "[bold red]Out of battle for 5m. "
                    + "Something has gone seriously wrong. "
                    + "Rejoining...[/bold red]"
                )
                self.rejoin()
                sleep(20)
                self.clean()
                time_since_success = time()
                continue

            loop += 1
            sleep(1)

    def main(self):
        tprint("Hello from [magenta bold]anime-card-clash[/magenta bold]! :)")
        tprint("[italic]I hope you didn't already press 'shift'[/italic]\n")
        self.clean()

        loop = 0
        mode = None
        time_since_success = time()

        while True:
            if not self.is_connected():
                tprint("[bold red]Disconnected, reconnecting...[/bold red]")
                click(DISCONNECT.button)
                sleep(12)
                self.clean()
                mode = None

            next_mode = "boss" if boss_ready() else "pots"

            if mode != next_mode:
                # stop previous

                if mode is not None:
                    tprint(f"[green bold]Stopping {mode}[/green bold]")

                if mode == "boss":
                    self.stop_boss()
                elif mode == "pots":
                    self.stop_pots()

                # start next
                tprint(f"[bold green]Starting {next_mode}[/bold green]")

                if next_mode == "boss":
                    self.start_boss()
                else:
                    self.start_pots()

            if loop % 45 == 0:
                self.dismiss()

            # TODO: make this a config option
            if pixel_matches(
                (0.7859375, 0.053703703703703705), "0xFFFFFF"
            ) or pixel_matches((0.9713541666666666, 0.040740740740740744), "0xFFFFFF"):
                tprint(
                    "[bold red]UI Nav mode detected stuck on, toggling off...[/bold red]"
                )
                key("\\")

            if pixel_matches(BATTLE_STATUS.while_closed, BATTLE_STATUS_COLOR):
                time_since_success = time()
            elif pixel_matches(BATTLE_STATUS.while_open, BATTLE_STATUS_COLOR):
                tprint(
                    "[bold red]Battle status is detected stuck "
                    + "open, will try to close[/bold red]"
                )
                self.try_close_battle(instant=True)
                key("\\")

            if time() - time_since_success >= 300:
                tprint(
                    "[bold red]Out of battle for 5m. "
                    + "Something has gone seriously wrong. "
                    + "Rejoining...[/bold red]"
                )
                self.rejoin()
                sleep(20)
                self.clean()
                mode = None
                time_since_success = time()
                continue

            mode = next_mode
            loop += 1
            sleep(1)
