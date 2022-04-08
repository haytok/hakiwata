---
draft: false
title: "Hugo のテンプレートを修正してみた"
date: 2021-06-11T17:37:01+09:00
tags: ["Hugo"]
pinned: false
ogimage: "img/images/20210611.png"
---

## 概要

- こんにちは！自分の Web サイトは Hugo を用いて運用しています。これまでは、デフォルトの設定で特に大きく変更すること無く使用していました。しかし、表示するコンテンツを追加したいと思い、思い切ってテンプレートに修正を加えていくことにしました。今回は、その際に行った修正などについての記録を残したいと思います。

## 背景と目的

- 記事を新しく追加していくと、`Latest Posts` の記事から、メモ的なお気に入りの記事が埋もれてしまう問題点がありました。現状の設定では `Latest Posts` に表示される記事の数は 5 件です。そこで、トップページに `Pinned Posts` の項目を追加し、メモ的なお気に入りの記事を表示させるようにしました。

## 方法

- 上述の目的を成し遂げるために以下の 3 つのことを行いました。

1. `archetypes/default.md` の `Front Matter Variables` に `pinned: false` を追加します。このパラメータは `Pinned Posts` の箇所に記事を表示させるかのフラグです。
2. `Pinned Posts` に表示させたい記事の `Front Matter Variables` に `pinned: true` を追記します。
3. `themes/manis-hugo-theme/layouts/index.html` を修正します。`pinned: true` の記事をフィルタリングし、 `Pinned Posts` を表示するようなロジックを追加します。

- `3` に関しては `Latest Post` のプログラムと公式のドキュメントの Hugo の文法を参考に実装しました。特に、[Nest where Clauses](https://gohugo.io/functions/where/#nest-where-clauses) が参考になりました。

## 感想

- 実装したい機能から逆算して修正すべきファイルに当たりをつけて、リバースエンジニアリング的に機能を拡張できて楽しかったです。Hugo は Golang の機能を活用して実装されています。Golang や Hugo に詳しいわけではないのですが、公式ドキュメントを読んでいると Hugo の文法も少し知ることができました。こうして、なんとか実現したい機能を調査と検証を繰り返しながら実装できて良かったです。また少し技術力が上がった気がします。

## 参考

- [Front Matter](https://gohugo.io/content-management/front-matter/)
- [Nest where Clauses](https://gohugo.io/functions/where/#nest-where-clauses)
- [hakiwata/issues/3](https://github.com/haytok/hakiwata/issues/3)
