---
draft: false
title: "CPython 調査ログ"
date: 2021-11-17T09:20:23Z
tags: ["CPython", "Python", "C"]
favorite: false
---

## 概要

- CPython のソースコードリーディングを行い、言語拡張やデータ構造がどのように C 言語で実装されているかを調査する。

## 調査ログ

### 2021/11/16

- 初期設定とプログラムのビルドを行う。ディレクトリは git から落としてきた `cpython` ディレクトリで行う。`-g` オプションで実行ファイルにデバッグシンボルを埋め込む。そして、`-O0` オプションで最適化度合いを最低に落とす。こうすると、GDB などのデバッガでデバッグの情報を読み出すことができる。また、`--prefix` オプションでインストールするフォルダを指定する。

```bash
CFLAGS="-O0 -g" ./configure --with-pydebug --prefix=/home/h-kiwata/oss/cpython
make -j $(nproc)
make install
```

- `${HOME}/test/bin/python3 main.py` でビルドしたバイナリで Python のファイルを実行することができる。ちなみに、`main.py` の中身は以下である。

```python
a = 1000
a += 20
print('Hello World')
```

### 2021/11/17

- token のオブジェクトの中身を見てみる。

- `cpython/Parser/pegen.c` 内の `_PyPegen_run_parser_from_file_pointer` 内で token のオブジェクトの生成が完了している。この関数の中で字句解析された各 token を確認する。

```c
...
_PyPegen_run_parser_from_file_pointer(FILE *fp, int start_rule, PyObject *filename_ob,
                             const char *enc, const char *ps1, const char *ps2,
                             PyCompilerFlags *flags, int *errcode, PyArena *arena)
{
    struct tok_state *tok = _PyTokenizer_FromFile(fp, enc, ps1, ps2);
...
    char *start, *end;
    while (1) {
        int tok_type = _PyTokenizer_Get(tok, &start, &end);
        printf("token %s\n", _PyParser_TokenNames[tok_type]);
        if (tok_type == ENDMARKER) {
            break;
        }
    }
}
```

- こういう調査って興味があり続ければ、手を動かし続けらればある程度理解することができる。その先にパッチを当てられると信じている。

### 2021/11/18

- 特に何もしなかった。

### 2021/11/19

- ファイルからプログラムを実行すると、`Parser/pegen.c` 内の `_PyPegen_run_parser_from_file_pointer` が呼び出される。この内部ではすでに字句解析されたオブジェクト `struct tok_state *tok` が生成されている。この関数の中に以下のロジックを埋め込むと、分割された文字列が確認できる。

```cpp
char *start, *end;
while (1) {
    // printf("tok_state %s, tok %s, len %d\n", tok->buf, tok->start, tok->cur - tok->start);
    int tok_type = _PyTokenizer_Get(tok, &start, &end);
    printf("type %s, name %.*s\n", _PyParser_TokenNames[tok_type], tok->cur - tok->start, tok->start);
    if (tok_type == ENDMARKER) {
        break;
    }
}
```

- このプログラムを埋め込んで `${HOME}/test/bin/python3 main.py` を実行すると、以下のように字句解析されたトークンとそのタイプを確認できる。

```bash
type NAME, name a
type EQUAL, name =
type NUMBER, name 1000
type NEWLINE, name

type NAME, name a
type PLUSEQUAL, name +=
type NUMBER, name 20
type NEWLINE, name

type NAME, name print
type LPAR, name (
type STRING, name 'Hello World'
type RPAR, name )
type NEWLINE, name 

type ENDMARKER, name
```

## 参考

- [Changing CPython’s Grammar](https://devguide.python.org/grammar/)

