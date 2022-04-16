---
draft: true
title: "GitHub Pages を自動デプロイする\n Actions を調査してみた"
date: 2022-04-10T13:29:37Z
tags: ["GitHub", "CI", "CD"]
pinned: false
ogimage: "img/images/20220410.png"
---

## 概要

- こんにちは :) 先日から GitHub ID を長きに渡って愛用してきた `dilmnqvovpnmlib` から `haytok` に移行する作業を行っています。[haytok/haytok](https://github.com/haytok/haytok) のリポジトリで GitHub ID を変更する作業を行なっていると、デプロイのフローが上手く整備されていないことに気づきました。そのため、現状の機能を残しつつデプロイのフローを再整備する形でリファクタリングを行いました。そこで、今回はそのリファクタリングを行った際の作業ログなどを簡単に記録として残したいと思います。

## 背景と課題

- もともと [haytok/haytok](https://github.com/haytok/haytok) のリポジトリでは、修士 1 年の時に作成した Web サイトと [GitHub のユーザのページ](https://github.com/haytok/) に表示される [README.md](https://github.com/haytok/haytok/blob/gh-pages/README.md) とその定期更新プログラムを管理していました。Web サイト自体は、[React](https://reactjs.org/) + [GitHub Pages](https://pages.github.com/) でデプロイされていました。具体的なデプロイのフローを図 1 に示します。

{{<img_title src="media/fig1.png" title="図 1　改善前の各ブランチに配置されているファイルとデプロイのフロー" width="80%" height="80%" >}}

- `master ブランチ`には、Web サイトのフロントエンドのソースコードと自動デプロイを行うワークフローの GitHub Actions が組み込まれていました。そして、`gh-pages ブランチ`にはフロントエンドのソースコードがビルドされた生成物や REDME.md を定期的に更新するためのプログラムやワークフローが組み込まれていました。各ワークフローは独立しています。

- 今回のデプロイにおける問題点は大きく2 つありました。

  - 1 つ目は、フロントエンドのソースコードを修正し、リモートのリポジトリに push した際、自動デプロイが失敗してしまうことでした。具体的には、図 1 の ② の処理で失敗し、ビルドされた生成物が上手く公開されないような状況でした。昔はどのような手順でデプロイを行っていたのかが気になり、デプロイのための過去のメモなどを見返してみたところ、デプロイは `GitHub Actions` を経由して行っていたのではなく、ローカルマシンで `npm run build` と `npm run deploy` を実行することで行なっていました。正直なぜこのような方法でデプロイを行っていたのかは謎です。

  - 2 つ目の問題点は、`master ブランチ`で生成されたファイルを `gh-pages ブランチ`に配置する際に、元から存在するファイルを上書きしてしまうことでした。具体的には、`master ブランチ`で自動デプロイのフローが実行され、ビルドして生成された assets が `gh-pages ブランチ`に配置される際、`gh-pages ブランチ`に配置されている README.md やそれを更新するプログラムなどのファイルが assets によって上書きしてしまうことでした。これは、`gh-pages ブランチ` に追加で cron の処理を実装してから `master ブランチ`のソースコードを修正することがなかったため、これまでこのバグに気づきませんでした。

## 目的

- 今回の実装の目的は、手動でデプロイしないで済むようにデプロイのワークフローを整備し、README.md の更新プログラムなどと conflict しないように GitHub Actions を使いこなすことです。これにより、デプロイのコマンドを意識することなくソースコードの修正を行うことができます。そして、デプロイのワークフローとは独立して `gh-pages ブランチ`では定義した cron の処理が GitHub Actions により行われます。

- 最終的には、図 2 のようなワークフローの実装を目指しました。これにより、フロントエンドのソースコードを修正したい時は、修正コードをリモートのリポジトリに push するだけで良くなります。そして、自動デプロイにより `gh-pages ブランチ`に配置されているプログラムが削除されることがなくなります。

{{<img_title src="media/fig2.png" title="図 2　改善後の各ブランチに配置されているファイルとデプロイのフロー" width="80%" height="80%" >}}
 
## 方法

- これらの課題を踏まえると、デプロイのワークフローは、以下のような YAML になりました。デプロイのための GitHub Action には、[peaceiris/actions-gh-pages](https://github.com/peaceiris/actions-gh-pages) を活用しています。このリポジトリは、自分一人でしか開発を行わないので、`master ブランチ`に push をした時点でデプロイの処理が走るようになっています。`public_dir` に `npm run build` でビルドすることで作成された生成物を配置します。そして、その配下にあるファイルを `gh-pages ブランチ` の `destination_dir` に配置します。

```yaml
...
      - name: Deploy
        uses: peaceiris/actions-gh-pages@v3
        if: ${{ github.ref == 'refs/heads/master' }}
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./build
          destination_dir: docs
...
```

- この YAML における `destination_dir` の設定とGitHub Pages で公開する静的ファイルの格納先の設定の整合性を取る必要があります。その設定を図 3 に示します。GitHub Pages のための URL にアクセスすると、`/docs` 配下のディレクトリを見に行くような設定になっています。

{{<img_title src="media/settings.png" title="図 3　ビルドしたファイルを gh-pages ブランチで公開するための GitHub 上での設定" width="100%" height="100%" margin-top="20px" >}}

## 結果

- こうして、期待するロジックを維持しつつ、各ブランチで行う処理を整理することができました。

- `master ブランチ` では、プロフィールページの React のソースコードと、それらをビルドし`gh-pages ブランチ` に配置するためのワークフローを管理します。そして、`gh-pages ブランチ` には、 React のビルドされた静的なファイル群、README.md, GitHub Actions の schedule で定期的に README.md を更新するための Golang のプログラム、Golang のプログラムを cron で処理を行う GitHub Actions のワークフロー、そして Work Log を配置するような構成となりました。このように、各ブランチで管理するファイルをキレイに整理することができました。

- また、元々は `destination_dir` は特に設定をしていなかったので、ビルドした生成物が `gh-pages ブランチ` のルートディレクトリに配置される設定となっていました。この設定ではビルドされた生成物が散らばってしまい、見た目が悪かったです。そのため、`destination_dir` で設定した一つのディレクトリにまとめて管理することができるようになり、見た目がスッキリしました。

## 注意点

#### [peaceiris/actions-gh-pages](https://github.com/peaceiris/actions-gh-pages) 関連

- [peaceiris/actions-gh-pages](https://github.com/peaceiris/actions-gh-pages) では、`publish_dir` に配置された生成物が `destination_dir` にコピーを行います。この際、`publish_dir` の中身は最初に削除されるため、注意をしなければなりません。

- しかし、コピー先のディレクトリのファイルには削除したくないファイルが存在するかもしれません。[peaceiris/actions-gh-pages](https://github.com/peaceiris/actions-gh-pages) には、`keep_files` というパラメータがあります。このパラメータを `true` に設定することで、デプロイ先のディレクトリに元からあるファイル (`publish_dir` 内のファイル) が消されることなくファイルがコピーされます。参考として以下に、このパラメータに該当するドキュメントとサンプルコードを記載しておきます。

> By default, existing files in the publish branch (or only in destination_dir if given) will be removed. If you want the action to add new files but leave existing ones untouched, set the optional parameter keep_files to true.

- [peaceiris/actions-gh-pages](https://github.com/peaceiris/actions-gh-pages) には、`exclude_assets` というパラメータがあります。このパラメータには、アセットを公開することから除外するファイルやディレクトリを設定します。この `exclude_assets` の初期値は `.github` です。つまり `publish_dir` に `.github/workflows/*.yaml` のようなディレクトリが含まれると、そのエントリのコピーが行われた後に削除されてしまいます。そのため、`publish_dir` に `.github/workflows/*.yaml` のようなディレクトリが含まれる場合には、`exclude_assets: ''` のようにパラメータをセットし、アセットに `.github` を含むようにする必要があります。参考として以下に、このパラメータに該当するドキュメントを記載しておきます。

> Set files or directories to exclude from publishing assets. The default is .github. Values should be split with a comma.

> Set exclude_assets to empty for including the .github directory to deployment assets.

```yaml
- name: Deploy
  uses: peaceiris/actions-gh-pages@v3
  with:
    deploy_key: ${{ secrets.ACTIONS_DEPLOY_KEY }}   # Recommended for this usage
    # personal_token: ${{ secrets.PERSONAL_TOKEN }} # An alternative
    # github_token: ${{ secrets.GITHUB_TOKEN }}     # This does not work for this usage
    exclude_assets: ''
```

#### GitHub Actions のワークフロー関連

- YAML で定義するワークフローは配置するブランチによって実行できるものと、そうで無いものがあります。例えば、手動でワークフローを実行できる `workflow_dispatch イベント` です。これは、ワークフローのデバッグ用によく使用しますが、デフォルトブランチの配下にワークフローを定義しなければなりません。参考として、以下に該当するドキュメントを記載しておきます。

> To run a workflow manually, the workflow must be configured to run on the workflow_dispatch event. To trigger the workflow_dispatch event, your workflow must be in the default branch. For more information about configuring the workflow_dispatch event, see "Events that trigger workflows".

- また、GitHub Actions 上で定期処理を行うことができる `schedule イベント` に関しても、デフォルトブランチの配下のワークフローに定義しなければなりません。参考として、以下に該当するドキュメントを記載しておきます。

| Webhook event payload | Activity types | GITHUB_SHA | GITHUB_REF |
| :---: | :---: | :---: | :---: |
| n/a | n/a | Last commit on default branch | 	Default branch |

- これらの 2 つのイベント (`workflow_dispatch` と `schedule`) はデフォルトブランチ配下にワークフローを配置しないと動作しないことは検証済みです。

## 結論

- こうして、あまり編集することはないかもしれませんが、過去に作成した Web ページのリファクタリングと自動デプロイのフローを整備することができました。活用している GitHub Actions が期待した挙動をしないときは、出力されるデバッグのログやソースコードを調査を行いましたが、このプロセスで内部の構造を明らかにしつつ原因を突き止めることができて楽しかったです :) 

## その他

- ちなみに、[actions/javascript-action](https://github.com/actions/javascript-action) を活用すると、GitHub Actions を簡単に自作することができるそうです。これを用いて何か作ってみたいと思いました。

- また、この調査過程を通して、ローカル環境で GitHub Actions を検証することができる [nektos/act](https://github.com/nektos/act) を見つけました。少し手元で動作させてみたのですが、すごい手軽に GitHub Actions を動かすことができて感動しました。これを用いると、修正したワークフローの差分を毎回リモートリポジトリに push することで動作を検証する必要が無くなり、素早くワークフローの検証を行うことができると思います。

## WL

- [peaceiris/actions-gh-pages](https://github.com/peaceiris/actions-gh-pages) の挙動を確認するために、ソースコードを追ったりもしたので、その調査ログも簡単に残しておきます。具体的には、`exclude_assets` というパラメータに `.github` を設定したときの GitHub Action の挙動を Actions のログとソースコードから調査することです。その際の Actions の Log を図 4 の赤の四角の枠に示します。

{{<img_title src="media/log.png" title="図 4　Actions の Log" width="80%" height="80%" margin-top="20px" >}}

- このログからもわかるように、`exclude_assets: '.github'` を設定すると、 `gh-pages` ブランチのコピー先であるディレクトリ配下にある `.github` が削除されてしまいます。最初はなぜこの挙動をするのかすごい不思議だったので、使用している Actions が発火した時の処理の流れを確認してみました。(後々考えてみると、`gh-pages` ブランチに配置するのを除外するパラメータなので、`.github` を設定すると削除されるのは自明でした。)

- まず初めに、Actions が発火してから行われるフローを図 5 に示します。

{{<img_title src="media/flow.png" title="図 5　Actions が発火してから行われる処理の流れ" width="80%" height="80%" margin-top="20px" >}}

- 次に、ワークフローにおいてポイントとなる `setRepo` の実装を確認してみました。重要な処理には、コメントを追加しておきました。

```ts
export async function setRepo(inps: Inputs, remoteURL: string, workDir: string): Promise<void> {
  // 定義した YAML から publish_dir と destination_dir の値を受け取る
  const publishDir = path.isAbsolute(inps.PublishDir)
    ? inps.PublishDir
    : path.join(`${process.env.GITHUB_WORKSPACE}`, inps.PublishDir);

  if (path.isAbsolute(inps.DestinationDir)) {
    throw new Error('destination_dir should be a relative path');
  }
  const destDir = ((): string => {
    if (inps.DestinationDir === '') {
      return workDir;
    } else {
      return path.join(workDir, inps.DestinationDir);
    }
  })();

...

  try {
    // git clone を実行して、リポジトリからソースコードをクローンする
    result.exitcode = await exec.exec(
      'git',
      ['clone', '--depth=1', '--single-branch', '--branch', inps.PublishBranch, remoteURL, workDir],
      options
    );
    // git clone が成功したとき
    if (result.exitcode === 0) {
      await createDir(destDir);

      // 定義した YAML に keep_files が true に設定されたとき
      if (inps.KeepFiles) {
        core.info('[INFO] Keep existing files');
      } else {
        core.info(`[INFO] clean up ${destDir}`);
        core.info(`[INFO] chdir ${destDir}`);
        process.chdir(destDir);
        await exec.exec('git', ['rm', '-r', '--ignore-unmatch', '*']);
      }

      core.info(`[INFO] chdir ${workDir}`);
      process.chdir(workDir);
      // copyAssets が実行されると、publish_dir の assets が destination_dir に配置する処理が行われる。
      await copyAssets(publishDir, destDir, inps.ExcludeAssets);
      return;
    } else {
      throw new Error(`Failed to clone remote branch ${inps.PublishBranch}`);
    }
  } catch (e) {
...
  }
}
```

- 次に、`copyAssets` の実装を確認してみました。重要な処理には、コメントを追加しておきました。

```ts
export async function copyAssets(
  publishDir: string,
  destDir: string,
  excludeAssets: string
): Promise<void> {
  core.info(`[INFO] prepare publishing assets`);

  if (!fs.existsSync(destDir)) {
    core.info(`[INFO] create ${destDir}`);
    await createDir(destDir);
  }

  const dotGitPath = path.join(publishDir, '.git');
  if (fs.existsSync(dotGitPath)) {
    core.info(`[INFO] delete ${dotGitPath}`);
    rm('-rf', dotGitPath);
  }

  core.info(`[INFO] copy ${publishDir} to ${destDir}`);
  // この Action が配置されたブランチの publish_dir 配下にあるものを destination_dir にコピーする。
  cp('-RfL', [`${publishDir}/*`, `${publishDir}/.*`], destDir);

  // 公開する assets から除外したいファイル群を指定して削除する。
  await deleteExcludedAssets(destDir, excludeAssets);

  return;
}
```

- 次に、`deleteExcludedAssets` の実装を確認してみました。重要な処理には、コメントを追加しておきました。

```ts
export async function deleteExcludedAssets(destDir: string, excludeAssets: string): Promise<void> {
  // exclude_assets には、デフォルトで .github が設定されている。
  // 定義した YAML に exclude_assets: "" を設定すると、特に何も削除することなく return される。
  if (excludeAssets === '') return;
  core.info(`[INFO] delete excluded assets`);
  const globber = await glob.create(excludedAssetPaths.join('\n'));
  // 削除対象となるファイルやディレクトリを excludedAssetPaths に集約する処理が実装されている。
  // 除外したいファイルを複数指定したい場合は、ユーザは , で区切って対象のファイルを指定する。
  const excludedAssetNames: Array<string> = excludeAssets.split(',');
  const excludedAssetPaths = ((): Array<string> => {
    const paths: Array<string> = [];
    for (const pattern of excludedAssetNames) {
      paths.push(path.join(destDir, pattern));
    }
    return paths;
  })();
  const globber = await glob.create(excludedAssetPaths.join('\n'));
  const files = await globber.glob();
  for await (const file of globber.globGenerator()) {
    core.info(`[INFO] delete ${file}`);
  }
  // 指定されたファイル群を実際に削除する。
  rm('-rf', files);
  return;
}
```

- こうして、`exclude_assets` に設定された値に対応するファイルやディレクトリが削除されるフローを確認することができました。ドキュメントにも記載があったように、`,` で区切って除外するファイルを複数指定することができるのも、ソースコードレベルで理解することができました。

- 補足として、各パラメータには、初期値が設定されています。例えば、`publish_branch` の初期値は `gh-pages` です。こういった各パラメータにどんな初期値の設定が行われているかを確認するには [action.yml](https://github.com/peaceiris/actions-gh-pages/blob/main/action.yml) を見ると良いです。

## 参考

- [GitHub Actions でデフォルトブランチにないワークフローの動作確認をする](https://qiita.com/trackiss/items/02eefc2ab8ccfd41768c)
- [Manually running a workflow](https://docs.github.com/en/actions/managing-workflow-runs/manually-running-a-workflow)
- [Events that trigger workflows](https://docs.github.com/en/actions/using-workflows/events-that-trigger-workflows)
- [GitHub Pages Action](https://github.com/peaceiris/actions-gh-pages)
