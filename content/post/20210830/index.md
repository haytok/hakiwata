---
draft: false
title: "自作 OS 日記"
date: 2021-08-29T19:11:00Z
tags: ["OS", "Kernel", "C"]
favorite: false
---

## 概要

- こんにちは！最近、研究室の隣の同期に影響されて自作 OS を始めました。そこで、今回は自作 OS が成長していく様子を日記としてこの記事に残したいと思います。

## 日記

### 2021 年 8 月 13 日

#### osbook_day01

- 自作 OS を始めました！名前は HonOS です！

![osbook_day01.png](osbook_day01.png)

### 2021 年 8 月 28 日

#### osbook_day09b

![osbook_day09b.gif](osbook_day09b.gif)

#### osbook_day09c

![osbook_day09c.gif](osbook_day09c.gif)

#### osbook_day09d

![osbook_day09d.gif](osbook_day09d.gif)

### 2021 年 8 月 29 日

#### osbook_day09e

![osbook_day09e.gif](osbook_day09e.gif)

#### osbook_day10a

![osbook_day10a.gif](osbook_day10a.gif)

#### osbook_day10b-invalid

- `FrameBuffer::Copy` の実装が間違っていたせいで表示がバグってしまいました。状況を切り分けつつバグを調査する過程が最高に楽しかったです。

![osbook_day10b-invalid.gif](osbook_day10b-invalid.gif)

#### osbook_day10b

- ウィンドウを表示することができました！

![osbook_day10b.gif](osbook_day10b.gif)

#### osbook_day10c

- Kernel の main 関数の for ループ回数を書き込んだウィンドウを表示することができました！

![osbook_day10c-invalid.gif](osbook_day10c-invalid.gif)

### 2021 年 8 月 30 日

- しかし、この記事を見た同期に表示されている色の挙動がおかしいと指摘されました。そこで、[osbook_day10c](https://github.com/uchan-nos/mikanos/tree/osbook_day10c) に checkout し、正常系の挙動を確認してみました。そうすると、確かに正常系と比較すると、挙動がおかしかったので、バグを調査し修正しました。原因は `constexpr PixelColor ToColor(uint32_t c);` の色のビットシフトが逆になっていたことでした。だいぶ画面がチカチカしていますが、そのリファクタリングは次節以降でできればと思っています！

![osbook_day10c.gif](osbook_day10c.gif)

### 2021 年 8 月 31 日

#### osbook_day10d

![osbook_day10d.gif](osbook_day10d.gif)

#### osbook_day10e

![osbook_day10e.gif](osbook_day10e.gif)

#### osbook_day10f

- USB ドライバからデータを取り出すプログラムは、マウスのボタンが押されたかとマウスがどれだけ移動したかの変位を取得できる機能のものでした。しかし、なぜかドライバから Kernel にそれらのデータが渡されませんでした。`make clean` や `rm kernel.elf` を実行し、クリアな状況にしても状況が改善されませんでした。そこで、`Makefile` を本家からコピーすると正常な動きをするようになりましたが、なぜデータが Kernel 側に受け渡されなかったかの原因が不明のまま解決してしまいました。

![osbook_day10f.gif](osbook_day10f.gif)

#### osbook_day10g

![osbook_day10g.gif](osbook_day10g.gif)

### 2021 年 9 月 1 日

#### osbook_day11a

- main 関数のリファクタリングを行いました。main 関数が大きすぎて大変でした。見た目の挙動は osbook_day10g と変わりません。

![osbook_day11a.gif](osbook_day11a.gif)

#### osbook_day11b

- 周期的に割り込むタイマを実装しました。一定のカウントが刻まれると、割り込みが入り、背景に文字列が表示されます。

![osbook_day11b.gif](osbook_day11b.gif)

#### osbook_day11c

- 前節よりも短い周期で割り込みを行わせ、その割り込み回数を計算します。

![osbook_day11c.gif](osbook_day11c.gif)

### 2021 年 9 月 2 日

#### osbook_day11d

- 複数のタイマを作成し、それらからのタイムアウト通知を受け取ることができるように修正しました。

![osbook_day11d.gif](osbook_day11d.gif)

#### osbook_day11e

- Kernel で Root System Description Pointer を取得できるように修正しました。これは、後々 IO ポート番号を求めるのに役立ちます。

![osbook_day11e.gif](osbook_day11e.gif)

#### osbook_day12a

- IO ポート番号を求めるのに必要な FADT というテーブルのデータを取得する実装を行いました。UI に変化はありません。

### 2021 年 9 月 3 日

#### osbook_day12b

- ACPI PM タイマ (基準となる軸で、fadt->pm_tmr_blk から求められる。) を使用して Local APIC タイマの 1 カウントが何秒なのかを計測します。

![osbook_day12b.gif](osbook_day12b.gif)

#### osbook_day12c

![osbook_day12c.gif](osbook_day12c.gif)

#### osbook_day12d

![osbook_day12d.gif](osbook_day12d.gif)

#### osbook_day12e

![osbook_day12e.gif](osbook_day12e.gif)

#### osbook_day12f

![osbook_day12f.gif](osbook_day12f.gif)

### 2021 年 9 月 4 日

#### osbook_day13a

- 協調的マルチタスクの機能を実装しました！

![osbook_day13a.gif](osbook_day13a.gif)

#### osbook_day13b

- プリミティブなプリエンプティブマルチタスクの機能を実装しました！特にコンテキストスイッチの自動化を行いました。

![osbook_day13b.gif](osbook_day13b.gif)

#### osbook_day13c

- マルチタスクが実装できるかを検証しました。Hello Window と TaskB Window のカウンタが 1 秒おきに切り替わっていることがわかります。しかし、カウンタは 2 秒間分のカウントを刻んでいます。

![osbook_day13c.gif](osbook_day13c.gif)

#### osbook_day13d

- マルチタスクを管理するための TaskManager を実装しました。タスクを増やせば増やすほどマウスがカクつく問題が生じたので、次章以降で修正していきたいと思います！

![osbook_day13d.gif](osbook_day13d.gif)

### 2021 年 9 月 5 日

#### osbook_day14a

![osbook_day14a.gif](osbook_day14a.gif)

#### osbook_day14b

![osbook_day14b.gif](osbook_day14b.gif)

#### osbook_day14c

![osbook_day14c.gif](osbook_day14c.gif)

#### osbook_day14d

![osbook_day14d.gif](osbook_day14d.gif)

### 2021 年 9 月 6 日

#### osbook_day15a

- ウィンドウの描画をメインスレッドで行うようにリファクタリングを行う。

- 実装中🤞

### 2021 年 9 月 9 日

#### osbook_day15c

![osbook_day15c.gif](media/osbook_day15c.gif)

#### osbook_day15d

![osbook_day15d.gif](media/osbook_day15d.gif)

## 参考

- [honOS](https://github.com/dilmnqvovpnmlib/honOS)
- [mikanos](https://github.com/uchan-nos/mikanos)
