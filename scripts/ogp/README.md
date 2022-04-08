# 概要

- この配下のディレクトリには GitHub Actions で実行される OGP を作成するために必要なスクリプトとそれに関連するファイルを配置している。

# 環境の構築

- Docker Image のビルド

```bash
make dev-build
```

- Docker コンテナの起動

```bash
make dev-up
```

- Docker コンテナを落とす

```bash
make dev-down
```

---

## 一連の流れ

- OGP の画像の作成
  - 使用するツールの技術選定
  - 環境構築と Makefile の作成
  - Python スクリプトの作成
- Hugo から OGP を読み出す設定
  - favicon.ico を修正
  - meta タグ関連の修正
- GitHub Actions で OGP を自動生成する workflow の作成
- 作業ログの作成

---

## OGP を作成するためのツールの取捨選択に関して

- `Twitter Card Image Generator` の Go 製のライブラリである [Ladicle/tcardgen](https://github.com/Ladicle/tcardgen) を検討した。

- しかし、痒いところの手が届かないので、イメージとしては [kinpoko/vercel-generating-og-images](https://github.com/kinpoko/vercel-generating-og-images) を元に Pyhton で OGP を作るスクリプトを自作することにした。

- [テキストを折り返し画像に収まるように表示する](https://tat-pytone.hatenablog.com/entry/2020/02/10/213332)
  - タイトルによっては折り返しが必要なケースもある。その際には、標準ライブラリの `textwrap` を活用し、良い感じでタイトルが折り返されるように調整を行った。
- また、`textwrap` を活用しても意図した通りに改行されないケースも存在した。そのため、タイトルに `\n` を入れると、その箇所で改行されるように Python のスクリプトに修正を加えた。しかし、タイトル数が長くなりすぎると (おそらく 40 文字以上) 描画がバグる可能性がある。したがって、できるだけタイトルが長くなりすぎず簡潔に書くようにする。

---

## 環境構築における docker-compose.yml に関して

- `docker-compose.yml` と `docker-compose.dev.yml` と `docker-compose.override.yml` を活用して開発環境と GitHub Actions 上で実行するコマンドを使い分ける。

### 参考

- [hk-41/docker-compose.override.yml](https://github.com/haytok/hk-41/blob/master/docker-compose.override.yml)
- [ファイル間、プロジェクト間での Compose 設定の共有](https://docs.docker.jp/compose/extends.html)

## docker-compose.yml とコンテナ内でファイルを作成した時の権限に関して

- Makefile 内で以下のように設定する方法 1
  - docker-compose run のオプションを活用する。

```bash
$(eval USER_ID := $(shell id -u $(USER)))
$(eval GROUP_ID := $(shell id -g $(USER)))

.PHONY: prod-run
prod-run:
	docker-compose run --rm \
		-v /etc/group:/etc/group:ro \
		-v /etc/passwd:/etc/passwd:ro \
		-u $(USER_ID):$(GROUP_ID) \
		ogp_creater
```

- Makefile 内で以下のように設定する方法 2
  - docker-compose.dev.yml の volumes の Long syntax を活用する。

```bash
$(eval USER_ID := $(shell id -u $(USER)))
$(eval GROUP_ID := $(shell id -g $(USER)))

.PHONY: dev-up
dev-up:
	USER_ID=${USER_ID} GROUP_ID=${GROUP_ID} docker-compose -f docker-compose.yml -f docker-compose.dev.yml up
```

- `docker-compose.dev.yml` 内での権限周りの設定の記述は以下である。
  - `source` には相対パスで指定することができない。従って、`sorce` にはこのプロジェクト自体は Short syntax を使って指定した。

```bash
    user: "${USER_ID}:${GROUP_ID}"
    volumes:
      - type: bind
        source: /etc/group
        target: /etc/group
        read_only: true
      - type: bind
        source: /etc/passwd
        target: /etc/passwd
        read_only: true
      - ../../:/app
```

- 色々加味した結果、`docker-compose.dev.yml` 内での権限周りの設定の記述は以下のようにした。`read only` のファイルに関しては以下の書き方をするようにする。
  - 結局 `docker-compose run` コマンドの `v` オプションを `docker-compose.dev.yml` に持ってきただけである。
  - しかし、`docker-compose.yml` の `volumes` ディレクティブの Short syntax と Long syntax の違いを認知できて良かった。

```bash
    user: "${USER_ID}:${GROUP_ID}"
    volumes:
      - /etc/group:/etc/group:ro
      - /etc/passwd:/etc/passwd:ro
      - ../../:/app
```

### 参考

- [Dockerでファイルのパーミッションをホストユーザと合わせる方法](https://blog.odaryo.com/2020/07/user-permission-in-docker/)
  - `ro オプション` があるので、それを活用する。
- [Dockerで実行ユーザーとグループを指定する](https://qiita.com/acro5piano/items/8cd987253cb205cefbb5#%E8%A7%A3%E6%B1%BA%E7%AD%96%E3%81%9D%E3%81%AE3-docker-composeyml%E3%81%A7%E6%8C%87%E5%AE%9A)
- [docker-composeのvolumesのパス指定の整理](https://pc.atsuhiro-me.net/entry/2020/03/19/105714)
- [The Compose Specification](https://github.com/compose-spec/compose-spec/blob/master/spec.md#volumes)
- [Compose file version 3 reference](https://docs.docker.com/compose/compose-file/compose-file-v3/#volumes)
  - 仕様書は GitHub の README.md を使って公開しているものと Web ページで公開しているものがあった。
  - volumes.type の種類に `volume` と `type` があり概念がややこしかった。`docker-compose.yml` の書き方はこの仕様書を参考にすると書ける。違いに関しては実際にコンテナを起動させて所望の挙動をするかで確認した。
- [Dockerのボリュームとバインドマウントの違い](https://losenotime.jp/docker-mount/)
  - マウントの仕方には 2 通りの方法があり、ボリュームとバインドマウントがある。
- [Dockerのまとめ - コンテナとボリューム編](https://qiita.com/kompiro/items/7474b2ca6efeeb0df80f)
  - Docker の内部のマウントの仕組みを解像度を上げて理解したい。
- [Dockerのデータ永続化機構（ボリューム）について](https://zenn.dev/eitches/articles/2021-0320-docker-volumes)
- [Docker run reference](https://docs.docker.com/engine/reference/run/#volume-shared-filesystems)
  - ボリュームと Bind Mounting の違いについてわかりやすく解説されていた。
  - docker run のドキュメントにも書かれてるように `v オプション` でマウント元のデータは 2 つ指定することができる。絶対パスを指定する時はホストとそのパスのファイル群を共有する。一方、名前のみを指定すると、Docker が作成する Volume を共有する形となる。後者は DB などの外部に永続化させたいものを扱う際に使用する。
  - 相対パスでマウント先を指定したい時は `docker-compose.yml` を定義するのが無難だと思う。
```bash
The container-dest must always be an absolute path such as /src/docs. The host-src can either be an absolute path or a name value. If you supply an absolute path for the host-src, Docker bind-mounts to the path you specify. If you supply a name, Docker creates a named volume by that name.
```
- [docker-compose の bind mount を1行で書くな](https://zenn.dev/sarisia/articles/0c1db052d09921#long-syntax)
  - `docker-compose.yml` の volumes ディレクティブは Short syntax よりも Long syntax を使うべきと言う主張を具体例を交えて解説しているわかりやすい記事だった。
- [DockerのVolume](https://qiita.com/wwbQzhMkhhgEmhU/items/7285f05d611831676169#%E3%83%9C%E3%83%AA%E3%83%A5%E3%83%BC%E3%83%A0%E3%81%A3%E3%81%A6%E4%BD%95%E3%82%92%E3%81%99%E3%82%8B%E3%82%82%E3%81%AE2)
  - volume と bind を具体例を交えてわかりやすく解説されていた。
- [Docker, mount volumes as readonly](https://stackoverflow.com/questions/19158810/docker-mount-volumes-as-readonly)
- この記事の docker-compose の段落のコメントが参考になった。(`You can also do - './my-file.txt:/container-readonly-file.txt:ro' under volumes - note the :ro at the end. `)

## Docker が把握している Volume 関連のコマンド

- 以下のコマンドを活用してどのタイミングで Volume が作成されたかを確認してみた。

```bash
docker volume list -q | xargs docker volume inspect | grep CreatedAt | grep 2021
```

- `docker volume prune` コマンドで不要な Volume を全て削除した。

### 参考
- [volume ls](https://docs.docker.jp/engine/reference/commandline/volume_ls.html)

---

## OGP を作成するするスクリプトの実装に関して

### 参考

- [PythonでPillowを使ってOGP画像を作ろう]](https://zenn.dev/makiart/articles/78d53694e70105)
- [kinpoko/vercel-generating-og-images](https://github.com/kinpoko/vercel-generating-og-images)

## 差分のあるファイル情報から正規表現を使ってファイル名を取得する

- 各エントリは `yyyymmdd/index.md` か `yyyymmdd.md` のどちらかのファイルで作成している。それを含んだ情報を Python のスクリプト内で正規表現を使って取得した。そのスクリプトは以下である。

```python
import re

def is_valid_date_format(value):
    return True if re.fullmatch('[0-9]{8}', value) else False
```

### 参考

- [［解決！Python］正規表現を使って文字列が数字だけで構成されているかどうかを判定するには](https://atmarkit.itmedia.co.jp/ait/articles/2102/16/news019.html)
- [正規表現：数字の表現。桁数や範囲など ](https://www-creators.com/archives/4241#i-3)

## git log コマンドと bash を工夫して差分のあるファイル名を取得する

- もともとは `git log -p -2` コマンドの出力結果をパースして差分のあるファイル名を出力しようとしたが、パーサを実装するのがめんどくさくなったので、違う方法を模索することにした。
- 次に考えた方法は、ハッシュ値とコミットを活用して差分のファイルを求める方法です。これは、以下のシェルスクリプトで求めることが可能です。しかし、その求めたファイル名を最終的には OGP を作成する Python のスクリプトに引き渡さなければなりません。そこで、この方法は諦めました。

```bash
#!/bin/bash
commit_hash_list=(`git log --pretty=%H`);
index=1; # index=0 だと今の diff が出力される。
file_list=(`git diff ${commit_hash_list[$index]} --name-only`);
echo $file_list;
git diff ${commit_hash_list[$index]}
echo ${commit_hash_list[$index]};
```

- 次に考えた方法は、GitHub API を Python のスクリプトから呼び出し、直前のコミットからファイルの差分があるかを確認する方法です。git コマンドを実行し差分のあるファイル名を取得する処理とそのファイルのメタデータから OGP を作成する処理を一つにすることで、処理がスッキリしました。

### 参考

- [2.3 Git の基本 - コミット履歴の閲覧](https://git-scm.com/book/ja/v2/Git-%E3%81%AE%E5%9F%BA%E6%9C%AC-%E3%82%B3%E3%83%9F%E3%83%83%E3%83%88%E5%B1%A5%E6%AD%B4%E3%81%AE%E9%96%B2%E8%A6%A7)

  - `git log -p -2 ` を実行すると直近の 2 エントリの log を出力できる。
```bash
git log -3
    Limits the number of commits to show to 3.
```
- [git logでコミットハッシュだけほしい](https://otiai10.hatenablog.com/entry/2016/06/15/072039)

- [GitHub APIでコミット履歴を取得する](https://qiita.com/nannany_hey/items/23f847e0a331da52ed77)
- [List commits](https://docs.github.com/en/github-ae@latest/rest/reference/repos#list-commits)
- [How can I get last commit from GitHub API](https://stackoverflow.com/questions/45726013/how-can-i-get-last-commit-from-github-api)
  - `GET /repos/:owner/:repo/commits/master` にアクセスすると、一番最新のコミットにアクセスできる。

## Python の requests で外部の API を呼び出す際の例外処理に関して

- 今回は、`Response.raise_for_status()` を活用することにした。

### 参考

- [requestsが送出した例外からレスポンスボディを取得する](https://kamatimaru.hatenablog.com/entry/2021/05/18/073757)
- [Python API通信時の例外処理](https://qiita.com/d_kvn/items/5da7f5cdfc8200172a39)

## GitHub API を呼び出した時に返ってくるレスポンスの例

```bash
"files": [
    {
        "sha": "hogehoge",
        "filename": "content/post/20210430/index.md",
        "status": "renamed",
        "additions": 0,
        "deletions": 0,
        "changes": 0,
        "blob_url": "hogehoge",
        "raw_url": "hogehoge",
        "contents_url": "hogehoge",
        "previous_filename": "content/post/20210430.md"
    },
]
```

---

## favicon.ico の変更に関して

- OGP を作成するついてに favicon.ico も修正しようと思った。しかし、ローカルには favicon.ico が見つからない。本番環境では favicon.ico は設定されているのでおかしいと思い gh-pages ブランチを見に行くと、`img/images/kiwata.png` があった。これは、main ブランチの `static/img/` に対応しているはずと思ったので、そこに favicon.ico を新しく作成し、デプロイすると新しい favicon.ico が適用された。

## Hugo 側の追加の設定に関して

- 各エントリの OPG の画像のパスに関する情報は Markdown ファイルのフロントマターに記述している。具体的には、`ogimage: "img/images/<画像名>"` である。これは、`hugo new` コマンドで自動的に設定したいので、`default.md` に追加した。

- OGP を読み出す設定をするために `themes/manis-hugo-theme/layouts/partials/meta.html` を書き換える必要がある。しかし、origin のリソースは書き換えたくないので、`layouts/partials/meta.html` を作成し、それをカスタマイズし、OGP を読み出す設定を行った。

### 参考

- [Hugoでfaviconをつけよう](https://竹内電設.com/post/hugo%E3%81%A7favicon%E3%82%92%E3%81%A4%E3%81%91%E3%82%88%E3%81%86/)
- [サイトのFavicon画像を作成して設置してみる](https://hugo-de-blog.com/favicon-generate/)

- [Hugo の OGP 画像を自動生成できる「tcardgen」を試した](https://kakakakakku.hatenablog.com/entry/2020/07/03/095053)
- [[Hugo] tcardgen を使って OGP 画像を自動生成する](https://michimani.net/post/development-generate-ogp-image-by-tcardgen-in-hugo/#%e5%90%84%e8%a8%98%e4%ba%8b%e5%86%85%e3%81%a7%e3%81%ae%e8%a8%ad%e5%ae%9a)
- [HugoのブログサイトでOGP設定をする](https://hugo-de-blog.com/hugo-ogp/)
- [Twitterカードを設定してリンク画像を表示させる方法｜表示できない場合の対処法も解説！](https://unique1.co.jp/column/sns_operation/3033/)
- 実際に運用されているブログをのソースコードを見て OGP の設定の仕方を調査する
  - [michimani/simplog](https://github.com/michimani/simplog)
  - [simplog/layouts/partials/head.html](https://github.com/michimani/simplog/blob/master/layouts/partials/head.html)
  - [simplog/archetypes/default.md](https://raw.githubusercontent.com/michimani/simplog/master/archetypes/default.md)
- 研究室の同期のブログとそのテンプレートの大本のソースコードを参考にした
  - [hugo-theme-mini/layouts/partials/head.html](https://github.com/nodejh/hugo-theme-mini/blob/a521aa7ccd4578a9fc5d13ea8be9f7a0ac879cb7/layouts/partials/head.html)
  - [kinpokoblog/layouts/partials/head.html](https://github.com/kinpoko/kinpokoblog/blob/main/layouts/partials/head.html)

## Hugo 側から OGP を読み出す設定とデバッグに関して

- 初めは、Chrome の拡張機能を使って OGP が適切に読み出せているかを確認していた。しかし、拡張機能自体が正常に動作していない気がした。そのため、localhost で起動させているアプリケーションのページのソースコードをブラウザ上で確認し、`meta タグ` に `property="og:image"` が付いているエレメントの `content` を逐一確認するようにした。
- 以下が正常に動作するケースの `meta タグ` である。

```html
<meta property="og:image" content="http://localhost:1313/img/images/20211110.png">
```

### 参考

- [localhostの状態でOGPのテストを開発環境で行う](https://qiita.com/TeruhisaFukumoto/items/6032efde115a17b45637)
- [ローカル環境でOGPをテストできるChrome拡張機能をリリースしました](https://nullnull.dev/blog/localhost-open-graph-debugger/#%F0%9F%8F%A9%E2%98%81)

- [HugoでOGP設定](https://kinpokoblog.com/posts/setting-up-ogp-in-hugo/)

## Hugo の yml ファイル内の Front Matter Formats に関して

- Hugo でブログを書く際、Markdown の先頭にメタデータを記述する。これは、フロントマターと呼ばれ、そのファイルのメタデータを記述することができる。

### 参考

- [Front Matter](https://gohugo.io/content-management/front-matter/)

---

## OGP のチェック

- [Twitter Card validator](https://cards-dev.twitter.com/validator)

## OGP を作成する workflow に関して

- 初めは、OGP を作成する workflow を別のファイルに定義し、[GitHub Action for Dispatching Workflows](https://github.com/benc-uk/workflow-dispatch) を活用してブログをデプロイする workflow から呼び出すつもりだった。しかし、workflow の処理順を逐次的に行うことができなかった。そのため、ファイルを分割せず、一つのファイルに OGP を作成する処理とデプロイの処理を記述するようにした。

### 参考

- [あるワークフローから他のワークフローを実行する方法](https://qiita.com/zomaphone/items/77ea3818e0922ed4173c)
- [GitHub Action for Dispatching Workflows](https://github.com/benc-uk/workflow-dispatch)

## GitHub Actions で回す CI に関して

- `git diff --exit-code --quiet <ファイルパス>` で差分があると `exit code` に `1` が格納され、差分がないと `0` が格納される。
- この結果 `exit_code` の結果は `$?` に格納されるので、 `echo $?` で確認することができる。`$?` に `exit code` が格納されているのを忘れがちだが、たまに出番が出てくる。
- `untracked file` に対して `git diff --exit-code` を実行しても `exit code` には `0` が格納される。したがって、事前に `untracked file` を `git add -n untracked file` のコマンドで `tracked な状態` に変更しておく必要がある。
- OGP を作成するスクリプト内で画像は `static/img/images/` に保存するような仕様にしている。そのため、`git diff` を実行する際には、そのディレクトリ配下に差分があるかを確認すれば仕様的には問題がない。
- `git diff --exit-code --quiet <ファイルパス>` は差分の状態を表すフラグを `$?` に格納し、`--quiet` オプションで差分がある時は差分を表示しないようする。

```bash
git add -N static/img/images/*.png
if ! git diff --exit-code --quiet static/img/images/*.png
then
  git config --global user.name haytok
  git config --global user.email haytok@users.noreply.github.com
  git pull
  git add static/img/images/*.png
  git commit -m 'update OGP images'
  git push origin main
fi
```

## 参考

- [Git での新規ファイル作成を含んだファイル変更有無の判定方法 ](https://reboooot.net/post/how-to-check-changes-with-git/)
  - `git diff --exit-code` に関する解説が書かれていて大変参考になった。
