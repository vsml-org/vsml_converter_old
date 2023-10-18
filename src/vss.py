from __future__ import annotations
import re
from definition.vss import STYLE_VALUE_PATTERN

SELECTOR_PATTERN = r'(\.|#)?[a-zA-Z0-9_\-]+'
PROPERTY_PATTERN = r'[a-z\-]+'
VALUE_PATTERN = r'[^;]+'
SELECTORS_PATTERN = fr'{SELECTOR_PATTERN}(\s*(,| )\s*{SELECTOR_PATTERN})*'
PROP_VAL_PATTERN = fr'\s*{PROPERTY_PATTERN}\s*:\s*{VALUE_PATTERN}\s*;?\s*'

ONE_VSS_PATTERN = fr'\s*(?P<selectors>{SELECTORS_PATTERN})\s*\{{(?P<properties>({PROP_VAL_PATTERN})+)\}}\s*'

VSS_PATTERN = fr'^({ONE_VSS_PATTERN})*$'

def validate_vss(vss_text: str) -> bool:
    vss_text = re.sub(r'/\*.*?\*/', '', vss_text, flags=re.S)
    vss_pattern = re.compile(VSS_PATTERN, flags=re.S)
    return bool(vss_pattern.fullmatch(vss_text))

def convert_vss_dict(vss_text: str) -> dict[str, dict[str, str]]:
    vss_object = {}

    if not validate_vss(vss_text):
        raise Exception()

    vss_pattern = re.compile(ONE_VSS_PATTERN, flags=re.S)
    for match_text in vss_pattern.finditer(vss_text):

        selectors_text = match_text.group('selectors').strip()
        properties_text = match_text.group('properties').strip()
        properties = {}
        
        for prop_text in properties_text.split(';'):
            prop_text = prop_text.strip()
            if not prop_text:
                continue
            prop, value = [s.strip() for s in prop_text.split(':', 1)]
            properties[prop] = value

        for selector in selectors_text.split(','):
            vss_object[re.sub(r'\s+', ' ', selector.strip())] = properties

    # propertyごとのvalueのvalidate
    for selector, style in vss_object.items():
        for property, value in style.items():
            if re.fullmatch(STYLE_VALUE_PATTERN[property], value, re.IGNORECASE) is None:
                del vss_object[selector][property]

    return vss_object
