# VSS
## 共通プロパティ
全てのタグに適用されるプロパティ

- [x] object-length
    - タイムラインオブジェクトの長さの指定
    - `fit|source|<time[s]>|<frame[f]>|<percent[%]>`
- [x] time-margin
    - タイムラインオブジェクトの外側の時間的余白の長さ指定
    - `(<time[s]>|<frame[f]>|<percent[%]>) (<time[s]>|<frame[f]>|<percent[%]>)?`
- [x] time-margin-start
    - タイムラインオブジェクトの前側の時間的余白の長さ指定
    - `<time[s]>|<frame[f]>|<percent[%]>`
- [x] time-margin-end
    - タイムラインオブジェクトの後ろ側の時間的余白の長さ指定
    - `<time[s]>|<frame[f]>|<percent[%]>`
- [x] time-padding
    - タイムラインオブジェクトの内側の時間的余白の長さ指定
    - `(<time[s]>|<frame[f]>|<percent[%]>) (<time[s]>|<frame[f]>|<percent[%]>)?`
- [x] time-padding-start
    - タイムラインオブジェクトの内前側の時間的余白の長さ指定
    - `<time[s]>|<frame[f]>|<percent[%]>`
- [x] time-padding-end
    - タイムラインオブジェクトの内後ろ側の時間的余白の長さ指定
    - `<time[s]>|<frame[f]>|<percent[%]>`
- [x] order
    - sequence, parallelの指定
    - `sequence|parallel`
- [ ] source-loop
    - 長さを持つソースをループするか否か
    - `true|false`
- [ ] playback-speed
    - 再生速度
    - `<percent[%]>`

## 映像プロパティ
画像や動画、テキストなどのグラフィック関連の操作をするプロパティ

- [x] layer-mode
    - 子要素を1枚のレイヤーに横並びさせるか、各要素を1レイヤーとして重ねるか
    - `single|multi`
- [x] direction
    - 子要素を並べる際の方向
    - `row|column|row-reverse|column-reverse`
- [x] background-color
    - 背景色
- [x] margin
    - 自要素領域の外側の余白
- [x] margin-top
    - 自要素領域の外側の上の余白
- [x] margin-left
    - 自要素領域の外側の左の余白
- [x] margin-bottom
    - 自要素領域の外側の下の余白
- [x] margin-right
    - 自要素領域の外側の右の余白
- [x] padding
    - 自要素領域の内側の余白
- [x] padding-top
    - 自要素領域の内側の上の余白
- [x] padding-left
    - 自要素領域の内側の左の余白
- [x] padding-bottom
    - 自要素領域の内側の下の余白
- [x] padding-right
    - 自要素領域の内側の右の余白
- [x] width
    - グラフィックオブジェクトの横幅
- [x] height
    - グラフィックオブジェクトの縦幅
- [ ] min-width
    - グラフィックオブジェクトの最小の横幅
- [ ] max-width
    - グラフィックオブジェクトの最大の横幅
- [ ] min-height
    - グラフィックオブジェクトの最小の縦幅
- [ ] max-height
    - グラフィックオブジェクトの最大の縦幅
- [ ] opacity
    - 透明度
- [ ] chroma-key
    - クロマキー
- [ ] magnification
    - 拡大率
- [ ] rotate
    - 回転量
- [ ] border
    - 自要素の領域の縁取り指定
- [ ] border-color
    - 自要素の領域の縁取りの色指定
- [ ] border-width
    - 自要素の領域の縁取りの太さ指定
- [ ] border-bottom
    - 自要素の領域の下縁取り指定
- [ ] border-bottom-color
    - 自要素の領域の下縁取りの色指定
- [ ] border-bottom-width
    - 自要素の領域の下縁取りの太さ指定
- [ ] border-left
    - 自要素の領域の左縁取り指定
- [ ] border-left-color
    - 自要素の領域の左縁取りの色指定
- [ ] border-left-width
    - 自要素の領域の左縁取りの太さ指定
- [ ] border-right
    - 自要素の領域の右縁取り指定
- [ ] border-right-color
    - 自要素の領域の右縁取りの色指定
- [ ] border-right-width
    - 自要素の領域の右縁取りの太さ指定
- [ ] border-top
    - 自要素の領域の上縁取り指定
- [ ] border-top-color
    - 自要素の領域の上縁取りの色指定
- [ ] border-top-width
    - 自要素の領域の上縁取りの太さ指定
- [ ] border-radius
    - 自要素領域の境界線の角丸
- [ ] border-bottom-left-radius
    - 自要素領域の左下境界線の角丸
- [ ] border-bottom-right-radius
    - 自要素領域の右下境界線の角丸
- [ ] border-top-left-radius
    - 自要素領域の左上境界線の角丸
- [ ] border-top-right-radius
    - 自要素領域の右上境界線の角丸

## 音声プロパティ
音声関連の操作をするプロパティ

- [x] audio-volume
    - 音量
- [x] audio-system
    - モノラル・ステレオ

## テキストプロパティ
テキストを操作をするプロパティ

- [x] font-color
    - 字幕の色
- [x] font-border
    - 字幕の縁取り情報
- [x] font-border-color
    - 字幕の縁取りの色
- [x] font-border-width
    - 字幕の縁取りの太さ
- [x] font-family
    - 使用フォントの指定
- [x] font-size
    - フォントのサイズ
- [x] font-style
    - Italicの指定
- [x] font-weight
    - Boldの指定
