from typing import Any, Optional, Union
from dataclasses import dataclass
from vsml import SortType, SourceContentType

@dataclass
class Process:
    video: Any
    audio: Any
    length: Optional[float]
