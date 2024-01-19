import re
from typing import Optional

from matplotlib import font_manager
from PIL import ImageFont

font_dict: dict[str, dict[str, str]] = {}
font_files = font_manager.findSystemFonts(fontpaths=None, fontext="ttf")
for font_file in font_files:
    try:
        font_info = font_manager.get_font(font_file)
    except Exception:
        continue
    if not font_dict.get(font_info.family_name):
        font_dict[font_info.family_name] = {}
    font_dict[font_info.family_name] |= {
        font_info.style_name.lower().strip(): font_file
    }


def get_font_list():
    return list(font_dict.keys())


def get_bi_font(
    font_dict: dict[str, str], compromising: bool = True
) -> Optional[str]:
    bi_fonts = [
        items[1]
        for items in font_dict.items()
        if re.match(".*bold.*", items[0]) and re.match(".*italic.*", items[0])
    ]
    if len(bi_fonts) > 0:
        return bi_fonts[0]
    if compromising:
        bold_font = get_bold_font(font_dict, compromising=False)
        if bold_font is not None:
            return bold_font
        return get_italic_font(font_dict)


def get_bold_font(
    font_dict: dict[str, str], compromising: bool = True
) -> Optional[str]:
    bold_fonts = [
        items[1]
        for items in font_dict.items()
        if re.match(".*bold.*", items[0])
        and not re.match(".*italic.*", items[0])
    ]
    if len(bold_fonts) > 0:
        return bold_fonts[0]
    if compromising:
        return get_regular_font(font_dict)


def get_italic_font(
    font_dict: dict[str, str], compromising: bool = True
) -> Optional[str]:
    italic_fonts = [
        items[1]
        for items in font_dict.items()
        if not re.match(".*bold.*", items[0])
        and re.match(".*italic.*", items[0])
    ]
    if len(italic_fonts) > 0:
        return italic_fonts[0]
    if compromising:
        return get_regular_font(font_dict)


def get_regular_font(font_dict: dict[str, str]) -> Optional[str]:
    regular_fonts = [
        items[1]
        for items in font_dict.items()
        if re.match(".*regular.*", items[0])
    ]
    if len(regular_fonts) > 0:
        return regular_fonts[0]
    regular_fonts = [
        items[1]
        for items in font_dict.items()
        if re.match(".*medium.*", items[0])
        or re.match(".*book.*", items[0])
        or re.match(".*light.*", items[0])
        or re.match(".*thin.*", items[0])
    ]
    if len(regular_fonts) > 0:
        return regular_fonts[0]


def find_font_files(
    font_names: list[str], bold: bool = False, italic: bool = False
) -> Optional[str]:
    for font_name in font_names:
        font_name_dict = font_dict.get(font_name)
        if font_name_dict is None:
            continue
        values = list(font_name_dict.values())
        if len(values) == 1:
            return values[0]
        match bold, italic:
            case True, True:
                return get_bi_font(font_name_dict)
            case True, False:
                return get_bold_font(font_name_dict)
            case False, True:
                return get_italic_font(font_name_dict)
            case False, False:
                return get_regular_font(font_name_dict)


def calculate_text_size(
    font_path: Optional[str],
    text: str,
    font_size: int,
    font_border_width: Optional[int],
):
    text_lines = text.split("\n")
    if font_path is None:
        max_width = max(map(len, text_lines)) * font_size
        one_line_height = font_size
        if font_border_width is not None:
            max_width += font_border_width * 2
            one_line_height += font_border_width * 2
        return (
            max_width,
            len(text_lines) * one_line_height,
        )
    else:
        font = ImageFont.truetype(font_path, font_size)

        text_widths: list[int] = []
        text_heights: list[int] = []
        for text_line in text_lines:
            offset_x, offset_y, text_width, text_height = font.getbbox(
                text_line
            )
            text_widths.append(text_width - offset_x)
            text_heights.append(text_height - offset_y)

        width = max(text_widths)
        height = sum(text_heights)

        if font_border_width is not None:
            width += font_border_width * 2
            height += font_border_width * 2 * len(text_lines)

        return width, height
