---
draft: false
title: "Docker Error on WSL2"
date: 2023-02-25T10:06:16Z
tags: ["Docker", "WSL2", "Linux"]
pinned: true
ogimage: "img/images/20230225-docker-error-on-wsl.png"
---

久しぶりに PC を起動してから、WSL2 を起動させて docker コマンドを実行すると、以下のエラーが生じた。

```bash
docker: Cannot connect to the Docker daemon at unix:///var/run/docker.sock. Is the docker daemon running?.
```

このエラーメッセージを読むと docker daemon が動いてなさそう。(推測) なので、このエラーメッセージをもとに適当にググると、以下の Docker のコミュニティのフォーラムの記事がヒットした。

- [WSL - Cannot connect to the Docker daemon at unix:///var/run/docker.sock. Is the docker daemon running? - General Discussions / General - Docker Community Forums](https://forums.docker.com/t/wsl-cannot-connect-to-the-docker-daemon-at-unix-var-run-docker-sock-is-the-docker-daemon-running/116245)

この記事によると、`sudo service docker start` を実行すると docker daemon が起動して、上述のエラーが発生しなくなるとあった。試してみると、確かにエラーは発生しなくなったが、PC をシャットダウンしてから起動した後に、WSL2 を起動するたびに `sudo service docker start` を実行するのは面倒臭い。なんか良い方法はないかと調べてみると、`/etc/wsl.conf` に WLS2 が起動したときに実行できるコマンドを指定できることが下記の記事から明らかになった。

- [WSL-UbuntuでDockerを起動時に動かす | nryblog](https://nryblog.work/wsl-boot-and-start-docker/#WSL%E3%81%AE%E5%BD%B1%E9%9F%BF%E3%81%A7systemd%E3%81%8C%E5%8B%95%E3%81%8B%E3%81%AA%E3%81%84)
- [WSL での詳細設定の構成 | Microsoft Learn](https://learn.microsoft.com/ja-jp/windows/wsl/wsl-config)

```bash
haytok@DESKTOP-SK03JO0:~/hakiwata$ cat /etc/wsl.conf
[boot]
command = service docker start;
```

これによって、PC を起動して WSL2 を起動したとしても、特に手動でコマンドを実行することなく docker daemon を実行することができるようになった。

---

とういうか、そもそも WSL2 における Docker や systemd 

初期化プロセス / システムには `SysVInit` と `SystemD` がある。`SystemD` は新しめの初期化システムである。

- [The Difference Between Systemctl and Service Command in Linux | Baeldung on Linux](https://www.baeldung.com/linux/differences-systemctl-service)

> SysVInit is the classic initialization process in Linux. The initialization process relies on the individual service to install relevant scripts on the /etc/init.d directory. Additionally, the scripts must support the standard commands such as start, stop, and status. One of the main characteristics of this init system is that it is a start-once process and does not track the individual services afterward. The service command is used for running these init scripts from the terminal.

> SystemD, on the other hand, is a recent initialization system that aims to replace SysVInit. In fact, most Linux distributions such as Debian and Red Hat are already using SystemD as their init system out of the box. In contrast to SysVInit, SystemD continues to run as a daemon process after the initialization is completed. Additionally, they are also actively tracking the services through their cgroups. The systemctl command is the entry point for users to interact and configures the SystemD.

> In short, the differences between service and systemctl commands can be summarized as two different commands for two different init systems.

- [initまとめ(ざっくり) - Qiita](https://qiita.com/h_tyokinuhata/items/26b7dd3526e7061596b9)
- [What is systemd? | DigitalOcean](https://www.digitalocean.com/community/tutorials/what-is-systemd)
- [System and Service Manager](https://systemd.io/)

`Ubuntu 20.04 LTS on WSL2` では始祖のプロセスは `init` である。

```bash
haytok@2023-02-26 16:47:44:~/hakiwata (main *%=)
>>> cat /etc/lsb-release
DISTRIB_ID=Ubuntu
DISTRIB_RELEASE=20.04
DISTRIB_CODENAME=focal
DISTRIB_DESCRIPTION="Ubuntu 20.04.5 LTS"
haytok@2023-02-26 16:48:10:~/hakiwata (main *%=)
>>> ps 1
  PID TTY      STAT   TIME COMMAND
    1 ?        Sl     0:00 /init
```

一方、`Amazon Linux 2 on EC2 (AL2)` では始祖のプロセスは `systemd` だった。

```bash
[haytok@ip-172-31-3-204 ~]$ cat /etc/os-release
NAME="Amazon Linux"
VERSION="2"
ID="amzn"
ID_LIKE="centos rhel fedora"
VERSION_ID="2"
PRETTY_NAME="Amazon Linux 2"
ANSI_COLOR="0;33"
CPE_NAME="cpe:2.3:o:amazon:amazon_linux:2"
HOME_URL="https://amazonlinux.com/"
[haytok@ip-172-31-3-204 ~]$ ps 1
  PID TTY      STAT   TIME COMMAND
    1 ?        Ss     0:07 /usr/lib/systemd/systemd --switched-root --system --deserialize 21
```

以上から、比較的新しめの `AL2` では `systemd` が使われている一方で、`Ubuntu 20.04 LTS on WSL2` では `init` が使用されている。なので、`WSL2` では docker daemon を起動させるために毎回 `/etc/init.d/docker` コマンドを実行する必要がある。

```bash
haytok@2023-02-26 16:58:04:~/hakiwata (main *%=)
>>> ls /etc/init.d | grep docker
docker
```

`/etc/init.d` 配下にあるスクリプトはデーモンなどの起動スクリプトが設置されている。詳細は下記の情報を参考にすると良い。

- [「/etc/init.d」ディレクトリ - Linux技術者認定 LinuC | LPI-Japan](https://linuc.org/study/knowledge/514/)
- [Linux service関連　基本コマンドメモ - Qiita](https://qiita.com/manjiroukeigo/items/2b217ffbb50b119d5f58)

`/etc/init.d/docker` の中身は以下である。

```bash
#!/bin/sh
set -e

... (省略)

case "$1" in
	start)
		check_init
		
		fail_unless_root

		cgroupfs_mount

		touch "$DOCKER_LOGFILE"
		chgrp docker "$DOCKER_LOGFILE"

		ulimit -n 1048576

		# Having non-zero limits causes performance problems due to accounting overhead
		# in the kernel. We recommend using cgroups to do container-local accounting.
		if [ "$BASH" ]; then
			ulimit -u unlimited
		else
			ulimit -p unlimited
		fi

		log_begin_msg "Starting $DOCKER_DESC: $BASE"
		start-stop-daemon --start --background \
			--no-close \
			--exec "$DOCKERD" \
			--pidfile "$DOCKER_SSD_PIDFILE" \
			--make-pidfile \
			-- \
				-p "$DOCKER_PIDFILE" \
				$DOCKER_OPTS \
					>> "$DOCKER_LOGFILE" 2>&1
		log_end_msg $?
		;;

... (省略)
```

この `/etc/init.d/docker` の中身からもわかるように、`/etc/init.d/docker start` を実行すると docker daemon がバックグラウンドで起動する。

ちなみに、下記の記事にもあるように pid 1 が init プロセスの場合、`service コマンド` を使用して `/etc/init.d/` 配下のプログラムを実行させることができる。

- [serviceコマンド | 日経クロステック（xTECH）](https://xtech.nikkei.com/it/article/COLUMN/20070605/273739/)

> 指定されたLinuxデーモン（サービス）の起動や停止，ステータスの確認を実行する。実際はシェル・スクリプトであり，/sbin/serviceをテキスト・エディタなどで開くとスクリプトの中身を確認できる。また，serviceコマンドの中では，/etc/init.d（/etc/rc.d/init.d）にあるサービス・スクリプトを実行しているだけである。そのため，/etc/init.d以下のスクリプトを直接実行してもserviceコマンドと同じ作業ができるが，全サービスのステータスを表示したりパスをいちいち入力する必要がないため，コマンドとして使ったほうが便利である。

これは、`service コマンド` の中身の `A convenient wrapper for the /etc/init.d init scripts.` からも確認できる。

```bash
haytok@2023-02-26 17:12:25:~
>>> which service
/usr/sbin/service
haytok@2023-02-26 17:12:32:~
>>> head -n 10 /usr/sbin/service
#!/bin/sh

###########################################################################
# /usr/bin/service
#
# A convenient wrapper for the /etc/init.d init scripts.
#
# This script is a modified version of the /sbin/service utility found on
# Red Hat/Fedora systems (licensed GPLv2+).
#
```

なので、本環境の `WSL2` では `/etc/wsl.conf` に `service docker start` のコマンドを記述すると、`WSL2` をシャットダウンして起動したとしても docker daemon が起動した状態になり、前述のエラーが発生しなくなる。

---

ちなみに、以下の記事にもあるように PID 1 に `systemd` を起動させることができるらしい。1 つ目の記事に「`「systemd」に依存するLinuxアプリケーションを「WSL」で利用可能になる。`」とあるように Docker 自体が `systemd` に依存したアプリケーションやったから、今回のようなエラーが発生したんかな ...

- [「Windows Subsystem for Linux」が「systemd」に対応へ - 窓の杜](https://forest.watch.impress.co.jp/docs/news/1441775.html)
- [Systemd support is now available in WSL! - Windows Command Line](https://devblogs.microsoft.com/commandline/systemd-support-is-now-available-in-wsl/)

設定する項目としては以下である。そうすると、`WSL2` で `systemd` とやり取りするための `systemctl` コマンドの実行が可能になる。

```conf
[boot]
systemd=true
```

なお、当該環境の Windows11 のビルドバージョンは `22621.1265` である。

```bash
PS C:\Users\simpl> wsl --version
WSL バージョン: 1.0.3.0
カーネル バージョン: 5.15.79.1
WSLg バージョン: 1.0.47
MSRDC バージョン: 1.2.3575
Direct3D バージョン: 1.606.4
DXCore バージョン: 10.0.25131.1002-220531-1700.rs-onecore-base2-hyp
Windowsバージョン: 10.0.22621.1265
```

`systemd` を使用するのに必要な要件は、Windows のビルドのバージョンが 22000.0 以上であることなので、動作要件は満たしている。

- [A preview of WSL in the Microsoft Store is now available! - Windows Command Line](https://devblogs.microsoft.com/commandline/a-preview-of-wsl-in-the-microsoft-store-is-now-available/#how-to-install-and-use-wsl-in-the-microsoft-store)

> Are using a Windows 11 build or higher (Windows build number 22000 or higher)

- [WSL2のUbuntu 22.04でSystemdでDockerを起動させる - 技術的な何か。](https://level69.net/archives/31296)
- [WSLでsystemdのPID=1に対応したらしいので試してみた - 技術的な何か。](https://level69.net/archives/31767)

メモをまとめていて気づいたが、Ubuntu のディストリビューションで Docker を起動させる場合 (この組み合わせの場合の話)、PID 1 に systemd が起動していることが前提っぽいのが、下記の doc から読み取れる。なので、当該エラーを解消するには PID 1 のプロセスを systemd にするか、service コマンドで docker daemon を起動させるように設定する必要がある。

- [Linux post-installation steps for Docker Engine](https://docs.docker.com/engine/install/linux-postinstall/#configure-docker-to-start-on-boot-with-systemd)

> Configure Docker to start on boot with systemd
> Many modern Linux distributions use systemd to manage which services start when the system boots. On Debian and Ubuntu, the Docker service starts on boot by default. To automatically start Docker and containerd on boot for other Linux distributions using systemd, run the following commands:

- [systemd と Docker の管理・設定 — Docker-docs-ja 1.9.0b ドキュメント](https://docs.docker.jp/engine/articles/systemd.html)

> systemd と Docker の管理・設定
> 多くの Linux ディストリビューションが systemd を使って Docker デーモンを起動します。このドキュメントは、様々な Docker の設定例を紹介します。

---

ちなみに、[arkane-systems/genie: A quick way into a systemd "bottle" for WSL](https://github.com/arkane-systems/genie) を使用すると、`WSL2` で pid 1 に `systemd` を起動させることができるらしい。

> Well, this gives you a way to run systemd as pid 1, with all the trimmings, inside WSL 2. It does this by creating a pid namespace, the eponymous poor-man's-container "bottle", starting up systemd in there, and entering it, and providing some helpful shortcuts to do so.

WSL2 で systemd を起動させるハックが紹介されていた。

- [WSL2でSystemdを使うハック - Qiita](https://qiita.com/matarillo/items/f036a9561a4839275e5f)

## 疑問

systemd と Linux kernel のコードの関連性が全く掴めていないので、今後の課題にしたい。

## 参考

- [WSL - Cannot connect to the Docker daemon at unix:///var/run/docker.sock. Is the docker daemon running? - General Discussions / General - Docker Community Forums](https://forums.docker.com/t/wsl-cannot-connect-to-the-docker-daemon-at-unix-var-run-docker-sock-is-the-docker-daemon-running/116245)
- [WSL-UbuntuでDockerを起動時に動かす | nryblog](https://nryblog.work/wsl-boot-and-start-docker/#WSL%E3%81%AE%E5%BD%B1%E9%9F%BF%E3%81%A7systemd%E3%81%8C%E5%8B%95%E3%81%8B%E3%81%AA%E3%81%84)
- [WSL での詳細設定の構成 | Microsoft Learn](https://learn.microsoft.com/ja-jp/windows/wsl/wsl-config)
- [Windows Terminal で終了コードによらず WSL の終了と同時にウィンドウを閉じる方法 | MSeeeeN](https://mseeeen.msen.jp/exit-linux-on-windows-terminal/)

---

- [第10章 systemd によるサービス管理 Red Hat Enterprise Linux 7 | Red Hat Customer Portal](https://access.redhat.com/documentation/ja-jp/red_hat_enterprise_linux/7/html/system_administrators_guide/chap-managing_services_with_systemd#tabl-Managing_Services_with_systemd-Introduction-Units-Types)
- [systemdとは何をしているものなのか | ABlog](https://blog.ablaze.one/1582/2022-03-09/)
- [systemdとは？systemctlコマンドとは | .LOG](https://log.dot-co.co.jp/systemd-systemctl/)

---

- [Windows10/11のWSL2でDocker Engineを使う - ぶていのログでぶログ](https://tech.buty4649.net/entry/2022/10/20/162036)
- [Windows 10 or 11 （WSL2）のUbuntuでsystemctlを利用する方法（systemdをPID1で動作させる方法） | Snow System](https://snowsystem.net/other/windows/wsl2-ubuntu-systemctl/)
- [WSL2 Ubuntu で PID1 を sytemd にする](https://zenn.dev/fehde/articles/103560f2a7065f)
