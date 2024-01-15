import json

from args import get_args
from converter import convert_image_from_frame, convert_video
from xml_parser import parsing_vsml


def main():
    """
    VSMLのメイン関数。受け取ったファイルからVSMLオブジェクトを生成し、それを元に動画を出力する。
    """

    # コマンド引数を受け取る
    args = get_args()

    # ファイルのVSMLを解析
    vsml_data = parsing_vsml(args.filename, args.offline)

    if args.debug:
        content_str = (
            str(vsml_data.content)
            .replace("'", '"')
            .replace("True", "true")
            .replace("False", "false")
            .replace("None", "null")
        )
        content_str = json.dumps(
            (json.loads(content_str)), indent=2, ensure_ascii=False
        )
        with open("./debug.json", "w") as f:
            f.write(content_str)

    if args.frame is None:
        # 解析したデータをもとにffmpegで動画を構築
        convert_video(
            vsml_data,
            args.output,
            args.debug,
            args.overwrite,
        )
    else:
        convert_image_from_frame(
            vsml_data,
            args.frame,
            args.output,
        )


if __name__ == "__main__":
    main()
