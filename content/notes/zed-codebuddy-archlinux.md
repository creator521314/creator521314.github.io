---
title: "Arch Linux 下 Zed 对接 CodeBuddy Code"
linkTitle: "Zed 对接 CodeBuddy Code"
date: 2026-11-03T20:24:00+08:00
description: "在 Arch Linux 上让 Zed 通过 ACP 接入 CodeBuddy Code：安装、登录、配置、验证、排错，以及 Rust/Bevy 场景下的补全分工。"
layout: note
draft: false
url: "/notes/zed-codebuddy-archlinux/"
---

> 验证环境：Arch Linux（rolling）· Zed `1.26.2-1`（extra 源）· CodeBuddy Code CLI `2.52.3` · Node.js `26.13.0`
> 适用范围：Zed 通过 **ACP（Agent Client Protocol）** 接入 CodeBuddy Code，提供问答、智能体编辑、工具调用（文件读写 / 终端）。
> 最后更新：2026-11-03

---

## 1. 原理：为什么是 ACP

CodeBuddy Code 是腾讯云的 CLI 编码智能体，它原生实现了 ACP 协议——Zed 用来对接外部智能体的标准协议。启动方式：

```bash
codebuddy --acp
```

此时 CodeBuddy 作为一个 ACP **服务端**，Zed 作为**客户端**通过 stdio 通信。Zed 侧只需在 `settings.json` 的 `agent_servers` 里登记一条启动命令，即可在 Agent 面板里创建 CodeBuddy Thread。

这与"装插件"是两条完全不同的路径：

| 方式 | 是否存在 | 说明 |
|---|---|---|
| VS Code / JetBrains 插件 | 有 | 带行内补全、代码补全候选 |
| **Zed ACP 接入** | **有（本方案）** | 问答 + 智能体编辑 + 工具调用 |
| Zed 扩展市场插件 | 无 | CodeBuddy 未提供 Zed 扩展 |

这一点必须先说清楚：**ACP 路线不提供打字时的行内补全**，补全仍由 Zed 自身的 Edit Prediction 或 Copilot 扩展负责（见第 9 节）。

---

## 2. 安装 Zed（Arch 官方源）

```bash
sudo pacman -S zed
```

`zed` 在 `extra` 源中，当前版本 `1.26.2-1`，与官方 stable 同步。

> **Arch 特有陷阱**：这个包把二进制安装为 **`/usr/bin/zeditor`**，而不是 `zed`。原因是避免与其它包冲突。
> 所以终端里请用 `zeditor`，`zed` 命令是不存在的：
>
> ```bash
> zeditor --version      # ✅
> zed --version          # ❌ command not found
> ```
>
> 如果习惯 `zed` 这个命令名，自己建个软链即可：
>
> ```bash
> sudo ln -sf /usr/bin/zeditor /usr/local/bin/zed
> ```

**可选替代**：

```bash
yay -S zed-preview-bin   # 预览版，比 stable 早约一周
yay -S zed-cn-bin        # 中文汉化版（社区维护）
```

**图形依赖**：Zed 使用 Vulkan 渲染。若启动报 GPU 相关错误：

```bash
sudo pacman -S vulkan-icd-loader mesa            # Intel / AMD
# NVIDIA 用户还需：nvidia-utils（并确认 vulkaninfo 可用）
vulkaninfo --summary | head -20
```

---

## 3. 安装 CodeBuddy Code CLI

Arch 的 `nodejs`（`26.13.0`）与 `npm`（`12.2.1`）已满足要求（Node ≥ 18）。

```bash
# 建议先看一眼是否已装
which codebuddy && codebuddy --version

# 安装 / 升级到最新
sudo npm install -g @tencent-ai/codebuddy-code
```

安装后入口在 `/usr/bin/codebuddy`（软链到 `/usr/lib/node_modules/@tencent-ai/codebuddy-code/bin/codebuddy`）。

> **Arch 习惯提醒**：`npm -g` 会往 `/usr/lib/node_modules` 写文件，属于 pacman 管辖范围之外的污染。
> 介意的话改用用户级前缀，之后把 `~/.local/bin` 加进 PATH 即可：
>
> ```bash
> npm config set prefix ~/.local
> npm install -g @tencent-ai/codebuddy-code
> ```

---

## 4. 登录 CodeBuddy

两种方式，任选其一。

### 4.1 交互式扫码（推荐，一次性）

```bash
codebuddy
```

首次运行会在终端打印登录二维码 / 链接，用微信或浏览器完成授权。登录凭据缓存在 `~/.codebuddy/`，之后 ACP 模式直接复用，**不需要再登**。

### 4.2 API Key（适合 CI、多机、免交互）

在 Zed 配置里通过 `env` 注入：

```json
"env": {
  "CODEBUDDY_API_KEY": "your-api-key",
  "CODEBUDDY_INTERNET_ENVIRONMENT": "internal"
}
```

`CODEBUDDY_INTERNET_ENVIRONMENT` 必须与版本匹配，否则鉴权失败：

| 版本 | 取值 |
|---|---|
| 中国版（codebuddy.cn） | `internal` |
| 国际版 | 不设置（默认） |
| iOA 版 | `ioa` |

---

## 5. 配置 Zed 接入 ACP

### 5.1 方式 A：手写 `settings.json`（可控，推荐）

编辑 `~/.config/zed/settings.json`（Zed 内 `Ctrl+,`，或命令面板执行 `zed: open settings`）：

```json
{
  "agent_servers": {
    "CodeBuddy Code": {
      "command": "codebuddy",
      "args": ["--acp"],
      "env": {}
    }
  }
}
```

- `command`：`codebuddy` 需在 GUI 会话的 PATH 中。若从桌面图标启动时找不到，写绝对路径 `/usr/bin/codebuddy` 最稳妥。
- `args`：`["--acp"]` 是协议开关，不能省。
- `env`：可选，放 API Key 或代理变量（Arch 上常需要，见 7.2）。

### 5.2 方式 B：在 Zed 界面里一键添加

Zed 1.26 内置了 ACP 智能体注册表，`codebuddy-code` 已在官方索引中：

1. 打开左侧 **Agent 面板**
2. 智能体下拉 → **Add Agent** / 浏览注册表
3. 搜索 `Codebuddy`，选中 **Codebuddy Code**（Tencent Cloud）
4. 点击安装，Zed 会用 `npx @tencent-ai/codebuddy-code --acp` 拉起

> 方式 B 的好处是版本自动跟随注册表（比本地 npm 全局包新）；
> 代价是首次启动要联网走 npx，且多一层 node 进程。
> 两种方式可共存，用哪个由 Agent 面板里选中的条目决定。

### 5.3 重启生效

配置改完执行 `zed: reload`（命令面板）或直接重启：

```bash
pkill -f zeditor; zeditor ~/your-project &
```

---

## 6. 验证

**第 1 步 · 确认 ACP 能起来**（脱离 Zed 单独测）：

```bash
echo '' | timeout 5 codebuddy --acp
```

无 "command not found"、无鉴权报错即正常（它会等待 stdin 上的 JSON-RPC，超时退出属预期）。

**第 2 步 · 在 Zed 里建 Thread**：

1. Agent 面板 → 智能体选择器 → 选中 **CodeBuddy Code**
2. 点 **+** 新建 Thread，发一句 `你好，当前仓库是做什么的？`
3. 正常表现：有流式回复、顶部显示当前登录用户、输入框支持 `/` 命令补全、执行文件改动时弹出 diff 供审阅

**第 3 步 · 看日志**（出问题时唯一可信来源）：

```bash
tail -f ~/.local/share/zed/logs/Zed.log | grep -i -E "acp|agent|codebuddy"
```

---

## 7. 排错清单

### 7.1 Zed 报"agent 启动失败 / command not found"

**根因**：GUI 会话的 PATH 与终端不同。Arch 上 GNOME/KDE 从 `.desktop` 启动时**不会**读取 `.bashrc`，因此 `~/.cargo/bin`、`~/.local/bin`、npm 的用户级前缀统统不在 PATH 里。

**三步定位**：

```bash
# 在 Zed 内置终端里（Ctrl+`）执行，这才是 Zed 的真实环境
echo $PATH
which codebuddy
```

修法（按优先级）：

1. 配置里写死绝对路径：`"command": "/usr/bin/codebuddy"`
2. 或者在配置里补 PATH：

```json
"env": {
  "PATH": "/usr/local/bin:/usr/bin:/bin:/home/your-user/.cargo/bin:/home/your-user/.local/bin"
}
```

> 把 `your-user` 换成你自己的用户名。`env.PATH` 是字面量，`$HOME` 不会在这里被展开，
> 所以必须写绝对路径。

### 7.2 公司网络 / 需要代理

```json
"env": {
  "HTTP_PROXY": "http://127.0.0.1:7890",
  "HTTPS_PROXY": "http://127.0.0.1:7890"
}
```

> 端口按你本机代理的实际配置调整；回环地址只指向本机，不会暴露外部网络信息。

### 7.3 鉴权失败（401 / 未登录）

- 终端交互式再登一次：`codebuddy` → 扫码
- 或检查 `CODEBUDDY_INTERNET_ENVIRONMENT` 是否为 `internal`
- 凭据目录：`~/.codebuddy/`（清掉后重新登录可解异常态）

### 7.4 版本不一致（本地 CLI 与注册表差很多）

```bash
codebuddy --version                      # 本地
curl -s https://cdn.agentclientprotocol.com/registry/v1/latest/registry.json | grep -A2 codebuddy-code
```

升级本地：`sudo npm install -g @tencent-ai/codebuddy-code@latest`

### 7.5 Thread 建了但没反应

多数是 `--acp` 参数漏了，或 `command` 指向了某个 shell 包装脚本导致 stdio 被污染。用 7.1 的绝对路径 + 第 6 节第 1 步单独验证。

---

## 8. Rust 开发增强（Arch + Bevy 场景）

Zed 本身是 Rust 写的，`rust-analyzer` 是它的头等公民。Arch 上装 rustup 后还有两个必配项。

### 8.1 让 Zed 找得到 rust-analyzer

```bash
rustup component add rust-analyzer      # 若未安装
ln -sf ~/.cargo/bin/rust-analyzer /usr/local/bin/rust-analyzer
```

不建软链的话，症状是：Rust 项目打开后没补全、没跳转、底部无 check 状态——因为 GUI 的 PATH 里没有 `~/.cargo/bin`（同 7.1 根因）。

### 8.2 rust-analyzer 针对 Bevy 调优

```json
"lsp": {
  "rust-analyzer": {
    "initialization_options": {
      "check": { "command": "clippy" },
      "cargo": { "features": "all", "targetDir": true },
      "procMacro": { "enable": true },
      "inlayHints": { "lifetimeElisionHints": { "enable": "skip_trivial" } }
    }
  }
}
```

- `check.command: "clippy"`：诊断质量高于 `cargo check`
- `cargo.targetDir: true`：Zed 的诊断产物与终端 `cargo build` 分离，避免 target 锁争用
- Bevy 的 proc-macro 极重，`procMacro.enable` 保证 derive 正常展开；索引首次会慢，之后走缓存

### 8.3 调试

扩展市场装 **CodeLLDB**（Linux 下基于 LLDB 的 DAP 适配器），支持断点、变量面板、调用栈。

### 8.4 三方分工

| 职责 | 承担者 |
|---|---|
| 语义补全、跳转、重构、内联类型提示 | rust-analyzer（LSP） |
| 打字时的行内预测 | Zed Edit Prediction（Zeta）或 Copilot 扩展 |
| 自然语言任务（"把这个 system 改成 Query 过滤写法"） | CodeBuddy（ACP） |

---

## 9. 能力边界：关于"代码补全"

必须明确区分两个概念，否则会误以为是配置没生效：

- **行内补全（Edit Prediction，边打字边出现灰字）** → Zed 只支持自家 Zeta 模型、Copilot、Supermaven 三类 provider。**CodeBuddy 不提供 Zed 的补全 provider**，这是生态缺口，不是配置问题。
- **行内改写（Inline Assist，选中代码后 Ctrl+Enter 下指令）** → 走 assistant 语言模型；CodeBuddy 的入口在 Agent 面板，两者不互通。

所以本方案的实际收益是：**问答、跨文件重构、跑命令、读代码库**。若你也想要 CodeBuddy 级别的补全，目前只能退回 VS Code 插件，或接受 Zed 自带 Edit Prediction。

---

## 10. 附录：一份完整的 `~/.config/zed/settings.json`

```json
{
  "ui_font_size": 16,
  "buffer_font_size": 15,
  "theme": {
    "mode": "system",
    "light": "One Light",
    "dark": "One Dark"
  },

  "agent_servers": {
    "CodeBuddy Code": {
      "command": "/usr/bin/codebuddy",
      "args": ["--acp"],
      "env": {
        "PATH": "/usr/local/bin:/usr/bin:/bin:/home/your-user/.cargo/bin:/home/your-user/.local/bin"
      }
    }
  },

  "lsp": {
    "rust-analyzer": {
      "initialization_options": {
        "check": { "command": "clippy" },
        "cargo": { "features": "all", "targetDir": true },
        "procMacro": { "enable": true }
      }
    }
  },

  "languages": {
    "Rust": {
      "inlay_hints": { "enabled": true },
      "format_on_save": "on",
      "formatter": { "language_server": { "name": "rust-analyzer" } }
    }
  }
}
```

> 示例里的 `your-user` 换成自己的用户名，代理端口按本机实际配置调整。

改完 `zed: reload`，Agent 面板选 CodeBuddy Code 建 Thread 即可。

---

## 附：命令速查

```bash
sudo pacman -S zed                            # 装 Zed（二进制名 zeditor）
sudo npm i -g @tencent-ai/codebuddy-code      # 装 CodeBuddy CLI
codebuddy                                     # 首次登录（扫码）
codebuddy --acp                               # 手动验证 ACP 服务端
ln -sf ~/.cargo/bin/rust-analyzer /usr/local/bin/rust-analyzer   # 修 rust-analyzer 可见性
tail -f ~/.local/share/zed/logs/Zed.log       # 看日志
zeditor ~/project                             # 打开项目
```
