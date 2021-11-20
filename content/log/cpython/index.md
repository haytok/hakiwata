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
cd cpython
CFLAGS="-O0 -g" ./configure --with-pydebug --prefix=/home/h-kiwata/test
make -j $(nproc)
make install

make -j $(nproc) && make install
```

- `${HOME}/test/bin/python3 main.py` でビルドしたバイナリで Python のファイルを実行することができる。ちなみに、`main.py` の中身は以下である。

```python
a = 1000
a += 20
print('Hello World')
```

- ちなみに、今回の調査で使用している Python は `Python 3.11.0a2+` である。

#### 参考

- [Changing CPython’s Grammar](https://devguide.python.org/grammar/)

### 2021/11/17

- token のオブジェクトの中身を見てみる。

- `cpython/Parser/pegen.c` 内の `_PyPegen_run_parser_from_file_pointer` 内で token のオブジェクトの生成が完了している。この関数の中で字句解析された各 token を確認する。

```cpp
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

- こういう調査は興味があり手を動かし続けられれば、ある程度理解することができる。その先に何かしらのパッチを投げられるのではないかと思った。

### 2021/11/18

- 特に何もしなかった。

### 2021/11/19

- ファイルからプログラムを実行すると、`Parser/pegen.c` 内の `_PyPegen_run_parser_from_file_pointer` が呼び出される。この内部ではすでに字句解析されたオブジェクト `struct tok_state *tok` が生成されている。この関数の中に以下のロジックを埋め込むと、分割された文字列が確認できる。

```cpp
struct tok_state *tok = _PyTokenizer_FromFile(fp, enc, ps1, ps2);
if (tok == NULL) {
...
char *start, *end;
while (1) {
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

- 従って、`_PyTokenizer_FromFile` 内で字句解析が行われていると推測できる。この時点で自分はファイルポインタが生成される実装とどのように token オブジェクトが生成されているかに興味を持った。

- ファイルポインタ `FILE *fp` の生成には `Modules/main.c` 内の `pymain_run_file_obj` 関数内の `_Py_fopen_obj` 関数で行われている。使われ方は以下である。この関数内でプラットフォームに応じたファイルを開く処理が行われており、`fopen` が呼び出されている。

```cpp
FILE *fp = _Py_fopen_obj(filename, "rb");
```

- この `FILE fp*` を用いてファイルの中身を読み出し、字句解析する実装がどこかにあるはずである。

- 途中で `make install` が実行できなくて困った。

### 2021/11/20

- `Parser/pegen.c` の `_PyPegen_run_parser_from_file_pointer` を読むと、`Parser/pegen.c` の `_PyPegen_run_parser` がポイントだと感じた。そのため、その関数を読むと、`_PyPegen_parse` の理解が必要だと感じた。そこで、`Parser/parser.c` の `_PyPegen_parse` を読もうと思った。しかし、`Parser/parser.c` は `./Grammar/python.gram` から自動で生成されるファイルなので、一旦読むのを諦めて、言語自体を拡張する方にシフトすることにした。

- 文法を拡張する機能としては以下が挙げられる。
  - `&&`, `||`, `!` の追加
  - `else if` の追加
  <!-- - 
  - 
  -  -->

- 新しく token や PEG を変更すると以下のコマンドを叩く必要がある。

```bash
make regen-token
make regen-pegen
make -j $(nproc)  && make install
```

- しかし、使用している環境 (Amazon Linux 2) のデフォルトの Python のバージョンが古いため、`make regen-pegen` を実行することができない。そこで `pyenv` を用いてグローバル環境に Python 3.7 以降の環境を作成してから `make regen-pegen` を実行することにした。`pyenv` のインストールには [pyenv/pyenv](https://github.com/pyenv/pyenv#installation) を参考にする。Qiita の記事は今回使用している環境との相性が悪かった。
- `pyenv` をインストール後、自前でビルドしている Python のバージョンと合わせようと思い、`pyenv install 3.11.0a2+` を実行しようとした。しかし、`openssl` 関連のライブラリをインストール必要があった。この依存関係の解決が面倒臭かったので、`Python 3.8.0` を使用することにしてその場しのぎの解決策を講じた。

```bash
pyenv install --list
pyent install 3.8.0
pyenv global 3.8.0
```

- 以下のように Python のバージョンを確認した。

```bash
> python --version
Python 3.8.0 
```

- こうして Python のバージョンを変更すると、`make regen-pegen` を実行することができ、Python の文法を拡張することができた。拡張できたかどうかは以下の `main.py` を作成し、実行することで確認することができた。

```bash
> cat main.py
if false:
    print('karin')
else if true || false:
    print('risa')
> ./fuga/bin/python3 main.py
risa
```

#### 参考

- [PythonにC言語っぽい文法を追加する](https://doss2020-3.hatenablog.com/entry/2020/10/25/155612)
- [pyenv/pyenv](https://github.com/pyenv/pyenv#installation)
- [pyenv global が効かなくなった（？）話](https://blog.serverworks.co.jp/2021/05/12/233520)

### 2021/11/21

- 🤞
