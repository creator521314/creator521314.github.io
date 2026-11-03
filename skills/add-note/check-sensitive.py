#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""发布前敏感信息筛查：把机器 / 个人专属信息换成通用占位符。

用法：
    python3 check-sensitive.py <file.md>                # 只报告，不改文件
    python3 check-sensitive.py <file.md> --fix          # 自动替换可安全通用的项
    python3 check-sensitive.py <file.md> --deny a,b     # 追加自定义敏感词（人工确认）

退出码：
    0  无待处理项（或 --fix 后已清零）
    1  存在可自动替换项但没加 --fix
    2  存在必须人工确认的项（真实凭据、身份信息、内网地址等）
"""

import argparse
import os
import re
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# 规则表
#   action = auto    可安全替换为通用值，--fix 时自动执行
#   action = review  不自动替换：可能是真实凭据 / 身份信息，先人工确认并轮换
#   action = info    仅提示，属于通用示例，可保留
# 替换值一律用「读者一眼能看出要改」的占位符，不用 <user> 这种尖括号（HTML 里会被转义）。
# ---------------------------------------------------------------------------
RULES = [
    {
        "id": "home-linux",
        "label": "Linux 本机用户目录",
        "pattern": r"/home/(?!your-user/)[A-Za-z0-9._-]+/",
        "action": "auto",
        "replacement": "/home/your-user/",
        "note": "替换后请在正文补一句：把 your-user 换成自己的用户名",
    },
    {
        "id": "home-macos",
        "label": "macOS 本机用户目录",
        "pattern": r"/Users/(?!your-user/)[A-Za-z0-9._-]+/",
        "action": "auto",
        "replacement": "/Users/your-user/",
        "note": "同上，补占位符说明",
    },
    {
        "id": "home-windows",
        "label": "Windows 本机用户目录",
        "pattern": r"[A-Za-z]:\\Users\\[^\\\s\"']+\\",
        "action": "auto",
        "replacement": "C:\\Users\\your-user\\",
        "note": "同上，补占位符说明",
    },
    {
        "id": "email",
        "label": "邮箱地址",
        "pattern": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
        "action": "review",
        "replacement": None,
        "note": "若是公开联系邮箱可保留；私人邮箱改成 you@example.com",
    },
    {
        "id": "cn-mobile",
        "label": "手机号",
        "pattern": r"(?<!\d)1[3-9]\d{9}(?!\d)",
        "action": "review",
        "replacement": None,
        "note": "改成 13800000000 之类示例号",
    },
    {
        "id": "credential",
        "label": "疑似真实凭据 / 私钥",
        "pattern": (
            r"\b(?:sk|ghp|gho|ghu|ghs|ghr|github_pat)_[A-Za-z0-9_]{16,}\b"
            r"|\bAKIA[0-9A-Z]{16}\b"
            r"|-----BEGIN [A-Z ]*PRIVATE KEY-----"
        ),
        "action": "review",
        "replacement": None,
        "note": "若确为真实凭据：先去平台吊销 / 轮换，再改成占位符；已 push 的历史也要处理",
    },
    {
        "id": "secret-assignment",
        "label": "密钥 / 口令赋值（非占位符）",
        "pattern": (
            r"(?i)([\"']?[A-Za-z0-9_-]*(?:api[_-]?key|access[_-]?token|auth[_-]?token"
            r"|secret|password|passwd|private[_-]?key)[\"']?\s*[:=]\s*[\"'])"
            r"(?!your|YOUR|<|\$|xxx|placeholder|example|changeme|\{)[^\"'\s]{8,}[\"']"
        ),
        "action": "review",
        "replacement": None,
        "note": "值不像占位符，需确认是不是真实密钥；是则先轮换再改",
    },
    {
        "id": "url-secret",
        "label": "URL 里带令牌参数",
        "pattern": r"[?&](?:token|key|secret|password|api_key|access_token)=[^&\s\"'<>]{4,}",
        "action": "review",
        "replacement": None,
        "note": "去掉查询串或换成 YOUR_TOKEN",
    },
    {
        "id": "private-ip",
        "label": "内网 IP / 内部地址",
        "pattern": (
            r"(?<![\d.])(?:10\.\d{1,3}\.\d{1,3}\.\d{1,3}"
            r"|192\.168\.\d{1,3}\.\d{1,3}"
            r"|172\.(?:1[6-9]|2\d|3[01])\.\d{1,3}\.\d{1,3})(?![\d.])"
        ),
        "action": "review",
        "replacement": None,
        "note": "改成 192.168.1.1 之类示例地址；不自动替换以免破坏语义",
    },
    {
        "id": "loopback-proxy",
        "label": "本机回环代理（通用示例，可保留）",
        "pattern": r"https?://(?:127\.0\.0\.1|localhost):\d{2,5}",
        "action": "info",
        "replacement": None,
        "note": "回环地址不泄露本机信息；若端口是你的专属配置，可加一句「按实际端口调整」",
    },
]

# 邮箱白名单：这些是文档惯例用的示例域，不算个人信息。
EMAIL_ALLOW = re.compile(r"@(?:example\.(?:com|org|net)|localhost|test\.com)\b", re.I)


def accepted(rule, value):
    """过滤明显是公开示例的误报。"""
    if rule["id"] == "email" and EMAIL_ALLOW.search(value):
        return False
    return True


def mask(value):
    """REVIEW 项在报告里脱敏，避免把真实凭据打印进终端 / 日志。"""
    value = value.replace("\n", " ")
    if len(value) <= 8:
        return value[:2] + "***"
    return value[:4] + "*" * min(12, len(value) - 6) + value[-2:]


def scan(text, extra_deny):
    rules = list(RULES)
    words = [w.strip() for w in extra_deny if w.strip()]
    if words:
        rules.append({
            "id": "custom-deny",
            "label": "自定义敏感词",
            "pattern": "|".join(re.escape(w) for w in words),
            "action": "review",
            "replacement": None,
            "note": "人工确认是否需要换成通用称呼",
        })

    hits = []
    for rule in rules:
        for m in re.finditer(rule["pattern"], text):
            value = m.group(0)
            if not accepted(rule, value):
                continue
            hits.append({
                "rule": rule,
                "start": m.start(),
                "end": m.end(),
                "value": value,
                "line": text.count("\n", 0, m.start()) + 1,
            })
    hits.sort(key=lambda h: (h["start"], -(h["end"] - h["start"])))
    return hits


def report(path, hits):
    print("=== 敏感信息筛查 · {} ===".format(path))
    if not hits:
        print("未发现敏感或机器专属信息。")
        return
    for h in hits:
        rule = h["rule"]
        tag = {"auto": "[AUTO  ]", "review": "[REVIEW]", "info": "[INFO  ]"}[rule["action"]]
        shown = h["value"] if rule["action"] != "review" else mask(h["value"])
        print("{} 第 {} 行  {}".format(tag, h["line"], rule["label"]))
        if rule["action"] == "auto":
            replaced = re.sub(rule["pattern"], lambda _m, r=rule["replacement"]: r, h["value"])
            print("        - {}".format(shown))
            print("        + {}".format(replaced))
        else:
            print("        {}  · {}".format(shown, rule["note"]))


def summarize(hits):
    counts = {"auto": 0, "review": 0, "info": 0}
    for h in hits:
        counts[h["rule"]["action"]] += 1
    print("汇总：可自动替换 {} 处 · 需人工确认 {} 处 · 提示 {} 处".format(
        counts["auto"], counts["review"], counts["info"]))
    return counts


def apply_fixes(text, hits):
    """从后往前替换，避免前面的偏移影响后面的位置。"""
    patches = []
    seen = set()
    for h in hits:
        rule = h["rule"]
        if rule["action"] != "auto" or rule["replacement"] is None:
            continue
        key = (h["start"], h["end"])
        if key in seen:
            continue
        seen.add(key)
        replaced = re.sub(rule["pattern"], lambda _m, r=rule["replacement"]: r, h["value"])
        patches.append((h["start"], h["end"], replaced))
    for start, end, value in sorted(patches, reverse=True):
        text = text[:start] + value + text[end:]
    return text, len(patches)


def main():
    parser = argparse.ArgumentParser(description="发布前敏感信息筛查与通用化")
    parser.add_argument("file", help="要检查的 Markdown 文件")
    parser.add_argument("--fix", action="store_true", help="自动替换可安全通用的项并写回文件")
    parser.add_argument("--deny", default=os.environ.get("NOTE_SENSITIVE_NAMES", ""),
                        help="逗号分隔的自定义敏感词，默认读环境变量 NOTE_SENSITIVE_NAMES")
    args = parser.parse_args()

    path = Path(args.file)
    if not path.is_file():
        print("文件不存在：{}".format(path), file=sys.stderr)
        return 3

    text = path.read_text(encoding="utf-8")
    hits = scan(text, args.deny.split(","))
    report(str(path), hits)
    counts = summarize(hits)

    if args.fix:
        fixed, n = apply_fixes(text, hits)
        if n:
            path.write_text(fixed, encoding="utf-8")
            print("已写回 {} 处通用化替换：{}".format(n, path))
        again = scan(path.read_text(encoding="utf-8"), args.deny.split(","))
        left = summarize(again)
        if left["review"]:
            print("仍有需人工确认的项，请处理后重新检查。")
            return 2
        return 0

    if counts["review"]:
        print("存在必须人工确认的项，请先处理。")
        return 2
    if counts["auto"]:
        print("加 --fix 可自动替换为通用信息。")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
