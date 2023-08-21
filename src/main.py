from args import get_args
from perser import parsing_vsml
from converter import convert_video
import os

def main():
    ## コマンド引数を受け取る
    args = get_args()

    ## ファイルのVSMLを解析
    vsml_data = parsing_vsml(args.filename)

    ## 解析したデータをもとにffmpegで動画を構築
    convert_video(vsml_data, args.output)

if __name__ == '__main__':
    main()
