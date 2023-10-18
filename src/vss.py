from __future__ import annotations

import re

from definition.vss import (
    STYLE_VALUE_PATTERN,
)

SELECTOR_PATTERN = r"(\.|#)?[a-zA-Z0-9_\-]+"
PROPERTY_PATTERN = r"[a-z\-]+"
VALUE_PATTERN = r"[^;]+"
SELECTORS_PATTERN = r"{0}(\s*(,| )\s*{0})*".format(SELECTOR_PATTERN)
PROP_VAL_PATTERN = r"\s*{}\s*:\s*{}\s*;?\s*".format(
    PROPERTY_PATTERN, VALUE_PATTERN
)

ONE_VSS_PATTERN = (
    r"\s*(?P<selectors>{})\s*\{{(?P<properties>({})+)\}}\s*".format(
        SELECTORS_PATTERN, PROP_VAL_PATTERN
    )
)

VSS_PATTERN = r"^({})*$".format(ONE_VSS_PATTERN)


def validate_vss(
    vss_text: str,
) -> bool:
    vss_text = re.sub(
        r"/\*.*?\*/",
        "",
        vss_text,
        flags=re.S,
    )
    vss_pattern = re.compile(VSS_PATTERN, flags=re.S)
    return bool(vss_pattern.fullmatch(vss_text))


def convert_vss_dict(
    vss_text: str,
) -> dict[str, dict[str, str]]:
    vss_object = {}

    if not validate_vss(vss_text):
        raise Exception()

    vss_pattern = re.compile(ONE_VSS_PATTERN, flags=re.S)
    for match_text in vss_pattern.finditer(vss_text):
        selectors_text = match_text.group("selectors").strip()
        properties_text = match_text.group("properties").strip()
        properties = {}

        for prop_text in properties_text.split(";"):
            prop_text = prop_text.strip()
            if not prop_text:
                continue
            prop, value = [s.strip() for s in prop_text.split(":", 1)]
            properties[prop] = value

        for selector in selectors_text.split(","):
            vss_object[
                re.sub(
                    r"\s+",
                    " ",
                    selector.strip(),
                )
            ] = properties

    # propertyごとのvalueのvalidate
    for (
        selector,
        style,
    ) in vss_object.items():
        copy_style = style.copy()
        for (
            property,
            value,
        ) in style.items():
            if (
                re.fullmatch(
                    STYLE_VALUE_PATTERN.get(property, ""),
                    value,
                    re.IGNORECASE,
                )
                is None
            ):
                del copy_style[property]
        vss_object[selector] = copy_style

    return vss_object
