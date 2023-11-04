from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional


@dataclass
class TagInfoTree:
    tag_name: str
    class_name: list[str]
    id_name: Optional[str]
    parent: Optional[TagInfoTree]


class VSMLManager:
    root_path: str
    root_resolution: WidthHeight
    root_fps: float

    @staticmethod
    def set_root_path(root_path: str):
        VSMLManager.root_path = root_path

    @staticmethod
    def get_root_path() -> str:
        return VSMLManager.root_path

    @staticmethod
    def set_root_resolution(
        resolution: WidthHeight,
    ):
        VSMLManager.root_resolution = resolution

    @staticmethod
    def get_root_resolution() -> WidthHeight:
        return VSMLManager.root_resolution

    @staticmethod
    def set_root_fps(root_fps: float):
        VSMLManager.root_fps = root_fps

    @staticmethod
    def get_root_fps() -> float:
        return VSMLManager.root_fps


class WidthHeight:
    width: int
    height: int

    def __init__(self, w: int, h: int) -> None:
        self.width = w
        self.height = h

    def __repr__(self) -> str:
        return "'WidthHeight({}, {})'".format(self.width, self.height)

    @classmethod
    def from_str(cls, x_str: str):
        return cls(*map(int, x_str.split("x")))

    def get_str(self) -> str:
        return "{}x{}".format(self.width, self.height)

    def get_min(self) -> int:
        return min(self.width, self.height)

    def get_max(self) -> int:
        return max(self.width, self.height)


class SourceType(Enum):
    IMAGE = auto()
    VIDEO = auto()
    AUDIO = auto()
    TEXT = auto()
