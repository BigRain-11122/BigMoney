# -*- coding: utf-8 -*-
"""r334 bm-b: CODELY.md 20th-batch hot/cold archival (<=10KB hard line, in-window law).

- append fresh r334 pitlaw (asof-key dedup collapse recurrence, r87 bmc law)
- move 4 full-text entries verbatim -> research/memory-archive/202609.md 20th-batch
  section, leave pointer lines (drop condition anchored to full form '坑律：**'
  per r89 stub-drop law; pointer lines strictly preserved)
- fail-closed: exact-once match asserts + byte-equal verbatim verify + size assert
"""
import io

CODY = "CODELY.md"
ARCH = r"research\memory-archive\202609.md"

TARGETS = [  # (full-line prefix anchor, pointer replacement line)
    ("- [2026-09-27 16:1x r332 bm-b] 坑律：**tick 自提交落点",
     "- [2026-09-27 16:1x r332 bm-b] 坑律（二十批外迁·指针）：tick 自提交落点 :X2:5x/陈读丢弃真丢失窗/reflog 定谳后 union 收敛——全文 verbatim=research/memory-archive/202609.md『坑律归档 2026-09-27 二十批』节。"),
    ("- [2026-09-27 16:2x r335 bm-a] 坑律：**PowerShell ConvertFrom-Json",
     "- [2026-09-27 16:2x r335 bm-a] 坑律（二十批外迁·指针）：PowerShell ConvertFrom-Json 假红/权威解析一律 python——全文 verbatim=archive 202609.md 二十批节。"),
    ("- [2026-09-27 16:1x r89 bm-c] 坑律：**stub-drop 配方",
     "- [2026-09-27 16:1x r89 bm-c] 坑律（二十批外迁·指针）：stub-drop 锚全文形态防指针误伤+面积口径统一 encode 字节数——全文 verbatim=archive 202609.md 二十批节。"),
    ("- [2026-09-27 16:3x r333 bm-b] 坑律：**tick 的 git 危险窗",
     "- [2026-09-27 16:3x r333 bm-b] 坑律（二十批外迁·指针）：tick git 危险窗扩至 :X3 后（post-commit fetch+push 对账尾）——全文 verbatim=archive 202609.md 二十批节。"),
]

NEW_ENTRY = ("- [2026-09-27 17:3x r334 bm-b] 坑律：**rolling-ledger union 的 dedup 键族必含面实时间键"
             "（r87 bmc 键探律再犯实弹）——resolver 键元组 ts-only 在 asof 键件上全 None 塌缩丢行**"
             "——r334 实弹：regime history 2+2→union=1（asof 行 4 条同键全塌缩，正确=2），"
             "union 行数 vs |A∪B| 目视核对当场拦下未落地；正典=①resolver dedup 键=逐面实探字段并集"
             "（ts/asof/...）写进配方②每 ledger union 必印 |ours|+|theirs|→union 并核对并集数"
             "③写回前 python 三方 blob 复验（_r334bmb_verify_regime.py 范式）。"
             "指针=results/_r333bmb_push_resolve.py+results/_r334bmb_verify_regime.py+round_reports r334。")

cl = io.open(CODY, encoding="utf-8").read().splitlines()
moved = []
for anchor, pointer in TARGETS:
    hits = [i for i, l in enumerate(cl) if l.startswith(anchor) and "坑律：**" in l]
    assert len(hits) == 1, f"anchor not exactly-once: {anchor} hits={hits}"
    moved.append(cl[hits[0]])
    cl[hits[0]] = pointer
assert len(moved) == 4

# fresh entry appended at file end (Reference section is last)
cl.append(NEW_ENTRY)
new_c = "\n".join(cl) + "\n"

arch = io.open(ARCH, encoding="utf-8").read()
assert "二十批" not in arch, "20th-batch section already exists"
section = ("\n## 坑律归档 2026-09-27 二十批（r334 bm-b·水位律当窗整编·行级零丢失）\n"
           + "\n".join(moved) + "\n")
new_a = arch + section

with io.open(CODY, "w", encoding="utf-8", newline="") as f:
    f.write(new_c)
with io.open(ARCH, "w", encoding="utf-8", newline="") as f:
    f.write(new_a)

# ---- 4-check zero-loss verification
c2 = io.open(CODY, encoding="utf-8").read()
a2 = io.open(ARCH, encoding="utf-8").read()
for orig, (anchor, pointer) in zip(moved, TARGETS):
    assert orig in a2, f"verbatim lost in archive: {anchor[:40]}"
    assert pointer in c2, f"pointer missing in CODELY: {anchor[:40]}"
    assert orig not in c2, f"full text still in CODELY (should be pointer): {anchor[:40]}"
assert NEW_ENTRY in c2
cb = len(c2.encode("utf-8"))
print(f"CODELY.md: {cb}B (<=10240: {cb <= 10240}) moved=4 verbatim-verified pointers=4")
assert cb <= 10240, f"still over 10KB hard line: {cb}"
print("ARCHIVAL-OK 二十批")
