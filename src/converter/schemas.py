from typing import Any, Optional
from dataclasses import dataclass
from utils import WidthHeight, Position

@dataclass
class Process:
    video: Any
    audio: Any
    length: Optional[float]
    size: Optional[WidthHeight]
    start_position: Optional[Position]
