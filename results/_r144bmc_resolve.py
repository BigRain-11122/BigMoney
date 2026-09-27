# results/_r144bmc_resolve.py -- r144 discharge pick-6765e877 UU closeout (bm-c)
# Non-registry duo (CODELY.md + archive 202609.md) for the 6-UU batch.
# 4 registry JSON faces already resolved via `merge_lane_views.py resolve`
# (r381 law; face_view output, no hand-assembly r376).
# Laws applied here:
#   - r384 bidirectional entry-coverage union (both sides in-place folded
#     batch-33 -> manual review path of _r143bmc_resolve.py, done here)
#   - r386 same-window batch-number collision: first-landed origin survives,
#     losing side yields with 让路注记 (batch-31 precedent pattern)
#   - r209 git objects read as subprocess BYTES; r361 BOM-normalized parse
#     gate; r365 in-memory assembly -> single atomic write (no wb-then-write)
#   - hot-layer <=10KB hard line re-checked post-union (D-20260928-03 family)
import os
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = []


def log(msg):
    OUT.append(msg)


def stage(idx, path):
    r = subprocess.run(["git", "show", f":{idx}:{path}"],
                       capture_output=True, cwd=ROOT)
    if r.returncode != 0:
        raise SystemExit(f"stage :{idx}:{path} missing: {r.stderr[:200]!r}")
    return r.stdout


def eol_of(blob):
    return b"\r\n" if b"\r\n" in blob[:4096] else b"\n"


def atomic_write(relpath, payload):
    full = os.path.join(ROOT, os.path.normpath(relpath))
    assert b"<<<<<<<" not in payload and b">>>>>>>" not in payload, \
        f"{relpath}: marker leak"
    payload.decode("utf-8")          # parse gate before write (r185/r361)
    with open(full, "wb") as fh:      # single atomic write of assembled bytes
        fh.write(payload)


# --- CODELY.md: origin (:2:) survives; my r143 pitlaw entry recovered from
# :3:; batch-33 pointer gets the r386-style collision note ------------------
CP = "CODELY.md"
base, a, b = stage(1, CP), stage(2, CP), stage(3, CP)
nl = eol_of(a)

lines_b = b.splitlines(keepends=True)
r143_lines = [ln for ln in lines_b
              if ln.startswith("- [2026-09-28 07:1x r143 bm-c] 坑律".encode())]
assert len(r143_lines) == 1, f"r143 entry not found uniquely in :3: ({len(r143_lines)})"
r143_entry = r143_lines[0].rstrip(b"\r\n")

# bidirectional coverage audit (r384): unique-line census both sides
set_a = {ln.rstrip(b"\r\n") for ln in a.splitlines()}
set_b = {ln.rstrip(b"\r\n") for ln in b.splitlines()}
only_a = set_a - set_b
only_b = set_b - set_a
for ln in only_b:
    if ln == r143_entry.rstrip(b"\r\n"):
        continue
    if ln in set_a:
        continue
    # only remaining :3:-unique line class = my batch-33 pointer wording
    # (yields per r386 law -- verified by collision note below)
    assert ln.startswith("冷层指针：坑律正典 2026-09-28 三十三批".encode()), \
        f"unexpected :3:-unique line: {ln[:80]!r}"

# find origin's batch-33 pointer line and append the collision note
note = ("（r143 bm-c 同窗独立整编同批号撞号：两条件恒等、bm-c 节让路=archive "
        "让路注记；bm-c 新坑律 r143 已并入热层）").encode()
lines_a = a.splitlines(keepends=True)
hit = 0
for i, ln in enumerate(lines_a):
    if ln.rstrip(b"\r\n").startswith("冷层指针：坑律正典 2026-09-28 三十三批".encode()):
        assert note not in ln, "collision note already present"
        lines_a[i] = ln.rstrip(b"\r\n") + note + nl
        hit += 1
assert hit == 1, f"batch-33 pointer line count={hit} (expect 1)"

# append my r143 entry at hot-layer tail (mirrors :3: blank-line style)
codely = b"".join(lines_a)
if not codely.endswith(nl):
    codely += nl
codely += r143_entry + nl
atomic_write(CP, codely)
size = len(codely)
log(f"CODELY.md: origin-survives union -> {size}B "
    f"(hard-line {'OK' if size <= 10240 else 'OVER'}); "
    f"r143 entry recovered; collision note x{hit}")

# coverage post-check: nothing unique lost on either side; a line modified
# by note-append counts as covered when it is a prefix of a merged line
merged_lines = [ln.rstrip(b"\r\n") for ln in codely.splitlines()]
merged_exact = set(merged_lines)
lost_a = [ln for ln in only_a
          if ln not in merged_exact
          and not any(ml.startswith(ln) for ml in merged_lines)]
lost_b = [ln for ln in only_b
          if ln not in merged_exact
          and not any(ml.startswith(ln) for ml in merged_lines)
          and not ln.startswith("冷层指针：坑律正典 2026-09-28 三十三批".encode())]
assert not lost_a and not lost_b, f"coverage loss: a={lost_a[:2]} b={lost_b[:2]}"
log("CODELY.md coverage: zero entry loss (r384 audit pass)")

# --- archive 202609.md: origin (:2:) batch-33 section survives; my section
# yields only if both bullet entries are verbatim-contained (r386 law) -----
AP = "research/memory-archive/202609.md"
abase, aa, bb = stage(1, AP), stage(2, AP), stage(3, AP)
nl_a = eol_of(aa)
bullets_b = [ln for ln in bb.splitlines()
             if ln.rstrip(b"\r\n").startswith(b"- [2026-09-28 06:")]
missing = [ln for ln in bullets_b
           if ln.rstrip(b"\r\n") not in {x.rstrip(b"\r\n") for x in aa.splitlines()}]
assert not missing, \
    f"my-side archive bullet(s) not contained in origin section: {missing[:1]}"
yield_note = (
    "> 让路注记（r143 bm-c·commit 时间序 bm-a r389 三十三批先落 origin=正典节）："
    "bm-c r143 同窗独立整编同批号（两条件 r363/r386 逐条恒等且⊂本节），"
    "bm-c 侧节让路丢弃=零内容损失；bm-c 新坑律（r143 Start-Process 批法）"
    "已并入 CODELY 热层，热层指针行让路注记同窗（r328 双批注律）。"
).encode()
assert yield_note not in aa, "yield note already present"
arch = aa
if not arch.endswith(nl_a):
    arch += nl_a
arch += yield_note + nl_a
atomic_write(AP, arch)
log(f"archive 202609.md: origin section survives, my identical section "
    f"yields (bullets contained x{len(bullets_b)}); yield note appended -> {len(arch)}B")

# --- existence sentinel (r365 law): 0-byte / missing tracked file hunt -----
uu_faces = ["CODELY.md", "research/memory-archive/202609.md",
            "results/compute_audit.json", "results/crash_fuse.json",
            "results/futures_update_status.json", "results/lhb_update_status.json"]
for p in uu_faces:
    full = os.path.join(ROOT, os.path.normpath(p))
    sz = os.path.getsize(full)
    assert sz > 0, f"sentinel: {p} is 0 bytes"
    log(f"sentinel: {p} {sz}B")

for line in OUT:
    print(line.encode("ascii", "backslashreplace").decode())
