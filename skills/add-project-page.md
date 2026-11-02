# Skill：把 pet-project 做成首页独立项目页

适用场景：`pet-projects` 里新增了一个项目，要在个人主页给它一个 `/projects/<slug>/` 页面，
并出现在首页的项目列表里。

整个流程只碰 4–6 个文件，不写新样式（复用 `assets/css/project.css`），约 20 分钟。

---

## 0. 先备齐四样东西

| 输入 | 说明 |
| --- | --- |
| slug | 目录名，小写短横线，如 `ibus-rime`、`arctic-ink` |
| 一句话介绍 | 首页卡片和 `description` 用 |
| 3–4 个事实 | 平台 / 技术栈 / 输入输出 / 交付物，填 `.facts` |
| 可分发文件 | 没有就跳过第 4 步 |

---

## 1. 放素材

```
static/assets/<slug>/
├── cover.webp    # 1440×832，页面顶部大图
└── thumb.webp    # 720×416，首页卡片缩略图
```

两张都是 WebP，控制在 50 KB 内。没有截图时用 ImageMagick 画一张深色卡片
（配色跟站点一致：底 `#0b0f14`、面板 `#0e1a24`、强调 `#2ec6b0`、正文 `#e6edf3`、次要 `#93a4b4`）：

```bash
magick -size 1440x832 xc:'#0b0f14' \
  -fill '#0e1a24' -stroke '#1d2b38' -strokewidth 2 \
  -draw 'roundrectangle 60,60 1380,772 24,24' -stroke none \
  -font Adwaita-Sans-Bold -pointsize 66 -fill '#e6edf3' -annotate +100+172 '<slug>' \
  -font /usr/share/fonts/MapleMono-CN-Regular.ttf -pointsize 22 -fill '#93a4b4' \
  -annotate +118+326 '<一行说明>' \
  -strip -quality 84 static/assets/<slug>/cover.webp

magick static/assets/<slug>/cover.webp -resize 720x416 \
  -strip -quality 84 static/assets/<slug>/thumb.webp
```

---

## 2. 建项目页

新建 `content/projects/<slug>.html`，front matter 一定要有：

```yaml
---
title: "<项目名> · <一句话> · Serene Walker"
description: "<搜索与分享用的描述>"
og_title: "<项目名> · <一句话>"
og_description: "<分享卡片描述>"
og_type: article
extra_css: ["project"]          # 复用项目页样式
url: "/projects/<slug>/"        # 决定线上地址
back: "/"
back_label: 返回首页
---
```

正文按这个骨架写（类名都在 `project.css` 里）：

```html
<a class="back" href="/">← 返回首页</a>
<p class="eyebrow">项目 0N · 分类</p>
<h1>项目名</h1>
<p class="lede">两句话说明它解决什么问题。</p>

<div class="actions">
  <a class="btn primary" href="https://github.com/creator521314/pet-projects/tree/main/<slug>"
     target="_blank" rel="noopener">GitHub 仓库 ↗</a>
  <a class="btn" href="#files">文件</a>
</div>

<dl class="facts">
  <div><dt>平台</dt><dd>…</dd></div>
  <div><dt>技术栈</dt><dd>…</dd></div>
  <div><dt>交付</dt><dd>…</dd></div>
  <div><dt>状态</dt><dd>…</dd></div>
</dl>

<figure class="shot">
  <img src="/assets/<slug>/cover.webp" width="1440" height="832"
       alt="一句话描述这张图" decoding="async">
  <figcaption>图注。</figcaption>
</figure>

<section>
  <h2>为什么做</h2>
  <p class="section-note">一句话点题。</p>
  <ul class="bullets"><li>…</li></ul>
</section>

<section>
  <h2>怎么做</h2>
  <div class="table-wrap"><table>…</table></div>
</section>

<section>
  <h2>配置 / 用法片段</h2>
  <pre><code>…</code></pre>
  <p class="note">注意点。</p>
</section>

<section id="files"> …文件列表，见第 4 步… </section>

<section>
  <h2>踩过的坑</h2>
  <ul class="bullets"><li>…</li></ul>
</section>
```

> 主页面的 `.eyebrow` 编号按首页卡片顺序递增（项目 01、02…）。

---

## 3. 首页加卡片

编辑 `content/_index.html` 的 `#projects`，复制一张已有卡片改内容：

```html
<a class="project featured" href="/projects/<slug>/">
  <img class="project-thumb" src="/assets/<slug>/thumb.webp"
       width="720" height="416" decoding="async"
       alt="一句话描述缩略图">
  <div class="project-body">
    <span class="project-tag">分类 · 技术栈</span>
    <h3>项目名<span class="arrow" aria-hidden="true">↗</span></h3>
    <p>一句话说明它解决什么问题。</p>
  </div>
</a>
```

- `project featured` 是左图右文；不想配图就用 `class="project"`。
- 缩略图**不要加** `loading="lazy"`，否则首屏可能先空一块。

---

## 4. 文件下载（可选）

存放：

```
static/projects/<slug>/files/...
```

页面上加清单，每项两个动作：

```html
<ul class="filelist">
  <li>
    <div class="file-info">
      <code>install.sh</code>
      <span>一句话说明这个文件</span>
    </div>
    <div class="file-meta">
      <span>18 KB</span>
      <a href="/viewer.html?p=<slug>&amp;f=install.sh">查看</a>
      <a href="files/install.sh" download>下载</a>
    </div>
  </li>
</ul>
```

然后在 `static/assets/js/viewer.js` 的 `PROJECTS` 里登记，否则「查看」会报错：

```js
'<slug>': { title: '<显示名>', path: 'projects/<slug>/' }
```

---

## 5. 本地验证

```bash
hugo server            # 或 .tools/hugo server
```

逐项点一遍：

- `/projects/<slug>/` 能打开，封面、代码块、表格正常；
- 首页出现新卡片，缩略图正常；
- 「查看」打开查看器、带行号；「下载」拿到正确文件；
- 390px 宽度下不横向溢出。

---

## 6. 发布

```bash
git add -A
git commit -m "Add <slug> project page"
git push
```

Actions 约 1 分钟完成。之后核对线上页面与文件直链，并确认 `/projects/<slug>/` 返回 200。

---

## 约定

- slug 用小写短横线，页面地址由 front matter 的 `url` 决定。
- 站内链接、图片一律写根路径（`/assets/...`、`/projects/...`）。
- 页面样式复用 `project.css`；确实要新样式时加 `static/assets/css/<slug>.css` 并写
  `extra_css: ["<slug>"]`。
- 文件清单里的**大小是手写的**，换文件后要同步。
- `content/projects/_index.html` 用来抑制 `/projects/` 自动列表页，不要删。
- 项目目录在 `pet-projects` 仓库里，页面只做展示和下载镜像。

## 验收清单

- [ ] `/projects/<slug>/` 200，标题/描述/OG 正确
- [ ] 首页卡片出现，缩略图加载
- [ ] `cover.webp` 与 `thumb.webp` 尺寸、体积正常
- [ ] 查看器能打开每个文本文件
- [ ] 下载链接命中真实文件
- [ ] 移动端无横向溢出
- [ ] Actions 成功，线上与本地一致

## 实践里踩过的坑

1. **内容文件必须有 front matter**，否则 Hugo 当静态文件，不套布局也不生成页面。
2. **卡片缩略图不要 lazy**，无头截图和慢网络下会先显示空白框。
3. **查看器要登记项目**，否则 `?p=<slug>` 直接落到「项目参数不对」。
4. **文件大小是硬编码**，换了脚本不同步就会和实际不符。
5. **封面别用真实截图以外的东西冒充**；没有截图就做一张明确的说明卡，图注写清楚。
6. 页面正文是 HTML，Hugo 不会做 Markdown 转换；`<` 要写成 `&lt;`。
