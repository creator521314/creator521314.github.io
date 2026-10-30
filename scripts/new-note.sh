#!/usr/bin/env bash
# 新建一篇文章：./scripts/new-note.sh "标题" [slug]
# 生成 content/notes/<日期>-<slug>.md，写完 push 即自动发布。
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [ $# -lt 1 ] || [ -z "${1// }" ]; then
  echo '用法: ./scripts/new-note.sh "文章标题" [slug]' >&2
  exit 1
fi

TITLE="$1"
SLUG="${2:-}"

if [ -n "$SLUG" ] && ! [[ "$SLUG" =~ ^[A-Za-z0-9_-]+$ ]]; then
  echo "slug 只能包含字母、数字、- 和 _" >&2
  exit 1
fi

if [ -z "$SLUG" ]; then
  SLUG=$(printf '%s' "$TITLE" \
    | tr '[:upper:]' '[:lower:]' \
    | sed -E 's/[^a-z0-9]+/-/g; s/^-+//; s/-+$//')
fi
[ -z "$SLUG" ] && SLUG="note"

DATE=$(date +%Y-%m-%d)
STAMP=$(date +%Y-%m-%dT%H:%M:%S%:z)
BASE="$ROOT/content/notes/$DATE-$SLUG"
FILE="$BASE.md"
n=2
while [ -e "$FILE" ]; do
  FILE="$BASE-$n.md"
  n=$((n + 1))
done

# 标题里的双引号要转义，否则 front matter 的 YAML 会坏
TITLE_YAML=${TITLE//\"/\\\"}

mkdir -p "$ROOT/content/notes"
cat > "$FILE" <<EOF
---
title: "$TITLE_YAML"
date: $STAMP
description: ""
layout: note
draft: false
---

<!-- 在这里写正文，支持 Markdown。写完后：git add -A && git commit -m "note: $TITLE_YAML" && git push -->
EOF

NAME="content/notes/$(basename "$FILE")"
echo "已创建 $NAME"
echo "编辑：\$EDITOR $NAME"
echo "发布：git add -A && git commit -m \"note: $TITLE_YAML\" && git push"
