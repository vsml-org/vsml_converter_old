from dataclasses import dataclass
from typing import Any, Optional

from utils import Position, WidthHeight


@dataclass
class Process:
    video: Any
    audio: Any
    duration: Optional[float]
    resolution: Optional[WidthHeight]
    start_position: Optional[Position]
