# -*- coding: utf-8 -*-
"""r456 bm-c S4: append one pit line to repo CODELY.md (shared append-only
face). Bytes mode, EOL detect (r641 family), zero-loss containment asserts:
prior tail marker intact + new line exactly once (r453 dedup/marker laws)."""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, "CODELY.md")
LINE = (
    "- [2026-10-04 09:02 r456 bm-c] merge 解探针 per-key union 零命中静默整面走 theirs "
    "坑（token_usage machines 条目无 per-key ts→r456 通用 per-key 腿 side-pick 计数=0="
    "基座静默全 theirs，丢我方 08:52 bm-c 面）：per-key union 腿必须断言 side-pick>0，零命中"
    "即显式转整面新鲜度键判（r455 同 keyset+ours-newer=整面 ours 判例）；双侧原字节一律 "
    "HEAD:/MERGE_HEAD: 直取（add 已抹 stage2/3·r657 律②当场兑现）。修=results/"
    "_r456bmc_token_fix.py（merge 未推前当场抓回·零 origin 伤害·push 前自检立功）。"
)

with open(P, "rb") as f:
    raw = f.read()
assert raw.count("五连push-race收口三坑律".encode("utf-8")) == 1, "prior tail marker lost"
assert LINE.encode("utf-8") not in raw, "line already present (dedup law)"
eol = b"\r\n" if b"\r\n" in raw[-400:] else b"\n"
addition = LINE.encode("utf-8") + eol
if not raw.endswith(b"\n"):
    addition = eol + addition
with open(P, "ab") as f:
    f.write(addition)
with open(P, "rb") as f:
    back = f.read()
assert back.count("五连push-race收口三坑律".encode("utf-8")) == 1, "tail marker dup/lost"
assert back.count(LINE.encode("utf-8")) == 1, "new line count != 1"
assert back.startswith(raw), "zero-loss violated (prefix changed)"
print("CODELY_APPEND_OK bytes=%d eol=%r" % (len(addition), eol))
