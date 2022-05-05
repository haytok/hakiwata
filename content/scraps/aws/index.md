---
draft: false
title: "AWS CLI メモ"
date: 2022-04-29T12:29:34Z
tags: ["AWS"]
pinned: false
ogimage: "img/images/aws.png"
---

## 概要

- AWS CLI のメモを残す。

## コマンド

### S3

- ローカルから特定の S3 バケットにファイルを `Upload` する。

```bash
aws s3 cp <ファイル名> s3://<バケット名>
```

- ローカルから特定のディレクトリを S3 バケットに `Upload` する。

```bash
aws s3 cp <ディレクトリ名> s3://<バケット名> --recursive
```

- 特定の S3 バケットからファイルを `Download` する。

```bash
aws s3 cp s3://<バケット名>/<ファイル名> .
```

- 有効期限付きで特定の S3 バケットのファイルを公開する presigned URLs を発行する。

```bash
aws s3 presign --expires-in <有効時間 (秒)> s3://<バケット名>/<オブジェクト名> --region <リージョン名>
```

#### 参考

- [AWS CLI での高レベル (S3) コマンドの使用](https://docs.aws.amazon.com/ja_jp/cli/latest/userguide/cli-services-s3-commands.html#using-s3-commands-managing-objects-copy)

### Lambda

- Lambda functions の一覧を返す。

```bash
aws lambda list-functions
```

#### 参考

- [list-functions](https://docs.aws.amazon.com/cli/latest/reference/lambda/list-functions.html)
