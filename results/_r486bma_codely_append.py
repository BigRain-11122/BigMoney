# -*- coding: utf-8 -*-
# r486 bm-a: CODEY.md lesson append (one entry, dirty-tree dual-sync law)
import os

entry = (
    "- [2026-09-30 18:5x r486 bm-a] 脏树并发窗双同步坑律（r484/r485 连续弃 pull 后 r486 实弹修正）："
    "并发交互会话 staged 件在飞时 ①pull --rebase 必拒（rebase 要净树）——本地 ahead=0 时正解="
    "git merge --ff-only origin/main（零本地提交时 ff≡rebase 等价·零重放），前提=先 "
    "git diff --stat HEAD origin/main -- <并发件> 验空（远端零触碰并发件则 ff 安全·其 staged 态无损保留）；"
    "②本窗提交一律 pathspec 偏提交 git commit -m msg -- <本窗产出路径>（partial-commit=只提交匹配路径·"
    "他人 staged 件原样留 index）=事前免疫 add -A 吞件（r483 事后 amend 剔出的事前版）；"
    "③PS 内联 python 手拼 ISO 偏移坑=str(timedelta) 去':' 拼法出 +80000 坏钟读"
    "（正解=strftime('%z') 前3+冒号+后2）——心跳 clock_read 契约 +08:00 缺一即 F7 红面。"
    "How：未来脏树窗先跑①验证面再 ff 勿整窗弃同步；提交一律②式；时间戳一律③式。\n"
)

path = "CODELY.md"
with open(path, "a", encoding="utf-8") as f:
    f.write(entry)

size = os.path.getsize(path)
assert size < 10240, f"CODELY.md over 10KB hard line: {size}"
print("appended; new size", size, "bytes; under 10KB line OK")
