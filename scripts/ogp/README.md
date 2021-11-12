# 概要

- この配下のディレクトリには GitHub Actions で実行される OGP を作成するために必要なスクリプトとそれに関連するファイルを配置している。

## OGP を作成するためのツールの取捨選択に関して

- `Twitter Card Image Generator` の Go 製のライブラリである [Ladicle/tcardgen](https://github.com/Ladicle/tcardgen) を検討した。

- しかし、痒いところの手が届かないので、イメージとしては [kinpoko/vercel-generating-og-images](https://github.com/kinpoko/vercel-generating-og-images) を元に Pyhton で OGP を作るスクリプトを自作することにした。

- [テキストを折り返し画像に収まるように表示する](https://tat-pytone.hatenablog.com/entry/2020/02/10/213332)
  - タイトルによっては折り返しが必要なケースもある。その際には、標準ライブラリの `textwrap` を活用し、良い感じでタイトルが折り返されるように調整を行った。
- また、`textwrap` を活用しても意図した通りに改行されないケースも存在した。そのため、タイトルに `\n` を入れると、その箇所で改行されるように Python のスクリプトに修正を加えた。しかし、タイトル数が長くなりすぎると (おそらく 40 文字以上) 描画がバグる可能性がある。したがって、できるだけタイトルが長くなりすぎず簡潔に書くようにする。

## OGP を作成するスクリプトを実装するに当たって工夫したこと

### 差分のあるファイル情報から正規表現を使ってファイル名を取得する

- 各エントリは `yyyymmdd/index.md` か `yyyymmdd.md` のどちらかのファイルで作成している。それを含んだ情報を Python のスクリプト内で正規表現を使って取得した。そのスクリプトは以下である。

```python
import re

def is_valid_date_format(value):
    return True if re.fullmatch('[0-9]{8}', value) else False
```

#### 参考

- [［解決！Python］正規表現を使って文字列が数字だけで構成されているかどうかを判定するには](https://atmarkit.itmedia.co.jp/ait/articles/2102/16/news019.html)
- [正規表現：数字の表現。桁数や範囲など ](https://www-creators.com/archives/4241#i-3)

## OGP のチェック

- [Twitter Card validator](https://cards-dev.twitter.com/validator)

## OGP を作成する workflow に関して

- 初めは、OGP を作成する workflow を別のファイルに定義し、[GitHub Action for Dispatching Workflows](https://github.com/benc-uk/workflow-dispatch) を活用してブログをデプロイする workflow から呼び出すつもりだった。しかし、workflow の処理順を逐次的に行うことができなかった。そのため、ファイルを分割せず、一つのファイルに OGP を作成する処理とデプロイの処理を記述するようにした。

### 参考

- [あるワークフローから他のワークフローを実行する方法](https://qiita.com/zomaphone/items/77ea3818e0922ed4173c)
- [GitHub Action for Dispatching Workflows](https://github.com/benc-uk/workflow-dispatch)

# GitHub Actions で回す CI に関して

- `git diff --exit-code --quiet <ファイルパス>` で差分があると `exit code` に `1` が格納され、差分がないと `0` が格納される。
- この結果 `exit_code` の結果は `$?` に格納されるので、 `echo $?` で確認することができる。`$?` に `exit code` が格納されているのを忘れがちだが、たまに出番が出てくる。
- `untracked file` に対して `git diff --exit-code` を実行しても `exit code` には `0` が格納される。したがって、事前に `untracked file` を `git add -n untracked file` のコマンドで `tracked な状態` に変更しておく必要がある。
- OGP を作成するスクリプト内で画像は `static/img/images/` に保存するような仕様にしている。そのため、`git diff` を実行する際には、そのディレクトリ配下に差分があるかを確認すれば仕様的には問題がない。
- `git diff --exit-code --quiet <ファイルパス>` は差分の状態を表すフラグを `$?` に格納し、`--quiet` オプションで差分がある時は差分を表示しないようする。

```bash
git add -N static/img/images/*.png
if ! git diff --exit-code --quiet static/img/images/*.png
then
  git config --global user.name dilmnqvovpnmlib
  git config --global user.email dilmnqvovpnmlib@users.noreply.github.com
  git pull
  git add static/img/images/*.png
  git commit -m 'update OGP images'
  git push origin main
fi
```

## 参考

- [Git での新規ファイル作成を含んだファイル変更有無の判定方法 ](https://reboooot.net/post/how-to-check-changes-with-git/)
  - `git diff --exit-code` に関する解説が書かれていて大変参考になった。

## docker-compose.yml に関して

- `docker-compose.yml` と `docker-compose.dev.yml` と `docker-compose.override.yml` を活用して開発環境と GitHub Actions 上で実行するコマンドを使い分ける。

### 参考

- [hk-41/docker-compose.override.yml](https://github.com/dilmnqvovpnmlib/hk-41/blob/master/docker-compose.override.yml)
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
