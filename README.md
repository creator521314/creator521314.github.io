# Serene Walker · 个人主页

一个单文件、零依赖的静态个人主页，直接由 GitHub Pages 托管。

## 本地预览

直接双击打开 `index.html`，或在目录中启动一个静态服务器：

```bash
python3 -m http.server 8000
# 然后访问 http://localhost:8000
```

## 发布到 GitHub Pages

```bash
git add .
git commit -m "Add personal homepage"
git push -u origin main
```

推送后，在 GitHub 仓库中进入 **Settings → Pages**：

- **Source** 选择 `Deploy from a branch`
- **Branch** 选择 `main`，目录选择 `/ (root)`
- 保存，等待 1–2 分钟即可访问

访问地址：

```
https://creator521314.github.io/
```

> 这是 GitHub 用户主页站点：仓库名必须与用户名一致（`creator521314.github.io`），
> Pages 的 Source 为 `main` 分支根目录。页面使用相对路径，所以本地目录名可以不同。

## 自定义清单

所有内容都在 `index.html` 中，搜索替换即可：

| 位置 | 需要修改的内容 |
| --- | --- |
| `<title>`、`og:*`、`<h1>`、`.brand` | 名字与页面标题 |
| `.avatar` 中的 `SW` | 姓名缩写，或替换为 `<img>` 头像 |
| `.tagline` | 一句话简介 |
| `#about` | 自我介绍 |
| `#projects` 三个 `.project` | 项目名称、描述、链接 |
| `#links` | GitHub、邮箱等社交链接 |
| `footer` | 版权信息 |
| `mailto:` | 你的邮箱地址 |

配色在 `:root` 的 CSS 变量中修改，深色模式对应 `[data-theme="dark"]` 段落。
