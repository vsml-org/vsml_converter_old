from os.path import dirname
from lxml.etree import fromstring, XML, XMLSchema, XMLParser
from vsml import VSML

CONFIG_FILE = dirname(dirname(__file__)) + '/config/vsml.xsd'

def parsing_vsml(filename: str) -> VSML:
    with open(CONFIG_FILE, 'r') as f:
        next(f)
        xsd_str = f.read()
    schema_root = XML(xsd_str, None)
    schema = XMLSchema(schema_root)
    parser = XMLParser(schema = schema, remove_comments=True, remove_blank_text=True)

    with open(filename, 'r') as f:
        next(f)
        vsml_str = f.read()
    vsml_root = fromstring(vsml_str, parser)

    vsml_dir = dirname(filename) + '/'

    return VSML(vsml_root, vsml_dir)
