# -*- coding: utf-8 -*-
# r608 S0 faceted repair: restore D-artifacts + stale other-machine faces (origin verbatim),
# keep bm-a live-write faces, union pool_core_samples (r570/r600/r595/r580 laws)
import subprocess, sys

def git(args):
    r = subprocess.run(["git"] + args, capture_output=True, encoding="utf-8", errors="replace")
    return r.returncode, r.stdout, r.stderr

# 1) D rows -> all restore (HEAD==origin, files exist in canon)
d_restore = [
    "fleet/inbox/MSG-2026-10-03-0350-bmb-bmc-quality-faces-transfer.md",
    "fleet/tasks/T-2026-10-03-152-P1.json",
    "fleet/tasks/T-2026-10-03-153-P1.json",
    "research/FUND-QUALITY-P1.md",
    "results/_fund_quality_p1_transfer_probe.json",
    "results/_r601bmb_bookkeep.py",
    "results/_r601bmb_closecheck.py",
    "results/_r601bmb_closeout.py",
    "results/_r601bmb_ringcheck.py",
    "results/_r601bmb_s6_runner.ps1",
    "results/_r602bmb_d19_check.py",
    "results/_r602bmb_fuseprobe.py",
    "results/_r602bmb_vpbx2_verify.py",
    "results/_r603bmb_ff_align.py",
    "results/_r603bmb_sensprobe.py",
    "results/fund_quality_p1/d6.json",
    "results/fund_quality_p1/probe.json",
    "results/pool_claims/FUND-VALUE-P1-CELL-VALUEPB-X2/fund-value-p1-cell-valuepb-x2-0of1.bm-b.json",
    "scripts/fund_quality_p1.py",
    "scripts/fund_quality_p1_probe.py",
]
# 2) M rows: stale other-machine faces + stale shared -> origin verbatim
m_restore = [
    "CODELY.md",
    "research/HANDOVER.md",
    "fleet/machines/bm-b.json",
    "logs/iteration-loop/round_reports.md",
    "state.json",
    "results/astock_daily_update_status.json",
    "results/autofill_state.bm-b.json",
    "results/compute_audit.bm-b.json",
    "results/crash_fuse.bm-b.json",
    "results/etf_daily_pull_status.json",
    "results/fund_value_p1/cells_VALUE-PB_x2.jsonl",
    "results/futures_update_status.bm-b.json",
    "results/lhb_update_status.bm-b.json",
    "results/p1d_gates.json",
    "results/pool_dualrun.bm-b.jsonl",
    "results/prospect_promotion/_summary.json",
    "results/regime_state.bm-b.json",
    "results/runnable_pool.bm-b.json",
    "results/saturation_engine/face_bm-b.json",
    "results/saturation_engine/history_bm-b.jsonl",
    "results/saturation_engine/state_bm-b.json",
    "results/token_usage.bm-b.json",
    "results/update_status.bm-b.json",
]
# keep-local: autofill_state.bm-a.json, crash_fuse.bm-a.json, crash_fuse.json,
#             saturation_engine/{face,history,ledger,state}_bm-a.*, pool_core_samples.jsonl (union below)

rc, o, e = git(["checkout", "--"] + d_restore + m_restore)
print("checkout rc=", rc, e.strip()[:300] if rc else "OK (%d files restored)" % (len(d_restore) + len(m_restore)))
if rc != 0:
    sys.exit(1)

# 3) pool_core_samples.jsonl union: origin blob base + local dict-only rows (bytes space, r600)
path = "results/pool_core_samples.jsonl"
rc, blob, e = git(["show", "HEAD:" + path])
if rc != 0:
    print("BLOB FAIL", e); sys.exit(1)
raw = subprocess.run(["git", "show", "HEAD:" + path], capture_output=True).stdout
blob_crlf = raw.count(b"\r\n") > raw.count(b"\n") - raw.count(b"\r\n")
blob_lines = [l for l in raw.split(b"\n") if l.strip()]
with open(path, "rb") as f:
    disk_lines = [l for l in f.read().split(b"\n") if l.strip()]
norm = lambda ls: [l.rstrip(b"\r") for l in ls]
bn, dn = norm(blob_lines), norm(disk_lines)
bset = set(bn)
extra = [l for l in dn if l not in bset]  # local dict rows not in origin
import json as _j
extra = [l for l in extra if _j.loads(l.decode("utf-8")) and isinstance(_j.loads(l.decode("utf-8")), dict)]
eol = b"\r\n" if blob_crlf else b"\n"
out = eol.join(bn + extra) + (eol if raw.endswith(b"\n") or raw.endswith(b"\r\n") else b"")
with open(path, "wb") as f:
    f.write(out)
print("union: blob=%d local_extra=%d -> wrote %d lines, eol=%s" % (len(bn), len(extra), len(bn) + len(extra), "CRLF" if blob_crlf else "LF"))

# 4) verify
rc, o, e = git(["status", "--porcelain"])
print("=== post-repair status ===")
print(o)
