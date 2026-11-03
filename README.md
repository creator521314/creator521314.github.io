# Serene Walker · 个人主页

用 Hugo 构建、由 GitHub Actions 发布到 GitHub Pages 的静态站点。首页是个人简介、项目列表与最近文章；
文章用 Markdown 写，项目页里附可直接查看 / 下载的原始文件。

## 目录结构

```
.
├── hugo.toml                    # baseURL、标题、参数、内容安全策略
├── assets/                      # 走 Hugo Pipes：压缩 + 内容指纹
│   ├── css/                     # base / home / project / viewer
│   └── js/                      # site.js（构建时内联）/ viewer.js（查看器）
├── layouts/
│   ├── baseof.html              # 全站骨架：head、顶栏、页脚、CSS/JS 引入
│   ├── home.html                # 首页内容包装
│   ├── page.html                # 项目页 / 查看器的内容包装
│   ├── note.html                # 文章正文（标题 + 日期 + 正文）
│   ├── section.html             # /notes/ 与 /projects/ 列表页
│   ├── 404.html                 # 404 页
│   ├── sitemap.xml              # 自定义 sitemap，跳过 noindex 页面
│   └── shortcodes/
│       └── notes-section.html   # 首页「文章」区块（无文章时整块不渲染）
├── content/
│   ├── _index.html              # 首页
│   ├── notes/
│   │   ├── _index.md            # /notes/ 的说明
│   │   ├── <日期>-<slug>.md     # 文章，脚本生成
│   │   └── <slug>.md            # 手写文章，用 front matter 的 url 固定地址
│   ├── projects/
│   │   ├── _index.html          # /projects/ 列表页
│   │   ├── arctic-ink.html      # 项目详情页
│   │   └── ibus-rime.html      # 项目详情页
│   └── viewer.html              # 通用代码查看器
├── static/
│   ├── assets/                  # 页面用图（WebP）与 og-card.png
│   ├── favicon.svg              # 站点图标
│   ├── robots.txt               # 带 Sitemap 声明
│   └── projects/<项目>/files/   # 可下载的原始文件，原样发布
├── scripts/new-note.sh          # 新建文章的脚本
├── skills/add-project-page/     # 从 pet-project 到项目页的流程（SKILL.md）
├── skills/add-note/             # 整理 Markdown 为文章的流程（SKILL.md）
├── .github/workflows/pages.yml  # 构建 + 发布
└── README.md
```

## 构建与发布

推送 `main` 后由 `.github/workflows/pages.yml` 完成：检出（`fetch-depth: 0`，供 `enableGitInfo`
算最后更新时间）→ 安装 Hugo 0.169.0 extended → `hugo --minify --gc` → 上传 artifact →
`deploy-pages`。仓库 **Settings → Pages** 的 Source 是 **GitHub Actions**，不要再改回分支发布。

`public/` 是构建产物，不入库（见 `.gitignore`）。

CSS 与 JS 不再放在 `static/`，而是放在 `assets/` 走 Hugo Pipes：构建时自动压缩并加上内容指纹
（`/css/base.min.<hash>.css`），改样式后用户不会吃到旧缓存。`site.js` 会被内联进 `<head>`，
省一个请求，同时保证主题在首屏前生效。

本地构建需要 Hugo 0.169+：

```bash
hugo server        # http://localhost:1313
hugo --minify      # 产物在 public/
```

## 发表文章

一条命令生成新文章：

```bash
./scripts/new-note.sh "标题" [slug]
```

- 生成 `content/notes/<日期>-<slug>.md`，front matter 已填好 `title`、`date`、`layout: note`、`draft: false`。
- 不传 slug 时从标题生成；中文标题会退化成 `note`，建议顺手给个英文 slug。
- 同一天重名会自动加 `-2`，不会覆盖。
- 线上地址是 `/notes/<日期>-<slug>/`。

**已经有一份写好的 Markdown**（教程、配置说明、踩坑记录）时，不必走脚本：直接放进
`content/notes/<slug>.md`，补齐 front matter（`title` / `date` / `description` / `layout: note` /
`draft: false` / `url`，长标题再给个 `linkTitle`），删掉正文第一行的大标题——`note.html`
已经输出 `<h1>`。线上地址用 `url` 固定，以后别改文件名。完整流程与验收清单见
[skills/add-note/SKILL.md](skills/add-note/SKILL.md)。

然后编辑正文（Markdown），写完：

```bash
git add -A
git commit -m "note: 标题"
git push
```

约 1 分钟后自动发布。首页的「文章」区显示最近 3 篇，`/notes/` 是全部列表，顶栏有入口。

约定：

- 排序按 front matter 的 `date` 倒序；`draft: true` 的文章不会被构建。
- 列表页与首页文章区显示 `linkTitle`（没写则回退到 `title`）；缺 `date` 会显示零值日期，务必写全。
- 代码块用中性样式（没有语法高亮），深浅色都跟随站点配色。
- 图片暂不支持上传流程：临时可以放在 `static/assets/`，正文里写 `![说明](/assets/xxx.png)`；
  以后接图床，只需要把正文里的图片地址换掉。

## 页面约定

- 页面正文是 `content/**.html`：front matter 写标题、描述和额外资源，正文直接写 HTML。
- 文章是 `content/notes/*.md`，由 Hugo 渲染 Markdown。
- `hugo.toml` 里 `[security] allowContent` 只放行 `text/html` 与 `text/markdown`（Hugo 默认禁止 HTML 内容）。
- 通用 head / 顶栏 / 页脚在 `layouts/baseof.html`，页面内容经 `block "main"` 注入。
- 站内链接写根路径（`/assets/...`），站点部署在域名根目录。
- 页面专属样式放 `assets/css/<名字>.css`，用 front matter 的 `extra_css` 引入；脚本放
  `assets/js/<名字>.js`，用 `extra_js` 引入——两者都会在构建时压缩并加指纹。
- 页脚返回链接由 front matter 的 `back` / `back_label` 控制，不写则显示「由 GitHub Pages 托管」。
- 页脚会自动显示「更新于 <日期>」，取自 git 提交时间（`enableGitInfo`）。
- 列表页（`/notes/`、`/projects/`）用 `.LinkTitle` 显示条目标题，所以长标题的页面要写
  `linkTitle` 给一个短名字。

## 文件与下载

- 原始文件在 `static/projects/<项目>/files/`，构建后路径不变，可直接访问、下载。
- 项目页的「查看」走 `viewer.html?p=<项目>&f=<相对路径>`，站内读取并带行号显示；
  「下载」指向文件本身，链接带 `download` 属性。
- 查看器在 `assets/js/viewer.js` 的 `PROJECTS` 里登记项目，并对 `p` / `f` 做路径校验。
- 清单里的文件大小是手写的，换文件后记得同步。

这些文件与 [pet-projects](https://github.com/creator521314/pet-projects) 仓库的
`gnome-theme/` 保持一致，更新时同步：

```bash
rsync -a --exclude backup/ ../pet-projects/gnome-theme/ static/projects/arctic-ink/files/
```

没有上传 `backup/`：里面是本机的 dconf 备份与扩展清单，含个人设置。

`wallpapers/*-1920x1080.jpg` 是站点侧派生的轻量版（2560×1440 PNG 约 3 MB，1080p JPEG 约 30 KB），
pet-projects 仓库里没有这两个文件；重新 rsync 不会覆盖它们。原图换了记得一起重导：

```bash
cd static/projects/arctic-ink/files/wallpapers
for n in arctic-ink arctic-mist; do
  magick "$n-2560x1440.png" -resize 1920x1080 -strip -quality 88 "$n-1920x1080.jpg"
done
```

## 新增一个项目

1. 新建 `content/projects/<项目>.html`，front matter 写 `title`、`linkTitle`（列表页用的短名）、
   `description`、`og_image`（可选，默认用 `og-card.png`）、`url: /projects/<项目>/`、`extra_css`。
2. 需要分发的文件放进 `static/projects/<项目>/files/`，在详情页 `.filelist` 里加条目。
3. 在 `assets/js/viewer.js` 的 `PROJECTS` 里登记：
   `'<项目>': { title: '显示名', path: 'projects/<项目>/' }`。
4. 页面用图放 `static/assets/<项目>/`，优先 WebP；首屏以下的大图加 `loading="lazy"`。
5. 在 `content/_index.html` 的 `#projects` 里追加卡片。

完整流程、页面骨架、查看器登记和验收清单见 [skills/add-project-page/SKILL.md](skills/add-project-page/SKILL.md)。

## 收录与分享

- `static/assets/og-card.png` 是全站默认的分享图（1200×630）。页面可以用 front matter 的
  `og_image` 覆盖，项目页现在分别用 `style-card.webp` 与 `cover.webp`。
- `layouts/baseof.html` 输出 `canonical`、`og:url`、`og:image`、`twitter:card`，以及浅色 / 深色
  两段 `theme-color`（`#fbfaf7` / `#14171a`），手机浏览器地址栏会跟着站点主题走。
- `layouts/sitemap.xml` 会跳过 `noindex` 页面——查看器因此不会出现在 sitemap 里。
- `static/robots.txt` 声明了 sitemap 地址；`layouts/404.html` 是自定义 404（GitHub Pages 会直接用
  `public/404.html`）。

## 自定义清单

| 位置 | 需要修改的内容 |
| --- | --- |
| `hugo.toml` | 站点标题、baseURL、参数、`og_image` 默认值 |
| `content/_index.html` 的 front matter | 首页标题与描述 |
| `content/_index.html` 的 `.avatar` / `.tagline` | 姓名缩写、一句话简介 |
| `content/_index.html` 的 `#about` | 自我介绍 |
| `content/_index.html` 的 `#projects` | 项目卡片 |
| `layouts/baseof.html` 的页脚 | 版权与托管说明 |
| `mailto:` | 邮箱地址 |

配色与圆角等设计变量集中在 `assets/css/base.css` 的 `:root` 里，深色模式对应
`@media (prefers-color-scheme: dark)` 与 `[data-theme="dark"]` 两段。

## 内容来源

- `content/projects/arctic-ink.html` 由本地 GNOME 美化方案整理而来，脚本与文件与
  [pet-projects](https://github.com/creator521314/pet-projects) 仓库的 `gnome-theme/` 一致。
- 页面内嵌的预览图由该方案的 `scripts/make-preview.sh` 生成后转成 WebP：
  `style-card.webp`（1600×1060）与 `thumb.webp`（720×416，首页卡片用）。
