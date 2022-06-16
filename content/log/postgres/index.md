---
draft: false
title: "PostgreSQL"
date: 2022-06-14T12:26:50Z
tags: ["PostgreSQL"]
pinned: false
ogimage: "img/images/postgres.png"
---

## 概要

- この Log では、PostgreSQL の内部アーキテクチャを勉強する際に調査したことを残す。

## Outline

- [x] [PostgreSQL を利用できる環境の構築方法について教えてください。](#0)
  - [x] Docker + docker-compose を用いた構築方法
  - [ ] AWS CLI + RDS for PostgreSQL を用いた構築方法
  - [ ] AWS CLI + Aurora PostgreSQL を用いた構築方法

- [ ] [RDBMS あるいは PostgreSQL のアーキテクチャについて詳しくなるために読んでいる本や資料について教えてください。](#1)

- [x] [ポスグレの主なファイル群について教えてください。](#2)

- [ ] [TOAST について教えてください。](#3)

- [ ] ページって何ですか。教えてください。

- [ ] WAL バッファがディスクに保存されるまでに DB がクラッシュすると WAL バッファは消えてしまいます。この際、直前の書き込みまでのロールバックが物理的に不可能になる気がするのですが、これは正しいでしょうか？また、正しければ、このような状況になったとするとどのようにデータの復旧を行えば良いですか？

- [ ] WAL Log と Archive Log の違いはなんですか？

- [ ] WAL Log の書き込みが失敗することはあるのですか？

- [ ] 物理レプリケーションと論理レプリケーションの違いを教えて下さい。
  - 物理レプリケーション -> ストリーミングレプリケーション (Streaming)
  - 論理レプリケーション -> ロジカルレプリケーション (Logical)

- [ ] WAL Sender について教えてください。

- [ ] Lock の全てのレベルについて説明してください。

- [ ] ポスグレのページに関して教えてください。

---

## PostgreSQL を利用できる環境の構築方法について教えてください。 {#0}

- RDS for PostgreSQL や Aurora PostgreSQL を使用しても良いが、起動に時間がかかってしまう。待ち時間を減らして、サクッと検証したい時は参考情報 [1] をもとに Docker + docker-compose を使用する。

- 使用する docker-comopose.yaml

```yaml
version: '3'

services:
  db:
    image: postgres:14
    container_name: postgres
    ports:
      - 5432:5432
    volumes:
      - db-store:/var/lib/postgresql/data
    environment:
      - POSTGRES_PASSWORD=passw0rd
volumes:
  db-store:
```

- 起動して、PostgreSQL に接続するコマンドを以下に示す。

```bash
docker-compose up -d
docker exec -it postgres bash
psql -h localhost -U postgres
```

### 参考情報

1. [【Docker】postgresqlの構築](https://zenn.dev/re24_1986/articles/b76c3fd8f76aec)

---

## RDBMS あるいは PostgreSQL のアーキテクチャについて詳しくなるために読んでいる本や資料について教えてください。 {#1}

- [ ] ［改訂新版］内部構造から学ぶPostgreSQL 設計・運用計画の鉄則

---

## ポスグレの主なファイル群について教えてください。 {#1}

- 主に、3 つのファイルがある。

1. データファイル
2. Index ファイル
3. WAL ファイル
  - pg_xlog ディレクトリに WAL ファイルは配置され、16 MB の固定サイズで作成される。
    - xlog は、Transaction Log のことを指してる？
  - 大量の tx 処理があると xlog も増えるので、バッチ処理を行う場合にはその点に気をつけて WAL を破棄するタイミングを設定しないといけない。

---

## TOAST について教えてください。 {#2}

- TOAST とは、The Over-sized Attribute Storage Technique の頭文字を取った略称のことで、日本語では過大属性格納技法と呼ばれる。
- 非常に長い (大きい) データをポスグレの固定帳の 8KB のページに収めるための手法である。


- OID (Object ID)

- CHECKPOINT とはトランザクションログのチェックポイントを強制的に実行するコマンドのことである。
