# Serene Walker · 个人主页

用 Jekyll 构建、由 GitHub Pages 托管的静态站点。首页是个人简介与项目列表；
每个项目在 `projects/` 下有独立详情页，页面里附可直接查看 / 下载的原始文件。

## 目录结构

```
.
├── _config.yml                 # 站点配置：标题、作者、默认布局、排除项
├── _layouts/
│   └── default.html            # 全站骨架：head、顶栏、页脚、CSS/JS 引入
├── index.html                  # 首页
├── viewer.html                 # 通用代码查看器（?p=项目&f=文件路径）
├── projects/
│   ├── arctic-ink.html         # 旧地址跳转 → /projects/arctic-ink/
│   └── arctic-ink/
│       ├── index.html          # 项目详情页
│       └── files/              # 可下载的原始文件（Jekyll 原样复制）
├── assets/
│   ├── css/                    # base / home / project / viewer
│   ├── js/                     # site.js（主题）/ viewer.js（查看器）
│   └── arctic-ink/             # 页面内嵌用图（WebP）
└── README.md                   # 本文件，已在 _config.yml 中排除
```

## 构建方式

推送 `main` 后 GitHub Pages 自动用 Jekyll 构建，不需要 Actions，也不需要提交产物。
页面靠 front matter 提供标题与描述，骨架统一在 `_layouts/default.html`：

```yaml
---
title: "页面标题"
description: "一句话描述"
extra_css: [home]        # 追加 assets/css/home.css
extra_js: [viewer]       # 追加 assets/js/viewer.js
back: /                  # 页脚返回链接；不写则显示「由 GitHub Pages 托管」
back_label: 返回首页
og_type: article         # 默认 website
noindex: true            # 可选，输出 robots noindex
---
```

静态文件（`assets/`、`files/`、图片）没有 front matter，会被原样发布，不会被 Markdown 化。

本地预览需要 Ruby + Jekyll：

```bash
gem install jekyll
jekyll serve          # http://127.0.0.1:4000
```

## 文件与下载

- 原始文件放在 `projects/<项目>/files/`，站点上就是这些路径，直接可访问、可下载。
- 项目页的「查看」走 `viewer.html?p=<项目>&f=<相对路径>`，站内读取并带行号显示；
  「下载」指向文件本身，链接带 `download` 属性。
- 查看器按「项目 → 文件路径」拼接，对 `p` / `f` 做白名单与路径校验；
  新增项目时在 `viewer.html` 的 `PROJECTS` 里补一条。
- 清单里的文件大小是手写的，换文件后记得同步。

这些文件与 [pet-projects](https://github.com/creator521314/pet-projects) 仓库里的
`gnome-theme/` 保持一致，更新时同步：

```bash
rsync -a --exclude backup/ ../pet-projects/gnome-theme/ projects/arctic-ink/files/
```

没有上传 `backup/`：里面是本机的 dconf 备份与扩展清单，含个人设置。

## 新增一个项目

1. 建目录 `projects/<项目>/`，详情页写成 `index.html`（复制 `projects/arctic-ink/index.html`
   作骨架），front matter 里写标题、描述和 `extra_css`。
2. 需要分发的文件放进 `projects/<项目>/files/`，在详情页 `.filelist` 里加条目；
   文本文件走 `viewer.html`，图片直接链到文件。
3. 在 `viewer.html` 的 `PROJECTS` 里登记：`'<项目>': { title: '显示名', path: 'projects/<项目>/' }`。
4. 页面用图放 `assets/<项目>/`，优先 WebP（单张控制在 ~100 KB 内）。
5. 在 `index.html` 的 `#projects` 里追加卡片。

## 写页面时的约定

- 站内链接和静态资源用 `{{ '/path' | relative_url }}`，别写死绝对路径。
- 全站样式在 `assets/css/base.css`（配色变量、顶栏、按钮、页脚）；
  页面专属样式放 `assets/css/<页面>.css`，通过 `extra_css` 引入。
- 页面内容直接写 HTML，不需要 Markdown；需要 Markdown 时新建 `.md` 并加 front matter。

## 自定义清单

| 位置 | 需要修改的内容 |
| --- | --- |
| `_config.yml` | 站点标题、作者、描述 |
| `index.html` 的 front matter | 首页标题与描述 |
| `index.html` 的 `.avatar` / `.tagline` | 姓名缩写、一句话简介 |
| `index.html` 的 `#about` | 自我介绍 |
| `index.html` 的 `#projects` | 项目卡片 |
| `_layouts/default.html` 的页脚 | 版权与托管说明 |
| `mailto:` | 邮箱地址 |

配色与圆角等设计变量集中在 `assets/css/base.css` 的 `:root` 里，深色模式对应
`@media (prefers-color-scheme: dark)` 与 `[data-theme="dark"]` 两段。

## 内容来源

- `projects/arctic-ink/` 由本地 GNOME 美化方案整理而来，脚本与文件与
  [pet-projects](https://github.com/creator521314/pet-projects) 仓库的 `gnome-theme/` 一致。
- 页面内嵌的预览图由该方案的 `scripts/make-preview.sh` 生成后转成 WebP：
  `style-card.webp`（1600×1060）与 `thumb.webp`（720×416，首页卡片用）。
