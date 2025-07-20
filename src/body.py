from collections.abc import Iterable
import datetime
from time import sleep
from ahk import AHK

from config import DISMISS
import ocr
from utils.logging import tprint
from utils.types import Rect


# Wraps libraries for interfacing with the outside

ahk = AHK(executable_path="./AutoHotkey/AutoHotkeyU32.exe")
_mouse_speed: float = 2.5


def roblox():
    roblox = ahk.find_window(title="Roblox")

    if not roblox:
        raise ValueError("Can't find roblox")

    return roblox


def mouse_move(coord: tuple[float, float], speed: float = 1, coord_mode="roblox"):
    _, _, width, height = roblox().get_position()
    x = coord[0] * width
    y = coord[1] * height
    ahk.mouse_move(x, y, speed=speed * _mouse_speed, coord_mode=coord_mode)


def mouse_pos() -> tuple[float, float]:
    x, y = ahk.mouse_position
    _, _, width, height = roblox().get_position()
    return (x / width, y / height)


def scroll(amount: int):
    roblox().activate()
    direction = "wheeldown" if amount > 0 else "wheelup"

    for _ in range(abs(amount)):
        ahk.click(button=direction)


def mouse_right_drag(offset: tuple[float, float], speed=1):
    x = offset[0]
    y = offset[1]
    ahk.mouse_drag(x, y, button="right", relative=True, coord_mode="Screen")


def pixel_matches(coord: tuple[float, float], color: str):
    _, _, width, height = roblox().get_position()
    x = coord[0] * width
    y = coord[1] * height
    return ahk.pixel_get_color(x, y) == color


def until_pixel(coord: tuple[float, float], color: str, timeout: float = 15):
    """
    Waits for a coordinate to be a pixel.
    @returns False on timeout and logs.
    """
    start_time = datetime.datetime.now()
    mouse_move(DISMISS)

    while not pixel_matches(coord, color):
        if datetime.datetime.now() - start_time > datetime.timedelta(seconds=timeout):
            return False

        click()
        sleep(0.2)

    return True


def until_text(
    region: Rect, text: str, timeout: int = 15, window_title: str = "Roblox"
):
    start_time = datetime.datetime.now()
    mouse_move(DISMISS)

    while not ocr.try_text(region, text, window_title):
        if datetime.datetime.now() - start_time > datetime.timedelta(seconds=timeout):
            tprint(f"Timeout while waiting for text '{text}' in region {region}")
            return False

        click()
        sleep(0.2)

    return True


def keys(
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

    roblox().activate()

    if simultaneous:
        for key in keys:
            ahk.key_down(key)
            sleep(interval)

        sleep(duration - interval)

        for key in keys:
            ahk.key_up(key)
            sleep(interval)
    else:
        for key in keys:
            ahk.key_down(key)
            sleep(duration)
            ahk.key_up(key)
            sleep(interval)


def key(key: str, duration: float = 0):
    """
    Presses a single key for a given duration.
    """
    keys([key], duration=duration)


def click(coord: tuple[float, float] | None = None, double=True, and_wait=0.2):
    roblox().activate()

    if coord is not None:
        mouse_move(coord)
    if and_wait:
        sleep(and_wait)

    ahk.click()

    if double:
        ahk.click()
