---
draft: false
title: "bash メモ"
date: 2023-02-25T19:38:21Z
tags: ["bash"]
pinned: false
ogimage: "img/images/bash.png"
---

- `cat コマンド` と `EOF` を使用したワンライナー ??? でファイルに書き込みができるコマンドの例 (毎回調べる記憶があるのでメモしておいた。)

```bash
cat <<EOF > /etc/wsl.conf
[boot]
command = service docker start;
EOF
```

bash の変数展開 (数式)

```bash
i=1234
echo $((i*2))
```

## 参考

- [知ると便利なヒアドキュメント - Qiita](https://qiita.com/kite_999/items/e77fb521fc39454244e7)
- [Bash $((算術式)) のすべて - A 基本編 - Qiita](https://qiita.com/akinomyoga/items/9761031c551d43307374)
