# VSS

## 共通スタイル

全てのタグに適用されるスタイル

- [ ] **object-length**
    - `cut`
        - ？？？？？
    - `fit`
        - 親要素の長さの最後まで伸ばす。
    - `source`
        - ソースの持つ長さまで伸ばす。動画や音声のデフォルト値はこれ。
    - `<time[s]>`
        - その秒数まで伸ばす。
    - `<flame>`
        - そのフレーム数まで伸ばす。
- [ ] source-loop
- [ ] playback-speed
- [ ] time-margin
- [ ] time-margin-start
- [ ] time-margin-end
- [ ] time-padding
- [ ] time-padding-start
- [ ] time-padding-end

## 映像スタイル

画像や動画、テキストなどのグラフィック関連の操作をするスタイル

- [ ] opacity
- [ ] width
- [ ] min-width
- [ ] max-width
- [ ] height
- [ ] min-height
- [ ] max-height
- [ ] background-color
    - `<color>`
- [ ] object-fit
    - `contain`
        - アス比を維持してwidth-heightからはみ出さないようにリサイズ
    - `cover`
        - アス比を維持してwidth-heightを埋めるようにリサイズ
    - `fill`
        - width-heightにピッタリ合うようにリサイズ
    - `none`
        - width-heightを気にせずセンターに元サイズの画像を置く
    - `scale-down`
        -   min(contain, none)のような感じ。はみだしたらcontain
- [ ] chroma-key
    - `<color> <percentage>`
- [ ] magnification
    - `<percentage>`
- [ ] rotate
    - `<degree>`
- [ ] border
- [ ] border-color
    - `<color>`
- [ ] border-style
- [ ] border-width
- [ ] border-bottom
- [ ] border-bottom-color
    - `<color>`
- [ ] border-bottom-style
- [ ] border-bottom-width
- [ ] border-left
- [ ] border-left-color
    - `<color>`
- [ ] border-left-style
- [ ] border-left-width
- [ ] border-right
- [ ] border-right-color
    - `<color>`
- [ ] border-right-style
- [ ] border-right-width
- [ ] border-top
- [ ] border-top-color
    - `<color>`
- [ ] border-top-style
- [ ] border-top-width
- [ ] top
- [ ] left
- [ ] bottom
- [ ] right
- [ ] flex-direction
- [ ] flex-wrap
- [ ] align-content
- [ ] justify-content
- [ ] align-items
- [ ] margin
- [ ] margin-top
- [ ] margin-left
- [ ] margin-bottom
- [ ] margin-right
- [ ] padding
- [ ] padding-top
- [ ] padding-left
- [ ] padding-bottom
- [ ] padding-right
- [ ] border-radius
- [ ] border-bottom-left-radius
- [ ] border-bottom-right-radius
- [ ] border-top-left-radius
- [ ] border-top-right-radius
- [ ] visibility
    - `visible`
        - 見える
    - `hidden`
        - 隠す
    - `collapse`
        - 存在しなくする
- [ ] box-shadow

## 音声スタイル

音声関連の操作をするスタイル

- [ ] audio-volume

## テキストスタイル

テキストを操作をするスタイル

- [ ] color
    - `<color>`
- [ ] text-border
- [ ] text-border-color
    - `<color>`
- [ ] text-border-width
- [ ] font
- [ ] font-family
- [ ] font-size
- [ ] font-stretch
- [ ] font-style
- [ ] font-weight
- [ ] text-align
- [ ] text-decoration
- [ ] text-decoration-color
    - `<color>`
- [ ] text-decoration-line
- [ ] text-decoration-style
- [ ] text-decoration-thickness
- [ ] text-orientation
- [ ] text-overflow
- [ ] text-shadow
- [ ] line-break
- [ ] line-height
- [ ] letter-spacing
- [ ] white-space
- [ ] word-break
