# Serene Walker · 个人主页

用 Hugo 构建、由 GitHub Actions 发布到 GitHub Pages 的静态站点。首页是个人简介、项目列表与最近文章；
文章用 Markdown 写，项目页里附可直接查看 / 下载的原始文件。

## 目录结构

```
.
├── hugo.toml                    # baseURL、标题、参数、内容安全策略
├── layouts/
│   ├── baseof.html              # 全站骨架：head、顶栏、页脚、CSS/JS 引入
│   ├── home.html                # 首页内容包装
│   ├── page.html                # 项目页 / 查看器的内容包装
│   ├── note.html                # 文章正文（标题 + 日期 + 正文）
│   ├── section.html             # /notes/ 列表页
│   └── shortcodes/
│       └── notes-section.html   # 首页「文章」区块（无文章时整块不渲染）
├── content/
│   ├── _index.html              # 首页
│   ├── notes/
│   │   ├── _index.md            # /notes/ 的说明
│   │   └── <日期>-<slug>.md     # 文章，脚本生成
│   ├── projects/
│   │   ├── _index.html          # 抑制 /projects/ 自动列表页
│   │   ├── arctic-ink.html      # 项目详情页
│   │   └── ibus-rime.html       # 项目详情页
│   └── viewer.html              # 通用代码查看器
├── static/
│   ├── assets/css/              # base / home / project / viewer
│   ├── assets/js/               # site.js（主题）/ viewer.js（查看器）
│   ├── assets/arctic-ink/       # 项目页用图（WebP）
│   ├── assets/ibus-rime/        # 封面与首页缩略图
│   └── projects/<项目>/files/   # 可下载的原始文件，原样发布
├── scripts/new-note.sh          # 新建文章的脚本
├── skills/add-project-page/     # 从 pet-project 到项目页的流程（SKILL.md）
├── .github/workflows/pages.yml  # 构建 + 发布
└── README.md
```

## 构建与发布

推送 `main` 后由 `.github/workflows/pages.yml` 完成：检出 → 安装 Hugo 0.169.0 extended →
`hugo --minify --gc` → 上传 artifact → `deploy-pages`。仓库 **Settings → Pages** 的
Source 是 **GitHub Actions**，不要再改回分支发布。

`public/` 是构建产物，不入库（见 `.gitignore`）。

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

然后编辑正文（Markdown），写完：

```bash
git add -A
git commit -m "note: 标题"
git push
```

约 1 分钟后自动发布。首页的「文章」区显示最近 3 篇，`/notes/` 是全部列表，顶栏有入口。

约定：

- 排序按 front matter 的 `date` 倒序；`draft: true` 的文章不会被构建。
- 代码块用中性样式（没有语法高亮），深浅色都跟随站点配色。
- 图片暂不支持上传流程：临时可以放在 `static/assets/`，正文里写 `![说明](/assets/xxx.png)`；
  以后接图床，只需要把正文里的图片地址换掉。

## 页面约定

- 页面正文是 `content/**.html`：front matter 写标题、描述和额外资源，正文直接写 HTML。
- 文章是 `content/notes/*.md`，由 Hugo 渲染 Markdown。
- `hugo.toml` 里 `[security] allowContent` 放开了 html 内容格式（Hugo 默认禁止 HTML 内容）。
- 通用 head / 顶栏 / 页脚在 `layouts/baseof.html`，页面内容经 `block "main"` 注入。
- 站内链接写根路径（`/assets/...`），站点部署在域名根目录。
- 页面专属样式放 `static/assets/css/<名字>.css`，用 front matter 的 `extra_css` 引入；
  脚本同理用 `extra_js`。
- 页脚返回链接由 front matter 的 `back` / `back_label` 控制，不写则显示「由 GitHub Pages 托管」。

## 文件与下载

- 原始文件在 `static/projects/<项目>/files/`，构建后路径不变，可直接访问、下载。
- 项目页的「查看」走 `viewer.html?p=<项目>&f=<相对路径>`，站内读取并带行号显示；
  「下载」指向文件本身，链接带 `download` 属性。
- 查看器在 `static/assets/js/viewer.js` 的 `PROJECTS` 里登记项目，并对 `p` / `f` 做路径校验。
- 清单里的文件大小是手写的，换文件后记得同步。

这些文件与 [pet-projects](https://github.com/creator521314/pet-projects) 仓库的
`gnome-theme/` 保持一致，更新时同步：

```bash
rsync -a --exclude backup/ ../pet-projects/gnome-theme/ static/projects/arctic-ink/files/
```

没有上传 `backup/`：里面是本机的 dconf 备份与扩展清单，含个人设置。

## 新增一个项目

1. 新建 `content/projects/<项目>.html`，front matter 写 `title`、`description`、
   `url: /projects/<项目>/`、`extra_css`。
2. 需要分发的文件放进 `static/projects/<项目>/files/`，在详情页 `.filelist` 里加条目。
3. 在 `static/assets/js/viewer.js` 的 `PROJECTS` 里登记：
   `'<项目>': { title: '显示名', path: 'projects/<项目>/' }`。
4. 页面用图放 `static/assets/<项目>/`，优先 WebP。
5. 在 `content/_index.html` 的 `#projects` 里追加卡片。

完整流程、页面骨架、查看器登记和验收清单见 [skills/add-project-page/SKILL.md](skills/add-project-page/SKILL.md)。

## 自定义清单

| 位置 | 需要修改的内容 |
| --- | --- |
| `hugo.toml` | 站点标题、baseURL、参数 |
| `content/_index.html` 的 front matter | 首页标题与描述 |
| `content/_index.html` 的 `.avatar` / `.tagline` | 姓名缩写、一句话简介 |
| `content/_index.html` 的 `#about` | 自我介绍 |
| `content/_index.html` 的 `#projects` | 项目卡片 |
| `layouts/baseof.html` 的页脚 | 版权与托管说明 |
| `mailto:` | 邮箱地址 |

配色与圆角等设计变量集中在 `static/assets/css/base.css` 的 `:root` 里，深色模式对应
`@media (prefers-color-scheme: dark)` 与 `[data-theme="dark"]` 两段。

## 内容来源

- `content/projects/arctic-ink.html` 由本地 GNOME 美化方案整理而来，脚本与文件与
  [pet-projects](https://github.com/creator521314/pet-projects) 仓库的 `gnome-theme/` 一致。
- 页面内嵌的预览图由该方案的 `scripts/make-preview.sh` 生成后转成 WebP：
  `style-card.webp`（1600×1060）与 `thumb.webp`（720×416，首页卡片用）。
