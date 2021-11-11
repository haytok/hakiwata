# 概要

- この配下のディレクトリには GitHub Actions で実行される OGP を作成するために必要なスクリプトとそれに関連するファイルを配置しています。

## OGP のチェック

- [Twitter Card validator](https://cards-dev.twitter.com/validator)

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
