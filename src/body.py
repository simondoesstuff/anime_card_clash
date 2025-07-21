import pydirectinput as pdi
import pyautogui
from collections.abc import Iterable
import datetime
from time import sleep
import pygetwindow as gw

from config import DISMISS
import ocr
from utils.logging import tprint
from utils.types import Rect

# --- Notes on the Transition from AHK to PyDirectInput ---
#
# 1. Dependency Change: This script now uses `pydirectinput-rgx` for all keyboard and mouse inputs
#    and `pyautogui` for reading pixel colors.
#    Please install them:
#    pip install pydirectinput-rgx
#    pip install pyautogui
#
# 2. Coordinate System: PyDirectInput uses absolute screen coordinates. All functions that accept
#    relative coordinates (e.g., 0.5 for center) now convert them to absolute screen coordinates
#    based on the Roblox window's current position and size.
#
# 3. Pixel Matching: AHK's `PixelGetColor` returns a BGR hex string (e.g., 0xFF0000 is Blue).
#    PyAutoGUI's `pixel()` returns an RGB tuple. The `pixel_matches` function now handles this
#    conversion, so you can continue to use your existing BGR hex color strings.
#
# 4. Speed vs. Duration: AHK's `speed` parameter (0-100) is replaced by PyDirectInput's `duration`
#    parameter (in seconds). The functions `mouse_move` and `mouse_right_drag` now interpret the
#    old `speed` value to calculate a suitable duration.

# Set a fail-safe to prevent the mouse from being stuck at a screen corner.
pdi.FAILSAFE = True


def roblox() -> gw.Window:
    """
    Finds and returns the active Roblox window object.
    
    Raises:
        ValueError: If the Roblox window cannot be found.
        
    Returns:
        The first window object found with the title "Roblox".
    """
    try:
        roblox_windows = gw.getWindowsWithTitle("Roblox")
        if not roblox_windows:
            raise ValueError("Cannot find Roblox window.")
        return roblox_windows[0]
    except gw.PyGetWindowException:
        raise ValueError("Cannot find Roblox window.")


def mouse_move(coord: tuple[float, float], speed: float = 2.5):
    """
    Moves the mouse to a coordinate relative to the Roblox window.

    Args:
        coord: A tuple (x, y) with relative coordinates (0.0 to 1.0).
        speed: A multiplier for movement speed. Higher is faster.
    """
    win = roblox()
    win_x, win_y, width, height = win.box

    # Convert relative coordinates to absolute screen coordinates
    abs_x = win_x + (coord[0] * width)
    abs_y = win_y + (coord[1] * height)

    # Convert speed to a duration for pydirectinput. A higher speed means a lower duration.
    # This conversion can be tuned for desired "feel".
    duration = 0.4 / speed
    pdi.moveTo(int(abs_x), int(abs_y), duration=duration)


def get_mouse_pos() -> tuple[float, float]:
    """
    Gets the current mouse position as normalized coordinates relative to the Roblox window.

    Returns:
        A tuple (x, y) of the mouse's relative coordinates (0.0 to 1.0),
    """
    win = roblox() # Assumes roblox() function from previous script exists
    win.activate()
    win_x, win_y, width, height = win.box

    # Get absolute screen coordinates
    abs_x, abs_y = pyautogui.position()

    # Convert absolute coordinates to be relative to the window
    # Clamping the values between 0 and 1 handles cases where the mouse is outside the window
    rel_x = max(0.0, min(1.0, (abs_x - win_x) / width))
    rel_y = max(0.0, min(1.0, (abs_y - win_y) / height))

    return (rel_x, rel_y)


def get_pixel_color(coord: tuple[float, float]) -> str | None:
    """
    Gets the BGR hex color of the pixel at a given normalized coordinate.

    Args:
        coord: A tuple (x, y) with normalized coordinates (0.0 to 1.0).

    Returns:
        The BGR hex color string (e.g., "0xFF0000" for blue),
        or None if the window or pixel cannot be read.
    """
    try:
        win = roblox() # Assumes roblox() function from previous script exists
        win_x, win_y, width, height = win.box

        # Convert normalized coordinates to absolute screen coordinates
        abs_x = win_x + (coord[0] * width)
        abs_y = win_y + (coord[1] * height)

        # pyautogui.pixel() returns an (R, G, B) tuple.
        r, g, b = pyautogui.pixel(int(abs_x), int(abs_y))

        # Convert RGB to a BGR hex string to match AutoHotKey's format for consistency.
        pixel_color_bgr_hex = f"0x{b:02X}{g:02X}{r:02X}"
        
        return pixel_color_bgr_hex
        
    except (ValueError, OSError) as e:
        tprint(f"Error: Could not read pixel at {coord}. Details: {e}")
        return None


def scroll(amount: int):
    """
    Scrolls the mouse wheel.

    Args:
        amount: The number of "clicks" to scroll. Positive scrolls down, negative scrolls up.
    """
    roblox().activate()
    # pydirectinput: positive value scrolls UP, negative scrolls DOWN.
    # We invert the amount to match the intuitive logic (positive = down).
    pdi.scroll(-amount)


def pixel_matches(coord: tuple[float, float], color: str) -> bool:
    """
    Checks if the pixel at a relative coordinate matches a given BGR hex color.

    Args:
        coord: A tuple (x, y) with relative coordinates (0.0 to 1.0).
        color: The BGR hex color string to match (e.g., "0xFF0000" for blue).

    Returns:
        True if the pixel color matches, False otherwise.
    """
    win = roblox()
    win_x, win_y, width, height = win.box

    abs_x = win_x + (coord[0] * width)
    abs_y = win_y + (coord[1] * height)

    try:
        # pyautogui.pixel() returns an (R, G, B) tuple.
        r, g, b = pyautogui.pixel(int(abs_x), int(abs_y))

        # Convert RGB to a BGR hex string to match AHK's format.
        pixel_color_bgr_hex = f"0x{b:02X}{g:02X}{r:02X}"

        return pixel_color_bgr_hex.lower() == color.lower()
    except OSError:
        tprint(f"Warning: Could not read pixel at ({int(abs_x)}, {int(abs_y)}).")
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


def until_text(region: Rect, text: str, timeout: int = 15, window_title: str = "Roblox") -> bool:
    """
    Waits until specific text appears in a given region of the window.

    Returns:
        False on timeout, True on success.
    """
    start_time = datetime.datetime.now()
    mouse_move(DISMISS)  # Move mouse away

    while not ocr.try_text(region, text, window_title):
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
    roblox().activate()

    if simultaneous:
        for key in keys_to_press:
            pdi.keyDown(key)
            sleep(interval)

        # Hold for the remaining duration
        hold_time = duration - (interval * len(list(keys_to_press)))
        if hold_time > 0:
            sleep(hold_time)

        for key in keys_to_press:
            pdi.keyUp(key)
            sleep(interval)
    else:
        for key in keys_to_press:
            pdi.press(key, presses=1, interval=interval, duration=duration)


def key(key_to_press: str, duration: float = 0):
    """
    Presses a single key.

    Args:
        key_to_press: The key to press.
        duration: Time in seconds to hold the key down.
    """
    keys([key_to_press], duration=duration)


def click(coord: tuple[float, float] | None = None, double: bool = True, and_wait: float = 0.2):
    """
    Performs a mouse click.

    Args:
        coord: Optional relative coordinates to move to before clicking.
        double: If True, performs a double click.
        and_wait: Time in seconds to wait before the click.
    """
    roblox().activate()

    if coord is not None:
        mouse_move(coord)

    if and_wait > 0:
        sleep(and_wait)

    if double:
        pdi.doubleClick()
    else:
        pdi.click()