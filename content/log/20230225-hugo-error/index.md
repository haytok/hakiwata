---
draft: false
title: "Hugo のバージョンをアップグレードできない事象の解消方法"
date: 2023-02-25T09:52:52Z
tags: ["Hugo"]
pinned: false
ogimage: "img/images/20230225-hugo-error.png"
---

本アプリケーションで使用している Hugo のバージョンを `0.81.1` から `0.101.0` にアップグレードしようとしていた。しかし、Hugo バージョン `0.101.0` を使用すると本アプリケーションを起動させることができず、下記のエラーが生じた。

```bash
haytok@DESKTOP-SK03JO0:~/hakiwata$ make server
docker run --rm -it \
        -v /home/haytok/hakiwata:/src \
        -p 1313:1313 \
        klakegg/hugo:0.101.0 server
Start building sites …
hugo v0.101.0-466fa43c16709b4483689930a4f9ac8add5c9f66 linux/amd64 BuildDate=2022-06-16T07:09:16Z VendorInfo=gohugoio
ERROR 2023/02/25 09:38:30 render of "page" failed: "/src/themes/manis-hugo-theme/layouts/_default/single.html:1:3": execute of template failed: template: _default/single.html:1:3: executing "_default/single.html" at <partial "header" .>: error calling partial: "/src/themes/manis-hugo-theme/layouts/partials/header.html:3:3": execute of template failed: template: partials/header.html:3:3: executing "partials/header.html" at <partial "meta" .>: error calling partial: "/src/layouts/partials/meta.html:4:12": execute of template failed: template: partials/meta.html:4:12: executing "partials/meta.html" at <.hugo.Generator>: can't evaluate field hugo in type *hugolib.pageState
ERROR 2023/02/25 09:38:30 render of "page" failed: "/src/themes/manis-hugo-theme/layouts/_default/single.html:1:3": execute of template failed: template: _default/single.html:1:3: executing "_default/single.html" at <partial "header" .>: error calling partial: "/src/themes/manis-hugo-theme/layouts/partials/header.html:3:3": execute of template failed: template: partials/header.html:3:3: executing "partials/header.html" at <partial "meta" .>: error calling partial: "/src/layouts/partials/meta.html:4:12": execute of template failed: template: partials/meta.html:4:12: executing "partials/meta.html" at <.hugo.Generator>: can't evaluate field hugo in type *hugolib.pageState
ERROR 2023/02/25 09:38:30 render of "page" failed: "/src/themes/manis-hugo-theme/layouts/_default/single.html:1:3": execute of template failed: template: _default/single.html:1:3: executing "_default/single.html" at <partial "header" .>: error calling partial: "/src/themes/manis-hugo-theme/layouts/partials/header.html:3:3": execute of template failed: template: partials/header.html:3:3: executing "partials/header.html" at <partial "meta" .>: error calling partial: "/src/layouts/partials/meta.html:4:12": execute of template failed: template: partials/meta.html:4:12: executing "partials/meta.html" at <.hugo.Generator>: can't evaluate field hugo in type *hugolib.pageState
ERROR 2023/02/25 09:38:30 render of "page" failed: "/src/themes/manis-hugo-theme/layouts/_default/single.html:1:3": execute of template failed: template: _default/single.html:1:3: executing "_default/single.html" at <partial "header" .>: error calling partial: "/src/themes/manis-hugo-theme/layouts/partials/header.html:3:3": execute of template failed: template: partials/header.html:3:3: executing "partials/header.html" at <partial "meta" .>: error calling partial: "/src/layouts/partials/meta.html:4:12": execute of template failed: template: partials/meta.html:4:12: executing "partials/meta.html" at <.hugo.Generator>: can't evaluate field hugo in type *hugolib.pageState
Error: Error building site: failed to render pages: render of "page" failed: "/src/themes/manis-hugo-theme/layouts/_default/single.html:1:3": execute of template failed: template: _default/single.html:1:3: executing "_default/single.html" at <partial "header" .>: error calling partial: "/src/themes/manis-hugo-theme/layouts/partials/header.html:3:3": execute of template failed: template: partials/header.html:3:3: executing "partials/header.html" at <partial "meta" .>: error calling partial: "/src/layouts/partials/meta.html:4:12": execute of template failed: template: partials/meta.html:4:12: executing "partials/meta.html" at <.hugo.Generator>: can't evaluate field hugo in type *hugolib.pageState
Built in 87 ms
make: *** [Makefile:12: server] Error 255
```

エラーメッセージの内容と下記の記事の内容を参考にして、テーマのテンプレートを `{{ .Hugo.Generator }}` から `{{ hugo.Generator }}` に変更すると、`0.101.0` の Hugo で本アプリケーションを起動させることができた。

- [Can't evaluate field Hugo in *hugolib.PageState - support - HUGO](https://discourse.gohugo.io/t/cant-evaluate-field-hugo-in-hugolib-pagestate/37862)

バージョンを上げることによって表現できる文法が変更されたため、今回のようなエラーが発生したんやろうか ... 詳細は全くわかっていない :(
