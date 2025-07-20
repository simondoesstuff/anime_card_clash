import easyocr
import numpy as np
from mss import mss
from PIL import Image
import pygetwindow as gw
from rich import print

from utils.jaccard import jaccard_similarity
from utils.types import Rect


def _issue(*args, **kwargs):
    # TODO: standarize logging with error methods
    """
    A simple wrapper for printing issues to the console.
    """
    print("[red]" + " ".join(map(str, args)) + "[/red]", **kwargs)


# --- Initialization ---
# Initialize the EasyOCR reader once. The first run downloads the model.
try:
    reader = easyocr.Reader(["en"])
except Exception as e:
    _issue(
        f"Failed to initialize EasyOCR Reader. It may need to be reinstalled. Error: {e}"
    )
    reader = None


def scan_screen(scan_region: Rect, window_title: str = "Roblox") -> list[str] | None:
    """
    Performs OCR on a window or screen region, returning only the detected text.

    Args:
        window_title: The title (or partial title) of the window to scan.
        scan_region: A Rect object defining the region to scan.

    Returns:
        A list of the detected text strings, or None if a critical error occurs.
    """
    # --- Guard Clauses (Early Returns) ---
    if not reader:
        # The reader failed to initialize at startup.
        raise RuntimeError(
            "EasyOCR Reader is not initialized. Please check the installation."
        )

    # --- Determine Capture Coordinates ---
    try:
        target_window = gw.getWindowsWithTitle(window_title)[0]
    except IndexError:
        _issue(f"Window with title containing '{window_title}' not found.")
        return None

    capture_coords = {
        "top": target_window.top + int(scan_region.pos[1] * target_window.height),
        "left": target_window.left + int(scan_region.pos[0] * target_window.width),
        "width": int(scan_region.size[0] * target_window.width),
        "height": int(scan_region.size[1] * target_window.height),
    }

    # --- Screen Capture and OCR ---
    try:
        with mss() as sct:
            sct_img = sct.grab(capture_coords)
            img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
            # img.show()
            img_np = np.array(img)

            # Perform OCR and extract only the text
            results = reader.readtext(img_np)
            # Return a list of the text strings
            return [text for (bbox, text, prob) in results]
    except Exception as e:
        _issue(f"Screen capture or OCR failed. Error: {e}")
        return None


def try_text(region: Rect, query: str, window_title: str = "Roblox") -> bool:
    """
    Attempts to find and return the text in a specific region of a window.

    Args:
        region: The Rect object defining the region to search.
        text: The text to search for.
        window_title: The title (or partial title) of the window to scan.

    Returns:
        True if the text is found, False otherwise.
    """
    results = scan_screen(region, window_title)

    if results is None:
        return False

    return any(
        jaccard_similarity(query.lower(), result.lower()) > 0.75 for result in results
    )
