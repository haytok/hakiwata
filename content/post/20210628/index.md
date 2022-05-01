---
draft: false
title: "自作ブログの開発環境を\n Docker で移行した"
date: 2021-06-26T20:39:56Z
tags: ["make", "Docker", "Hugo"]
pinned: false
ogimage: "img/images/20210628.png"
---

## 概要

- こんにちは！前回は、[Hugo で Markdown が上手く parse されない原因を調査してみた](https://haytok.jp/post/20210624/)という記事を書きました。この際、開発環境を Docker で作ることで、 Hugo のバージョンを上げました。そこで今回は、開発環境の移行で行ったことについての記録を残したいと思います。

## 背景と目的

- もともとはホスト OS に Hugo のバイナリをインストールして開発環境を構築していました。しかし、この開発方法だと[前回の記事](https://haytok.jp/post/20210624/)のように Hugo のバイナリのバージョンを上げたいと思った時にすぐにバージョンアップをすることが面倒臭いです。そのため、今回は `make コマンド` と `Docker` を使用して開発の体験を上げ、Hugo のバージョンの変更に対応しやすいように開発環境を作り直しました。

## 方法

- 以下の 3 つの機能を `make コマンド` でまとめることが最終目標でした。

1. Hugo のバージョン管理をしやすくすること
2. 開発用サーバを起動するコマンドを作ること
3. 新規コンテンツを作成するコマンドを作ること

- 今回、実際に実装した `Makefile` は以下のようになりました。`VERSION 変数` で Hugo のバージョン管理をしやすくしています。また、`make server` コマンドで開発用サーバが起動し、`make new D="directory name"` で新規コンテンツのセットアップを行うようにしました。

```bash
VERSION=0.83.1
PORT=1313

OLD_VERSION=0.65.3

$(eval USER_ID := $(shell id -u $(USER)))
$(eval GROUP_ID := $(shell id -g $(USER)))

.PHONY: server
server:
    docker run --rm -it \
        -v $(PWD):/src \
        -p $(PORT):1313 \
        klakegg/hugo:$(VERSION) server

.PHONY: new
new:
    @echo "Directory name is $(D)"

    mkdir -p content/post/$(D)

    docker run --rm -it \
        -v /etc/group:/etc/group:ro \
        -v /etc/passwd:/etc/passwd:ro \
        -v $(PWD):/src \
        -u $(USER_ID):$(GROUP_ID) \
        klakegg/hugo:$(VERSION) new "content/post/$(D)/index.md"
```

- 1 つだけ注意しなければならないことがあります。それは、`make new D="directory name"` コマンドで新しくディレクトリとファイルを作成する際に、コンテナ内のユーザとホストのユーザが同一でなければならないことです。この権限をホスト側に合わせていないと、ホスト側で新規作成した `index.md` を更新することができません。そこで、[dockerでvolumeをマウントしたときのファイルのowner問題](https://qiita.com/yohm/items/047b2e68d008ebb0f001) を参考にホスト側で `index.md` を修正できるようにしました。

- もちろん、`docker exec コマンド` や `VSCode Remote Container` を活用してコンテナ内で `index.md` を編集する方法を選択しても良かったです。しかし、あまり慣れていないのとそれまで作成したファイルの権限を全て変更するのが面倒臭かったので、今回の方法を選択しました。

## 最後に

- `Makefile` を活用することで、開発する際のストレスを減らし、Hugo のバージョンの管理をしやすくすることができて良かったです。`make コマンド` は奥が深いので、今後も活用していきたいと思いました🤞

## 参考

- [klakegg/hugo](https://hub.docker.com/r/klakegg/hugo/)
- [dockerでvolumeをマウントしたときのファイルのowner問題](https://qiita.com/yohm/items/047b2e68d008ebb0f001)
