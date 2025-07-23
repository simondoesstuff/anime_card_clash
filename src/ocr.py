import easyocr
import numpy as np
from mss import mss
from PIL import Image
import pygetwindow as gw
from rich import print

import body
from utils.jaccard import jaccard_similarity
from utils.types import Rect


# --- Initialization ---
# Initialize the EasyOCR reader once. The first run downloads the model.
reader = easyocr.Reader(["en"])
    
    
def fetch_screen(scan_region: Rect):
    x, y, w, h = body.roblox(activate=False)

    # --- Determine Capture Coordinates ---
    capture_coords = {
        "top": y + int(scan_region.pos[1] * h),
        "left": x + int(scan_region.pos[0] * w),
        "width": int(scan_region.size[0] * w),
        "height": int(scan_region.size[1] * h)
    }

    # --- Screen Capture and OCR ---
    with mss() as sct:
        sct_img = sct.grab(capture_coords)
        img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
        # img.show()
        img_np = np.array(img)
        return img_np
        
        
def read_text(scan) -> list[tuple]:
    """
    Performs OCR on a window or screen region

    Args:
        scan_region: A Rect object defining the region to scan OR an image

    Returns:
        A list of (text, bbox) items where bbox is a list of 4 coordinate pairs.
    """
    if isinstance(scan, Rect):
        img_np = fetch_screen(scan)
    else:
        img_np = scan
    
    # Perform OCR and extract only the text
    results = reader.readtext(img_np) # type: ignore
    # Return a list of the text strings
    return [(text, bbox) for (bbox, text, prob) in results]


def try_text(region: Rect, query: str) -> bool:
    """
    Attempts to find and return the text in a specific region of a window.

    Args:
        region: The Rect object defining the region to search.
        text: The text to search for.
        window_title: The title (or partial title) of the window to scan.

    Returns:
        True if the text is found, False otherwise.
    """
    results = read_text(region)

    if results is None:
        return False

    return any(
        jaccard_similarity(query.lower(), result.lower()) > 0.75 for (result, _) in results
    )
