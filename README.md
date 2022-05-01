# hakiwata

- これは、Hugo + GitHub Pages で作成した[自作ブログ](https://haytok.jp/)のソースコードです。開発環境は Docker を使用しています。

![image](https://user-images.githubusercontent.com/44946173/141357296-4d6d5f3f-16f5-4ac2-a2c3-d0c6673041ec.png)


## 環境構築

- 開発用サーバの起動

```bash
make or make server
```

- 新規コンテンツの作成

```bash
make new D=<directory name>
```

- 新規 Log の作成

```bash
make log D=<directory name>
```

- 新規スクラップの作成

```bash
make scraps D=<directory name>
```

- ビルド

```bash
make build
```

