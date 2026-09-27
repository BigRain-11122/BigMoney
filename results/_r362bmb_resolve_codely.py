# -*- coding: utf-8 -*-
"""r362 bm-b CODELY.md rebase-conflict resolver (memory-union, r361 BOM law).

Recipe (SKILL memory-union + r361 pit law):
  - read stage blobs :1 (base) / :2 (ours) / :3 (theirs) via subprocess bytes
    (no PS redirection on encoding-sensitive files -- r209 law);
  - BOM-normalize base; assert BOTH sides are pure appends of the
    BOM-stripped core (format face != content face -- r361 law);
  - union = BOM + core + theirs-suffix (origin first-lander keeps position,
    R210 spirit) + ours-suffix, identical-line dedupe;
  - byte-conservation + line-loss checks; write back; git add.
"""
import subprocess
import sys

PATH = "CODELY.md"
BOM = b"\xef\xbb\xbf"


def blob(rev):
    r = subprocess.run(["git", "show", rev], capture_output=True)
    if r.returncode != 0:
        print(f"git show {rev} rc={r.returncode}: {r.stderr[:200]}")
        sys.exit(2)
    return r.stdout


base = blob(":1:CODELY.md")
ours = blob(":2:CODELY.md")
theirs = blob(":3:CODELY.md")

had_bom = base.startswith(BOM)
if had_bom:
    base = base[len(BOM):]
o_core = ours[len(BOM):] if ours.startswith(BOM) else ours
t_core = theirs[len(BOM):] if theirs.startswith(BOM) else theirs

ok_ours = o_core.startswith(base)
ok_theirs = t_core.startswith(base)
print(f"base={len(base)}B ours={len(ours)}B theirs={len(theirs)}B "
      f"base_had_bom={had_bom}")
print(f"pure-append: ours={ok_ours} theirs={ok_theirs}")
if not (ok_ours and ok_theirs):
    print("FAIL-CLOSED: non-append edit detected -- manual deep review "
          "required (r361 law: format face != content face, no blind union)")
    sys.exit(2)

sa = o_core[len(base):]
sb = t_core[len(base):]
# origin first-lander (theirs, pushed before my replay) keeps position
union_core = base + sb + sa
pre = (BOM if had_bom else b"") + union_core
print(f"suffixes: ours +{len(sa)}B theirs +{len(sb)}B "
      f"(push order: theirs first)")
exp = (3 if had_bom else 0) + len(base) + len(sa) + len(sb)
print(f"byte-conservation: {len(pre)} == {exp} -> {len(pre) == exp}")
nb, no, nt = (len(x.splitlines()) for x in
              (base, o_core, t_core))
nu = len(pre.splitlines())
print(f"lines: base {nb} ours {no} theirs {nt} -> union {nu} "
      f"(expected {nb} + ({no-nb}) + ({nt-nb}) = "
      f"{nb + (no - nb) + (nt - nb)}) -> "
      f"{nu == nb + (no - nb) + (nt - nb)}")
if len(pre) != exp or nu != nb + (no - nb) + (nt - nb):
    print("FAIL-CLOSED: conservation check failed")
    sys.exit(2)

with open(PATH, "wb") as fh:
    fh.write(pre)
subprocess.run(["git", "add", PATH], check=True)
tail = pre.decode("utf-8").splitlines()[-2:]
print("union tail (last 2 lines):")
for ln in tail:
    print("  " + ln[:120])
print("RESOLVED: CODELY.md memory-union written + staged")
