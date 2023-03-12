---
draft: false
title: "Learning Memory Model for Linux kernel"
date: 2023-02-25T10:36:23Z
tags: ["Linux", "WIP"]
pinned: false
ogimage: "img/images/20230225-memory-model-for-linux.png"
---

下記のツールを使ってメモリモデルの挙動を確認してみる。

- [linux/tools/memory-model at master · torvalds/linux · GitHub](https://github.com/torvalds/linux/tree/master/tools/memory-model)
- [Simulating memory models with herd7](http://diy.inria.fr/doc/herd.html)

## 準備

検証環境

```bash
haytok@2023-03-01 01:33:47:~/memory-model
>>> uname -r
5.15.79.1-microsoft-standard-WSL2
haytok@2023-03-01 01:40:52:~/memory-model
>>> cat /etc/lsb-release
DISTRIB_ID=Ubuntu
DISTRIB_RELEASE=20.04
DISTRIB_CODENAME=focal
DISTRIB_DESCRIPTION="Ubuntu 20.04.5 LTS"
```

セットアップの手順は以下である。

```bash
sudo apt update
sudo apt install -y opam
opam init
opam install herdtools7
# ~/.bashrc に eval $(opam config env); を追記する。
```

実際に実行した手順は以下である。

```bash
haytok@DESKTOP-SK03JO0:~$ mkdir memory-model
haytok@DESKTOP-SK03JO0:~/memory-mode$ cd memory-model/
haytok@DESKTOP-SK03JO0:~/memory-mode$ pwd
/home/haytok/memory-model
haytok@DESKTOP-SK03JO0:~/memory-mode$ sudo apt install -y opam
... (省略)
haytok@DESKTOP-SK03JO0:~/memory-mode$ opam --version
2.0.5
haytok@DESKTOP-SK03JO0:~/memory-model$ opam init
[NOTE] Will configure from built-in defaults.
Checking for available remotes: rsync and local, git, mercurial, darcs. Perfect!
... (省略)
Done.
# Run eval $(opam env) to update the current shell environment

haytok@DESKTOP-SK03JO0:~/memory-model$ opam install herdtools7
The following actions will be performed:
... (省略)
∗ installed herdtools7.7.56.3
Done.
# Run eval $(opam env) to update the current shell environment
```

`~/.bashrc` に `eval $(opam config env);` を追記する。追記しないと以下のエラーが発生して悩むことになる。

```bash
haytok@DESKTOP-SK03JO0:~/memory-model$ herd7 --help
herd7: command not found
```

`~/.bashrc` に追記すると、`herd7` コマンドを実行できる。

```bash
haytok@2023-02-26 19:39:52:~/memory-model
>>> herd7 -version
7.56+03, Rev: exported
```

サンプルのコマンドを実行してみると、正常にシミュレーションが完了した。

> SB+fencembonceonces.litmus
> 	This is the fully ordered (again, via smp_mb() version of store buffering, which forms the core of Dekker's mutual-exclusion algorithm.

```bash
haytok@2023-02-26 22:24:42:~/memory-model
>>> herd7 -conf linux-kernel.cfg litmus-tests/SB+fencembonceonces.litmus
Test SB+fencembonceonces Allowed
States 3
0:r0=0; 1:r0=1;
0:r0=1; 1:r0=0;
0:r0=1; 1:r0=1;
No
Witnesses
Positive: 0 Negative: 3
Condition exists (0:r0=0 /\ 1:r0=0)
Observation SB+fencembonceonces Never 0 3
Time SB+fencembonceonces 0.01
Hash=d66d99523e2cac6b06e66f4c995ebb48
```

以上から litmus のプログラムを実行するための準備が完了した。

## 検証

下記のページにある `LITMUS TESTS` を一通り動かしてみて結果を確認しみる。

- [linux/tools/memory-model/litmus-tests at master · torvalds/linux](https://github.com/torvalds/linux/tree/master/tools/memory-model/litmus-tests)

### #0 `SB+fencembonceonces.litmus` RES

シミュレートするスレッド

```c
P0(int *x, int *y)
{
	int r0;

	WRITE_ONCE(*x, 1);
	smp_mb();
	r0 = READ_ONCE(*y);
}

P1(int *x, int *y)
{
	int r0;

	WRITE_ONCE(*y, 1);
	smp_mb();
	r0 = READ_ONCE(*x);
}
```

`smp_mb()` の定義をチラッと確認しておく。

```bash
haytok@2023-03-01 01:30:38:~/memory-model
>>> grep -rn "#define\ssmp_mb(" /home/haytok/linux/ --exclude-dir={riscv,csky,s390,powerpc,parisc,sh,xtensa,loongarch,tools}
/home/haytok/linux/arch/arm64/include/asm/vdso/compat_barrier.h:31:#define smp_mb()     aarch32_smp_mb()
/home/haytok/linux/include/asm-generic/barrier.h:99:#define smp_mb()    do { kcsan_mb(); __smp_mb(); } while (0)
/home/haytok/linux/include/asm-generic/barrier.h:113:#define smp_mb()   barrier()
haytok@2023-03-01 01:30:44:~/memory-model
>>> grep -rn "#define\s__smp_mb(" /home/haytok/linux/ --exclude-dir={riscv,csky,s390,powerpc,parisc,sh,xtensa,loongarch,tools}
/home/haytok/linux/arch/x86/include/asm/barrier.h:57:#define __smp_mb() asm volatile("lock; addl $0,-4(%%" _ASM_SP ")" ::: "memory", "cc")
/home/haytok/linux/arch/arm64/include/asm/barrier.h:116:#define __smp_mb()      dmb(ish)
/home/haytok/linux/arch/arm/include/asm/barrier.h:77:#define __smp_mb() dmb(ish)
/home/haytok/linux/include/asm-generic/barrier.h:85:#define __smp_mb()  mb()
```

`smp_mb()` は memory barrier のことやと思う。なので、本プログラムのそれぞれの鵜スレッドは
それぞれリオーダリングが発生しないと考えられる。

litmus のプログラム (デフォルト) の実行結果

```bash
haytok@2023-03-01 01:33:17:~/memory-model
>>> herd7 -conf linux-kernel.cfg litmus-tests/SB+fencembonceonces.litmus
Test SB+fencembonceonces Allowed
States 3
0:r0=0; 1:r0=1;
0:r0=1; 1:r0=0;
0:r0=1; 1:r0=1;
No
Witnesses
Positive: 0 Negative: 3
Condition exists (0:r0=0 /\ 1:r0=0)
Observation SB+fencembonceonces Never 0 3
Time SB+fencembonceonces 0.01
Hash=d66d99523e2cac6b06e66f4c995ebb48
```

-> この結果は自分が想定した結果やった。

### #1 `S+fencewmbonceonce+poacquireonce.litmus` WIP

シミュレートするスレッド

```c
P0(int *x, int *y)
{
	WRITE_ONCE(*x, 2);
	smp_wmb();
	WRITE_ONCE(*y, 1);
}

P1(int *x, int *y)
{
	int r0;

	r0 = smp_load_acquire(y);
	WRITE_ONCE(*x, 1);
}
```

`smp_wmb()` の定義を kernel のコードから確認する。(多分 write memory barrier のことやと思う。)

```bash
haytok@2023-03-01 00:54:16:~/memory-model
>>> grep -rn "#define\ssmp_wmb" /home/haytok/linux/ --exclude-dir={riscv,csky,s390,powerpc,parisc,sh,xtensa,loongarch,tools}
/home/haytok/linux/arch/arm64/include/asm/vdso/compat_barrier.h:33:#define smp_wmb()    aarch32_smp_wmb()
/home/haytok/linux/include/asm-generic/barrier.h:107:#define smp_wmb()  do { kcsan_wmb(); __smp_wmb(); } while (0)
/home/haytok/linux/include/asm-generic/barrier.h:121:#define smp_wmb()  barrier()
```

- [linux/barrier.h at master · torvalds/linux](https://github.com/torvalds/linux/blob/master/include/asm-generic/barrier.h#L107)

```c
#ifdef CONFIG_SMP

... (省略)

#ifndef smp_wmb
#define smp_wmb()	do { kcsan_wmb(); __smp_wmb(); } while (0)
#endif

... (省略)

#else	/* !CONFIG_SMP */

... (省略)

#ifndef smp_wmb
#define smp_wmb()	barrier()
#endif

#endif	/* CONFIG_SMP */
```

```bash
haytok@2023-03-01 01:16:24:~/memory-model
>>> grep -rn "#define\sbarrier(" /home/haytok/linux/ --exclude-dir={riscv,csky,s390,powerpc,parisc,sh,xtensa,loongarch,tools}
/home/haytok/linux/arch/um/include/shared/user.h:57:#define barrier() __asm__ __volatile__("": : :"memory")
/home/haytok/linux/include/linux/compiler-intel.h:16:#define barrier() __memory_barrier()
haytok@2023-03-01 01:16:45:~/memory-model
>>> grep -rn "#define\s__memory_barrier" /home/haytok/linux/ --exclude-dir={riscv,csky,s390,powerpc,parisc,sh,xtensa,loongarch,tools}
```

-> `barrier()` の定義は見つからんかった ...

```bash
haytok@2023-03-01 01:18:41:~/memory-model
>>> grep -rn "#define\s__smp_wmb" /home/haytok/linux/ --exclude-dir={riscv,csky,s390,powerpc,parisc,sh,xtensa,loongarch,tools}
/home/haytok/linux/arch/x86/include/asm/barrier.h:60:#define __smp_wmb()        barrier()
/home/haytok/linux/arch/arm64/include/asm/barrier.h:118:#define __smp_wmb()     dmb(ishst)
/home/haytok/linux/arch/arm/include/asm/barrier.h:79:#define __smp_wmb()        dmb(ishst)
/home/haytok/linux/include/asm-generic/barrier.h:93:#define __smp_wmb() wmb()
```

-> `wmb()` と `dmb()` の定義を追いたいところだが、一旦置いておく ...

- [ARM Compiler toolchain Assembler Reference Version 4.1](https://developer.arm.com/documentation/dui0489/c/arm-and-thumb-instructions/miscellaneous-instructions/dmb--dsb--and-isb)

> DMB
> Data Memory Barrier acts as a memory barrier. It ensures that all explicit memory accesses that appear in program order before the DMB instruction are observed before any explicit memory accesses that appear in program order after the DMB instruction. It does not affect the ordering of any other instructions executing on the processor.

-> ARM では DMB 命令の前に現れる全ての明示的なメモリアクセスが、DMB 命令の後に現れるあらゆる明示的なメモリアクセスより先に観測されることを保証するとのことなので、`dmb()` を跨いだリオーダリングは発生しないと解釈しました。 

一方、`smp_load_acquire()` の定義は下記に記述されている。

```bash
haytok@2023-03-01 00:53:09:~/memory-model
>>> grep -rn "#define\ssmp_load_acquire" /home/haytok/linux/ --exclude-dir={riscv,csky,s390,powerpc,parisc,sh,xtensa,loongarch,tools}
/home/haytok/linux/include/asm-generic/barrier.h:176:#define smp_load_acquire(p) __smp_load_acquire(p)
/home/haytok/linux/include/asm-generic/barrier.h:203:#define smp_load_acquire(p)
```

- [linux/barrier.h at master · torvalds/linux](https://github.com/torvalds/linux/blob/master/include/asm-generic/barrier.h#L175)

```c
#ifdef CONFIG_SMP

... (省略)

#ifndef smp_load_acquire
#define smp_load_acquire(p) __smp_load_acquire(p)
#endif

... (省略)

#else	/* !CONFIG_SMP */

... (省略)

#ifndef smp_load_acquire
#define smp_load_acquire(p)						\
({									\
	__unqual_scalar_typeof(*p) ___p1 = READ_ONCE(*p);		\
	compiletime_assert_atomic_type(*p);				\
	barrier();							\
	(typeof(*p))___p1;						\
})
#endif

#endif	/* CONFIG_SMP */
```

`__smp_load_acquire()` の定義も確認しておく。

```bash
haytok@2023-03-01 00:54:06:~/memory-model
>>> grep -rn "#define\s__smp_load_acquire" /home/haytok/linux/ --exclude-dir={riscv,csky,s390,powerpc,parisc,sh,xtensa,loongarch,tool
s}
/home/haytok/linux/arch/x86/include/asm/barrier.h:70:#define __smp_load_acquire(p)                                              \
/home/haytok/linux/arch/sparc/include/asm/barrier_64.h:48:#define __smp_load_acquire(p)                                         \
/home/haytok/linux/arch/arm64/include/asm/barrier.h:155:#define __smp_load_acquire(p)                                           \
/home/haytok/linux/arch/ia64/include/asm/barrier.h:63:#define __smp_load_acquire(p)                                             \
/home/haytok/linux/arch/alpha/include/asm/barrier.h:9:#define __smp_load_acquire(p)                                             \
/home/haytok/linux/include/asm-generic/barrier.h:148:#define __smp_load_acquire(p)
```

-> この出力結果から、`__smp_load_acquire()` の定義は architecture specific っぽいのがわかる。

x86 やと、定義は以下にある。

- [linux/barrier.h at master · torvalds/linux](https://github.com/torvalds/linux/blob/master/arch/x86/include/asm/barrier.h#L70)

```c
#define __smp_load_acquire(p)						\
({									\
	typeof(*p) ___p1 = READ_ONCE(*p);				\
	compiletime_assert_atomic_type(*p);				\
	barrier();							\
	___p1;								\
})
```

-> `barrier.h` にあった定義と同じ感じである。

arm の定義も確認しておく。

- [linux/barrier.h at master · torvalds/linux](https://github.com/torvalds/linux/blob/master/arch/arm64/include/asm/barrier.h#L158)

```c
#define __smp_load_acquire(p)						\
({									\
	union { __unqual_scalar_typeof(*p) __val; char __c[1]; } __u;	\
	typeof(p) __p = (p);						\
	compiletime_assert_atomic_type(*p);				\
	kasan_check_read(__p, sizeof(*p));				\
	switch (sizeof(*p)) {						\
	case 1:								\
		asm volatile ("ldarb %w0, %1"				\
			: "=r" (*(__u8 *)__u.__c)			\
			: "Q" (*__p) : "memory");			\
		break;							\
	case 2:								\
		asm volatile ("ldarh %w0, %1"				\
			: "=r" (*(__u16 *)__u.__c)			\
			: "Q" (*__p) : "memory");			\
		break;							\
	case 4:								\
		asm volatile ("ldar %w0, %1"				\
			: "=r" (*(__u32 *)__u.__c)			\
			: "Q" (*__p) : "memory");			\
		break;							\
	case 8:								\
		asm volatile ("ldar %0, %1"				\
			: "=r" (*(__u64 *)__u.__c)			\
			: "Q" (*__p) : "memory");			\
		break;							\
	}								\
	(typeof(*p))__u.__val;						\
})
```

マクロの定義の構造自体は同じ感じで、arm のメモリバリア関連の命令の `ldar` を使用して x86 でいうところの `barrier()` を実装している。なお、`ldar` は「この命令以降のメモリ読み書き命令がこの命令よりも先に実行されないことを保証」する命令である。 (ref. 並行プログラミング)

litmus のプログラム (デフォルト) の実行結果

```bash
haytok@2023-02-28 01:43:17:~/memory-model
>>> herd7 -conf linux-kernel.cfg litmus-tests/S+fencewmbonceonce+poacquireonce.litmus
Test S+fencewmbonceonce+poacquireonce Allowed
States 3
1:r0=0; [x]=1;
1:r0=0; [x]=2;
1:r0=1; [x]=1;
No
Witnesses
Positive: 0 Negative: 3
Condition exists ([x]=2 /\ 1:r0=1)
Observation S+fencewmbonceonce+poacquireonce Never 0 3
Time S+fencewmbonceonce+poacquireonce 0.01
Hash=c9ba02a9b2cbfb9a4d745aa4e0e586cb
```

`smp_load_acquire()` を `READ_ONCE()` に変えたときの litmus の結果 (検証プログラム 1)

```bash
haytok@2023-02-28 01:44:15:~/memory-model
>>> herd7 -conf linux-kernel.cfg litmus-tests/S+fencewmbonceonce+poacquireonce.litmus
Test S+fencewmbonceonce+poacquireonce Allowed
States 4
1:r0=0; [x]=1;
1:r0=0; [x]=2;
1:r0=1; [x]=1;
1:r0=1; [x]=2;
Ok
Witnesses
Positive: 1 Negative: 3
Condition exists ([x]=2 /\ 1:r0=1)
Observation S+fencewmbonceonce+poacquireonce Sometimes 1 3
Time S+fencewmbonceonce+poacquireonce 0.01
Hash=d5b9219bc582c5ff010f5a70d4590983
```

-> 取りうる状態が 1 つ増えた。この場合やと、`r0 = READ_ONCE(*y);` と `WRITE_ONCE(*x, 1);` の処理がリオーダリングして `WRITE_ONCE(*x, 1);` の処理が `r0 = READ_ONCE(*y);` の前、例えばスレッド P0 における `WRITE_ONCE(*x, 2);` より前に実行される可能性が考えられる。うーん、[lwn の記事](https://lwn.net/Articles/844224/) 的には `datum = smp_load_acquire(&message);` は `datum = READ_ONCE(message);smp_rmb();` と同様の処理とも読み取れるが、kernel のコード的にホンマか？となっている。疑問に思っていたのは `smp_load_acquire()` の内部の `barrier()` によってリオーダリングが発生しないと考えたが、合っているやろか ... マクロの展開が自分的にはややこしくて悩んだ原因やった。

`smp_load_acquire()` の内部の `barrier()` を模した検証プログラムを実装してみた。(検証プログラム 2)

```c
#include <stdio.h>

#define __scalar_type_to_expr_cases(type)                               \
                unsigned type:  (unsigned type)0,                       \
                signed type:    (signed type)0

#define __unqual_scalar_typeof(x) typeof(                               \
                _Generic((x),                                           \
                         char:  (char)0,                                \
                         __scalar_type_to_expr_cases(char),             \
                         __scalar_type_to_expr_cases(short),            \
                         __scalar_type_to_expr_cases(int),              \
                         __scalar_type_to_expr_cases(long),             \
                         __scalar_type_to_expr_cases(long long),        \
                         default: (x)))

#define __READ_ONCE(x)  (*(const volatile __unqual_scalar_typeof(x) *)&(x))

#define READ_ONCE(x)                            \
({                                  \
    __READ_ONCE(x);                         \
})

// 実装を参考にした kernel で定義された定義
// #define smp_load_acquire(p)						\
// ({									\
// 	__unqual_scalar_typeof(*p) ___p1 = READ_ONCE(*p);		\
// 	compiletime_assert_atomic_type(*p);				\
// 	barrier();							\
// 	(typeof(*p))___p1;						\
// })

#define smp_load_acquire(p)						\
({									\
	typeof(p) value = READ_ONCE(p); \
    puts("In smp_load_acquire"); \
    value + 1;						\
})

void main(void) {
    int value = 0;
    typeof(value) updated_value;

    updated_value = value;
    updated_value = smp_load_acquire(updated_value);

    printf("value is %d, updated_value is %d\n", value, updated_value);
}
```

```bash
haytok@2023-03-01 00:33:36:~/memory-model
>>> gcc -o test test.c && ./test
In smp_load_acquire
value is 0, updated_value is 1
```

`smp_load_acquire()` の内部で定義された `puts()` は呼び出され、マクロの引数として受け取った値に +1 して値を返す挙動をしている。

やから、この検証プログラム 1 と 2 の挙動から、やっぱり litmus のプログラムで実装されている `smp_load_acquire()` と `WRITE_ONCE()` はリオーダリングしないといっても良いと判断しました。

LWN の記事 ([An introduction to lockless algorithms [LWN.net]](https://lwn.net/Articles/844224/)) の "The message-passing pattern" もちゃんと読み直さなあかん ...

### #2 `S+poonceonces.litmus` RES

シミュレートするスレッド

```c
P0(int *x, int *y)
{
	WRITE_ONCE(*x, 2);
	WRITE_ONCE(*y, 1);
}

P1(int *x, int *y)
{
	int r0;

	r0 = READ_ONCE(*y);
	WRITE_ONCE(*x, 1);
}
```

これのシュミレーションでは、同一スレッドにおける値の依存関係はなく、バリア系の命令はないため、どちらのスレッドでもリオーダリングが発生し、4 パターンの取りうる結果がある。

```bash
haytok@2023-03-01 21:59:48:~/memory-model
>>> herd7 -conf linux-kernel.cfg litmus-tests/S+poonceonces.litmus
Test S+poonceonces Allowed
States 4
1:r0=0; [x]=1;
1:r0=0; [x]=2;
1:r0=1; [x]=1;
1:r0=1; [x]=2;
Ok
Witnesses
Positive: 1 Negative: 3
Condition exists ([x]=2 /\ 1:r0=1)
Observation S+poonceonces Sometimes 1 3
Time S+poonceonces 0.01
Hash=696942ff9c74183ff5d97898969e38ca
```

### #3 `SB+poonceonces.litmus` done

シミュレートするスレッド

```c
P0(int *x, int *y)
{
	int r0;

	WRITE_ONCE(*x, 1);
	r0 = READ_ONCE(*y);
}

P1(int *x, int *y)
{
	int r0;

	WRITE_ONCE(*y, 1);
	r0 = READ_ONCE(*x);
}
```

これのシュミレーションでは、同一スレッドにおける値の依存関係はなく、バリア系の命令はないため、どちらのスレッドでもリオーダリングが発生し、4 パターンの取りうる結果がある。

```bash
haytok@2023-03-01 22:12:47:~/memory-model
>>> herd7 -conf linux-kernel.cfg litmus-tests/SB+poonceonces.litmus
Test SB+poonceonces Allowed
States 4
0:r0=0; 1:r0=0;
0:r0=0; 1:r0=1;
0:r0=1; 1:r0=0;
0:r0=1; 1:r0=1;
Ok
Witnesses
Positive: 1 Negative: 3
Condition exists (0:r0=0 /\ 1:r0=0)
Observation SB+poonceonces Sometimes 1 3
Time SB+poonceonces 0.01
Hash=d2b6ca86cddfad6178a05767f57fafbf
```

### #4 `SB+rfionceonce-poonceonces.litmus` WIP

シミュレートするスレッド

```c
P0(int *x, int *y)
{
	int r1;
	int r2;

	WRITE_ONCE(*x, 1);
	r1 = READ_ONCE(*x);
	r2 = READ_ONCE(*y);
}

P1(int *x, int *y)
{
	int r3;
	int r4;

	WRITE_ONCE(*y, 1);
	r3 = READ_ONCE(*y);
	r4 = READ_ONCE(*x);
}
```

r1 と r3 に格納される値はそれぞれ、変数 x と y における依存関係があるのでリオーダリングが発生しない。そのため、r1 と r3 に格納される値はそれぞれ 1 である。あとは、#3 とかと同様に考えれば良い。

```bash
haytok@2023-03-01 22:17:17:~/memory-model
>>> herd7 -conf linux-kernel.cfg litmus-tests/SB+rfionceonce-poonceonces.litmus
Test SB+rfionceonce-poonceonces Allowed
States 4
0:r1=1; 0:r2=0; 1:r3=1; 1:r4=0; [x]=1; [y]=1;
0:r1=1; 0:r2=0; 1:r3=1; 1:r4=1; [x]=1; [y]=1;
0:r1=1; 0:r2=1; 1:r3=1; 1:r4=0; [x]=1; [y]=1;
0:r1=1; 0:r2=1; 1:r3=1; 1:r4=1; [x]=1; [y]=1;
Ok
Witnesses
Positive: 1 Negative: 3
Condition exists (0:r2=0 /\ 1:r4=0)
Observation SB+rfionceonce-poonceonces Sometimes 1 3
Time SB+rfionceonce-poonceonces 0.01
Hash=40de8418c4b395388f6501cafd1ed38d
```

### #5 `WRC+poonceonces+Once.litmus` RES

シミュレートするスレッド

```c
P0(int *x)
{
	WRITE_ONCE(*x, 1);
}

P1(int *x, int *y)
{
	int r0;

	r0 = READ_ONCE(*x);
	WRITE_ONCE(*y, 1);
}

P2(int *x, int *y)
{
	int r0;
	int r1;

	r0 = READ_ONCE(*y);
	r1 = READ_ONCE(*x);
}
```

メモリバリアのプログラムが差し込まれていないので、リオーダリングがたくさん発生しそう。つまり、取りうる値分の組み合わせが生じる。

litmus のプログラム (デフォルト) の実行結果

```bash
haytok@2023-02-27 22:16:37:~/memory-model
>>>  herd7 -conf linux-kernel.cfg litmus-tests/WRC+poonceonces+Once.litmus
Test WRC+poonceonces+Once Allowed
States 8
1:r0=0; 2:r0=0; 2:r1=0;
1:r0=0; 2:r0=0; 2:r1=1;
1:r0=0; 2:r0=1; 2:r1=0;
1:r0=0; 2:r0=1; 2:r1=1;
1:r0=1; 2:r0=0; 2:r1=0;
1:r0=1; 2:r0=0; 2:r1=1;
1:r0=1; 2:r0=1; 2:r1=0;
1:r0=1; 2:r0=1; 2:r1=1;
Ok
Witnesses
Positive: 1 Negative: 7
Condition exists (1:r0=1 /\ 2:r0=1 /\ 2:r1=0)
Observation WRC+poonceonces+Once Sometimes 1 7
Time WRC+poonceonces+Once 0.01
Hash=fb66830df5109eaa42fdf0150ba74c5e
```

### #6 `WRC+pooncerelease+fencermbonceonce+Once.litmus` WIP

シミュレートするスレッド

```c
P0(int *x)
{
	WRITE_ONCE(*x, 1);
}

P1(int *x, int *y)
{
	int r0;

	r0 = READ_ONCE(*x);
	smp_store_release(y, 1);
}

P2(int *x, int *y)
{
	int r0;
	int r1;

	r0 = READ_ONCE(*y);
	smp_rmb();
	r1 = READ_ONCE(*x);
}
```

```bash
haytok@2023-03-01 22:35:33:~/memory-model
>>> herd7 -conf linux-kernel.cfg litmus-tests/WRC+pooncerelease+fencermbonceonce+Once.litmus
Test WRC+pooncerelease+fencermbonceonce+Once Allowed
States 7
1:r0=0; 2:r0=0; 2:r1=0;
1:r0=0; 2:r0=0; 2:r1=1;
1:r0=0; 2:r0=1; 2:r1=0;
1:r0=0; 2:r0=1; 2:r1=1;
1:r0=1; 2:r0=0; 2:r1=0;
1:r0=1; 2:r0=0; 2:r1=1;
1:r0=1; 2:r0=1; 2:r1=1;
No
Witnesses
Positive: 0 Negative: 7
Condition exists (1:r0=1 /\ 2:r0=1 /\ 2:r1=0)
Observation WRC+pooncerelease+fencermbonceonce+Once Never 0 7
Time WRC+pooncerelease+fencermbonceonce+Once 0.01
Hash=7b9a1a22fbb821d557ea6448eb64707b
```

-> 全ての場合分けを考えたが、まともに計算するのがキツ過ぎて諦めた ...

## #7 `Z6.0+pooncelock+pooncelock+pombonce.litmus` UNA

Pass ...

## #8 `Z6.0+pooncelock+poonceLock+pombonce.litmus` UNA

Pass ...

## #9 `Z6.0+pooncerelease+poacquirerelease+fencembonceonce.litmus` UNA

Pass ...

## #10 `CoRR+poonceonce+Once.litmus` RES

シミュレートするスレッド

```c
P0(int *x)
{
	WRITE_ONCE(*x, 1);
}

P1(int *x)
{
	int r0;
	int r1;

	r0 = READ_ONCE(*x);
	r1 = READ_ONCE(*x);
}
```

P1 の r0 と r1 には依存関係がある。

litmus のプログラム (デフォルト) の実行結果

```bash
haytok@2023-03-02 01:35:31:~/memory-model
>>> herd7 -conf linux-kernel.cfg litmus-tests/CoRR+poonceonce+Once.litmus
Test CoRR+poonceonce+Once Allowed
States 3
1:r0=0; 1:r1=0;
1:r0=0; 1:r1=1;
1:r0=1; 1:r1=1;
No
Witnesses
Positive: 0 Negative: 3
Condition exists (1:r0=1 /\ 1:r1=0)
Observation CoRR+poonceonce+Once Never 0 3
Time CoRR+poonceonce+Once 0.01
Hash=378326ae44de3653b1ba8ac124001235
```

P1 における `r0 = READ_ONCE(*x);` と `r1 = READ_ONCE(*x);` の間に `smp_rmb();` を挟んでも挟まんくても結果は変わらんかった。(<- 気づいたときにちょいちょいいじるとおもろい。)

```c
P1(int *x)
{
	int r0;
	int r1;

	r0 = READ_ONCE(*x);
	smp_rmb();
	r1 = READ_ONCE(*x);
}
```

このことからも元のベースプログラムにおいても二つの処理のリオーダリングが発生しないことが明らかになった。

## #11 `CoRW+poonceonce+Once.litmus` RES

シミュレートするスレッド

```c
P0(int *x)
{
	int r0;

	r0 = READ_ONCE(*x);
	WRITE_ONCE(*x, 1);
}

P1(int *x)
{
	WRITE_ONCE(*x, 2);
}
```

litmus のプログラム (デフォルト) の実行結果

```bash
haytok@2023-03-03 01:16:41:~/memory-model
>>> herd7 -conf linux-kernel.cfg litmus-tests/CoRW+poonceonce+Once.litmus
Test CoRW+poonceonce+Once Allowed
States 3
0:r0=0; [x]=1;
0:r0=0; [x]=2;
0:r0=2; [x]=1;
No
Witnesses
Positive: 0 Negative: 3
Condition exists ([x]=2 /\ 0:r0=2)
Observation CoRW+poonceonce+Once Never 0 3
Time CoRW+poonceonce+Once 0.01
Hash=342ea0846b39cffa347927f119efd044
```

P0 の `r0 = READ_ONCE(*x);` と `WRITE_ONCE(*x, 1);` は依存関係があるので、リオーダリングが発生しないと考えられるので、3 通りのパターンしかない。

## #12 `CoWR+poonceonce+Once.litmus` RES

シミュレートするスレッド

```c
P0(int *x)
{
	int r0;

	WRITE_ONCE(*x, 1);
	r0 = READ_ONCE(*x);
}

P1(int *x)
{
	WRITE_ONCE(*x, 2);
}
```

litmus のプログラム (デフォルト) の実行結果

```bash
haytok@2023-03-03 01:44:43:~/memory-model
>>> herd7 -conf linux-kernel.cfg litmus-tests/CoWR+poonceonce+Once.litmus
Test CoWR+poonceonce+Once Allowed
States 3
0:r0=1; [x]=1;
0:r0=1; [x]=2;
0:r0=2; [x]=2;
No
Witnesses
Positive: 0 Negative: 3
Condition exists ([x]=1 /\ 0:r0=2)
Observation CoWR+poonceonce+Once Never 0 3
Time CoWR+poonceonce+Once 0.01
Hash=3f8770b94cb57e6487da7b89ad43ecb3
```

`WRITE_ONCE(*x, 1);` と `r0 = READ_ONCE(*x);` は依存関係があるので、リオーダリングが発生しないと考えられるので、3 通りのパターンしかない。

## #13 `CoWW+poonceonce.litmus` UNA

シミュレートするスレッド

```c
P0(int *x)
{
	WRITE_ONCE(*x, 1);
	WRITE_ONCE(*x, 2);
}
```

litmus のプログラム (デフォルト) の実行結果

```bash
haytok@2023-03-03 01:48:00:~/memory-model
>>> herd7 -conf linux-kernel.cfg litmus-tests/CoWW+poonceonce.litmus
Test CoWW+poonceonce Allowed
States 1
[x]=2;
No
Witnesses
Positive: 0 Negative: 1
Condition exists ([x]=1)
Observation CoWW+poonceonce Never 0 1
Time CoWW+poonceonce 0.01
Hash=260aac15e0895506fb610570ef05debc
```

`WRITE_ONCE(*x, 1);` と `WRITE_ONCE(*x, 2);` は依存関係があるので、リオーダリングが発生しないと考えられるので、1 通りのパターンしかない。

## #14 `IRIW+fencembonceonces+OnceOnce.litmus` UNA

シミュレートするスレッド

```c
P0(int *x)
{
	WRITE_ONCE(*x, 1);
}

P1(int *x, int *y)
{
	int r0;
	int r1;

	r0 = READ_ONCE(*x);
	smp_mb();
	r1 = READ_ONCE(*y);
}

P2(int *y)
{
	WRITE_ONCE(*y, 1);
}

P3(int *x, int *y)
{
	int r0;
	int r1;

	r0 = READ_ONCE(*y);
	smp_mb();
	r1 = READ_ONCE(*x);
}
```

Pass …

<!-- litmus のプログラム (デフォルト) の実行結果

```bash

``` -->

## #15 `IRIW+poonceonces+OnceOnce.litmus` UNA

シミュレートするスレッド

```c
P0(int *x)
{
	WRITE_ONCE(*x, 1);
}

P1(int *x, int *y)
{
	int r0;
	int r1;

	r0 = READ_ONCE(*x);
	r1 = READ_ONCE(*y);
}

P2(int *y)
{
	WRITE_ONCE(*y, 1);
}

P3(int *x, int *y)
{
	int r0;
	int r1;

	r0 = READ_ONCE(*y);
	r1 = READ_ONCE(*x);
}
```

Pass …

<!-- litmus のプログラム (デフォルト) の実行結果

```bash

``` -->

## #16 `ISA2+pooncelock+pooncelock+pombonce.litmus` UNA

シミュレートするスレッド

```c
P0(int *x, int *y, spinlock_t *mylock)
{
	spin_lock(mylock);
	WRITE_ONCE(*x, 1);
	WRITE_ONCE(*y, 1);
	spin_unlock(mylock);
}

P1(int *y, int *z, spinlock_t *mylock)
{
	int r0;

	spin_lock(mylock);
	r0 = READ_ONCE(*y);
	WRITE_ONCE(*z, 1);
	spin_unlock(mylock);
}

P2(int *x, int *z)
{
	int r1;
	int r2;

	r2 = READ_ONCE(*z);
	smp_mb();
	r1 = READ_ONCE(*x);
}
```

Pass ...

<!-- litmus のプログラム (デフォルト) の実行結果

```bash

``` -->

## #17 `ISA2+poonceonces.litmus` UNA

シミュレートするスレッド

```c
P0(int *x, int *y)
{
	WRITE_ONCE(*x, 1);
	WRITE_ONCE(*y, 1);
}

P1(int *y, int *z)
{
	int r0;

	r0 = READ_ONCE(*y);
	WRITE_ONCE(*z, 1);
}

P2(int *x, int *z)
{
	int r0;
	int r1;

	r0 = READ_ONCE(*z);
	r1 = READ_ONCE(*x);
}
```

Pass ...

<!-- litmus のプログラム (デフォルト) の実行結果

```bash

``` -->

## #18 `ISA2+pooncerelease+poacquirerelease+poacquireonce.litmus` UNA

シミュレートするスレッド

```c
P0(int *x, int *y)
{
	WRITE_ONCE(*x, 1);
	smp_store_release(y, 1);
}

P1(int *y, int *z)
{
	int r0;

	r0 = smp_load_acquire(y);
	smp_store_release(z, 1);
}

P2(int *x, int *z)
{
	int r0;
	int r1;

	r0 = smp_load_acquire(z);
	r1 = READ_ONCE(*x);
}
```

Pass ...

<!-- litmus のプログラム (デフォルト) の実行結果

```bash

``` -->

## #19 `LB+fencembonceonce+ctrlonceonce.litmus` RES

シミュレートするスレッド

```c
P0(int *x, int *y)
{
	int r0;

	r0 = READ_ONCE(*x);
	if (r0)
		WRITE_ONCE(*y, 1);
}

P1(int *x, int *y)
{
	int r0;

	r0 = READ_ONCE(*y);
	smp_mb();
	WRITE_ONCE(*x, 1);
}
```

litmus のプログラム (デフォルト) の実行結果

```bash
haytok@2023-03-12 21:06:52:~/memory-model
>>> herd7 -conf linux-kernel.cfg litmus-tests/LB+fencembonceonce+ctrlonceonce.litmus
Test LB+fencembonceonce+ctrlonceonce Allowed
States 2
0:r0=0; 1:r0=0;
0:r0=1; 1:r0=0;
No
Witnesses
Positive: 0 Negative: 2
Condition exists (0:r0=1 /\ 1:r0=1)
Observation LB+fencembonceonce+ctrlonceonce Never 0 2
Time LB+fencembonceonce+ctrlonceonce 0.01
Hash=e5260556f6de495fd39b556d1b831c3b
```

P0 のスレッドでは変数 r0 に対して依存関係があるので、リオーダリングが発生しない。また、P1 では smp_mb() が呼び出されているので、リオーダリングが発生しない。

## #20 `LB+poacquireonce+pooncerelease.litmus` RES (Good Question !!!)

LWN で紹介されていたケース ([An introduction to lockless algorithms [LWN.net]](https://lwn.net/Articles/844224/)) と似ていた。

シミュレートするスレッド

```c
P0(int *x, int *y)
{
	int r0;

	r0 = READ_ONCE(*x);
	smp_store_release(y, 1);
}

P1(int *x, int *y)
{
	int r0;

	r0 = smp_load_acquire(y);
	WRITE_ONCE(*x, 1);
}
```

litmus のプログラム (デフォルト) の実行結果

```bash
haytok@2023-03-12 21:18:47:~/memory-model
>>> herd7 -conf linux-kernel.cfg litmus-tests/LB+poacquireonce+pooncerelease.litmus
Test LB+poacquireonce+pooncerelease Allowed
States 3
0:r0=0; 1:r0=0;
0:r0=0; 1:r0=1;
0:r0=1; 1:r0=0;
No
Witnesses
Positive: 0 Negative: 3
Condition exists (0:r0=1 /\ 1:r0=1)
Observation LB+poacquireonce+pooncerelease Never 0 3
Time LB+poacquireonce+pooncerelease 0.01
Hash=b801d815f44d02d33711734a05577728
```

LWN の記事の読み込みが浅かったが、必ずしも READ_ONCE() -> smp_store_release() -> smo_load_acquire() -> WRITE_ONCE() の順序で処理が実行されるわけではないことが明らかになった。これは、各スレッドの ro の値から確認できた。

## #21 `LB+poonceonces.litmus` RES

シミュレートするスレッド

```c
P0(int *x, int *y)
{
	int r0;

	r0 = READ_ONCE(*x);
	WRITE_ONCE(*y, 1);
}

P1(int *x, int *y)
{
	int r0;

	r0 = READ_ONCE(*y);
	WRITE_ONCE(*x, 1);
}
```

litmus のプログラム (デフォルト) の実行結果

```bash
haytok@2023-03-12 21:23:26:~/memory-model
>>> herd7 -conf linux-kernel.cfg litmus-tests/LB+poonceonces.litmus
Test LB+poonceonces Allowed
States 4
0:r0=0; 1:r0=0;
0:r0=0; 1:r0=1;
0:r0=1; 1:r0=0;
0:r0=1; 1:r0=1;
Ok
Witnesses
Positive: 1 Negative: 3
Condition exists (0:r0=1 /\ 1:r0=1)
Observation LB+poonceonces Sometimes 1 3
Time LB+poonceonces 0.01
Hash=d96b009b18c3b7a0f61fc31b99c956d4
```

全ての通りのリオーダリングが発生するケースだった。

## #22 `LB+unlocklockonceonce+poacquireonce.litmus` WIP

> If two locked critical sections execute on the same CPU, all accesses in the first must execute before any accesses in the second, even if the critical sections are protected by different locks.  Note: Even when a write executes before a read, their memory effects can be reordered from the viewpoint of another CPU (the kind of reordering allowed by TSO).

コメントを読んだ感じ、同一 CPU 上で実行される処理内でロックされた 2 つのクリティカルセクションが実行される場合、順番に実行されるとある。なので、#20 と同様の結果が得られると思われる。

シミュレートするスレッド

```c
P0(spinlock_t *s, spinlock_t *t, int *x, int *y)
{
	int r1;

	spin_lock(s);
	r1 = READ_ONCE(*x);
	spin_unlock(s);
	spin_lock(t);
	WRITE_ONCE(*y, 1);
	spin_unlock(t);
}

P1(int *x, int *y)
{
	int r2;

	r2 = smp_load_acquire(y);
	WRITE_ONCE(*x, 1);
}
```

litmus のプログラム (デフォルト) の実行結果

```bash
haytok@2023-03-12 21:30:59:~/memory-model
>>> herd7 -conf linux-kernel.cfg litmus-tests/LB+unlocklockonceonce+poacquireonce.litmus
Test LB+unlocklockonceonce+poacquireonce Allowed
States 3
0:r1=0; 1:r2=0;
0:r1=0; 1:r2=1;
0:r1=1; 1:r2=0;
No
Witnesses
Positive: 0 Negative: 3
Condition exists (0:r1=1 /\ 1:r2=1)
Observation LB+unlocklockonceonce+poacquireonce Never 0 3
Time LB+unlocklockonceonce+poacquireonce 0.01
Hash=da6330e658ae65e07d480639bf637dd7
```

やはり、その結果になった。ただ、理解が合っているかどうかは有識者に出来たら確認したい。

## #23 `MP+fencewmbonceonce+fencermbonceonce.litmus` RES

シミュレートするスレッド

```c
P0(int *buf, int *flag) // Producer
{
	WRITE_ONCE(*buf, 1);
	smp_wmb();
	WRITE_ONCE(*flag, 1);
}

P1(int *buf, int *flag) // Consumer
{
	int r0;
	int r1;

	r0 = READ_ONCE(*flag);
	smp_rmb();
	r1 = READ_ONCE(*buf);
}
```

litmus のプログラム (デフォルト) の実行結果

```bash
haytok@2023-03-12 21:42:18:~/memory-model
>>> herd7 -conf linux-kernel.cfg litmus-tests/MP+fencewmbonceonce+fencermbonceonce.litmus
Test MP+fencewmbonceonce+fencermbonceonce Allowed
States 3
1:r0=0; 1:r1=0;
1:r0=0; 1:r1=1;
1:r0=1; 1:r1=1;
No
Witnesses
Positive: 0 Negative: 3
Condition exists (1:r0=1 /\ 1:r1=0)
Observation MP+fencewmbonceonce+fencermbonceonce Never 0 3
Time MP+fencewmbonceonce+fencermbonceonce 0.01
Hash=7e451c2d514abe8532fb9eb15fcc46c6
```

想定された結果になったのを確認することができた。

## #24 `MP+onceassign+derefonce.litmus` UNA

シミュレートするスレッド

```c
P0(int *x, int **p) // Producer
{
	WRITE_ONCE(*x, 1);
	rcu_assign_pointer(*p, x);
}

P1(int *x, int **p) // Consumer
{
	int *r0;
	int r1;

	rcu_read_lock();
	r0 = rcu_dereference(*p);
	r1 = READ_ONCE(*r0);
	rcu_read_unlock();
}
```

Pass ... (RCU 周りは全く勉強していないので ... :()

<!-- litmus のプログラム (デフォルト) の実行結果

```bash

``` -->

## #25 `MP+polockmbonce+poacquiresilsil.litmus` UNA

> Do spinlocks combined with smp_mb__after_spinlock() provide order to outside observers using spin_is_locked() to sense the lock-held state, ordered by acquire?  Note that when the first spin_is_locked() returns false and the second true, we know that the smp_load_acquire() executed before the lock was acquired (loosely speaking).

シミュレートするスレッド

```c
P0(spinlock_t *lo, int *x) // Producer
{
	spin_lock(lo);
	smp_mb__after_spinlock();
	WRITE_ONCE(*x, 1);
	spin_unlock(lo);
}

P1(spinlock_t *lo, int *x) // Consumer
{
	int r1;
	int r2;
	int r3;

	r1 = smp_load_acquire(x);
	r2 = spin_is_locked(lo);
	r3 = spin_is_locked(lo);
}
```

Pass ... (複雑すぎてわからん ...)

<!-- litmus のプログラム (デフォルト) の実行結果

```bash

``` -->

## #26 `MP+polockonce+poacquiresilsil.litmus` UNA

シミュレートするスレッド

```c
P0(spinlock_t *lo, int *x) // Producer
{
	spin_lock(lo);
	WRITE_ONCE(*x, 1);
	spin_unlock(lo);
}

P1(spinlock_t *lo, int *x) // Consumer
{
	int r1;
	int r2;
	int r3;

	r1 = smp_load_acquire(x);
	r2 = spin_is_locked(lo);
	r3 = spin_is_locked(lo);
}
```

Pass ... (複雑すぎてわからん ...)

<!-- litmus のプログラム (デフォルト) の実行結果

```bash

``` -->

## #27 `MP+polocks.litmus` UNA

シミュレートするスレッド

```c
P0(int *buf, int *flag, spinlock_t *mylock) // Producer
{
	WRITE_ONCE(*buf, 1);
	spin_lock(mylock);
	WRITE_ONCE(*flag, 1);
	spin_unlock(mylock);
}

P1(int *buf, int *flag, spinlock_t *mylock) // Consumer
{
	int r0;
	int r1;

	spin_lock(mylock);
	r0 = READ_ONCE(*flag);
	spin_unlock(mylock);
	r1 = READ_ONCE(*buf);
}
```

Pass ...

<!-- litmus のプログラム (デフォルト) の実行結果

```bash

``` -->

## #28 `MP+poonceonces.litmus` RES

この場合、双方のスレッドでリオーダリングが発生するので、全ての変数のパターンが発生する。

シミュレートするスレッド

```c
P0(int *buf, int *flag) // Producer
{
	WRITE_ONCE(*buf, 1);
	WRITE_ONCE(*flag, 1);
}

P1(int *buf, int *flag) // Consumer
{
	int r0;
	int r1;

	r0 = READ_ONCE(*flag);
	r1 = READ_ONCE(*buf);
}
```

litmus のプログラム (デフォルト) の実行結果

```bash
haytok@2023-03-12 22:03:39:~/memory-model
>>> herd7 -conf linux-kernel.cfg litmus-tests/MP+poonceonces.litmus
Test MP+poonceonces Allowed
States 4
1:r0=0; 1:r1=0;
1:r0=0; 1:r1=1;
1:r0=1; 1:r1=0;
1:r0=1; 1:r1=1;
Ok
Witnesses
Positive: 1 Negative: 3
Condition exists (1:r0=1 /\ 1:r1=0)
Observation MP+poonceonces Sometimes 1 3
Time MP+poonceonces 0.02
Hash=c0ebd8ca556580d772ac73303c4c4f84
```

## #29 `MP+pooncerelease+poacquireonce.litmus` RES

#23 と同じ結果になると思われる。

シミュレートするスレッド

```c
P0(int *buf, int *flag) // Producer
{
	WRITE_ONCE(*buf, 1);
	smp_store_release(flag, 1);
}

P1(int *buf, int *flag) // Consumer
{
	int r0;
	int r1;

	r0 = smp_load_acquire(flag);
	r1 = READ_ONCE(*buf);
}
```

litmus のプログラム (デフォルト) の実行結果

```bash
haytok@2023-03-12 22:04:36:~/memory-model
>>> herd7 -conf linux-kernel.cfg litmus-tests/MP+pooncerelease+poacquireonce.litmus
Test MP+pooncerelease+poacquireonce Allowed
States 3
1:r0=0; 1:r1=0;
1:r0=0; 1:r1=1;
1:r0=1; 1:r1=1;
No
Witnesses
Positive: 0 Negative: 3
Condition exists (1:r0=1 /\ 1:r1=0)
Observation MP+pooncerelease+poacquireonce Never 0 3
Time MP+pooncerelease+poacquireonce 0.01
Hash=f259d8efc86e0b40c7168bf58524ab49
```

確かに、同じになったのが確認できた。

## #30 `MP+porevlocks.litmus` UNA

シミュレートするスレッド

```c
P0(int *buf, int *flag, spinlock_t *mylock) // Consumer
{
	int r0;
	int r1;

	r0 = READ_ONCE(*flag);
	spin_lock(mylock);
	r1 = READ_ONCE(*buf);
	spin_unlock(mylock);
}

P1(int *buf, int *flag, spinlock_t *mylock) // Producer
{
	spin_lock(mylock);
	WRITE_ONCE(*buf, 1);
	spin_unlock(mylock);
	WRITE_ONCE(*flag, 1);
}
```

Pass ...

<!-- litmus のプログラム (デフォルト) の実行結果

```bash

``` -->

## #31 `MP+unlocklockonceonce+fencermbonceonce.litmus` UNA

シミュレートするスレッド

```c
P0(spinlock_t *s, spinlock_t *t, int *x, int *y)
{
	spin_lock(s);
	WRITE_ONCE(*x, 1);
	spin_unlock(s);
	spin_lock(t);
	WRITE_ONCE(*y, 1);
	spin_unlock(t);
}

P1(int *x, int *y)
{
	int r1;
	int r2;

	r1 = READ_ONCE(*y);
	smp_rmb();
	r2 = READ_ONCE(*x);
}
```

Pass ...

<!-- litmus のプログラム (デフォルト) の実行結果

```bash

``` -->

## #32 `R+fencembonceonces.litmus` RES

両方のスレッドでメモリバリアが機能する。

シミュレートするスレッド

```c
P0(int *x, int *y)
{
	WRITE_ONCE(*x, 1);
	smp_mb();
	WRITE_ONCE(*y, 1);
}

P1(int *x, int *y)
{
	int r0;

	WRITE_ONCE(*y, 2);
	smp_mb();
	r0 = READ_ONCE(*x);
}
```

litmus のプログラム (デフォルト) の実行結果

```bash
haytok@2023-03-12 22:16:12:~/memory-model
>>> herd7 -conf linux-kernel.cfg litmus-tests/R+fencembonceonces.litmus
Test R+fencembonceonces Allowed
States 3
1:r0=0; [y]=1;
1:r0=1; [y]=1;
1:r0=1; [y]=2;
No
Witnesses
Positive: 0 Negative: 3
Condition exists ([y]=2 /\ 1:r0=0)
Observation R+fencembonceonces Never 0 3
Time R+fencembonceonces 0.01
Hash=ca0b9c6c2fac803b694c4465a750b9bd
```

想定した結果になった。

## #33 `R+poonceonces.litmus` UNA

シミュレートするスレッド

```c
P0(int *x, int *y)
{
	WRITE_ONCE(*x, 1);
	WRITE_ONCE(*y, 1);
}

P1(int *x, int *y)
{
	int r0;

	WRITE_ONCE(*y, 2);
	r0 = READ_ONCE(*x);
}
```

litmus のプログラム (デフォルト) の実行結果

```bash
haytok@2023-03-12 22:16:16:~/memory-model
>>> herd7 -conf linux-kernel.cfg litmus-tests/R+poonceonces.litmus
Test R+poonceonces Allowed
States 4
1:r0=0; [y]=1;
1:r0=0; [y]=2;
1:r0=1; [y]=1;
1:r0=1; [y]=2;
Ok
Witnesses
Positive: 1 Negative: 3
Condition exists ([y]=2 /\ 1:r0=0)
Observation R+poonceonces Sometimes 1 3
Time R+poonceonces 0.01
Hash=96d794b154dbd14a4d2d4c927f7471b4
```

想定された挙動をした。

## 最後に

このシミュレータを使用することで、Linux kernel におけるメモリモデルの挙動がよりソースコードレベルでの理解が進んだ。

頼りにしていた `head7` の doc の図の意味が分からず泣いた。是非どなたかにご教示いただきたい ... :(

- [Simulating memory models with herd7](http://diy.inria.fr/doc/herd.html#intro%3Acandidate)
- [Armv8-A_メモリモデル.pdf - Speaker Deck](https://speakerdeck.com/shigemi1014/armv8-a-memorimoderu)
- [A working example of the Memory Model Tool - Architectures and Processors blog - Arm Community blogs - Arm Community](https://community.arm.com/arm-community-blogs/b/architectures-and-processors-blog/posts/how-to-use-the-memory-model-tool)

## 参考

- [An introduction to lockless algorithms [LWN.net]](https://lwn.net/Articles/844224/)
