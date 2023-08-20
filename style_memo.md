# Video Styling Sheet

## 採用属性

### フォント関連
- font
  - font-family
  - font-size
  - font-stretch
  - font-style
  - font-weight

### テキスト関連
- text-align
- text-decoration
  - text-decoration-color
  - text-decoration-line
  - text-decoration-style
  - text-decoration-thickness
- text-orientation
- text-overflow
- text-shadow
- line-break
- line-height
- letter-spacing
- white-space
 -word-break

### 図形的余白関連
- margin
  - margin-top
  - margin-left
  - margin-bottom
  - margin-right
- padding
  - padding-top
  - padding-left
  - padding-bottom
  - padding-right

### absolute/fixed関連
- top
- left
- bottom
- right

### flex関連
- flex-direction
- flex-wrap
- align-content
- justify-content
- align-items

### 色関連
- color
- background-color

### サイズ関連
- width
  - min-width
  - max-width
- height
  - min-height
  - max-height

### overflow関連
**スクロールはなし。はみ出しを切るかどうかとかで使う想定**
- overflow
  - overflow-x
  - overflow-y

### border関連
- border
  - border-color
  - border-style
  - border-width
  - border-bottom
    - border-bottom-color
    - border-bottom-style
    - border-bottom-width
  - border-left
    - border-left-color
    - border-left-style
    - border-left-width
  - border-right
    - border-right-color
    - border-right-style
    - border-right-width
  - border-top
    - border-top-color
    - border-top-style
    - border-top-width
  - border-radius
    - border-bottom-left-radius
    - border-bottom-right-radius
    - border-top-left-radius
    - border-top-right-radius

### visibility
- visibility

### display
- display

### position
- position

### opacity
- opacity

### object-fit
- object-fit

### rotate
- rotate

### z-index
- z-index

### 拡大率
- magnification

### 時間的余白関連
- time-margin
  - time-margin-start
  - time-margin-end
- time-padding
  - time-padding-start
  - time-padding-end

### タイムラインオブジェクトの並べ方
- order

### テキストの縁取り
- text-border

### オブジェクトの長さ
- object-length
#### 取れる要素
- cut
  - ？？？？？
- fit
  - 親要素の長さの最後まで伸ばす。
- source
  - ソースの持つ長さまで伸ばす。動画や音声のデフォルト値はこれ。
- \<time[s]>
  - その秒数まで伸ばす。
- \<flame>
  - そのフレーム数まで伸ばす。

### 動画や音声のループを許可するかどうか
- source-loop

### 音量
- audio-volume

### 再生速度
- playback-speed

### クロマキー
- chroma-key
#### 取れる要素
- \<color> \<percentage>
  - 透過する色と、その周辺透過率の指定。
