# 一次性：上下文源 token 成本审计（只读）
import glob
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")
root = r"C:\Users\sjs20\Desktop\Money"


def sz(p):
    try:
        return os.path.getsize(p)
    except OSError:
        return 0


items = [
    ("CODELY.md（每Codely会话自动加载）", sz(root + r"\CODELY.md")),
    ("SYSTEM_AUDIT.md（审查文档）", sz(root + r"\SYSTEM_AUDIT.md")),
    ("HANDOFF.md（交接文档）", sz(root + r"\HANDOFF.md")),
    ("DEV_NOTES.md（开发笔记）", sz(root + r"\DEV_NOTES.md")),
    ("README.md", sz(root + r"\README.md")),
    ("state/state.json（⚠️原始状态）", sz(root + r"\state\state.json")),
    ("logs/auto.log（⚠️守护日志）", sz(root + r"\logs\auto.log")),
]
vd = glob.glob(root + r"\logs\verdict_*.md")
t10 = glob.glob(root + r"\logs\top10_*.md")
if vd:
    items.append(("logs/最新verdict", max(sz(f) for f in vd)))
if t10:
    items.append(("logs/最新top10", max(sz(f) for f in t10)))

print("== 上下文源 token 成本（中文≈1token/1.5字节，粗估 tokens≈bytes/2.5）==")
total = 0
for name, b in items:
    total += b if "⚠" not in name else 0
    print(f"{name:38s} {b:>10,} B  ≈{int(b / 2.5):>7,} tok")
code = glob.glob(root + r"\quant\*.py")
cs = sum(sz(f) for f in code)
print(f"{'quant/*.py（' + str(len(code)) + '个文件，按需读单个）':38s} {cs:>10,} B  ≈{int(cs / 2.5):>7,} tok")
print(f"logs/*.md 文件数: {len(glob.glob(root + chr(92) + 'logs' + chr(92) + '*.md'))}")
