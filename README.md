VSML
====

HTML/CSSの記法で動画制作できる言語 VSMLを受け取り動画へ変換するエンコーダ

## Description
HTML/CSSの記法で動画制作できる言語 VSMLを受け取り動画へ変換するエンコーダ。
バックエンドにはFFmpeg v4を使用。このプログラム自体はFFmpegを呼び出すラッパープログラムとなっているので、[FFmpeg公式](https://ffmpeg.org/download.html)からFFmpegをダウンロードする必要がある。

## Demo
実際の挙動は[こちら](./syntax.md#サンプル)

## VS.
[Remotion](https://www.remotion.dev/)
類似プロダクトとしてReact.jsベースの動画編集ライブラリRemotionが挙げられる。
React.jsをベースとしているためCSSを流用して動画編集ができるが，VSMLは動画制作を目的とした言語として設計しているためより動画制作向きなプロパティを使用して動画制作することができる。

## Requirement
- Python 3.10
- FFmpeg v4

## Usage
[Github Releases](https://github.com/PigeonsHouse/VSML/releases)から自分のOSに合ったバイナリを入手する。
また、FFmpeg公式から自分のOSに合ったファイルをインストールする。
記述したVSMLファイルのパスを実行引数に渡すと動画への変換が始まる。

`./main example.vsml`

### option
| option | effect |
|-|-|
| `-o`, `--output` | 出力する動画のファイルパスの指定 |
| `-f`, `--frame` | 出力するプレビュー画像のフレーム数の指定 |
| `--overwrite` | 動画の上書き確認をスキップ |

## Install
```
$ pip install --upgrade pipenv
$ pipenv install
```

```
$ python src/main.py
```

## Licence

[MIT](https://github.com/tcnksm/tool/blob/master/LICENCE)

## Author

[PigeonsHouse](https://github.com/PigeonsHouse)
