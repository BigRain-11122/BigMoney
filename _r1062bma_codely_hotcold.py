# -*- coding: utf-8 -*-
"""r1062 bm-a CODELY.md hot-cold editorial (12,752B > 10KB hard line, O-20260927-0230 law;
D-20260924-01 paradigm; prescan rc3 registry-hit = TPL sec.2 authorized verbatim-migration
face per r1047/r1005/r983 precedent). Archive set: sec.4 pin twins (r575/r365) -> merged
pointer; r1048 / r1052 / r1005 full rows -> verbatim archive, operative essence compressed
into the live Reference pointer row. Zero-loss assertions fail-loud."""
import hashlib
import json
import time

ROOT = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"
CODELY = ROOT + r"\CODELY.md"
ARCHIVE = ROOT + r"\research\memory-archive\202610.md"
RECEIPT = ROOT + r"\results\_r1062bma_codely_hotcold_receipt.json"

BATCH = "热冷整编 2026-10-18 r1062 bm-a 窗批"

def read_raw(p):
    with open(p, "r", encoding="utf-8", newline="") as f:
        return f.read()

def write_raw(p, s):
    with open(p, "w", encoding="utf-8", newline="") as f:
        f.write(s)

def md5(s):
    return hashlib.md5(s.encode("utf-8")).hexdigest()

src = read_raw(CODELY)
src_lines = src.splitlines(keepends=True)
pre_size = len(src.encode("utf-8"))
pre_archive = read_raw(ARCHIVE)
pre_archive_size = len(pre_archive.encode("utf-8"))
eol = "\r\n" if "\r\n" in src else "\n"
arch_eol = "\r\n" if "\r\n" in pre_archive else "\n"

# --- locate the five target rows by unique line prefixes (assert count==1 each) ---
targets = {
    "r575":  "- [2026-10-02 12:5x r575 bm-a]",
    "r365":  "- [2026-10-02 12:3x r365 bm-c]",
    "r1048": "- [2026-10-18 07:4x r1048 bm-a]",
    "r1052": "- [2026-10-18 10:2x r1052 bm-a]",
    "r1005": "- [2026-10-18 11:2x r1005 bm-b]",
}
idx = {}
for k, pre in targets.items():
    hits = [i for i, ln in enumerate(src_lines) if ln.startswith(pre)]
    assert len(hits) == 1, "row %s prefix count=%d" % (k, len(hits))
    idx[k] = hits[0]
rows = {k: src_lines[i] for k, i in idx.items()}

# --- merged compact pointer replacing the sec.4 pin twins (canon = code + selftest legs) ---
MERGED = (
    "- §4 跳位语义钉死行合并指针（D-20261002-05 集团裁定·三机合流·原 r575 bm-a/r365 bm-c 两行全文"
    " verbatim=archive 202610.md『" + BATCH + "』节）：中位命中族（算术窗内非边缘端点命中·越 hit 起窗 vs"
    " 窗步链跳位两读法可分叉时）**一律越 hit 起窗**（窗自 hit+1 起扫首个净窗·非整窗步进链）；边缘端点/尾点族"
    "两读法恒同解免钉（W74/W81 判例）；W63 中位历史面勘注不回改（git 史保全）。正典=法典 §4 钉死行+"
    "scripts/perpetual_faces.py selftest 第 9 腿（9/9 PASS 正反断言）+n1 selftest D-20261002-05 pin leg"
    "（W68 判例锚·越 hit 读法==W68 注册带恒等/窗步链读法≠注册带拒绝）。"
)

# --- in-place single-occurrence replacements, grouped by host line (fail-loud per anchor) ---
REF_REPL = [
    ("r983/r1047/r1005 三批迁移史", "r983/r1047/r1005/r1062 四批迁移史"),
    ("_r1005bmb_codely_hotcold_receipt.json）",
     "_r1005bmb_codely_hotcold_receipt.json/_r1062bma_codely_hotcold_receipt.json）"),
    ("/idle fast-path 死锁解锁三件（r1046）。",
     "/idle fast-path 死锁解锁三件（r1046）/rebase --continue 三连坑=哑终端 git -c core.editor=true 修"
     "+commit 面不走 pre-commit 爪 continue 后必 marker 扫残+活写者重写 UU=MM 重 add newer-wins（r1048）"
     "/死窗遗产双线拓扑=继承窗先 git rev-parse main 核 detached·update-ref 前 reflog 核他窗提交/push 挂死"
     " 5min 零输出=零残留进程→ls-remote 探送达→fetch 重核→重放重推禁盲重试（r1005）。"),
]
R1053_REPL = [
    ("（r1052 律）。",
     "（r1052 律·r1052 原行 verbatim=archive 202610.md『" + BATCH + "』节）。"),
]
ALL_REPL = REF_REPL + R1053_REPL

def apply_group(ln, group, tag):
    for old, new in group:
        n = ln.count(old)
        assert n == 1, "%s anchor count=%d for %r" % (tag, n, old[:40])
        ln = ln.replace(old, new)
    return ln

# --- build new CODELY face: drop 5 rows, insert merged pointer at r575 position,
#     apply per-host-line replacements ---
drop = set(idx.values())
out_lines = []
for i, ln in enumerate(src_lines):
    if i in drop:
        if i == idx["r575"]:
            out_lines.append(MERGED + eol)
        continue
    if ln.startswith("- 冷层指针·热冷整编史合并行"):
        ln = apply_group(ln, REF_REPL, "refrow")
    elif ln.startswith("- [2026-10-18 10:5x r1053 bm-a]"):
        ln = apply_group(ln, R1053_REPL, "r1053row")
    out_lines.append(ln)
new_src = "".join(out_lines)
post_size = len(new_src.encode("utf-8"))

# --- archive section: header + five rows verbatim (EOL normalized to archive face) ---
section_lines = ["## " + BATCH + "（CODELY.md 12,752B>10KB 硬线·O-20260927-0230 当窗即办律·D-20260924-01 范式"
                 "·prescan rc3=登记簿命中=记忆类 TPL §2 授权迁移面 r1047 先例·receipt=results/_r1062bma_"
                 "codely_hotcold_receipt.json）"]
for k in ["r575", "r365", "r1048", "r1052", "r1005"]:
    section_lines.append(rows[k].rstrip("\r\n"))
section = arch_eol.join(section_lines) + arch_eol
new_archive = pre_archive + section
post_archive_size = len(new_archive.encode("utf-8"))

# --- zero-loss + size assertions (fail-loud) ---
for k in ["r575", "r365", "r1048", "r1052", "r1005"]:
    body = rows[k].rstrip("\r\n")
    assert body in new_archive, "archive missing verbatim row " + k
    assert body not in new_src, "CODELY still contains moved row " + k
assert post_size <= 10240, "post size %d over hard line" % post_size
assert new_src.count(MERGED) == 1, "merged pointer not unique"
for old, _ in ALL_REPL:
    assert old not in new_src, "stale anchor survived: %r" % old[:40]

write_raw(CODELY, new_src)
write_raw(ARCHIVE, new_archive)

# read-back verification (r504 validate-then-atomic face)
chk_codely = read_raw(CODELY)
chk_archive = read_raw(ARCHIVE)
assert chk_codely == new_src and chk_archive == new_archive, "read-back mismatch"
for k in ["r575", "r365", "r1048", "r1052", "r1005"]:
    assert rows[k].rstrip("\r\n") in chk_archive, "read-back archive missing " + k

receipt = {
    "ts": time.strftime("%Y-%m-%dT%H:%M:%S+08:00"),
    "machine": "bm-a",
    "round": "r1062",
    "action": "CODELY.md hot-cold editorial (10KB hard line, O-20260927-0230)",
    "prescan": "treasure_guard prescan rc3 HARD REJECT registry-hit (CODELY.md + archive 202610.md, "
               "redline s2.1) = memory/ledger class authorized verbatim-migration face per TPL sec.2 "
               "and r1047/r1005/r983 precedent; honest disclosure, zero-deletion proven below",
    "moved_rows": ["r575 bm-a sec4-pin twin", "r365 bm-c sec4-pin twin", "r1048 bm-a rebase-continue pits",
                   "r1052 bm-a orders_ack dual-face pit (superseded by r1053 gate tool)",
                   "r1005 bm-b dead-window dual-line topology pit"],
    "merged_pointer": "sec4 pin twins -> single compact pointer (canon = law-file sec.4 + selftest legs)",
    "essence_compression": "r1048/r1005 operative faces appended into live Reference pointer row; "
                           "r1053 row carries archive pointer note",
    "codely_pre_bytes": pre_size,
    "codely_post_bytes": post_size,
    "archive_pre_bytes": pre_archive_size,
    "archive_post_bytes": post_archive_size,
    "md5_codely_pre": md5(src),
    "md5_codely_post": md5(new_src),
    "md5_archive_pre": md5(pre_archive),
    "md5_archive_post": md5(new_archive),
    "zero_loss_assert": "PASS (each moved row verbatim-substring in archive, absent from CODELY; "
                        "line-level, read-back verified)",
    "batch_section": BATCH,
}
with open(RECEIPT, "w", encoding="utf-8", newline="") as f:
    json.dump(receipt, f, ensure_ascii=False, indent=1)
print(json.dumps({"codely_pre": pre_size, "codely_post": post_size,
                  "archive_pre": pre_archive_size, "archive_post": post_archive_size,
                  "zero_loss": "PASS", "receipt": RECEIPT}, ensure_ascii=False))
