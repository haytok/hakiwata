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

#### osbook_day10d

- 実装中🤞

<!-- ## 最後に -->


## 参考
