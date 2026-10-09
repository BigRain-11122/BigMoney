# -*- coding: utf-8 -*-
"""r813 bm-c C-03 receipt legs:
1) zero-loss assertion: every disk-only stripped line (2 gaming + 3 quant,
   from the pre-reset byte backups) must be present in the CURRENT pushed
   file; plus every origin-line preserved (stripped-set equality union).
2) fleet-workspace-audit re-run (post-rectification) -> A-check PASS face.
3) MiniMax-H3 order row capture (O-20261009-1746, arrived mid-round via
   eca78c3): extract the full row text for the closing sweep + round report."""
import subprocess
import io
import os

CNW = 0x08000000
G = "K:/Fluxgroup/FluxGroup"
R = "K:/Fluxgroup/FluxGroup/quant/bigmoney"
out = io.open(os.path.join(R, "results", "_r813bmc_c03_receipt.txt"), "w",
              encoding="utf-8")
w = out.write


def gb(args, t=75):
    r = subprocess.run(["git", "-C", G] + args, capture_output=True,
                       creationflags=CNW, timeout=t)
    return r.returncode, r.stdout.decode("utf-8", "replace"), \
        r.stderr.decode("utf-8", "replace")


def stripped_lines(txt):
    return set(l.strip() for l in txt.splitlines() if l.strip())


faces = {
    "gaming/CODELY.md": "_r813bmc_union_backup_gaming_CODELY.md",
    "quant/CODELY.md": "_r813bmc_union_backup_quant_CODELY.md",
}
all_ok = True
for f, bk in faces.items():
    disk = io.open(os.path.join(R, "results", bk), encoding="utf-8",
                   errors="replace").read()
    rc, org, _ = gb(["show", "origin/main:" + f])
    cur = io.open(os.path.join(G, f.replace("/", "\\"), ), encoding="utf-8",
                  errors="replace").read()
    ds, os_, cs = stripped_lines(disk), stripped_lines(org), stripped_lines(cur)
    disk_only = ds - os_
    kept = sum(1 for l in disk_only if l in cs)
    origin_kept = os_ <= cs
    w("%s: disk_only=%d kept_now=%d origin_lines_preserved=%s "
      "union_complete=%s\n" % (
          f, len(disk_only), kept, origin_kept,
          (kept == len(disk_only) and origin_kept)))
    if kept != len(disk_only) or not origin_kept:
        all_ok = False
w("ZERO-LOSS-ASSERT: %s\n" % ("PASS" if all_ok else "FAIL"))

# --- audit re-run ---
cmd = ["powershell", "-NoProfile", "-ExecutionPolicy", "-File",
       os.path.join(R, "results", "_r813bmc_Tools_fleet-workspace-audit.ps1"),
       "-Root", G]
try:
    p = subprocess.run(cmd, capture_output=True, creationflags=CNW,
                       timeout=300)
    audit = p.stdout.decode("utf-8", "replace")
    w("---AUDIT-RERUN---\n" + audit)
except subprocess.TimeoutExpired:
    w("---AUDIT-RERUN TIMEOUT---\n")

# --- MiniMax-H3 order row capture ---
rc, o, e = gb(["log", "-1", "--format=%H %s", "eca78c3"])
w("H3-order-commit: %s\n" % o.strip())
try:
    om = io.open(os.path.join(G, "docs", "orders.md"), encoding="utf-8",
                 errors="replace").read()
    for ln in om.splitlines():
        if "O-20261009-1746" in ln or "MiniMax-H3" in ln:
            w("H3-ROW: " + ln[:600] + "\n")
except Exception as ex:
    w("orders read err %s\n" % ex)
out.close()
print("receipt legs done")
