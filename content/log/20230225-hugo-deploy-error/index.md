---
draft: false
title: "Hugo Deploy Error"
date: 2023-02-25T18:15:42Z
tags: ["Hugo"]
pinned: false
ogimage: "img/images/20230225-hugo-deploy-error.png"
---

`deploy.yaml` に Hugo バージョン `0.101.1` を修正してすると、GitHub Actions において出力された以下のようなエラーメッセージによりデプロイができなかった。

```bash
Setup Hugo
Run peaceiris/actions-hugo@v2
  with:
    hugo-version: 0.101.1
    extended: false
  env:
    pythonLocation: /opt/hostedtoolcache/Python/3.9.16/x64
    LD_LIBRARY_PATH: /opt/hostedtoolcache/Python/3.9.16/x64/lib
Hugo version: 0.101.1
Error: Action failed with error Unexpected HTTP response: 404
```

なぜかわからないが、Hugo バージョン `0.101.1` を指定できないようだった。

下記の公式ページを確認したが、使用できるバージョン一覧等は確認できなかった。Hugo のバージョンは何でもよかったので、サンプルで挙げられていた `0.110.0` を使用するとデプロイエラーは解消された。

```yaml
        with:
          hugo-version: '0.110.0'
```

- [Hugo setup · Actions · GitHub Marketplace](https://github.com/marketplace/actions/hugo-setup)

エラーの原因は不明だが、何となく気になったので、エラーの原因を調査してみた。

エラーメッセージを出力しているのは以下の関数である。

- [actions-hugo/index.ts at main · peaceiris/actions-hugo](https://github.com/peaceiris/actions-hugo/blob/main/src/index.ts#L8)

```js
    core.setFailed(`Action failed with error ${e.message}`);
```

本来だったらエラーにならず成功するはずの `main.run()` の処理を追って行く。

メインの処理は以下である。

- [actions-hugo/main.ts at main · peaceiris/actions-hugo](https://github.com/peaceiris/actions-hugo/blob/main/src/main.ts#L49)

```js
export async function run(): Promise<ActionResult> {
  const toolVersion: string = core.getInput('hugo-version');

... (省略)

  if (toolVersion === '' || toolVersion === 'latest') {
    installVersion = await getLatestVersion(Tool.Org, Tool.Repo, 'brew');
  } else {
    installVersion = toolVersion;
  }

... (省略)

  await installer(installVersion);

... (省略)
```

`yaml` に `hugo-version` を指定するとそのバージョンが変数 `toolVersion` に格納される。そのバージョンをもとに関数 `installer()` が呼び出される。実装の詳細は以下である。

- [actions-hugo/installer.ts at main · peaceiris/actions-hugo](https://github.com/peaceiris/actions-hugo/blob/main/src/installer.ts#L46)

```js
export async function installer(version: string): Promise<void> {

... (省略)

  const toolURL: string = getURL(osName, archName, extended, version);
  core.debug(`toolURL: ${toolURL}`);

... (省略)
```

`hugo-version` を使用して Hugo のバイナリを取得する関数が `getURL()` なので、その詳細を確認する。

- [actions-hugo/get-url.ts at main · peaceiris/actions-hugo](https://github.com/peaceiris/actions-hugo/blob/main/src/get-url.ts#L27)

```js
... (省略)

  const hugoName = `hugo_${extendedStr(extended)}${version}_${os}-${arch}`;
  const baseURL = 'https://github.com/gohugoio/hugo/releases/download';
  const url = `${baseURL}/v${version}/${hugoName}.${ext(os)}`;

... (省略)
```

あー、これ、単純に Hugo のバイナリを配布しているリリースノートのリンクを生成してるだけっぽい。配布されているバージョンを以下のリンクから確認すると、配布されているバージョンに `0.101.1` はそもそもないため、`404` のエラーが返っていた。

- [Tags · gohugoio/hugo](https://github.com/gohugoio/hugo/tags?after=v0.103.0)

以上から、`hugo-version` で指定できるバージョンは Hugo のリリースノートに記載されているバージョンを適切に指定しないといけない。
