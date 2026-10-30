# Serene Walker · 个人主页

一个无构建、零依赖的静态站点，直接由 GitHub Pages 托管。
首页是单栏的个人简介与项目列表；每个项目在 `projects/` 下有独立详情页，页面里附可直接
查看 / 下载的原始文件，共用 `styles.css` 的设计令牌与 `site.js` 的主题切换。

## 目录结构

```
.
├── index.html                  # 首页：自我介绍 + 项目列表
├── styles.css                  # 共享样式：配色变量、排版、顶栏、按钮、页脚
├── site.js                     # 共享脚本：主题记忆与切换、页脚年份
├── viewer.html                 # 通用代码查看器（?p=项目&f=文件路径）
├── projects/
│   └── arctic-ink/
│       ├── index.html          # 项目详情页
│       └── files/              # 可下载的原始文件（原样发布，不做处理）
│           ├── install.sh
│           ├── README.md
│           ├── scripts/*.sh
│           ├── preview/style-card.png
│           └── wallpapers/*.png
├── assets/arctic-ink/          # 页面内嵌用图（WebP，已压缩）
├── .nojekyll                   # 跳过 Jekyll 处理，原样发布
└── README.md
```

## 本地预览

直接双击打开 `index.html` 即可（页面不含 fetch 请求，`file://` 下也能正常显示；
代码查看器因为要 `fetch`，需要在服务器下运行）。起一个静态服务器：

```bash
python3 -m http.server 8000
# 然后访问 http://localhost:8000
```

## 发布到 GitHub Pages

```bash
git add .
git commit -m "Update homepage"
git push
```

推送后 1–2 分钟自动生效，访问地址：

```
https://creator521314.github.io/
```

> 这是 GitHub 用户主页站点：仓库名必须与用户名一致（`creator521314.github.io`），
> Pages 的 Source 为 `main` 分支根目录。页面全部使用相对路径，本地目录名可以不同。

## 文件与下载

- 原始文件放在 `projects/<项目>/files/` 下，`.nojekyll` 保证它们被原样发布：
  `/projects/arctic-ink/files/install.sh` 就是一个可直接访问的真实文件。
- 项目页的「文件」清单里，每个条目提供两个动作：
  - **查看** → `viewer.html?p=<项目>&f=<相对路径>`，在站内读取并带行号显示；
  - **下载** → 文件本身，链接带 `download` 属性。
- 查看器按「项目 → 文件路径」拼接，并对 `p`、`f` 做白名单与路径校验；
  新增项目时，在 `viewer.html` 的 `PROJECTS` 映射里补一条即可。
- 清单里的文件大小是手写的：换文件后记得同步，否则显示会过时。

没有上传 `backup/`：里面是本机的 dconf 备份与扩展清单，含个人设置。

## 新增一个项目

1. 建目录 `projects/<项目>/`，把详情页写成 `index.html`，可复制 `projects/arctic-ink/index.html` 作骨架；
   资源路径前缀为 `../../`（相对站点根）。
2. 需要分发的文件放进 `projects/<项目>/files/`，在详情页的 `.filelist` 里加条目；
   文本文件走 `viewer.html`，图片直接链到文件。
3. 在 `viewer.html` 的 `PROJECTS` 里登记：`'<项目>': { title: '显示名', path: 'projects/<项目>/' }`。
4. 页面用图放 `assets/<项目>/`，优先 WebP（单张控制在 ~100 KB 内）。
5. 在 `index.html` 的 `#projects` 里追加卡片：

```html
<a class="project featured" href="projects/<项目>/">
  <img class="project-thumb" src="assets/<项目>/thumb.webp" width="720" height="416"
       decoding="async" alt="一句话描述这张图">
  <div class="project-body">
    <span class="project-tag">分类 · 技术栈</span>
    <h3>项目名<span class="arrow" aria-hidden="true">↗</span></h3>
    <p>一句话说明它解决什么问题。</p>
  </div>
</a>
```

首个卡片用 `project featured`（左图右文），其余项目直接用 `project` 即可。

## 关于构建与框架

站点刻意保持「无构建」：只有 3 个页面 + 1 个查看器，文件本身就是静态资源，任何静态托管
都支持下载，不需要框架介入。真正需要框架的是**页面变多之后的模板复用**（现在的顶栏、页脚、
`<head>` 在各页重复），以及数据驱动的清单。

真要迁移时：

| 方案 | 在 GitHub Pages 上 | 说明 |
| --- | --- | --- |
| Jekyll | 原生构建，无需 CI | 只有它能不改仓库设置就构建；用 `_layouts` 收掉重复结构 |
| Hugo | 需要 GitHub Actions | 单二进制、构建快；Pages 的 Source 要改成 Actions |
| Eleventy / Astro | 需要 GitHub Actions + Node | 能在构建期生成文件清单、大小与打包 zip |

当前 2 个内容页的规模，迁移收益还抵不上多一条构建链；等页面数量或清单维护量上来再动。

## 自定义清单

| 位置 | 需要修改的内容 |
| --- | --- |
| `index.html` 的 `<title>`、`og:*`、`<h1>`、`.brand` | 名字与页面标题 |
| `.avatar` 中的 `SW` | 姓名缩写，或替换为 `<img>` 头像 |
| `.tagline` | 一句话简介 |
| `#about` | 自我介绍 |
| `#projects` | 项目卡片与详情页链接 |
| `#links` | GitHub、邮箱等社交链接 |
| `footer` | 版权信息 |
| `mailto:` | 你的邮箱地址 |

配色与圆角等设计变量集中在 `styles.css` 的 `:root` 里，深色模式对应
`@media (prefers-color-scheme: dark)` 与 `[data-theme="dark"]` 两段（后者用于手动切换）。

## 内容来源

- `projects/arctic-ink/` 由本地 GNOME 美化方案整理而来：系统体检结论、配色、组件清单、
  `install.sh` 的用法与 `files/` 里的原始脚本，均来自该方案本身。
- 页面内嵌的预览图由方案的 `scripts/make-preview.sh` 生成后转成 WebP：
  `style-card.webp`（1600×1060）与 `thumb.webp`（720×416，首页卡片用）。
