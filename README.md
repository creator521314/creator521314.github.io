# Serene Walker · 个人主页

一个无构建、零依赖的静态站点，直接由 GitHub Pages 托管。
首页是单栏的个人简介与项目列表；每个项目在 `projects/` 下有独立详情页，共用 `styles.css` 的设计令牌。

## 目录结构

```
.
├── index.html              # 首页：自我介绍 + 项目列表
├── styles.css              # 共享样式：配色变量、排版、顶栏、按钮、页脚
├── projects/
│   └── arctic-ink.html     # 项目详情页（Arctic Ink · GNOME 桌面方案）
├── assets/
│   └── arctic-ink/         # 详情页与卡片用图（WebP，均已压缩）
├── .nojekyll               # 跳过 Jekyll 处理，原样发布
└── README.md
```

## 本地预览

直接双击打开 `index.html` 即可（页面不含 fetch 请求，`file://` 下也能正常显示）。
需要更接近线上的环境时，起一个静态服务器：

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

## 新增一个项目

1. 在 `projects/` 下新建 `xxx.html`，复制 `projects/arctic-ink.html` 作骨架：
   改 `<title>`/`<meta>`、正文内容，资源路径前缀 `../` 保持不变。
2. 图片放到 `assets/xxx/`，优先用 WebP（单张控制在 ~100 KB 内）。
3. 在 `index.html` 的 `#projects` 里追加一张卡片：

```html
<a class="project featured" href="projects/xxx.html">
  <img class="project-thumb" src="assets/xxx/thumb.webp" width="720" height="416"
       loading="lazy" decoding="async" alt="一句话描述这张图">
  <div class="project-body">
    <span class="project-tag">分类 · 技术栈</span>
    <h3>项目名<span class="arrow" aria-hidden="true">↗</span></h3>
    <p>一句话说明它解决什么问题。</p>
  </div>
</a>
```

首个卡片用 `project featured`（左图右文），其余项目直接用 `project` 即可。

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

- `projects/arctic-ink.html` 由本地 GNOME 美化方案整理而来：系统体检结论、配色、
  组件清单与 `install.sh` 的用法，均以该方案的 README 和脚本为准。
- 预览图由方案的 `scripts/make-preview.sh` 生成，站点内已转成 WebP：
  `style-card.webp`（1600×1060）与 `thumb.webp`（720×416，首页卡片用）。
