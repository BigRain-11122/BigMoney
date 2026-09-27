# -*- coding: utf-8 -*-
"""r390 bm-a push-storm resolver v2 (11-UU batch vs bm-c r143/r144 chain).

Skill-routed recipes, staged-blob probes only (R350), bytes via
subprocess (r209).  v2 corrections over v1:
  * twins / b_layer_filter unchanged (took :3: replay-side, fresher).
  * CODELY.md: origin side (bm-c r144 fold state, 9,607B) = canonical
    skeleton (landed first); replay-only ADDITIVE lines = my r390 pit-law
    entry + renumbered batch pointer.  Replay-side stale-hot entries
    (r389-CRLF, r365) that origin ALREADY archived -> drop from hot
    (zero loss: they live in the archive union).
  * batch-number collision: origin took 三十四/三十五批 -> my archive
    section renumbers 三十四批 -> 三十六批 (r386 撞号让路 family).
  * post-union watermark fold: union lands ~10,8xxB > 10,240B hard line
    -> same-window second fold migrates the two oldest entries (r389
    auto-clear [mine, superseded by this round's D-03(2) root fix] +
    r143 bm-c Start-Process) verbatim into the 三十六批 section.
"""
import json
import subprocess
import sys

def blob(stage, path):
    out = subprocess.run(
        ["git", "show", ":%s:%s" % (stage, path)],
        capture_output=True, check=True)
    return out.stdout

def has_marker(b):
    return any(m in b for m in (b"<<<<<<<", b">>>>>>>", b"======="))

def write(path, data_bytes):
    with open(path, "wb") as fh:
        fh.write(data_bytes)
    return data_bytes

fails = []

# ---------------- twins + b_layer (same as v1, both took :3:) --------
JP = "docs/daily_report/REPORT-2026-09-28.json"
MP = "docs/daily_report/REPORT-2026-09-28.md"
j2 = json.loads(blob(2, JP).decode("utf-8"))
j3 = json.loads(blob(3, JP).decode("utf-8"))
t2, t3 = str(j2.get("generated_at", "")), str(j3.get("generated_at", ""))
side = 3 if t3 >= t2 else 2
jp, mp = blob(side, JP), blob(side, MP)
write(JP, jp)
write(MP, mp)
json.loads(open(JP, "rb").read().decode("utf-8"))
if has_marker(jp) or has_marker(mp):
    fails.append("twins carry markers")
print(f"twins: {t2} vs {t3} -> :{side}: both twins byte-verbatim")

FB = "results/fundamental_b_layer_filter.json"
f2 = json.loads(blob(2, FB).decode("utf-8"))
f3 = json.loads(blob(3, FB).decode("utf-8"))
u2, u3 = str(f2.get("updated", "")), str(f3.get("updated", ""))
fbs = write(FB, blob(3 if u3 >= u2 else 2, FB))
json.loads(open(FB, "rb").read().decode("utf-8"))
if has_marker(fbs):
    fails.append("b_layer carries markers")
print(f"b_layer_filter: {u2} vs {u3} -> :{3 if u3 >= u2 else 2}:")

# ---------------- archive union FIRST (hot policy depends on it) -----
AP = "research/memory-archive/202609.md"
a1 = blob(1, AP).decode("utf-8")
a2 = blob(2, AP).decode("utf-8")
a3 = blob(3, AP).decode("utf-8")

FOLD_PREFIXES = (
    "- [2026-09-28 07:1x r143 bm-c] 坑律：",
    "- [2026-09-28 07:1x r389 bm-a] 坑律：**tick auto-clear",
)
RENAMED_HEADER = ("## 坑律归档 2026-09-28 三十六批（r390 bm-a 窗·撞号让路重编"
                 "〔origin 三十四/三十五批先落·本窗三十四批重编〕+push-storm 窗"
                 "二折〔CODELY union 复超 ≤10KB 硬线〕）")

def sections(text):
    lines = text.splitlines()
    pre, secs, cur = [], [], None
    for ln in lines:
        if ln.startswith("## "):
            if cur is not None:
                secs.append(cur)
            cur = [ln]
        else:
            (cur if cur is not None else pre).append(ln)
    if cur is not None:
        secs.append(cur)
    return pre, secs

p1, s1 = sections(a1)
p2, s2 = sections(a2)
p3, s3 = sections(a3)

# extract my replay-side batch-34 section body (r141/r142 + 迁移记录)
mine_sec = None
for s in s3:
    if "三十四批" in s[0] and "r390 bm-a" in s[0]:
        mine_sec = s
assert mine_sec is not None, "replay batch-34 section not found"
old_note = None
body = [ln for ln in mine_sec[1:] if ln.strip() and not ln.startswith(">")]
note = [ln for ln in mine_sec[1:] if ln.startswith(">")]
old_note = note[0] if note else ""

# r143 + r389-auto-clear entries pulled verbatim from the CODELY blobs
# (they are HOT-layer entries being folded OUT, not archive residents)
_CP = "CODELY.md"
fold_entries = {}
for stage in (1, 2, 3):
    src = blob(stage, _CP).decode("utf-8")
    for ln in src.splitlines():
        if any(ln.startswith(p) for p in FOLD_PREFIXES):
            fold_entries[ln[:60]] = ln
assert len(fold_entries) == 2, \
    f"expected 2 fold entries, got {len(fold_entries)}: {list(fold_entries)}"

fold_lines = [fold_entries[k] for k in sorted(fold_entries)]

NEW_NOTE = ("> 迁移记录（三十六批〔原三十四批·撞号重编·r386 让路族〕=四条坑律 "
            "r141 CLI 分发表零参调用+池分片键跨条目唯一、r142 crash-fuse "
            "FUSE_CONFIRM_MIN 静默死盲窗、r143 bm-c Start-Process 多腿批法、"
            "r389 bm-a auto-clear×lane-union 漂移〔过渡配方已被 D-03(2) "
            "cleared-tombstone 根修取代·r390 落地〕，自 CODELY.md 热层 "
            "verbatim 迁移〔行级零丢失校验〕；r389-CRLF/r365 两条=origin "
            "b34/b35 批已档·重活侧副本让位零复档；热层含三十六批指针行"
            "〔归档侧迁移史留痕〕。")

my_section = [RENAMED_HEADER, ""]
for ln in body:
    my_section.append(ln)
    my_section.append("")
for ln in fold_lines:
    my_section.append(ln)
    my_section.append("")
my_section.append(NEW_NOTE)

sec_map = {}
order = []
for sec in s1:
    sec_map[sec[0].strip()] = list(sec)
    order.append(sec[0].strip())
for src in (s2, s3):
    for sec in src:
        k = sec[0].strip()
        if "三十四批" in k and "r390 bm-a" in k:
            continue          # my section re-enters via my_section below
        if k not in sec_map:
            sec_map[k] = list(sec)
            order.append(k)
        else:
            seen_l = set(sec_map[k])
            for ln in sec:
                if ln not in seen_l:
                    sec_map[k].append(ln)
                    seen_l.add(ln)
my_key = RENAMED_HEADER
sec_map[my_key] = my_section
order.append(my_key)

arc_lines = list(p2)
for k in order:
    sec = sec_map[k]
    arc_lines.append("")
    arc_lines.extend(sec)
arc = "\r\n".join(arc_lines) + "\r\n"

for probe in ("r141 CLI 子命令分发表零参调用", "r142 crash-fuse FUSE_CONFIRM_MIN",
              "r143 bm-c", "tick auto-clear（码变→del sig→_save_fuse 双轨写）",
              "r389 bm-a] 坑律：**文本模式 universal-newlines",
              "r365 bm-b] 坑律：**resolver/收口脚本"):
    if probe not in arc:
        fails.append(f"archive lost probe: {probe}")
if "三十四批（r390 bm-a" in arc:
    fails.append("old batch-34 header still present in archive")
write(AP, arc.encode("utf-8"))
print(f"archive: {len(order)} sections; my section renumbered 三十六批 with "
      f"{len(body) + len(fold_lines)} entries")

# ---------------- CODELY hot: origin skeleton + replay additions -------
CP = "CODELY.md"
c1 = blob(1, CP).decode("utf-8")
c2 = blob(2, CP).decode("utf-8")
c3 = blob(3, CP).decode("utf-8")
for nm, c in (("base", c1), ("origin", c2), ("replay", c3)):
    if has_marker(c.encode("utf-8")):
        fails.append(f"CODELY {nm} has markers")

PTR = ("冷层指针：坑律正典 2026-09-28 三十六批（r390 bm-a 窗·撞号让路重编"
       "〔origin 三十四/三十五批先落〕+push-storm 窗二折〔union 复超 "
       "≤10KB 硬线〕）：r141 CLI 分发表零参+分片键唯一 / r142 fuse 25min "
       "盲窗 / r143 Start-Process 多腿批法 / r389 auto-clear×lane-union "
       "漂移〔D-03(2) 墓碑根修已取代〕四条全文 verbatim=archive "
       "202609.md『坑律归档 2026-09-28 三十六批』节（行级零丢失校验）。")

# origin side = canonical skeleton (their fold state landed first);
# the two newly folded entries are REMOVED from hot (they now live in
# the 三十六批 archive section built above)
lines2 = c2.splitlines()
out = []
for ln in lines2:
    if any(ln.startswith(p) for p in FOLD_PREFIXES):
        continue          # folded out this window, verbatim in archive
    out.append(ln)
# append my replay-only additive lines at EOF: r390 entry + pointer
r390_line = None
for ln in c3.splitlines():
    if ln.strip().startswith("- [2026-09-28 07:3x r390 bm-a]"):
        r390_line = ln
assert r390_line is not None, "replay r390 entry not found"
out.append("")
out.append(r390_line)
out.append("")
out.append(PTR)
codely = "\r\n".join(out) + "\r\n"

# zero-phantom: every base bullet line must survive in hot OR archive union
arc_all = arc
for ln in c1.splitlines():
    s = ln.strip()
    if s.startswith("- [") or s.startswith("冷层指针："):
        if ln not in codely and ln not in arc_all:
            fails.append(f"base line lost: {ln[:60]}")
# replay bullets likewise (r389-CRLF / r365 dropped from hot must be in
# archive; my OLD batch-34 pointer is intentionally superseded by the
# renumbered 三十六批 pointer -- exempt it)
old_ptr_probe = "冷层指针：坑律正典 2026-09-28 三十四批（r390 bm-a"
for ln in c3.splitlines():
    s = ln.strip()
    if s.startswith("- [") or s.startswith("冷层指针："):
        if ln.startswith(old_ptr_probe):
            continue
        if ln not in codely and ln not in arc_all and ln != old_note.strip():
            fails.append(f"replay line lost: {ln[:60]}")
# fold removal: folded entries must NOT be in hot
for ln in fold_lines:
    if ln in codely:
        fails.append(f"folded entry still in hot: {ln[:50]}")

size = len(codely.encode("utf-8"))
print(f"CODELY: origin-skeleton + r390 + 三十六批 pointer -> {size}B")
if size > 10240:
    fails.append(f"CODELY {size}B > 10,240B hard line")
write(CP, codely.encode("utf-8"))

if fails:
    for f in fails:
        print("FAIL:", f)
    sys.exit(1)
print("resolver v2: all faces resolved, parse-verified, marker-clean, "
      "watermark lawful")
