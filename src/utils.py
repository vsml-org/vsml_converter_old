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
