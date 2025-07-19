from dataclasses import dataclass


@dataclass
class Rect:
    pos: tuple[float, float]
    size: tuple[float, float]