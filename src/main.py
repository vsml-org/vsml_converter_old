from args import get_args
from converter import convert_video
from xml_parser import parsing_vsml


def main():
    """
    VSMLのメイン関数。受け取ったファイルからVSMLオブジェクトを生成し、それを元に動画を出力する。
    """

    ## コマンド引数を受け取る
    args = get_args()

    ## ファイルのVSMLを解析
    vsml_data = parsing_vsml(args.filename, args.offline)

    ## 解析したデータをもとにffmpegで動画を構築
    convert_video(vsml_data, args.output, args.debug, args.overwrite)


if __name__ == "__main__":
    main()
