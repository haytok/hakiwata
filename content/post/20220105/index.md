---
draft: true
title: "Python 標準ライブラリ textwrap \nのソースコードを読んでみる"
date: 2022-01-04T19:41:46Z
tags: ["Python"]
pinned: false
ogimage: "img/images/20220105.png"
---

## 概要

- こんにちは！先日、[ブログ](https://haytok.jp/post/20211124/) を書いた際に、OGP 画像のタイトルのレイアウトが崩れていることに気が付きました。この際、OGP 画像のタイトルを加工する際に使っている Python の標準ライブラリの [textwrap](https://docs.python.org/ja/3/library/textwrap.html) の内部の実装が気になりました。そこで、今回は [textwrap](https://docs.python.org/ja/3/library/textwrap.html) のソースコードを読んで内部の実装を簡単に紐解いていきたいと思います。

## 背景 ([textwrap](https://docs.python.org/ja/3/library/textwrap.html) の内部の実装が気になったキッカケ)

- hoge

## 調査方針 (目的)

1. `textwrap.wrap()` の `width` と改行の関係性を明らかにする
  1. ドキュメントを確認する。
  2. 標準ライブラリのソースコードから調査する
2. 1 の調査を元にライブラリを拡張するかを検討する
  1. ライブラリを拡張している人の記事 ([Pythonのtextwrap.wrap()が日本語で崩れる問題](https://www.freia.jp/taka/blog/python-textwrap-with-japanese/index.html)) を参考にして、拡張する方法を検討する

## 調査

- hoge

## 結果

- hoge

## 結論

- hoge

## 参考

- [textwrap --- テキストの折り返しと詰め込み](https://docs.python.org/ja/3/library/textwrap.html)
- [textwrap.py](https://github.com/python/cpython/blob/3.9/Lib/textwrap.py)
- [Pythonのtextwrap.wrap()が日本語で崩れる問題](https://www.freia.jp/taka/blog/python-textwrap-with-japanese/index.html)
