---
draft: false
title: "The Internals of PostgreSQL"
date: 2022-06-27T10:44:31Z
tags: ["PostgreSQL"]
pinned: false
ogimage: "img/images/interdb.png"
---

## 概要

- [The Internals of PostgreSQL](https://www.interdb.jp/pg/) を読んで追加で調査したことを記録に残す。

## Chapter 4

- Nested Loop Join

## Chapter 5

### 5.7.1 Visibility Check

- 5.6 の Visibility Check Rules の式は理解できなかったが、5.7 での具体的な評価例を見ると使い方はなんとなく理解できた。
- update するのと tx から見えるかはまた別の問題であることを説明している。select 構文でなぜその結果を取得できるかをソースコードレベルでの処理を解説している。(直感的には出力される結果はわかる。)
- ? txid = 201 において t_max = 200 の Tuple_1 が見えるのがおかしい気がした。けど、よくよく考えると Tuple_1 のオブジェクトはメモリ上では書き変わっているからそうなるか。
- commit 前の trx が見えると Dirty Read になるけど、PostgreSQL ではどの分離レベルにおいてもにおいても Dirty Read は生じない。

### 5.7.2. Phantom Reads in PostgreSQL‘s REPEATABLE READ Level

- PostgreSQL のデフォルトのトランザクション分離レベルは Read committed である。

| Isolation Level | Dirty Read | Phantom Read | Serializable |
| :---: | :---: | :---: | :---: |
| Read committed  | Not Possible | Possible | Possible | Possible |
| Repeatable read | Not Possible | Not Possible | Allowed, but not in PostgreSQL | Possible |

- ? なんで Snapshot(t_xmin:100) = active になるかがわからん。トランザクション開始時の状態で判断するから？
- ? 分離レベルに関わらず rule に基づいて Visibility が Invisibility かを判断していたが、それは問題ないん？どの分離レベルだろうが rule は rule ってこと？

### 5.8. Preventing Lost Updates

- anomaly : 異常
- Pseudocode : 疑似コード
- SI : Snapshot Isolation
- SSI : Serializable Snapshot Isolation
- embed : 組み込まれる

- 同一行を更新したときの挙動を観察する。Repeatable read と Serializable では ww-conflict (更新の紛失) を回避することができる。

### 5.9. Serializable Snapshot Isolation

- 全くわからんかった。
- ? 述語ロックってなんですか？
- false negative
> 本来は有害であると判断されるべき事象について、検査をすり抜けて正常であると誤って判断されてしまうことをフォールスネガティブという。

### 5.10. Required Maintenance Processes

- txid の周回問題を解消する Freeze 処理に関して解説。
- t_xmin に特殊な値の 2 を格納する処理。
- frozen txid は Tuple を inactive だが visible にする。これは vacuum の処理が走る際に実行される。(PostgreSQL のバージョンによって挙動が変わる。)
- 9.4 以上のバージョンでは t_informask の　XMIN_FROZEN のビットを立てる。
- ? Fig. 5.21 a) において the current txid が 50 million の時に Freeze process が走ったとすると、表の t_xmin が 99 と 100 はその対象にならんくないか？

## Chapter 6

- the persistent operation of PostgreSQL : ポスグレの永続的な運用
- facilitate : 運用する、容易にする

- vacuum のタスクは主に 2 つあり、dead tuple の削除と xid の Freeze である。

## Chapter 9

- WAL の論理あるいは物理的な構造
- WAL データの内部構造
- WAL データの書き込み
- WAL writer プロセス
- チェックポイントプロセス
- データベース復旧プロセス
- WAL セグメントファイルの管理方法
- 継続的なアーカイブ

<!-- ## 背景

## 目的

## 方法

## 結果

## 結論

## 参考 -->
