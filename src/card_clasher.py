import datetime
from time import sleep
from typing import final

from ahk import AHK
from body import (
    click,
    key,
    keys,
    mouse_move,
    pixel_matches,
    roblox,
    scroll,
    until_pixel,
    until_text,
)

from config import (
    DISMISS,
    TELEPORT,
    SETTINGS,
    CENTER,
    BATTLE_STATUS,
    BATTLE_STATUS_COLOR,
    LEAVE_BATTLE,
    DECK,
    DECK_SLOTS,
    START_POTS,
    DISCONNECT,
)
from utils.logging import tprint


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
        roblox().activate()
        click(DISMISS)

    def respawn(self):
        """
        teleport to ninja and back to lobby to reset position
        """
        roblox().activate()
        click(TELEPORT.button)

        if not until_text(TELEPORT.menu_text, "teleport"):
            tprint("[red bold]Couldn't open the teleport menu[/red bold]")
            return

        click(TELEPORT.ninja)
        sleep(1.5)
        click(TELEPORT.button)

        if not until_text(TELEPORT.menu_text, "teleport"):
            tprint("[red bold]Couldn't open the teleport menu[/red bold]")
            return

        click(TELEPORT.lobby)
        sleep(1.5)

    def close_menu(self):
        roblox().activate()
        keys(["\\", "Right", "Enter", "\\"], interval=0.2)

    def stop_boss(self):
        roblox().activate()

        def toggle_auto_raid():
            mouse_move(SETTINGS.button)
            click()
            sleep(0.2)
            mouse_move(CENTER)
            scroll(7)
            sleep(0.5)
            mouse_move(SETTINGS.raid_restart)
            click(double=False)
            mouse_move(SETTINGS.close)
            click()

        toggle_auto_raid()
        sleep(13)
        toggle_auto_raid()
        sleep(1)

    def set_tower_delay(self, delay: int):
        """
        Set the delay for the tower battle.
        """
        roblox().activate()
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
        roblox().activate()
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
            click(BATTLE_STATUS.while_closed)  # no harm clicking it while not in battle
            sleep(1.5)
            self.set_tower_delay(1)
            sleep(2)

    def set_deck(self, deck: int):
        roblox().activate()
        self.dismiss()
        click(DECK.button)
        coord = (DECK.deck1[0] + DECK.offset * (deck - 1), DECK.deck1[1])
        click(coord, and_wait=0.5)
        self.close_menu()
        sleep(0.5)

    def start_boss(self):
        roblox().activate()
        self.respawn()
        self.set_deck(DECK_SLOTS.boss)
        keys("as", 1.1, simultaneous=True)
        keys("a", 0.8, simultaneous=True)
        keys("s", 1.53, simultaneous=True)
        keys("as", 7.35, simultaneous=True)
        self.dismiss()
        sleep(0.5)
        key("e")
        self.try_close_battle()

    def start_pots(self):
        roblox().activate()
        self.respawn()
        self.set_deck(DECK_SLOTS.potion)
        keys("sd", 1.1, simultaneous=True)
        key("d", 4.4)
        sleep(0.5)
        click(START_POTS)
        self.close_menu()
        key("a", 1)
        self.try_close_battle()

    def try_close_battle(self):
        """
        Try to close the battle screen if it is open.
        """
        roblox().activate()

        if until_pixel(BATTLE_STATUS.while_open, BATTLE_STATUS_COLOR):
            self.close_menu()
        else:
            tprint(
                "[yellow]Tried to close the battle screen, but maybe it wasn't open[/yellow]"
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
        roblox().activate()
        self.set_tower_delay(1)
        self.set_sprint(True)

    def set_sprint(self, sprint: bool):
        roblox().activate()

        if self._is_sprinting == sprint:
            return

        key("Shift", 0.1)
        self._is_sprinting = sprint

    def main(self):
        tprint("Hello from [magenta bold]anime-card-clash[/magenta bold]! :)")
        tprint("[italic]I hope you didn't already press 'shift'[/italic]\n")
        self.clean()

        loop = 0
        mode = None

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

            if loop % 180 == 0:
                self.dismiss()
                # # this is because we're not sure if the server hop happens unless you press w
                # self.key("Space", duration=0.1)

            mode = next_mode
            loop += 1
            sleep(1)
