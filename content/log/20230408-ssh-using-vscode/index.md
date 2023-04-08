---
draft: false
title: "SSH Using VSCode on Windows11"
date: 2023-04-08T13:01:23Z
tags: ["VSCode"]
pinned: false
ogimage: "img/images/20230408-ssh-using-vscode.png"
---

## 概要

手元の Windows11 の VSCode の Remote-SSH を使用して EC2 インスタンスに接続しようとすると `Permission denied (publickey,gssapi-keyex,gssapi-with-mic).` のエラーが出ました。VSCode のエラーメッセージを読んでみると鍵周りの設定に不備があるようなので、直してください。

## 調査方法

まず、Windows11 のコマンドプロンプトで対象の EC2 インスタンスに ssh で接続できるかを確認する。その際に、`-v` を使用して接続して、デバッグメッセージが出力されるようにする。なお、`-v` に関しては下記のマニュアルを参考にして下さい。`-v` の `Verbose` は「言葉数の多い / 冗長な」を意味する。(verbose_name は Django の model のメタフィールド的な個所にもあった気がするけど、ニュアンスは同じ感じです。)

```bash
     -v      Verbose mode.  Causes ssh to print debugging messages about its progress.  This is helpful in debugging connection,
             authentication, and configuration problems.  Multiple -v options increase the verbosity.  The maximum is 3.
```

- [英語「verbose」の意味・読み方・表現 | Weblio英和辞書](https://ejje.weblio.jp/content/verbose)

> 言葉数の多い、多弁の、くどい、冗長な

最終的に、WSL2 側からは EC2 に接続できていたので、その鍵に関連するファイルを Windows 側の `.ssh` 配下のディレクトリにコピーすると正常に接続できた。

ちゃんと読んでないけど、下記の記事にインスパイアされて、イケそうやんとなった。

- [【VS Code】Remote SSHをWindows+WSL2で動かしてて困ったこと - echo("備忘録");](https://makky12.hatenablog.com/entry/2023/02/13/120500)

## 教訓

1. VSCode が吐き出したエラーメッセージを面倒臭がらずちゃんと読む。(サポートエンジニアなら猶更 ...)
2. 情報量を増やせるオプションを使いこなす。今回の場合なら `ssh` コマンドの `-v` オプションを指定して様子を見る。
   1. VSCode の Remote-SSH 由来なのか、それともそもそも ssh できないのかの切り分けを行った。
3. 正常系と異常系の動作を比較して、その差を確認する。
   1. WSL2 から接続できたのに、コマンドプロンプトから接続できない原因を探った。
