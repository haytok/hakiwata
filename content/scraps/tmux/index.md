---
draft: false
title: "tmux メモ"
date: 2021-09-19T22:14:46Z
tags: ["tmux"]
pinned: false
---

## 概要

- tmux のコマンドのメモを残す。

## コマンド

- 名前を付けてセッションを開始する。

```bash
tmux new -s <セッション名>
```

- 最後にデタッチしたセッションにアタッチする。

```bash
tmux a
```

- セッション名を指定してアタッチする。

```bash
tmux a -t <セッション名>
```

- セッション名を変更する。

```bash
tmux rename -t <変更前セッション名> <変更後セッション名>
```

- セッションを確認する。

```bash
tmux ls
```

- 上部ペインのサイズを変更する。ただし、以下のコマンドの `:` 以降を入力する。

```bash
Ctrl-b : resize-pane -U <数字>
```

## 参考

- [tmuxの基本的な操作方法のまとめ](tmuxの基本的な操作方法のまとめ)
- [tmuxでconsoleのスクロール(not mouse)を行う方法](https://qiita.com/sutoh/items/41ddd9bdbc9e23746c9d)
- [tmuxでペインレイアウトを変更する](https://qiita.com/tortuepin/items/1acbc7b0e749189a33b9)
- [tmuxを使いこなそう（ウインドウ、ペイン、セッション、アタッチ、デタッチ）](https://qiita.com/shoma2da/items/2e68c1e59938eb0c2f83#%E3%82%BB%E3%83%83%E3%82%B7%E3%83%A7%E3%83%B3%E3%82%92%E4%BD%BF%E3%81%84%E3%81%93%E3%81%AA%E3%81%99)
