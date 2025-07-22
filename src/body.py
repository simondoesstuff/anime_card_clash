import datetime
from collections.abc import Iterable
from time import sleep

from ahk import AHK

import ocr
from config import DISMISS
from utils.logging import tprint
from utils.types import Rect

# Initialize the AHK interface
ahk = AHK(executable_path="./AutoHotkey/AutoHotkeyU32.exe")
_mouse_speed: float = 2.5


def roblox(activate=True) -> tuple[int, int, int, int]:
    """
    Finds the Roblox window, activates it, and returns its size.

    Raises:
        ValueError: If the Roblox window cannot be found.

    Returns:
        A tuple (x, y, width, height) of the window in pixels.
    """
    roblox_win = ahk.find_window(title="Roblox")

    if not roblox_win:
        raise ValueError("Can't find Roblox window")

    if activate:
        roblox_win.activate()

    return roblox_win.get_position() # x, y, w, h


def mouse_move(coord: tuple[float, float], speed: float = 2.5):
    """
    Moves the mouse to a coordinate relative to the Roblox window.

    Args:
        coord: A tuple (x, y) with relative coordinates (0.0 to 1.0).
        speed: A value from 0 (fast) to 100 (slow) for movement speed.
    """
    # Get window dimensions directly from the new roblox() function
    _, _, width, height = roblox(activate=False)

    # Convert relative coordinates to absolute coordinates within the window
    x = coord[0] * width
    y = coord[1] * height

    # Assumes the AHK script is set to use Window Coordinate Mode
    ahk.mouse_move(x, y, speed=int(speed), coord_mode="Window")


def get_mouse_pos() -> tuple[float, float]:
    """
    Gets the current mouse position as normalized coordinates relative to the Roblox window.

    Returns:
        A tuple (x, y) of the mouse's relative coordinates (0.0 to 1.0).
    """
    # Get window position and dimensions directly
    win_x, win_y, width, height = roblox(activate=False)

    # Get absolute screen coordinates of the mouse
    abs_x, abs_y = ahk.mouse_position

    # Convert absolute screen coordinates to be relative to the window, clamped between 0 and 1
    rel_x = max(0.0, min(1.0, (abs_x - win_x) / width))
    rel_y = max(0.0, min(1.0, (abs_y - win_y) / height))

    return (rel_x, rel_y)


def get_pixel_color(coord: tuple[float, float]) -> str | None:
    """
    Gets the BGR hex color of the pixel at a given normalized coordinate.

    Args:
        coord: A tuple (x, y) with normalized coordinates (0.0 to 1.0).

    Returns:
        The BGR hex color string (e.g., "0xFF0000" for blue), or None on error.
    """
    try:
        # Get window position and dimensions directly
        win_x, win_y, width, height = roblox(activate=False)

        # Convert normalized coordinates to absolute screen coordinates
        abs_x = win_x + (coord[0] * width)
        abs_y = win_y + (coord[1] * height)

        # AHK's pixel_get_color uses screen coordinates by default and returns BGR format
        return ahk.pixel_get_color(int(abs_x), int(abs_y), coord_mode="Screen")

    except Exception as e:
        tprint(f"Error: Could not read pixel at {coord}. Details: {e}")
        return None


def scroll(amount: int):
    """
    Scrolls the mouse wheel.

    Args:
        amount: The number of "clicks" to scroll. Positive scrolls down, negative scrolls up.
    """
    roblox() # Called for activation; the returned tuple is ignored
    direction = "wheeldown" if amount > 0 else "wheelup"

    for _ in range(abs(amount)):
        ahk.click(button=direction)


def pixel_matches(coord: tuple[float, float], color: str) -> bool:
    """
    Checks if the pixel at a relative coordinate matches a given BGR hex color.

    Args:
        coord: A tuple (x, y) with relative coordinates (0.0 to 1.0).
        color: The BGR hex color string to match.

    Returns:
        True if the pixel color matches, False otherwise.
    """
    try:
        pixel_color = get_pixel_color(coord)
        if pixel_color is None:
            return False
        return pixel_color.lower() == color.lower()
    except Exception as e:
        tprint(f"Warning: Could not read pixel at {coord}. Details: {e}")
        return False


def until_pixel(coord: tuple[float, float], color: str, timeout: float = 15) -> bool:
    """
    Waits until a pixel at a specific coordinate has the expected color.

    Returns:
        False on timeout, True on success.
    """
    start_time = datetime.datetime.now()
    mouse_move(DISMISS)  # Move mouse away to not obstruct view

    while not pixel_matches(coord, color):
        if datetime.datetime.now() - start_time > datetime.timedelta(seconds=timeout):
            tprint(f"Timeout waiting for pixel color {color} at {coord}")
            return False

        click()  # Click to dismiss potential pop-ups
        sleep(0.2)

    return True


def until_text(region: Rect, text: str, timeout: int = 15) -> bool:
    """
    Waits until specific text appears in a given region of the window.

    Returns:
        False on timeout, True on success.
    """
    start_time = datetime.datetime.now()
    mouse_move(DISMISS)  # Move mouse away

    while not ocr.try_text(region, text):
        if datetime.datetime.now() - start_time > datetime.timedelta(seconds=timeout):
            tprint(f"Timeout while waiting for text '{text}' in region {region}")
            return False

        click()
        sleep(0.2)

    return True


def keys(
    keys_to_press: Iterable[str],
    duration: float = 0,
    interval: float = 0,
    simultaneous: bool = False,
):
    """
    Presses one or more keys.

    Args:
        keys_to_press: An iterable of key strings to press.
        duration: Time in seconds to hold each key down.
        interval: Time in seconds to wait between key presses.
        simultaneous: If True, press all keys down together, hold, then release.
    """
    roblox() # Called for activation; the returned tuple is ignored

    if simultaneous:
        for key in keys_to_press:
            ahk.key_down(key)
            sleep(interval)

        sleep(duration)

        for key in keys_to_press:
            ahk.key_up(key)
            sleep(interval)
    else:
        for key in keys_to_press:
            ahk.key_down(key)
            sleep(duration)
            ahk.key_up(key)
            sleep(interval)


def key(key_to_press: str, duration: float = 0):
    """
    Presses a single key.

    Args:
        key_to_press: The key to press.
        duration: Time in seconds to hold the key down.
    """
    keys([key_to_press], duration=duration)


def click(
    coord: tuple[float, float] | None = None,
    double: bool = True,
    and_wait: float = 0.2,
    right: bool = False,
):
    """
    Performs a mouse click.

    Args:
        coord: Optional relative coordinates to move to before clicking.
        double: If True, performs a double click.
        and_wait: Time in seconds to wait before the click.
        right: If True, performs a right click.
    """
    roblox() # Called for activation; the returned tuple is ignored

    if coord is not None:
        mouse_move(coord)

    if and_wait > 0:
        sleep(and_wait)

    button = "right" if right else "left"

    ahk.click(button=button)
    if double:
        ahk.click(button=button)