# VSML
## XMLの記法
記法はHTMLと類似しています。XMLの一種となっています。
以下の `vid` のように、単一のタグとして記述したり、 `txt` のように開始タグ、終了タグをわけて記述したりします。
`vid` の `src` のようなタグの追加情報を記述する書き方をアトリビュートと言います。
また、 `cont` のように、開始タグと終了タグで記述した場合、間に別の要素やテキストを記述できます。その際、間に記述するテキストはインデント上げすることを推奨します。
```xml
<cont>
  <vid src="" />
  <txt></txt>
</cont>
```

## 全体
```xml
<?xml version="1.0" encoding="UTF-8"?>
<vsml xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://vsml.pigeons.house/config/vsml.xsd">
...
</vsml>
```
基本的に上記のタグの間( `...` の箇所)に動画の情報を書いていきます。上記の詳細な意味は理解しなくても問題ありません。
`vsml` タグの中には、 `meta`, `cont` のタグを含めることが出来ます。 `meta` タグの挿入は任意ですが、 `cont` タグは必ず含めるようにしてください。( `meta` タグがあれば `meta` タグの下の位置に)

**↓ これは `cont` と `meta` が逆で動かない例**

```xml
<vsml>
  <cont>
  </cont>
  <meta>
  </meta>
</vsml>
```

## スタイル指定
`meta` タグの中には、 `style` タグを含めることが出来ます。 `style` タグで挟まれた範囲にVSSの記法で動画のスタイルを指定できます。VSSの記法は下で記述するので省略します。
```xml
<style>
  aud {
    audio-volume: 300%;
  }
</style>
```

また、 `style` タグは以下のように `src` アトリビュートでVSSファイルのパスを指定できます。VSMLファイルからの相対パス、もしくは絶対パスで指定できます。
```xml
<style src="./" />
```

## 動画の要素
`cont` タグには、`resolution`, `fps` の2つのアトリビュートが必須です。
`resolution` には `{width}x{height}` と、幅の数値, 'x'(小文字のX), 高さの数値を並べた文字列を指定します。
`fps` には 指定したいfpsの整数値を文字列にして指定します。
記述の仕方は以下の通りです。以下は幅1920px、高さ1080px、60fpsの動画を作成する際の記述例です。
```xml
<cont resolution="1920x1080" fps="60">
</cont>
```

`cont` タグの中には、以下のタグを含めることが出来ます。

**source系**
|タグ名|名前の意味|説明|
|--|--|--|
|vid|video|映像を表示します。 `src` アトリビュートで動画ファイルを相対パス、絶対パスで指定できます。時間的長さは映像の再生時間と同じになります。|
|aud|audio|音声を表示します。 `src` アトリビュートで動画ファイルを相対パス、絶対パスで指定できます。時間的長さは音声の再生時間と同じになります。|
|img|image|画像を表示します。 `src` アトリビュートで動画ファイルを相対パス、絶対パスで指定できます。時間的長さは無限になります。|
|txt|text|タグで挟まれた範囲に書いたテキストを字幕として表示します。改行する場合は `br` タグが使用できます。時間的長さは無限になります。|

**wrap系**
|タグ名|名前の意味|説明|
|--|--|--|
|seq|sequence-wrap|子要素に持つsource系、wrap系の要素を順番に再生します。子要素は左上揃えで再生されます。時間的長さは子要素の時間的長さの総和になります。|
|prl|parallel-wrap|子要素に持つsource系、wrap系の要素を並列に再生します。子要素は左上揃えで重ねて再生されます。時間的長さは、子要素の有限な時間的長さの最大値になります。子要素が全て時間的長さが無限である場合は無限になります。|
|rect|rectangle|seqの仕様をベースに、 `color` アトリビュートで背景色を指定できます。|
|layer|single-layer|prlの仕様をベースに、子要素は、上揃えで右向きに並べて再生されます。|

また、 `cont` タグは、 `seq` タグと同じく、子要素を順番に再生します。

`cont` を含む `cont` 以下のタグは全て、 `id`, `class`, `style` というアトリビュートを持てます。
`id`, `class` は、後述のVSSでスタイルを当てる対象として名前をつけることが出来ます。
(`id` に付ける名前と同一の名前の `id` は、VSMLファイル内で登場してはいけないのですが、現状の仕様として、制限をかけていないため、この2つのアトリビュートは同じ挙動を取ります。)
`style` は、アトリビュートの値にスタイルのプロパティと値を指定すると、そのタグ単体にそのスタイルが当てられます。

具体的な例は添付されている `.vsml` ファイルを確認ください。

## サンプル
### txt
<img src="https://hackmd.io/_uploads/rJUE_CqYp.png" alt="image" />
<br/>
<iframe src="https://drive.google.com/file/d/1uhtgLBO60V6WFQQ4BAMM8EGLXEI_Dkm-/preview" width="400" height="225" allow="autoplay"></iframe>

### img
<img src="https://hackmd.io/_uploads/SkJU_0cFa.png" alt="image" />
<br/>
<iframe src="https://drive.google.com/file/d/16uUWTOhTkzHVTvdGGOzx3b8oZ1nQ4W7G/preview" width="400" height="225" allow="autoplay"></iframe>

### aud
<img src="https://hackmd.io/_uploads/ry3zn05KT.png" alt="image" />
<br/>
<iframe src="https://drive.google.com/file/d/1l4QPf8aqOZ5Qcg-NEE_Jwku00QfNS53d/preview" width="400" height="225" allow="autoplay"></iframe>

### seq
<img src="https://hackmd.io/_uploads/SyF2BToKp.png" alt="image" />
<br/>
<iframe src="https://drive.google.com/file/d/1q14z4RpMb0aiD_M2XtnGVs-rBhixlNeW/preview" width="400" height="225" allow="autoplay"></iframe>

### prl
<img src="https://hackmd.io/_uploads/S1NHRTcYa.png" alt="image" />
<br/>
<iframe src="https://drive.google.com/file/d/1Y3tZEQt83-cnP_5jy7_vqT_IcZnTMW_x/preview" width="400" height="225" allow="autoplay"></iframe>
<br/>
<img src="https://hackmd.io/_uploads/Hkd2EasYT.png" alt="image" />
<br/>
<iframe src="https://drive.google.com/file/d/1yty7HHaHej2QIRqYEokcZYxSKHGii-oG/preview" width="400" height="225" allow="autoplay"></iframe>

### layer
<img src="https://hackmd.io/_uploads/Hy9UlCqY6.png" alt="image" />
<br/>
<iframe src="https://drive.google.com/file/d/1Cok2iHMy_Ul2miEpL1WdETT8iaq4rYwm/preview" width="400" height="225" allow="autoplay"></iframe>
