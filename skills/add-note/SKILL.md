---
name: add-note
description: 把一份已有的 Markdown 指导 / 记录整理成本站文章（/notes/），包括 front matter、正文去重、URL 与日期约定、首页文章区与 sitemap 验证、发布清单。也覆盖用 new-note.sh 从零写文章的路径。
---

# 把一份 Markdown 整理成站点文章

适用场景：手上已经有一份写好的 Markdown（教程、踩坑记录、配置说明），要放进 `content/notes/`
并在首页「文章」区、`/notes/` 列表和 sitemap 里正常出现。

与 `scripts/new-note.sh` 的分工：脚本负责**从零新建**并生成带日期的文件；本 skill 负责
**整理已有文件**以及两条路径共用的验收标准。全程只碰 1–3 个文件，约 10 分钟。

---

## 0. 两条入口

| 场景 | 做法 |
| --- | --- |
| 从零写一篇 | `./scripts/new-note.sh "标题" slug`，front matter 已填好，直接写正文 |
| 已有 Markdown（如 `zed-codebuddy-archlinux.md`） | 复制到 `content/notes/<slug>.md`，按第 2 步补 front matter |

文件名两种都合法：

- 脚本生成：`2026-11-03-<slug>.md`，URL 自动是 `/notes/2026-11-03-<slug>/`。
- 手动放置：语义化 slug 如 `zed-codebuddy-archlinux.md`，**用 front matter 的 `url` 固定线上地址**
  （`/notes/zed-codebuddy-archlinux/`），以后不要改名，否则外链会断。

中文标题 slug 会退化成 `note`，所以 slug 一律给英文小写短横线。

---

## 1. front matter（必填项一个都不能少）

```yaml
---
title: "Arch Linux 下 Zed 对接 CodeBuddy Code"
linkTitle: "Zed 对接 CodeBuddy Code"   # 列表页用的短名，不写则用 title
date: 2026-11-03T20:24:00+08:00        # 排序依据，务必带时区
description: "搜索与分享用的一句话描述"
layout: note                            # 关键：不写就不会套文章模板
draft: false
url: "/notes/zed-codebuddy-archlinux/"  # 手写文件时固定 URL
---
```

| 字段 | 必填 | 说明 |
| --- | --- | --- |
| `title` | 是 | 文章页 `<h1>` 与浏览器标题 |
| `date` | 是 | 首页 / 列表按它倒序；缺了会显示 `0001-01-01` |
| `layout: note` | 是 | 走 `layouts/note.html`（标题 + 中文日期 + 正文） |
| `draft: false` | 是 | `true` 不会被构建 |
| `description` | 建议 | meta description 与分享卡片 |
| `linkTitle` | 长标题建议 | `/notes/` 列表与首页文章区都显示它 |
| `url` | 手写文件时 | 固定地址，避免以后改名断链 |

---

## 2. 正文整理

- **删掉正文第一行的大标题**。`note.html` 已经输出 `<h1>{{ .Title }}</h1>`，正文再留一个 `# ...`
  会变成两个 h1。标题写进 front matter 就好。
- 正文是 Markdown，不是 HTML；`<` 要写成 `&lt;`，`&` 写成 `&amp;`。
- 代码块**没有语法高亮**（`hugo.toml` 里 `codeFences = false`），深浅色都跟随 `base.css`；
  保留 ```bash 这类语言标记无害。
- 站内图片放 `static/assets/`，正文写 `![说明](/assets/xxx.png)`（根路径）。
- 站内链接一律根路径（`/projects/...`、`/notes/...`）。
- 正文里不要出现 `{{ ... }}`，会被 Hugo 当模板语法解析。
- 表格、引用块、分隔线都用标准 Markdown，`base.css` 里已有对应样式。

> 本次范例：`content/notes/zed-codebuddy-archlinux.md`（ACP 接入指南，含 10 节、
> 3 张表格、22 段代码块），只做了「加 front matter + 删首行 h1」两处改动就接入了站点。

---

## 3. 本地验证

```bash
rm -rf public && ./.tools/hugo --minify --gc
```

逐项确认：

- `public/notes/<slug>/index.html` 存在，全文只有 **1 个 `<h1>`**；
- 文章页 meta description 正确，日期显示为「2026 年 11 月 3 日」这种中文格式；
- 首页出现 `id=notes` 区块，最近 3 篇按日期倒序，`<time>` 不是 `0001-01-01`；
- `/notes/` 列表里标题用 `linkTitle`，没有零值日期；
- `sitemap.xml` 多出该文章（自定义 `layouts/sitemap.xml` 会跳过 `noindex` 页面）；
- 代码块、表格、引用块渲染正常，无残留 `{{`。

> 首页文章区与 `/notes/` 列表都会在「无文章」时自动隐藏 / 显示提示，第一篇发布后
> 才会出现内容——不用改模板。

---

## 4. 发布

```bash
git add -A
git commit -m "note: <标题>"
git push          # 直连超时则先 export https_proxy=http://127.0.0.1:7890 http_proxy=...
```

Actions 约 1 分钟完成，之后核对线上 `/notes/<slug>/` 返回 200、文件与代码块正常。

---

## 约定

- 排序只认 front matter 的 `date`，与文件名里的日期无关。
- 页面正文是 `content/**.html` 时写 HTML；文章是 `content/notes/*.md` 时写 Markdown，别混。
- `hugo.toml` 的 `allowContent` 只放行 `text/html` 与 `text/markdown`。
- 顶栏「文章」指向 `/notes/`；首页文章区只显示最近 3 篇，其余去列表页看。
- 文章不用在 `viewer.js` 里登记，那套只服务于项目页的可下载文件。

## 验收清单

- [ ] front matter 七项齐全，`layout: note` 与 `draft: false` 都在
- [ ] 正文无重复 h1，无 `{{`，特殊字符已转义
- [ ] 构建无告警，文章页 / 首页文章区 / `/notes/` 三处都能看到
- [ ] 日期正确、按倒序排列
- [ ] `sitemap.xml` 与 `og:image`（默认 `og-card.png`）正常
- [ ] 移动端无横向溢出，长代码块可横向滚动
- [ ] Actions 成功，线上与本地一致

## 实践里踩过的坑

1. **没有 front matter**：Hugo 会把 `.md` 当普通静态文件，不套布局、不进文章列表。
2. **缺 `date`**：列表显示 `0001-01-01`；`section.html` 与 `notes-section.html` 已做零值判断，
   但排序仍会乱，所以日期必须写。
3. **正文自带 `# 标题`**：与模板的 h1 重复，删掉。
4. **想改文件名**：手写文件改名会断外链，靠 `url` 固定地址更稳。
5. **中文标题不给 slug**：`new-note.sh` 会退化成 `note`，同日再写会变成 `note-2`。
