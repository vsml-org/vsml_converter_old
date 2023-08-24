from args import get_args
from xml_parser import parsing_vsml
from converter import convert_video

def main():
    """
    VSMLのメイン関数。受け取ったファイルからVSMLオブジェクトを生成し、それを元に動画を出力する。
    """

    ## コマンド引数を受け取る
    args = get_args()

    ## ファイルのVSMLを解析
    vsml_data = parsing_vsml(args.filename)

    ## 解析したデータをもとにffmpegで動画を構築
    convert_video(vsml_data, args.output)

if __name__ == '__main__':
    main()
