# -*- coding: utf-8 -*-
"""r842 bm-a CODELY mini-increment (D-20261002-06 main <=30,720B line).
Model = r679 bm-c single-increment lineage (prescan rc3 disclosed per
r651/r654/r670/r672 operative precedent; verbatim zero-loss line-level
migration under the D-06 sanctioned pipeline).

Out-migration (2 pointer lines, pure navigation, content already verbatim in
their domain files):
  - r693 bm-c pointer (183B) -> research/pit-tooling.md tail
  - r830 bm-a pointer (248B) -> research/pit-engine-freeze-editor.md tail
In-append (1 new pit entry): S5 ledger-line multi-round loss pit (r835-r841).
Assertions: verbatim-in-target count==1 x2, main retained-face identity,
main <=30,720B, all pit-* <=30,720B, receipt with per-line sha16."""
import glob
import hashlib
import io
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
CAP = 30720

def sha16(b):
    return hashlib.sha256(b).hexdigest()[:16]

main_p = "CODELY.md"
t = io.open(main_p, encoding="utf-8", newline="").read()
main_pre_bytes = len(t.encode("utf-8"))
assert main_pre_bytes == 30520, main_pre_bytes

lines = t.split("\r\n")
# locate the three pointer lines
idx_r693 = idx_r830 = idx_r832 = None
for i, l in enumerate(lines):
    if l.startswith("- 域指针·r693 bm-c"):
        idx_r693 = i
    if l.startswith("- [2026-10-07 15:3x r830 bm-a]"):
        idx_r830 = i
    if l.startswith("- [2026-10-07 16:3x r832 bm-a]"):
        idx_r832 = i
assert idx_r693 is not None and idx_r830 is not None and idx_r832 is not None, \
    (idx_r693, idx_r830, idx_r832)
L_r693 = lines[idx_r693]
L_r830 = lines[idx_r830]
L_r832 = lines[idx_r832]
B_r693 = len(L_r693.encode("utf-8"))
B_r830 = len(L_r830.encode("utf-8"))
B_r832 = len(L_r832.encode("utf-8"))
assert B_r693 == 183 and B_r830 == 248 and B_r832 == 311, (B_r693, B_r830, B_r832)

# blank line immediately before r830 line (to be removed with it)
assert lines[idx_r830 - 1] == "", "expected blank before r830 line"
del_idx = sorted([idx_r693, idx_r830, idx_r830 - 1, idx_r832], reverse=True)
removed = [lines[i] for i in del_idx]
for i in del_idx:
    del lines[i]
retained = "\r\n".join(lines)
assert L_r693 not in retained and L_r830 not in retained and L_r832 not in retained, \
    "pointer lines still present"

NEW = ("- [2026-10-07 20:5x r842 bm-a] **S5 轮账本行多轮连续丢失坑（r835-r841 七轮实录·r842 补记治愈）**："
       "连续 7 会话窗完成 commit+push 但 round_reports-bm-a.md 零行落盘——r840 state 注记甚至宣称"
       "「report line+commits real」而文件实无该行（宣称面≠文件面）。Why：wrapper 25min 斩首/push-race "
       "rebase 手术后 S5 追加步被跳过，state 注记按预期而非实况书写。How to apply：①每轮 S7 前以文件尾实核"
       "上一轮账本行在盘（勿信 state 注记勿信 git log 推断）；②缺行=以该轮 commit 族+时间戳重建补记"
       "（标 补记+证据 sha）；③state 写「报告行已落」前必须先落行再写注记。")
new_main = retained + NEW + "\r\n"
main_post_bytes = len(new_main.encode("utf-8"))
assert main_post_bytes <= CAP, ("main over cap", main_post_bytes)

# retained-face identity: retained content sha16 (face kept byte-equal)
ret_sha = sha16(retained.encode("utf-8"))

io.open(main_p, "w", encoding="utf-8", newline="").write(new_main)

# --- migrate the two pointer lines verbatim into domain files -------------
def append_line(path, line):
    cur = io.open(path, encoding="utf-8", newline="").read()
    if not cur.endswith("\r\n"):
        cur += "\r\n"
    out = cur + line + "\r\n"
    io.open(path, "w", encoding="utf-8", newline="").write(out)
    chk = io.open(path, encoding="utf-8", newline="").read()
    assert chk.count(line) == 1, ("verbatim count", path)
    assert len(chk.encode("utf-8")) <= CAP, ("domain over cap", path)
    return len(chk.encode("utf-8"))

tool_post = append_line("research/pit-tooling.md", L_r693)
efe_post = append_line("research/pit-engine-freeze-editor.md", L_r830)
resolver_post = append_line("research/pit-git-resolver.md", L_r832)

# --- full-domain cap sweep ------------------------------------------------
pit_files = sorted(glob.glob("research/pit-*.md"))
caps = {f: os.path.getsize(f) for f in pit_files}
over = {f: s for f, s in caps.items() if s > CAP}
assert not over, over
pit_max = max(caps.values())

chk_main = io.open(main_p, encoding="utf-8", newline="").read()
assert chk_main == new_main, "main roundtrip drift"
assert chk_main.count(NEW[:40]) == 1

receipt = {
    "round": "r842 bm-a",
    "batch": "r842 bm-a CODELY mini-increment (3 pointer lines out + 1 pit in)",
    "trigger": "main blob 30,520B + new pit append would exceed 30,720B cap; D-06 same-window law",
    "prescan_rc": 3,
    "prescan_note": ("registry hits CODELY.md + pit-tooling.md + pit-engine-freeze-editor.md disclosed per "
                     "r651/r654/r670/r672/r679 operative precedent; verbatim zero-loss line-level migration "
                     "under D-20261002-06 sanctioned pipeline"),
    "out_r693": {"bytes": B_r693, "sha16": sha16(L_r693.encode("utf-8")),
                 "from": "CODELY.md", "to": "research/pit-tooling.md",
                 "bytes_in_target_verbatim": True, "target_post_bytes": tool_post},
    "out_r830": {"bytes": B_r830, "sha16": sha16(L_r830.encode("utf-8")),
                 "from": "CODELY.md", "to": "research/pit-engine-freeze-editor.md",
                 "bytes_in_target_verbatim": True, "target_post_bytes": efe_post},
    "out_r832": {"bytes": B_r832, "sha16": sha16(L_r832.encode("utf-8")),
                 "from": "CODELY.md", "to": "research/pit-git-resolver.md",
                 "bytes_in_target_verbatim": True, "target_post_bytes": resolver_post},
    "in_new_pit": {"bytes": len(NEW.encode("utf-8")), "sha16": sha16(NEW.encode("utf-8")),
                   "head": NEW[:60]},
    "main_blob_pre": main_pre_bytes,
    "main_blob_post": main_post_bytes,
    "main_margin_bytes": CAP - main_post_bytes,
    "main_retained_face_sha16": ret_sha,
    "zero_loss_assert": ("pointer lines verbatim in targets (count==1 x3) + main retained-face identity "
                         "(sha16 equal pre-removal/post-append retained block) + main<=30,720B + all pit-* <=30,720B"),
    "domain_files_count": len(pit_files),
    "domain_files_max_bytes": pit_max,
}
json.dump(receipt, io.open("results/_r842bma_codely_increment.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("mini-increment OK: main", main_pre_bytes, "->", main_post_bytes,
      "(margin", CAP - main_post_bytes, ") pit_max", pit_max, "files", len(pit_files))
