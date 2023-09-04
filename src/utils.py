import re
from chardet import UniversalDetector
from typing import Optional

class VSMLManager:
    root_path: str

    @staticmethod
    def set_root_path(root_path: str):
        VSMLManager.root_path = root_path

    @staticmethod
    def get_root_path() -> str:
        return VSMLManager.root_path

class Position:
    x: int
    y: int

    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y        

class WidthHeight:
    width: int
    height: int

    def __init__(self, w: int, h: int) -> None:
        self.width = w
        self.height = h        

    @classmethod
    def from_str(cls, x_str: str):
        return cls(*map(int, x_str.split('x')))

    def get_str(self) -> str:
        return f'{self.width}x{self.height}'

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
