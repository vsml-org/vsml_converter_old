import re
from enum import Enum, auto

from definition import COLOR_LIST


class Order(Enum):
    SEQUENCE = auto()
    PARALLEL = auto()

    def __str__(self) -> str:
        return f"'{self.name}'"

    def __repr__(self) -> str:
        return f"'{self.name}'"


class AudioSystem(Enum):
    MONAURAL = auto()
    STEREO = auto()

    def __str__(self) -> str:
        return f"'{self.name}'"

    def __repr__(self) -> str:
        return f"'{self.name}'"


class TimeUnit(Enum):
    PERCENT = auto()
    FRAME = auto()
    SECOND = auto()

    def __str__(self) -> str:
        match self.name:
            case self.PERCENT.name:
                return "%"
            case self.FRAME.name:
                return "f"
            case self.SECOND.name:
                return "s"
            case _:
                return ""

    def __repr__(self) -> str:
        match self.name:
            case self.PERCENT.name:
                return "%"
            case self.FRAME.name:
                return "f"
            case self.SECOND.name:
                return "s"
            case _:
                return ""


class GraphicUnit(Enum):
    PERCENT = auto()
    PIXEL = auto()
    RESOLUTION_WIDTH = auto()
    RESOLUTION_HEIGHT = auto()
    RESOLUTION_MIN = auto()
    RESOLUTION_MAX = auto()

    def __str__(self) -> str:
        match self.name:
            case self.PERCENT.name:
                return "%"
            case self.PIXEL.name:
                return "px"
            case self.RESOLUTION_WIDTH.name:
                return "rw"
            case self.RESOLUTION_HEIGHT.name:
                return "rh"
            case self.RESOLUTION_MIN.name:
                return "rmin"
            case self.RESOLUTION_MAX.name:
                return "rmax"
            case _:
                return ""

    def __repr__(self) -> str:
        match self.name:
            case self.PERCENT.name:
                return "%"
            case self.PIXEL.name:
                return "px"
            case self.RESOLUTION_WIDTH.name:
                return "rw"
            case self.RESOLUTION_HEIGHT.name:
                return "rh"
            case self.RESOLUTION_MIN.name:
                return "rmin"
            case self.RESOLUTION_MAX.name:
                return "rmax"
            case _:
                return ""


class ColorType(Enum):
    PURE = auto()
    HEX = auto()


class TimeValue:
    value: float
    unit: TimeUnit

    def __init__(self, val: str) -> None:
        match val[-1:]:
            case "s":
                self.unit = TimeUnit.SECOND
            case "f":
                self.unit = TimeUnit.FRAME
            case "%":
                self.unit = TimeUnit.PERCENT
            case _:
                raise ValueError()
        self.value = float(val[:-1])

    def __str__(self) -> str:
        return f"'{self.value}{self.unit}'"

    def __repr__(self) -> str:
        return f"'{self.value}{self.unit}'"


class GraphicValue:
    value: float
    unit: GraphicUnit

    def __init__(self, val: str) -> None:
        if val[-2:] == "px":
            self.unit = GraphicUnit.PIXEL
            self.value = float(val[:-2])
        elif val[-2:] == "rw":
            self.unit = GraphicUnit.RESOLUTION_WIDTH
            self.value = float(val[:-2])
        elif val[-2:] == "rh":
            self.unit = GraphicUnit.RESOLUTION_HEIGHT
            self.value = float(val[:-2])
        elif val[-4:] == "rmin":
            self.unit = GraphicUnit.RESOLUTION_MIN
            self.value = float(val[:-4])
        elif val[-4:] == "rmax":
            self.unit = GraphicUnit.RESOLUTION_MAX
            self.value = float(val[:-4])
        elif val[-1:] == "%":
            self.unit = GraphicUnit.PERCENT
            self.value = float(val[:-1])
        else:
            raise ValueError()

    def __str__(self) -> str:
        return f"'{self.value}{self.unit}'"

    def __repr__(self) -> str:
        return f"'{self.value}{self.unit}'"


class Color:
    value: str
    type: ColorType

    def __init__(self, val: str) -> None:
        if val in COLOR_LIST:
            self.value = val
            self.type = ColorType.PURE
        elif val[0] == "#":
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
            find_val = re.findall(r"rgb\(\s*(\d+)\s*,\s*(\d+)\s*,(\d+)\s*\)", val)
            if len(find_val) > 0:
                r, g, b = find_val[0]
                self.value = f"#{format(r, 'x').zfill(2)}{format(g, 'x').zfill(2)}{format(b, 'x').zfill(2)}"
        elif val[:5] == "rgba(":
            self.type = ColorType.HEX
            find_val = re.findall(
                r"rgb\(\s*(\d+)\s*,\s*(\d+)\s*,(\d+)\s*,(\d+)\s*\)", val
            )
            if len(find_val) > 0:
                r, g, b, a = find_val[0]
                self.value = f"#{format(r, 'x').zfill(2)}{format(g, 'x').zfill(2)}{format(b, 'x').zfill(2)}{format(a, 'x').zfill(2)}"
        else:
            raise ValueError()

    def __str__(self) -> str:
        return f"'{self.value}'"

    def __repr__(self) -> str:
        return f"'{self.value}'"
