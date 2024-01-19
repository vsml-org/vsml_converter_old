import json
from argparse import Action, ArgumentParser, Namespace
from collections.abc import Sequence

from style.utils import get_font_list


class FontFamilyAction(Action):
    def __init__(
        self,
        option_strings: Sequence[str],
        dest: str,
        default: str | None = None,
        help: str | None = None,
    ) -> None:
        super().__init__(
            option_strings=option_strings,
            dest=dest,
            default=default,
            nargs=0,
            help=help,
        )

    def __call__(
        self,
        parser: ArgumentParser,
        namespace,
        values,
        option_string,
    ) -> None:
        print(json.dumps(get_font_list(), indent=2))
        parser.exit()


def init_parser():
    parser = ArgumentParser(
        description="command line tool to struct video from xml"
    )
    parser.add_argument(
        "filename",
        metavar="filename",
        type=str,
        help="file name to convert xml",
    )
    parser.add_argument(
        "-o",
        "--output",
        metavar="output_path",
        type=str,
        help="path to output video",
    )
    parser.add_argument(
        "-f",
        "--frame",
        metavar="preview_frame",
        type=int,
        help="frame for preview",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="debug mode",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="allow overwrite output file",
    )
    parser.add_argument(
        "--offline",
        action="store_true",
        help="offline mode",
    )
    parser.add_argument(
        "--font-family-list",
        action=FontFamilyAction,
        help="get font family list",
    )
    return parser


def get_args() -> Namespace:
    parser = init_parser()
    return parser.parse_args()
