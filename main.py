import datetime
from types import SimpleNamespace
from typing import final
from time import sleep

from ahk import AHK


CENTER = (.5, .5)
SETTINGS = (.09, .6)
SETTINGS = SimpleNamespace(button=(.09, .6), inf=(.67, .3), raid=(.67, .75), raid_restart=(.65, .63), close=(.7, .15))
BATTLE_STATUS = (.345, .84)
BATTLE_STATUS_COLOR = '0xFFFFFF'
LEAVE_BATTLE = (.402, .356)
LEAVE_BATTLE_COLOR = '0xFFFFFF'
TELEPORT = SimpleNamespace(button=(.09, .5), ninja=(.64, .36), lobby=(.64, .27))
START_POTS = (.54, .47)
DECK = SimpleNamespace(
    button=(.04, .32),
    deck1=(.09, .78),
    offset=.04,
    close=(.94, .16)
)
DISCONNECT = SimpleNamespace(
    left=(.4, .4),
    right=(.6, .4),
    button=(.55, .58),
    background='0x393B3D'
)


def boss_ready():
    hour = datetime.datetime.now().hour
    start = (hour // 3) * 3
    end = start + 2
    return hour >= start and hour < end


@final
class CardClasher:
    def __init__(self) -> None:
        self.ahk = AHK(executable_path='./AutoHotkey/AutoHotkeyU32.exe')
        self.mouse_speed = 3
        
    def window(self):
        window = self.ahk.find_window(title="Roblox")

        if not window:
            raise ValueError("Can't find roblox")

        return window
        
    def mouse_move(self, coord: tuple[float, float], speed=2.5, coord_mode="Window"):
        _, _, width, height = self.window().get_position()
        x = coord[0] * width 
        y = coord[1] * height
        self.ahk.mouse_move(x, y, speed=speed, coord_mode=coord_mode)
        
    def scroll(self, amount: int):
        self.window().activate()
        direction = 'wheeldown' if amount > 0 else 'wheelup'

        for _ in range(abs(amount)):
            self.ahk.click(button=direction)
            
    def mouse_right_drag(self, offset: tuple[float, float], speed=1):
        x = offset[0]
        y = offset[1]
        self.ahk.mouse_drag(x, y, button='right', relative=True, coord_mode='Screen')
        
    def dismiss(self):
        self.mouse_move((.5, .05))
        self.ahk.click()

    def clean(self):
        self.window().activate()
        self.dismiss()
        # "respawn"
        self.mouse_move(TELEPORT.button)
        self.ahk.click()
        self.mouse_move(TELEPORT.ninja)
        sleep(.7)
        self.ahk.click()
        self.mouse_move(TELEPORT.button)
        sleep(1.5)
        self.ahk.click()
        self.mouse_move(TELEPORT.lobby)
        sleep(.7)
        self.ahk.click()
        sleep(1.5)
        
    def pixel_matches(self, coord: tuple[float, float], color: str):
        _, _, width, height = self.window().get_position()
        x = coord[0] * width
        y = coord[1] * height
        return self.ahk.pixel_get_color(x, y) == color
        
    def until(self, coord: tuple[float, float], color: str, throw=False):
        timeout = 10 if not throw else 30
        start_time = datetime.datetime.now()
        i = 0

        while True:
            if datetime.datetime.now() - start_time > datetime.timedelta(seconds=timeout):
                if not throw:
                    return False
                else:
                    raise TimeoutError(f"Timeout while waiting for {coord} to be {color}")
                    
            if self.pixel_matches(coord, color):
                return True
                
            if i % 20 == 0:
                self.dismiss()

            i += 1
            sleep(0.1)
            
    def keys_for(self, keys: str, time: float):
        self.window().activate()
        [ self.ahk.key_down(key) for key in keys ]
        sleep(time)
        [ self.ahk.key_up(key) for key in keys ]
        
    def is_battling(self):
        return self.until(BATTLE_STATUS, BATTLE_STATUS_COLOR)
        
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

    def stop_pots(self):
        self.mouse_move(SETTINGS.button)
        self.ahk.click()
        sleep(.2)
        self.mouse_move(CENTER)
        self.scroll(7)
        sleep(.5)
        self.mouse_move(SETTINGS.inf)
        self.ahk.click()
        sleep(.1)
        self.ahk.key_press('Right')
        self.ahk.send('0')
        self.mouse_move(SETTINGS.raid)
        self.ahk.click()
        sleep(.1)
        self.ahk.key_press('Right')
        self.ahk.send('0')
        self.mouse_move(SETTINGS.close)
        self.ahk.click()
        
        sleep(1.5)
        self.mouse_move(BATTLE_STATUS)
        sleep(.1)
        self.until(BATTLE_STATUS, BATTLE_STATUS_COLOR, throw=True)
        self.ahk.click()
        self.until(LEAVE_BATTLE, LEAVE_BATTLE_COLOR, throw=True)
        self.mouse_move(LEAVE_BATTLE)
        self.ahk.click()
        sleep(1.5)

        self.mouse_move(SETTINGS.button)
        self.ahk.click()
        sleep(.2)
        self.mouse_move(CENTER)
        self.scroll(7)
        sleep(.5)
        self.mouse_move(SETTINGS.inf)
        self.ahk.click()
        sleep(.1)
        self.ahk.key_press('Right')
        self.ahk.key_press('Right')
        self.ahk.key_press('Backspace')
        self.mouse_move(SETTINGS.raid)
        self.ahk.click()
        sleep(.1)
        self.ahk.key_press('Right')
        self.ahk.key_press('Right')
        self.ahk.key_press('Backspace')
        self.mouse_move(SETTINGS.close)
        self.ahk.click()
        sleep(2)
        
    def set_deck(self, deck: int):
        self.mouse_move(DECK.button)
        self.ahk.click()
        coord = [ DECK.deck1[0] + DECK.offset * (deck - 1), DECK.deck1[1] ]
        self.mouse_move(coord)
        sleep(.5)
        self.ahk.click()
        self.mouse_move(DECK.close)
        self.ahk.click()
        sleep(.5)

    def start_boss(self):
        self.set_deck(2)
        self.keys_for('as', 1.1)
        self.keys_for('a', .8)
        self.keys_for('s', 1.55)
        self.keys_for('as', 7.35)
        self.dismiss()
        sleep(0.5)
        self.ahk.send('e')

    def start_pots(self):
        self.set_deck(1)
        self.keys_for('sd', 1.1)
        self.keys_for('d', 4.4)
        self.dismiss()
        sleep(0.5)
        self.mouse_move(START_POTS)
        self.ahk.click()
        self.mouse_move(SETTINGS.close)
        self.ahk.click()
        
    def is_connected(self):
        if not self.pixel_matches(DISCONNECT.left, DISCONNECT.background):
            return True
        if not self.pixel_matches(DISCONNECT.right, DISCONNECT.background):
            return True
        return False
        
    def toggle_sprint(self):
        self.ahk.key_down('Shift')
        sleep(.1)
        self.ahk.key_up('Shift')

    def main(self):
        print("Hello from anime-card-clash!")
        self.window().activate()
        print("I hope you didn't already press shift")
        self.toggle_sprint()

        loop = 0
        mode = None

        while True:
            if not self.is_connected():
                print("Disconnected, reconnecting...")
                self.mouse_move(DISCONNECT.button)
                self.ahk.click()
                self.toggle_sprint()
                mode = None
                sleep(12)

            next_mode = "boss" if boss_ready() else "pots"

            if mode != next_mode:
                print(f"Starting {next_mode}")

                # stop previous
                if mode == "boss":
                    self.stop_boss()
                elif mode == "pots":
                    self.stop_pots()
                    
                self.clean()

                # start next
                if next_mode == "boss":
                    self.start_boss()
                else:
                    self.start_pots()

            if loop % 180 == 0:
                self.dismiss()

            mode = next_mode
            loop += 1
            sleep(1)


if __name__ == "__main__":
    # sleep(1)

    CardClasher().main()

    # cc = CardClasher()
    # while True:
    #     if not cc.is_connected():
    #         cc.mouse_move(DISCONNECT.button)
    #         cc.ahk.click()
    #         sleep(12)
    #         cc.clean()
        # try:
        #     CardClasher().main()
        # except Exception as e:
        #     print(e)

    # cc = CardClasher()
    # cc.window().activate()
    # cc.set_deck(1)

    # cc = CardClasher()
    # cc.window().activate()
    # cc.clean()
    # cc.start_boss()
    # exit(0)
    
    # cc = CardClasher()
    # while True:
    #     # get pixel color at current
    #     current_pos = cc.ahk.mouse_position
    #     color = cc.ahk.pixel_get_color(*current_pos)
    #     _, _, width, height = cc.window().get_position()
    #     current_pos = (current_pos[0] / width, current_pos[1] / height)
    #     print(f"Current position: {current_pos}, Color: {color}")