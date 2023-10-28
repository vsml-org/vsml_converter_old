from dataclasses import dataclass
from typing import Any

from style import Style


@dataclass
class Process:
    video: Any
    audio: Any
    style: Style
