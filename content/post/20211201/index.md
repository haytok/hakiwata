---
draft: true
title: "OGP のタイトルを作成するライブラリの比較と検討"
date: 2021-12-01T09:27:59Z
tags: ["Python"]
favorite: false
ogimage: "img/images/20211201.png"
---

## 概要

- この自作ブログの OGP は Python と GitHub Actions を使って自動生成するようになっています。ブログのタイトルを使用して良い感じに調整することで、OGP の画像のタイトルをつけます。しかし、[先日投稿したブログ](https://hakiwata.jp/post/20211124/)の OGP の画像のタイトルのレイアウトが崩れていました。そこで、今回は OGP の画像のタイトルをつけるための実装方針を再度考え直します。そして、実装に必要なライブラリの比較と検討を行いたいと思います。

## 事の発端 (原因) とライブラリの比較と検討を行おうと思った背景

- [CyberAgent のコンテナ技術に関する勉強会に参加してきた](https://hakiwata.jp/post/20211124/) の OGP の画像が意図した形になっていなかった。以下の上の画像が実際に生成されていた OPG の画像で、下の画像が生成されて欲しかった画像です。

{{<photo src="fig_1.png" title="図 1 タイトルのレイアウトがズレてしまった OGP 画像" width="80%" height="80%" >}}
{{<photo src="fig_2.png" title="図 2 タイトルのレイアウトが納得行く形の OGP 画像" width="80%" height="80%" >}}

- そもそも、現時点での OGP の画像を生成するためのロジックについて説明したいと思います。
- [textwrap](https://docs.python.org/ja/3/library/textwrap.html) と Hugo のフロントマターに改行用のフラグ (`\n`) を追加するのハイブリッド。

- しかし、この実装で `width=30` を指定して、`textwrap.wrap()` を用いると、`CyberAgent のコンテナ技術に関する勉強会に参加してきた` が変な箇所で改行される。
- [google/budoux](https://github.com/google/budoux) と言うライブラリを [Twitter](https://twitter.com/tushuhei/status/1461184410473033742?s=20) で知って、このブログに応用できるのではないかと思い、以前から試したいと思っていた。

## 実装の方針の比較

- 改めて OGP の画像にタイトルを付けるための実装方法を以下にまとめます。現時点での実装は、自動で行う方法の 1 と手動で行う方法の 1 のハイブリッドな実装となっています。

- 自動で行う方法
  1. [textwrap](https://github.com/python/cpython/blob/3.9/Lib/textwrap.py) を活用して雑に改行させる
  2. [textwrap](https://github.com/python/cpython/blob/3.9/Lib/textwrap.py) を拡張して改行させる
  3. [google/budoux](https://github.com/google/budoux) を活用して改行させる
- 手動で行う方法
  1. Hugo のフロントマターのタイトルに改行させたい箇所に `\n` を差し込み、Python の OGP を作成するスクリプトで改行させる

## 実装の方針の検討

- 自動で行う方法の 1 
  - よくよく考えると、必要ない。2 行以上になると日本語の文脈的に意味のある箇所で改行させる必要がある。そのため、`textwrap.wrap()` のデフォルトのアルゴリズムでは今回のように上手くいかないケースがどうしても出てきてしまう。
- 自動で行う方法の 2
  - デフォルトのアルゴリズムを書き換えたり拡張しても、結局自然言語処理をしないと意味のある箇所で改行できない。
- 自動で行う方法の 3
  - 意味のある単位でタイトルを分割できるが、分割させた単位でどう分けて改行させたいかに好みが分かれる。そのため、自動化は難しい。
- 手動で行う方法の 1 
  - 手動でやるロジックはすでに実装済みなので、タイトルがどうしても長くなる場合には、`\n` を差し込むのを忘れないようにして、運用でカバーする。

## 結論

- 手動で行う方法で OGP の画像のタイトルを生成するような実装に落ち着きました。


## 最後に

- [textwrap](https://github.com/python/cpython/blob/3.9/Lib/textwrap.py) の実装のソースコードレベルでの確認と拡張は別の記事で取り扱います。また、[google/budoux](https://github.com/google/budoux) を検証した内容に関しても、別の記事で取り扱いたいと思います。

----

## 調査方針

1. `textwrap.wrap()` の `width` と改行の関係性を標準ライブラリのソースコードから調査する
2. 1 の調査を元にライブラリを拡張するかを検討する
3. [google/budoux](https://github.com/google/budoux) を試してみて、使えるかを検討する
4. 1 ~ 3 を踏まえて OGP のタイトルを作成するためのライブラリを検討する
---
5. OGP の画像を手軽にデバッグするために、`main.py` をリファクタリングする

## 参考

- [textwrap](https://github.com/python/cpython/blob/3.9/Lib/textwrap.py)
- [google/budoux](https://github.com/google/budoux)
