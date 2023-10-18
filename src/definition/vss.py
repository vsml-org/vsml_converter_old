from . import regex

PROPERTY_LIST = [
    "object-length", "source-loop", "playback-speed", "time-margin", "time-margin-start", "time-margin-end", 
    "time-padding", "time-padding-start", "time-padding-end", "order", "layer", "opacity", "width", 
    "min-width", "max-width", "height", "min-height", "max-height", "background-color", "object-fit", 
    "chroma-key", "magnification", "rotate", "border", "border-color", "border-style", "border-width", 
    "border-bottom", "border-bottom-color", "border-bottom-style", "border-bottom-width", "border-left", 
    "border-left-color", "border-left-style", "border-left-width", "border-right", "border-right-color", 
    "border-right-style", "border-right-width", "border-top", "border-top-color", "border-top-style", 
    "border-top-width", "position", "display", "top", "left", "bottom", "right", "flex-direction", 
    "flex-wrap", "align-content", "justify-content", "align-items", "margin", "margin-top", "margin-left", 
    "margin-bottom", "margin-right", "padding", "padding-top", "padding-left", "padding-bottom", 
    "padding-right", "border-radius", "border-bottom-left-radius", "border-bottom-right-radius", 
    "border-top-left-radius", "border-top-right-radius", "visibility", "box-shadow", "audio-volume", 
    "audio-system", "font-color", "font-border", "font-border-color", "font-border-width", "font", 
    "font-family", "font-size", "font-stretch", "font-style", "font-weight", "text-align", "text-decoration", 
    "text-decoration-color", "text-decoration-line", "text-decoration-style", "text-decoration-thickness", 
    "text-orientation", "text-overflow", "text-shadow", "line-height", "letter-spacing", "word-break"
]

COLOR_LIST = [
    'aliceblue', 'antiquewhite', 'aqua', 'aquamarine', 'azure', 'beige', 'bisque', 'black',
    'blanchedalmond', 'blue', 'blueviolet', 'brown', 'burlywood', 'cadetblue', 'chartreuse',
    'chocolate', 'coral', 'cornflowerblue', 'cornsilk', 'crimson', 'cyan', 'darkblue', 'darkcyan',
    'darkgoldenrod', 'darkgray', 'darkgreen', 'darkkhaki', 'darkmagenta', 'darkolivegreen',
    'darkorange', 'darkorchid', 'darkred', 'darksalmon', 'darkseagreen', 'darkslateblue',
    'darkslategray', 'darkturquoise', 'darkviolet', 'deeppink', 'deepskyblue', 'dimgray',
    'dodgerblue', 'firebrick', 'floralwhite', 'forestgreen', 'fuchsia', 'gainsboro', 'ghostwhite',
    'gold', 'goldenrod', 'gray', 'green', 'greenyellow', 'honeydew', 'hotpink', 'indianred',
    'indigo', 'ivory', 'khaki', 'lavender', 'lavenderblush', 'lawngreen', 'lemonchiffon',
    'lightblue', 'lightcoral', 'lightcyan', 'lightgoldenrodyellow', 'lightgreen', 'lightgrey',
    'lightpink', 'lightsalmon', 'lightseagreen', 'lightskyblue', 'lightslategray', 'lightsteelblue',
    'lightyellow', 'lime', 'limegreen', 'linen', 'magenta', 'maroon', 'mediumaquamarine',
    'mediumblue', 'mediumorchid', 'mediumpurple', 'mediumseagreen', 'mediumslateblue',
    'mediumspringgreen', 'mediumturquoise', 'mediumvioletred', 'midnightblue', 'mintcream',
    'mistyrose', 'moccasin', 'navajowhite', 'navy', 'oldlace', 'olive', 'olivedrab', 'orange',
    'orangered', 'orchid', 'palegoldenrod', 'palegreen', 'paleturquoise', 'palevioletred',
    'papayawhip', 'peachpuff', 'peru', 'pink', 'plum', 'powderblue', 'purple', 'red', 'rosybrown',
    'royalblue', 'saddlebrown', 'salmon', 'sandybrown', 'seagreen', 'seashell', 'sienna',
    'silver', 'skyblue', 'slateblue', 'slategray', 'snow', 'springgreen', 'steelblue', 'tan',
    'teal', 'thistle', 'tomato', 'turquoise', 'violet', 'wheat', 'white', 'whitesmoke',
    'yellow', 'yellowgreen'
]

SECOND_PATTERN = f"{regex.REAL_NUMBER_PATTERN}s"
FRAME_PATTERN = f"{regex.REAL_NUMBER_PATTERN}f"

PIXEL_PATTERN = f"{regex.REAL_NUMBER_PATTERN}px"
RESOLUTION_WIDTH_PATTERN = f"{regex.REAL_NUMBER_PATTERN}rw"
RESOLUTION_HEIGHT_PATTERN = f"{regex.REAL_NUMBER_PATTERN}rh"
RESOLUTION_MIN_PATTERN = f"{regex.REAL_NUMBER_PATTERN}rmin"
RESOLUTION_MAX_PATTERN = f"{regex.REAL_NUMBER_PATTERN}rmax"

PERCENT_PATTERN = f"{regex.REAL_NUMBER_PATTERN}%"

TIME_PATTERN = f"({SECOND_PATTERN}|{FRAME_PATTERN}|{PERCENT_PATTERN})"
GRAPHIC_PATTERN = f"({PIXEL_PATTERN}|{RESOLUTION_WIDTH_PATTERN}|{RESOLUTION_HEIGHT_PATTERN}|{RESOLUTION_MIN_PATTERN}|{RESOLUTION_MAX_PATTERN}|{PERCENT_PATTERN})"

HEX_COLOR_PATTERN = f"#({regex.HEX_PATTERN}{{3}}|{regex.HEX_PATTERN}{{4}}|{regex.HEX_PATTERN}{{6}}|{regex.HEX_PATTERN}{{8}})"
RGB_COLOR_PATTERN = fr"rgb\(\s*{regex.REAL_NUMBER_PATTERN}\s*,\s*{regex.REAL_NUMBER_PATTERN}\s*,\s*{regex.REAL_NUMBER_PATTERN}\s*\)"
RGBA_COLOR_PATTERN = fr"rgba\(\s*{regex.REAL_NUMBER_PATTERN}\s*,\s*{regex.REAL_NUMBER_PATTERN}\s*,\s*{regex.REAL_NUMBER_PATTERN}\s*,\s*{regex.REAL_NUMBER_PATTERN}\s*\)"
PURE_COLOR_PATTERN = '|'.join(COLOR_LIST)
COLOR_PATTERN = f"({PURE_COLOR_PATTERN}|{HEX_COLOR_PATTERN}|{RGB_COLOR_PATTERN}|{RGBA_COLOR_PATTERN})"

STYLE_VALUE_PATTERN = {
    "object-length": f"(fit|source|{TIME_PATTERN})",
    "source-loop": "(true|false)",
    "playback-speed": f"{PERCENT_PATTERN}",
    "time-margin": fr"{TIME_PATTERN}(\s+{TIME_PATTERN})?",
    "time-margin-start": TIME_PATTERN,
    "time-margin-end": TIME_PATTERN,
    "time-padding": fr"{TIME_PATTERN}(\s+{TIME_PATTERN})?",
    "time-padding-start": TIME_PATTERN,
    "time-padding-end": TIME_PATTERN,
    "order": "(sequence|parallel)",
    "layer": "(single|multi)",
    "opacity": f"({regex.REAL_NUMBER_PATTERN}|{PERCENT_PATTERN})",
    "width": GRAPHIC_PATTERN,
    "min-width": "",
    "max-width": "",
    "height": GRAPHIC_PATTERN,
    "min-height": "",
    "max-height": "",
    "background-color": COLOR_PATTERN,
    "object-fit": "",
    "chroma-key": "",
    "magnification": "",
    "rotate": "",
    "border": "",
    "border-color": "",
    "border-style": "",
    "border-width": "",
    "border-bottom": "",
    "border-bottom-color": "",
    "border-bottom-style": "",
    "border-bottom-width": "",
    "border-left": "",
    "border-left-color": "",
    "border-left-style": "",
    "border-left-width": "",
    "border-right": "",
    "border-right-color": "",
    "border-right-style": "",
    "border-right-width": "",
    "border-top": "",
    "border-top-color": "",
    "border-top-style": "",
    "border-top-width": "",
    "position": "",
    "display": "",
    "top": "",
    "left": "",
    "bottom": "",
    "right": "",
    "flex-direction": "",
    "flex-wrap": "",
    "align-content": "",
    "justify-content": "",
    "align-items": "",
    "margin": fr"{GRAPHIC_PATTERN}(\s+{GRAPHIC_PATTERN}){{0,3}}",
    "margin-top": GRAPHIC_PATTERN,
    "margin-left": GRAPHIC_PATTERN,
    "margin-bottom": GRAPHIC_PATTERN,
    "margin-right": GRAPHIC_PATTERN,
    "padding": fr"{GRAPHIC_PATTERN}(\s+{GRAPHIC_PATTERN}){{0,3}}",
    "padding-top": GRAPHIC_PATTERN,
    "padding-left": GRAPHIC_PATTERN,
    "padding-bottom": GRAPHIC_PATTERN,
    "padding-right": GRAPHIC_PATTERN,
    "border-radius": "",
    "border-bottom-left-radius": "",
    "border-bottom-right-radius": "",
    "border-top-left-radius": "",
    "border-top-right-radius": "",
    "visibility": "",
    "box-shadow": "",
    "audio-volume": PERCENT_PATTERN,
    "audio-system": "(monaural|stereo)",
    "font-color": COLOR_PATTERN,
    "font-border": fr"({COLOR_PATTERN}\s+{PIXEL_PATTERN}|{PIXEL_PATTERN}\s+{COLOR_PATTERN})",
    "font-border-color": COLOR_PATTERN,
    "font-border-width": PIXEL_PATTERN,
    "font": "",
    "font-family": ".+",
    "font-size": GRAPHIC_PATTERN,
    "font-stretch": "",
    "font-style": "(normal|italic)",
    "font-weight": "(normal|bold)",
    "text-align": "",
    "text-decoration": "",
    "text-decoration-color": "",
    "text-decoration-line": "",
    "text-decoration-style": "",
    "text-decoration-thickness": "",
    "text-orientation": "",
    "text-overflow": "",
    "text-shadow": "",
    "line-height": "",
    "letter-spacing": "",
    "word-break": ""
}