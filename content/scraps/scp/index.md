---
draft: false
title: "scp メモ"
date: 2021-10-20T09:20:23Z
tags: ["scp"]
pinned: false
---

## 概要

- scp コマンドのメモを残す。

## コマンド

- `リモート`から`ローカル`にコピーする。

```bash
scp <ユーザ名>@<リモートの IP>:<リモートのファイルのパス> <保存したいローカルのパス>
```

- 例 (`IdentityFile` のオプションを scp の次に書かないと認証エラーになる。)

```bash
scp -i ~/.ssh/hoge.pem hoger@0.0.0.0:/home/hoge.md .
```

- `ローカル`から`リモート`にコピーする。

```bash
scp <転送ファイルしたいファイルのパス> <ユーザ名>@<リモートの IP>:<リモートの転送先のパス>
```

- 例

```bash
scp -i ~/.ssh/hoge.pem hoge.md hoge@0.0.0.0:/home
```

- ポート番号を指定する時は、`-P` オプション (大文字) を使用する。

## 参考

- [scpコマンドでサーバー上のファイルorディレクトリをローカルに落としてく](https://qiita.com/katsukii/items/225cd3de6d3d06a9abcb)
- [scpコマンドで、ポートとホスト、ディレクトリを指定してファイル送信する](https://qiita.com/2ko2ko/items/fe3bd0d37d04d21344db)
