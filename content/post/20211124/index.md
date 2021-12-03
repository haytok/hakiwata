---
draft: false
title: "CyberAgent のコンテナ技術に関する\n勉強会に参加してきた"
date: 2021-11-30T18:35:39Z
tags: ["CyberAgent", "Docker", "Kubernetes"]
pinned: false
ogimage: "img/images/20211124.png"
---

## 概要

- 先日 2021/11/24 に CyberAgent が主催する[CA 1Day Youth Boot Camp バックエンド/インフラエンジニア編：現場で使うコンテナ技術、Kubernetes＆コンテナ入門](https://www.cyberagent.co.jp/careers/students/career_event/detail/id=26761)と言う勉強会に参加してきました。これは、CyberAgent での社内の研修を 1 日体験できるイベントでした。今回は、その参加記を書きたいと思います。

![CA_1Day_Youth_Boot_Camp.jpg](CA_1Day_Youth_Boot_Camp.jpg)

## 参加したキッカケ

- 普段から Docker や Kubenetes を活用して趣味のプログラムや研究のコードを書いたりしています。しかし、これまでこれらの技術はほとんど独学で勉強をしてきました。そのため、自分の理解のレベル感が客観的に把握したことがありませんでした。また、最近 ES を書いたり外部の勉強会に参加するといった活動をしていませんでした。そんな時に、Twitter でたまたまこのイベントを見つけ、久しぶりにこういったチャンスに挑んでみたいと思い参加してみました。

## 学んだこと

- [Kubernetes の基礎編](https://speakerdeck.com/bo0km4n/ca-1day-youth-bootcamp-ciu-kubernetes) で Kubernetes の基本的なコンセプトや原理を復習できました。
- コンテナレジストリのミラーリポジトリに `mirror.gcr.io` 活用すると、Docker Hub のレート制限を抑えることができることを初めて知りました。
- Kubernetes in Docker ([kind](https://kind.sigs.k8s.io/)) と言う Docker コンテナのノードを使ってローカルに Kubernetes クラスタを実行するためのツールを初めて知りました。
- `kubectl edit` コマンドや `kubectl run` コマンドを始めて使いました。
- Kubernetes 内の Pod からしかアクセスできない Pod に対して、[busybox](https://hub.docker.com/_/busybox) と `kubectl run` コマンドを用いたデバッグを初めて知りました。

## 感想

- 学んだことに書いたように、知らなかったことをたくさん知るキッカケになりました。また、特に Kubernetes の研修に関しては、[CyberAgentHack/one-day-youth-bootcamp-ciu](https://github.com/CyberAgentHack/one-day-youth-bootcamp-ciu) にある演習問題を解いて手を動かす時間も設けられていたので、とても楽しかったです！ (演習問題は簡単でした。) しかし、この勉強会で学んだことと実際に現場で必要な知識や技術力にはかなり乖離があると感じました。そのため、Kubernetes を実際に運用するレベルのアプリケーションの実装を検討してみたいと思いました🤞

## 参考

- [コンテナ技術入門](https://speakerdeck.com/zuiurs/ca-1day-youth-boot-camp-introduction-to-container-technology)
- [Kubernetes の基礎編](https://speakerdeck.com/bo0km4n/ca-1day-youth-bootcamp-ciu-kubernetes)
- [CyberAgentHack/one-day-youth-bootcamp-ciu](https://github.com/CyberAgentHack/one-day-youth-bootcamp-ciu)
- [Container Registry の Docker Hub ミラーの使用](https://cloud.google.com/container-registry/docs/using-dockerhub-mirroring?hl=ja#cli)
- [kind](https://kind.sigs.k8s.io/)
- [busybox](https://hub.docker.com/_/busybox)
- [どのリクエストにも決まったレスポンスを返す、http-echoサーバー](https://kazuhira-r.hatenablog.com/entry/2020/11/13/004940)
