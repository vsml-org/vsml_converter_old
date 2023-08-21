from argparse import ArgumentParser, Namespace

def init_parser():
    parser = ArgumentParser(description='command line tool to struct video from xml')
    parser.add_argument(
        'filename',
        metavar='filename',
        type=str,
        help='file name to convert xml',
    )
    parser.add_argument(
        '-o',
        '--output',
        metavar='output_path',
        type=str,
        help='path to output video',
    )
    return parser

def get_args() -> Namespace:
    parser = init_parser()
    return parser.parse_args()
