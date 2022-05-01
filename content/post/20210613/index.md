---
draft: false
title: ".gitconfig を使って untracked files \nのみを退避させる"
date: 2021-06-13T06:13:26+09:00
tags: ["git"]
pinned: false
ogimage: "img/images/20210613.png"
---

## 概要

- 自分で運用している[ブログサイト](https://haytok.jp)は `git` を用いて管理しています。新しい記事を作成する際に、`untracked files` のみを `git stash` して、退避させたいことがありました。しかし、`git` にはデフォルトで `untracked files` のみを退避させるコマンドは無いそうです。そこで、今回は `.gitconfig` を使用して工夫したことについての記録を残したいと思います。

## 背景と目的

- 新しい記事を作成するために `hugo new` コマンドで記事の雛形を作成します。過去に書いた記事を参考にしつつ新しい記事を書いていると、過去の記事にタイポを見つけて修正したくなることや、言い回しを変えたくなる時があります。その内容を修正しつつ、一通り満足の行く新しい記事を書き終えると、`hugo` コマンドで修正したり作成したファイルを `build` を行った後に `push` する必要があります。しかし、修正した過去の記事と新規作成した記事の `build` を別々に行った後に `push` してコミットを分けたいと考えています。そのため、このようなケースでは一旦新規作成した記事を退避させて `build` を行い、`push` します。そして、その後に `git stash pop` で退避させた新規作成した記事を元に戻してから `build` を行い、`push` するようにします。

- こうして `untracked files` のみを退避させたいのですが、このコマンドは毎回調べているイメージがありました。その調べている時間が無駄でもったいないと感じていました。そこで、今回はその無駄な手順を省くために `.gitconfig` を使用し、 `untracked files` のみを退避させるエイリアスを設定しました。また、`.bashrc` に記述していた `git` コマンドのエイリアスも `.gitconfig` に移して、設定ファイルの整理も行いました。

## 方法

- `untracked files` のみを退避させる方法は [How to git stash only untracked files?](https://stackoverflow.com/questions/39026156/how-to-git-stash-only-untracked-files) を参考にさせて頂きました。加えて、普段からよく使うような `git` コマンドもエイリアスに追加しました。

```bash
[alias]
  s = status
  d = diff
  co = commit
  p = push origin HEAD
  pu = pull
  ch = checkout
  r = reset
  st = stash
  stp = stash pop
  stu = stash -u
  stash-untracked = "!f() {    \
      git stash;               \
      git stash -u;            \
      git stash pop stash@{1}; \
  }; f"
```

- `git stash-untracked` コマンドを実行した際の `stash list` の状況は以下のようになると推測できます。こうして `untracked files` のみを退避させているようです。

|      git コマンド (実行後)      |    stash list の状況    |
| :----------------------: | :------------------: |
|         git stash        |      {0}: 修正ファイル     |
|       git stash -u       | {0}: untracked files |
|                          |      {1}: 修正ファイル     |
| git stash pop stash@{1}; | {0}: untracked files |

- また、もともと `.bashrc` には、以下のように `git` コマンドのエイリアスを書いていました。これらを上述のようにエイリアスを `.gitconfig` に移行しました。

```bash
alias gs='git status'
```

## 感想

- 今回は、`.gitconfig` を使用して `untracked files` のみを退避させる `git stash-untracked` を設定しました。新しく知った `.gitconfig` を使ってエイリアスを設定できて良かったです。また、`.bashrc` に書いていた `git` コマンドのエイリアスを `.gitconfig` に移行し、`git` コマンド周りの設定を整理できて良かったです。

## 参考

- [How to git stash only untracked files?](https://stackoverflow.com/questions/39026156/how-to-git-stash-only-untracked-files)
- [【Git】エイリアス晒す＆書き方まとめ](https://qiita.com/YamEiR/items/d98ba009d2925e7eb305)
