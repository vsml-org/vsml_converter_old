import re
from chardet import UniversalDetector
from typing import Optional
from enum import Enum, auto

class Position:
    x: int
    y: int

    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y        

    def __repr__(self) -> str:
        return f"'Position({self.x}, {self.y})'"

class WidthHeight:
    width: int
    height: int

    def __init__(self, w: int, h: int) -> None:
        self.width = w
        self.height = h        

    def __repr__(self) -> str:
        return f"'WidthHeight({self.width}, {self.height})'"

    @classmethod
    def from_str(cls, x_str: str):
        return cls(*map(int, x_str.split('x')))

    def get_str(self) -> str:
        return f'{self.width}x{self.height}'

class VSMLManager:
    root_path: str
    root_resolution: WidthHeight

    @staticmethod
    def set_root_path(root_path: str):
        VSMLManager.root_path = root_path

    @staticmethod
    def get_root_path() -> str:
        return VSMLManager.root_path

    @staticmethod
    def set_root_resolution(resolution: WidthHeight):
        VSMLManager.root_resolution = resolution

    @staticmethod
    def get_root_resolution() -> WidthHeight:
        return VSMLManager.root_resolution

class AudioSystem(Enum):
    MONAURAL = auto()
    STEREO = auto()

    def __repr__(self) -> str:
        return f"'AudioSystem.{self.name}'"

def get_text_encoding(filename: str) -> Optional[str]:
    with open(filename, 'rb') as file:
        detector = UniversalDetector()
        for line in file:
            detector.feed(line)
            if detector.done:
                break
    detector.close()
    encoding = detector.result['encoding']
    if encoding == 'SHIFT_JIS':
        encoding = 'CP932'
    return encoding

def remove_indent(text: str) -> str:
    formatted_text = text.strip()
    formatted_text = re.sub(r'\n\s*', r'\n', formatted_text)
    return formatted_text
