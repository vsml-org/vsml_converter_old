from chardet import UniversalDetector
from typing import Optional

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
