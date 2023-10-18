import re
from enum import Enum, auto
from definition import COLOR_LIST

class ReprEnum(Enum):
    def __repr__(self) -> str:
        return f"'{self.__name__}.{self.name}'"

class TimeUnit(ReprEnum):
    PERCENT = auto()
    FRAME = auto()
    SECOND = auto()

class GraphicUnit(ReprEnum):
    PERCENT = auto()
    PIXEL = auto()
    RESOLUTION_WIDTH = auto()
    RESOLUTION_HEIGHT = auto()
    RESOLUTION_MIN = auto()
    RESOLUTION_MAX = auto()

class Order(ReprEnum):
    SEQUENCE = auto()
    PARALLEL = auto()

class ColorType(ReprEnum):
    PURE = auto()
    HEX = auto()

class AudioSystem(ReprEnum):
    MONAURAL = auto()
    STEREO = auto()

class TimeValue():
    value: float
    unit: TimeUnit

    def __init__(self, val: str) -> None:
        match val[-1]:
            case 's':
                self.unit = TimeUnit.SECOND
            case 'f':
                self.unit = TimeUnit.FRAME
            case '%':
                self.unit = TimeUnit.PERCENT
            case _:
                raise ValueError()
        self.value = float(val[:-1])

class GraphicValue():
    value: float
    unit: GraphicUnit

    def __init__(self, val: str) -> None:
        if val[-2] == 'px':
            self.unit = GraphicUnit.PIXEL
            self.value = float(val[:-2])
        elif val[-2] == 'rw':
            self.unit = GraphicUnit.RESOLUTION_WIDTH
            self.value = float(val[:-2])
        elif val[-2] == 'rh':
            self.unit = GraphicUnit.RESOLUTION_HEIGHT
            self.value = float(val[:-2])
        elif val[-4] == 'rmin':
            self.unit = GraphicUnit.RESOLUTION_MIN
            self.value = float(val[:-4])
        elif val[-4] == 'rmax':
            self.unit = GraphicUnit.RESOLUTION_MAX
            self.value = float(val[:-4])
        elif val[-1] == '%':
            self.unit = GraphicUnit.PERCENT
            self.value = float(val[:-1])
        else:
            raise ValueError()

class Color:
    value: str
    type: ColorType

    def __init__(self, val: str) -> None:
        if val in COLOR_LIST:
            self.value = val
            self.type = ColorType.PURE
        elif val[0] == '#':
            self.type = ColorType.HEX           
            hex_val = val[1:]
            match len(hex_val):
                case 3:
                    self.value = f"#{hex_val[0]}{hex_val[0]}{hex_val[1]}{hex_val[1]}{hex_val[2]}{hex_val[2]}"
                case 4:
                    self.value = f"#{hex_val[0]}{hex_val[0]}{hex_val[1]}{hex_val[1]}{hex_val[2]}{hex_val[2]}{hex_val[3]}{hex_val[3]}"
                case 6 | 8:
                    self.value = val
        elif val[:4] == "rgb(":
            self.type = ColorType.HEX           
            find_val = re.findall(r'rgb\(\s*(\d+)\s*,\s*(\d+)\s*,(\d+)\s*\)', val)
            if len(find_val) > 0:
                r, g, b = find_val[0]
                self.value = f"#{format(r, 'x').zfill(2)}{format(g, 'x').zfill(2)}{format(b, 'x').zfill(2)}"
        elif val[:5] == "rgba(":
            self.type = ColorType.HEX
            find_val = re.findall(r'rgb\(\s*(\d+)\s*,\s*(\d+)\s*,(\d+)\s*,(\d+)\s*\)', val)
            if len(find_val) > 0:
                r, g, b, a = find_val[0]
                self.value = f"#{format(r, 'x').zfill(2)}{format(g, 'x').zfill(2)}{format(b, 'x').zfill(2)}{format(a, 'x').zfill(2)}"
        else:
            raise ValueError()
