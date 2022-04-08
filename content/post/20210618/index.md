---
draft: false
title: "システムコール番号を使って \nwrite システムコールを呼び出す"
date: 2021-06-18T02:21:38+09:00
tags: ["C", "Assembler"]
pinned: false
ogimage: "img/images/20210618.png"
---

## 概要

- こんにちは！最近、低レイヤ寄りの実装に興味があり、[Linux Kernel](https://github.com/torvalds/linux) のシステムコール周りのソースコードを読む機会がありました。その際に、システムコールには、対応するシステムコール番号があるのを知りました。そこで、今回は C 言語やアセンブリ言語を書くことを通して、[write](https://linuxjm.osdn.jp/html/LDP_man-pages/man2/write.2.html) システムコールにおけるシステムコール番号とシステムコールの関係性について調査してみたいと思います。

## 背景と目的

- あるとき、[socket](https://linuxjm.osdn.jp/html/LDP_man-pages/man2/socket.2.html) システムコールは第三引数の `protocol` に応じてどのような処理が行われているかが気になったことがありました。その際、[socket](https://linuxjm.osdn.jp/html/LDP_man-pages/man2/socket.2.html) システムコールのプログラムを [Linux Kernel](https://github.com/torvalds/linux) のソースコードから紐解く静的解析を行いました。静的解析でプログラムを追っていくと、[write](https://linuxjm.osdn.jp/html/LDP_man-pages/man2/write.2.html) システムコールが呼び出されていることに気づきました。このことがキッカケで、一番プリミティブで親近感のある [write](https://linuxjm.osdn.jp/html/LDP_man-pages/man2/write.2.html) システムコールの実装やシステムコール番号との関係性に興味を持ちました。

- そこで、今回は検証プログラムを実装することを通して、[write](https://linuxjm.osdn.jp/html/LDP_man-pages/man2/write.2.html) システムコールにおけるシステムコール番号とシステムコールの関係性を明らかにします。

## 方法

- 以下の 1 と 2 と 3 の順序で検証を行います。

1. まず、[syscall](https://linuxjm.osdn.jp/html/LDP_man-pages/man2/syscall.2.html) 関数とシステムコール番号を使用して標準出力に文字列を出力する C 言語のプログラムを実装します。これにより、システムコール番号とシステムコールの対応関係に対する理解を深めます。

2. 次に、アセンブリ言語単体でシステムコールを呼び出すプログラムを実装します。これにより、システムコールを呼び出す際に必要な引数をスタックに詰んで、システムコールを呼び出す流れを確認します。

3. 最後に、アセンブリ言語でシステムコールを呼び出し、標準出力に文字列を出力させる関数を実装し、その関数を C 言語で書いたプログラムから呼び出します。こうして、C 言語で書いたプログラムとアセンブリ言語で書いたプログラムの関係性を確認します。ただし、ここで取り扱うアセンブリ言語のプログラムは 32 bit の実行ファイルを作成するためのプログラムです。

---

- それでは、1 を検証したいと思います。
- まず、[syscall](https://linuxjm.osdn.jp/html/LDP_man-pages/man2/syscall.2.html) 関数のマニュアルを確認すると、以下のような記述がありました。

```bash
NAME
       syscall - indirect system call

SYNOPSIS
       #define _GNU_SOURCE         /* See feature_test_macros(7) */
       #include <unistd.h>
       #include <sys/syscall.h>   /* For SYS_xxx definitions */

       long syscall(long number, ...);

DESCRIPTION
       syscall()  is  a  small  library  function  that invokes the system call whose assembly language interface has the specified number with the specified arguments.
       Employing syscall() is useful, for example, when invoking a system call that has no wrapper function in the C library.

       syscall() saves CPU registers before making the system call, restores the registers upon return from the system call, and stores any error code returned  by  the
       system call in errno(3) if an error occurs.

       Symbolic constants for system call numbers can be found in the header file <sys/syscall.h>.
```

- つまり、[syscall](https://linuxjm.osdn.jp/html/LDP_man-pages/man2/syscall.2.html) 関数の第一引数にシステムコール番号を、それ以降の可変長引数にそのシステムコール番号に対応するシステムコールの引数を格納して呼び出せば、システムコールを呼び出せそうです。そこで、以下のようなプログラム `test_1.c` を実装して検証しました。

```c
#define _GNU_SOURCE
#include <unistd.h>
#include <sys/syscall.h>
#include <asm/unistd_32.h>

int main(void) {
    char *buf = "Hi!\n";
    syscall(__NR_write, STDOUT_FILENO, buf, sizeof(buf));
    return 0;
}
```

- このプログラムを以下のコマンドでビルドをします。

```bash
gcc -m32 -o test_1 test_1.c
```

- 作成された実行ファイルを以下のコマンドで実行します。

```bash
./test_1
Hi!
```

- このように `Hi!` の文字列が標準出力に出力されます。こうして、[syscall](https://linuxjm.osdn.jp/html/LDP_man-pages/man2/syscall.2.html) 関数とシステムコール番号を使って [write](https://linuxjm.osdn.jp/html/LDP_man-pages/man2/write.2.html) システムコールを呼び出すことができました。

- ちなみに、システムコール番号は以下のコマンドを使用して確認しました。システムコール番号の変数名はマクロで定義されていて、`__NR` の文字列が入っていたのが経験的に知っていました。しかし、その変数名を正確には記憶していませんでした。そのため、以下のコマンドでシステムコール番号を確認しました。

```bash
grep -ilr __NR /usr/include/* 
```

- このコマンドの結果の一部を抜粋して以下に記載します。

```bash
/usr/include/asm/vsyscall.h
/usr/include/asm/unistd_64.h
/usr/include/asm/unistd_x32.h
/usr/include/asm/unistd_32.h
/usr/include/asm-generic/unistd.h
/usr/include/bits/unistd.h
/usr/include/bits/syscall.h
/usr/include/bits/stdlib.h
...
```

- とりあえずシステムコール番号が定義されていそうな雰囲気のある `/usr/include/asm/unistd_32.h` を確認すると、マクロで `#define __NR_write 4` が定義されているのが確認できると思います。つまり、[write](https://linuxjm.osdn.jp/html/LDP_man-pages/man2/write.2.html) システムコールのシステムコール番号が `4` であることが確認できました。

---

- 次に、2 を検証したいと思います。

- 以下のテーブルは、レジスタにどのような値をロードする必要があるかを表しています。これは [Linux System Call Table](https://chromium.googlesource.com/chromiumos/docs/+/master/constants/syscalls.md#calling-conventions) を参考に作成しています。32 bit の実行ファイルで [write](https://linuxjm.osdn.jp/html/LDP_man-pages/man2/write.2.html) システムコールを呼び出すのであれば、`eax` レジスタにはシステムコール番号を、`ebx` レジスタには呼び出すシステムコールの第一引数を、`ecx` レジスタには第二引数を、`edx` レジスタには第三引数をロードし、`int 0x80` を呼び出すようにアセンブリ言語を書く必要があります。

| arch | syscall NR | return | arg0 | arg1 | arg2 | arg3 | arg4 | arg5 |
| :---: | :---: |  :---:  | :---: | :---: | :---: | :---: | :---: | :---: |
| x86 | eax | eax | ebx | ecx | edx | esi | edi | ebp |
<!-- | x86_64 | rax | rax | rdi | rsi | rdx | r10 | r8 | r19 | -->

- これを元にレジスタに具体的な値をロードしていきます。`eax` には `__NR_write` の値である `4` を、`ebx` には標準出力を表す `1` を格納します。表示する文字列 `Hi!` に関しては、スタック経由で `ecx` に文字列の先頭のアドレスをロードします。今回は、最初に `push 0x0a216948` でスタックのトップに表示したい文字列を積んでいます。したがって、このアドレスを `ecx` にロードすれば良いです。最後に、`edx` には、表示する文字列のバイト数 `4` をロードします。

- こうして、標準出力に `Hi!` の文字列を出力するプログラム `test_2.asm` を以下に記述します。

```asm
global main

main:
  push 0x0a216948
  mov  eax, 0x4
  mov  ebx, 0x1
  mov  ecx, esp
  mov  edx, 0x4
  int  0x80
  add  esp, 0x4
```

- 次に、[nasm](https://www.nasm.us/) コマンドを用いてアセンブリ言語で書かれたプログラムをオブジェクトファイルに変換します。この変換には以下のコマンドを実行します。

```bash
nasm -g -f elf32 -o test_2.o test_2.asm
```

- 生成されたオブジェクトファイル `test_2.o` を gcc を用いて 32 bit の実行ファイルに変換します。この変換には以下のコマンドを実行します。

```bash
gcc -m32 -o test_2.out test_2.o
```

- これらの結果、`Hi!` という文字列を標準出力に書き込む実行ファイル `test_2.out` が作成されます。これは、以下のコマンドを実行することで確認することができます。

```bash
./test_2.out
Hi!
```

- こうして、アセンブリ言語を書くことで `write` システムコールを呼び出し、標準出力に文字列を書き込むことができました。これは、1 で実装した C 言語のプログラムをアセンブリ言語で書き換えたものであるとも言えます。

---

- 最後に、3 について検証したいと思います。

- まず、ベースとなる C 言語のプログラム `test_3.c` を以下のように実装します。ここでは、`#include　<stdio.h>` を書かず、標準出力をするためのロジックである `void hi(char *string, int len)` は `test_3.asm` で実装します。

```c
void hi(char *string, int len);

int main () {
    char *string = "Hi!\n";
    hi(string, 4);
    return 0;
}
```

- 実装した C 言語のプログラム `test_3.c` を以下のコマンドでオブジェクトファイル `test_3.o` を作成します。後で、アセンブリ言語で書いたプログラムから生成したオブジェクトファイルとリンクさせます。

```bash
gcc -m32 -o test_3.o -c test_3.c
```

- 次に、C 言語のプログラムから呼び出される関数 `hi` を `test_3.asm` に記述します。関数名が `hi` で、第一引数に文字列を第二引数にその文字列の長さを受け取ります。そして、受け取った文字列を標準出力に出力する関数です。基本的には 2 で実装したアセンブリをベースにしています。しかし、1 点だけ注意しないといけない点があります。それは、関数 `hi` の引数の値をスタックからレジスタにロードする必要があることです。2 では、標準出力する文字列とその長さをレジスタに直書きしていました。そのため、今回は `mov ecx, [esp+4]` や `mov edx, [esp+8]` の命令を使用してスタックの値をレジスタにロードします。これらの点に留意して実装したプログラムが以下になります。

```asm
bits 32

global hi

hi:
  mov eax, 0x4
  mov ebx, 0x1
  mov ecx, [esp+4]
  mov edx, [esp+8]
  int 0x80
  add esp, 0x4
  ret
```

- 実装したアセンブリ言語のプログラム `test_3.asm` から [nasm](https://www.nasm.us/) コマンドでオブジェクトファイル `syscall_test_3.o` を作成します。

```bash
nasm -f elf32 -o syscall_test_3.o test_3.asm
```

- ここまでで作成された 2 つのオブジェクトファイルを以下のコマンドでリンクして実行ファイル `test_3.out` を作成します。

```bash
gcc -m32 -o test_3.out test_3.o syscall_test_3.o
```

- 最終的に作成された実行ファイル `test_3.out` を実行すると、`Hi!` の文字列が出力されます。

```bash
./test_3.out
Hi!
```

- こうして、アセンブリ言語で [write](https://linuxjm.osdn.jp/html/LDP_man-pages/man2/write.2.html) システムコールを呼び出し、標準出力に文字列を出力させる関数を実装し、その関数を C 言語で書いたプログラムから呼び出すことができました。ちなみに、アセンブリのプログラムが上手く動作しないときは、[strace](https://man7.org/linux/man-pages/man1/strace.1.html) コマンドを使って、[write](https://linuxjm.osdn.jp/html/LDP_man-pages/man2/write.2.html) システムコールの引数に渡されている引数を確認してデバッグを行っていました。

## 結果と結論

- 以上の調査と検証の結果より、[write](https://linuxjm.osdn.jp/html/LDP_man-pages/man2/write.2.html) システムコールにおけるシステムコール番号とシステムコールが対応関係を明らかにしました。C 言語やアセンブリ言語を使用した複数の視点を通して、検証することができて楽しかったです。この記事を推敲している段階で、似たようなことを書かれている [魅力的なLinuxシステムコールの世界](https://www.linkedin.com/pulse/%E9%AD%85%E5%8A%9B%E7%9A%84%E3%81%AAlinux%E3%82%B7%E3%82%B9%E3%83%86%E3%83%A0%E3%82%B3%E3%83%BC%E3%83%AB%E3%81%AE%E4%B8%96%E7%95%8C-takao-shimizu/) という記事を見つけました。見つけた時は少し残念な気がしましたが、記事の方向性は悪くなかったと思いました🤞

## 参考

- [grepでファイル内を検索しよう](https://searchman.info/tips/1090.html)

- [はじめて学ぶバイナリ解析　不正なコードからコンピュータを守るサイバーセキュリティ技術](https://www.amazon.co.jp/%E3%81%AF%E3%81%98%E3%82%81%E3%81%A6%E5%AD%A6%E3%81%B6%E3%83%90%E3%82%A4%E3%83%8A%E3%83%AA%E8%A7%A3%E6%9E%90-%E4%B8%8D%E6%AD%A3%E3%81%AA%E3%82%B3%E3%83%BC%E3%83%89%E3%81%8B%E3%82%89%E3%82%B3%E3%83%B3%E3%83%94%E3%83%A5%E3%83%BC%E3%82%BF%E3%82%92%E5%AE%88%E3%82%8B%E3%82%B5%E3%82%A4%E3%83%90%E3%83%BC%E3%82%BB%E3%82%AD%E3%83%A5%E3%83%AA%E3%83%86%E3%82%A3%E6%8A%80%E8%A1%93-OnDeck-Books%EF%BC%88NextPublishing%EF%BC%89-%E5%B0%8F%E6%9E%97-%E4%BD%90%E4%BF%9D-ebook/dp/B084R85269) 
- [haytok/BinaryAnalysisBook](https://github.com/haytok/BinaryAnalysisBook/tree/main/s6)
- [Linux System Call Table](https://chromium.googlesource.com/chromiumos/docs/+/master/constants/syscalls.md)
- [2021/05/08](https://github.com/haytok/LowLevelProgramming/tree/main/log/20210508)
- [魅力的なLinuxシステムコールの世界](https://www.linkedin.com/pulse/%E9%AD%85%E5%8A%9B%E7%9A%84%E3%81%AAlinux%E3%82%B7%E3%82%B9%E3%83%86%E3%83%A0%E3%82%B3%E3%83%BC%E3%83%AB%E3%81%AE%E4%B8%96%E7%95%8C-takao-shimizu/)
