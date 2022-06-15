---
draft: true
title: "Golang"
date: 2022-01-15T16:20:48Z
tags: ["Golang"]
pinned: false
ogimage: "img/images/golang.png"
---

## 概要

- Golang 関連のログを残していきたいと思います。

## ログ

### `go mod` コマンドが実行できない

- `go mod` コマンドを実行することができない。

```bash
> go mod init haytok
go: unknown subcommand "mod"
Run 'go help' for usage.
```

- 普通に考えておかしいので、インストールされている Golang のバージョンを確認する。

```bash
> go version
go version go1.10.4 linux/amd64
```

- 大昔にインストールした Golang のバージョンが低すぎるのでそれが悪さをしていそう。そのため、インストールされたバイナリのバージョンをアップデートしたい。どこのパスにバイナリがインストールされているかを以下のコマンドで確認する。

```bash
> which go
/home/h-kiwata/.goenv/shims/go
```

- パット見た感じ、[goenv](https://github.com/syndbg/goenv) を使っているようなので、[goenv](https://github.com/syndbg/goenv) で管理されている最新のバージョンを確認する。

```bash
> goenv install --list
...
  1.17.5
  1.17.6
  1.18beta1
```

- できるだけ最新のバージョンをインストールしようと思い、`goenv install` コマンドで `1.17.6` のバイナリをインストールする。

```bash
> goenv install 1.17.6
Downloading go1.17.6.linux-amd64.tar.gz...
-> https://go.dev/dl/go1.17.6.linux-amd64.tar.gz
###################################################################################################################################################################### 100.0%###################################################################################################################################################################### 100.0%
Installing Go Linux 64bit 1.17.6...
Installed Go Linux 64bit 1.17.6 to /home/h-kiwata/.goenv/versions/1.17.6
```

- グローバル環境で特定のバージョンを使用したいなら、[goenv global](https://github.com/syndbg/goenv/blob/d607f7155baae4bb127d73676a4b4b28d9c8f69b/COMMANDS.md#goenv-global) コマンドを使って `~/.goenv/versions` 配下の特定のバージョンを反映させろとドキュメントに書かれている。したがって、以下のコマンドを実行する。

```bash
> goenv global 1.17.6
```

- そうすると、グローバル環境で [goenv](https://github.com/syndbg/goenv) を用いて管理されている Golang のバージョンが更新されたことが `go version` から確認できる。

```bash
> go version
go version go1.17.6 linux/amd64
```

- ついでに、[Uninstalling Go Versions](https://github.com/syndbg/goenv/blob/master/INSTALL.md#uninstalling-go-versions) を参考に `goenv uninstall 1.14.6` を実行して不要なバージョンを削除しておいた。
