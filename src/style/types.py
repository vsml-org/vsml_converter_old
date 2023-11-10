import re
from enum import Enum, auto

from definition import COLOR_LIST, COLOR_VALUE


class Order(Enum):
    SEQUENCE = auto()
    PARALLEL = auto()

    def __str__(self) -> str:
        return "'{}'".format(self.name)

    def __repr__(self) -> str:
        return "'{}'".format(self.name)


class LayerMode(Enum):
    SINGLE = auto()
    MULTI = auto()

    def __str__(self) -> str:
        return "'{}'".format(self.name)

    def __repr__(self) -> str:
        return "'{}'".format(self.name)


class AudioSystem(Enum):
    MONAURAL = auto()
    STEREO = auto()

    def __str__(self) -> str:
        return "'{}'".format(self.name)

    def __repr__(self) -> str:
        return "'{}'".format(self.name)


class TimeUnit(Enum):
    PERCENT = auto()
    FRAME = auto()
    SECOND = auto()
    FIT = auto()
    SOURCE = auto()

    def __str__(self) -> str:
        match self.name:
            case self.PERCENT.name:
                return "%"
            case self.FRAME.name:
                return "f"
            case self.SECOND.name:
                return "s"
            case self.FIT.name:
                return "fit"
            case self.SOURCE.name:
                return "source"
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
            case self.FIT.name:
                return "fit"
            case self.SOURCE.name:
                return "source"
            case _:
                return ""


class GraphicUnit(Enum):
    AUTO = auto()
    PERCENT = auto()
    PIXEL = auto()
    RESOLUTION_WIDTH = auto()
    RESOLUTION_HEIGHT = auto()
    RESOLUTION_MIN = auto()
    RESOLUTION_MAX = auto()

    def __str__(self) -> str:
        match self.name:
            case self.AUTO.name:
                return "auto"
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
            case self.AUTO.name:
                return "auto"
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
        if val == "fit":
            self.unit = TimeUnit.FIT
        elif val == "source":
            self.unit = TimeUnit.SOURCE
        else:
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
        match self.unit:
            case TimeUnit.FIT | TimeUnit.SOURCE:
                return "{}".format(self.unit)
            case _:
                return "'{}{}'".format(self.value, self.unit)

    def __repr__(self) -> str:
        match self.unit:
            case TimeUnit.FIT | TimeUnit.SOURCE:
                return "{}".format(self.unit)
            case _:
                return "'{}{}'".format(self.value, self.unit)

    def get_second(self, fps: float, default_value: float = 0) -> float:
        if self.unit == TimeUnit.SECOND:
            return self.value
        elif self.unit == TimeUnit.FRAME:
            return self.value / fps
        else:
            return default_value


class GraphicValue:
    value: int
    unit: GraphicUnit

    def __init__(self, val: str) -> None:
        if val == "auto":
            self.unit = GraphicUnit.AUTO
            self.value = -1
        elif val[-2:] == "px":
            self.unit = GraphicUnit.PIXEL
            self.value = int(val[:-2])
        elif val[-2:] == "rw":
            self.unit = GraphicUnit.RESOLUTION_WIDTH
            self.value = int(val[:-2])
        elif val[-2:] == "rh":
            self.unit = GraphicUnit.RESOLUTION_HEIGHT
            self.value = int(val[:-2])
        elif val[-4:] == "rmin":
            self.unit = GraphicUnit.RESOLUTION_MIN
            self.value = int(val[:-4])
        elif val[-4:] == "rmax":
            self.unit = GraphicUnit.RESOLUTION_MAX
            self.value = int(val[:-4])
        elif val[-1:] == "%":
            self.unit = GraphicUnit.PERCENT
            self.value = int(val[:-1])
        else:
            raise ValueError()

    def __str__(self) -> str:
        match self.unit:
            case GraphicUnit.AUTO:
                return "{}".format(self.unit)
            case _:
                return "'{}{}'".format(self.value, self.unit)

    def __repr__(self) -> str:
        match self.unit:
            case GraphicUnit.AUTO:
                return "{}".format(self.unit)
            case _:
                return "'{}{}'".format(self.value, self.unit)

    def get_pixel(self, default_value: int = 0) -> int:
        return self.value if self.unit == GraphicUnit.PIXEL else default_value


class Color:
    value: str
    type: ColorType
    r_value: int
    g_value: int
    b_value: int
    a_value: int = 255

    def __init__(self, val: str) -> None:
        if val in COLOR_LIST:
            self.value = val
            self.type = ColorType.PURE
            self.r_value, self.g_value, self.b_value = COLOR_VALUE.get(
                val, [0, 0, 0]
            )
        elif val[0] == "#":
            self.type = ColorType.HEX
            hex_val = val[1:]
            match len(hex_val):
                case 3:
                    self.value = "#{0}{0}{1}{1}{2}{2}".format(
                        hex_val[0], hex_val[1], hex_val[2]
                    )
                case 4:
                    self.value = "#{0}{0}{1}{1}{2}{2}{3}{3}".format(
                        hex_val[0], hex_val[1], hex_val[2], hex_val[3]
                    )
                case 6 | 8:
                    self.value = val
            if len(self.value) == 7:
                self.r_value = int(self.value[1:3], 16)
                self.g_value = int(self.value[3:5], 16)
                self.b_value = int(self.value[5:7], 16)
            elif len(self.value) == 9:
                self.r_value = int(self.value[1:3], 16)
                self.g_value = int(self.value[3:5], 16)
                self.b_value = int(self.value[5:7], 16)
                self.a_value = int(self.value[7:9], 16)
        elif val[:4] == "rgb(":
            self.type = ColorType.HEX
            find_val = re.findall(
                r"rgb\(\s*(\d+)\s*,\s*(\d+)\s*,(\d+)\s*\)",
                val,
            )
            if len(find_val) > 0:
                r, g, b = find_val[0]
                self.value = "#{}{}{}".format(
                    format(r, "x").zfill(2),
                    format(g, "x").zfill(2),
                    format(b, "x").zfill(2),
                )
                self.r_value = int(r)
                self.g_value = int(g)
                self.b_value = int(b)
        elif val[:5] == "rgba(":
            self.type = ColorType.HEX
            find_val = re.findall(
                r"rgb\(\s*(\d+)\s*,\s*(\d+)\s*,(\d+)\s*,(\d+)\s*\)",
                val,
            )
            if len(find_val) > 0:
                r, g, b, a = find_val[0]
                self.value = "#{}{}{}{}".format(
                    format(r, "x").zfill(2),
                    format(g, "x").zfill(2),
                    format(b, "x").zfill(2),
                    format(a, "x").zfill(2),
                )
                self.r_value = int(r)
                self.g_value = int(g)
                self.b_value = int(b)
                self.a_value = int(a)
        else:
            raise ValueError()

    def __str__(self) -> str:
        return "'{}'".format(self.value)

    def __repr__(self) -> str:
        return "'{}'".format(self.value)
