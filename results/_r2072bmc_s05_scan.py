"""S0.5 double scan for r2072 (bm-c): orders diff + group decisions watermark.

Pure read-only.  Two questions, one file:

  1. every O-*.md in fleet/orders against the heartbeat's `orders_ack` set -- the scan is a
     set difference, never a timestamp filter (R13 O-1820 skipped-id precedent), and it
     prints the ones that matter (November) separately from the historical broadcast tail;
  2. the group decision ledger's watermark: `git cat-file blob origin/main:docs/decisions.md`
     straight to a temp file and hashed there -- never through a PowerShell string roundtrip
     (r1911 / r2048: `>` plus `2>&1` re-encodes the stream and the sha stops being the
     object's sha), compared with state-bm-c.json's `last_decisions_sha`.
"""
import glob
import hashlib
import io
import json
import os
import subprocess
import sys
import tempfile

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ORDERS = os.path.join(REPO, "fleet", "orders")
HEARTBEAT = os.path.join(REPO, "fleet", "machines", "bm-c.json")
STATE = os.path.join(REPO, "state-bm-c.json")
GROUP = r"K:\Fluxgroup\FluxGroup"


def ack_set():
    with io.open(HEARTBEAT, encoding="utf-8") as f:
        hb = json.load(f)
    acked = set()
    for raw in hb.get("orders_ack") or []:
        name = os.path.basename(str(raw))
        acked.add(name)
        if name.endswith(".md"):
            acked.add(name[:-3])
        else:
            acked.add(name + ".md")
    return acked


def scan_orders():
    files = sorted(glob.glob(os.path.join(ORDERS, "O-*.md")))
    acked = ack_set()
    rows = []
    for p in files:
        base = os.path.basename(p)
        rows.append({"file": base, "acked": base in acked})
    missing = [r["file"] for r in rows if not r["acked"]]
    nov = [m for m in missing if "-202611" in m]
    return {"n_files": len(files), "n_acked": len(files) - len(missing),
            "n_unacked": len(missing), "nov_unacked": nov,
            "unacked_sample": missing[:8]}


def decisions_watermark():
    fd, tmp = tempfile.mkstemp(prefix="dec_", suffix=".bin")
    os.close(fd)
    try:
        with open(tmp, "wb") as out:
            rc = subprocess.run(
                ["git", "-C", GROUP, "cat-file", "blob", "origin/main:docs/decisions.md"],
                stdout=out, stderr=subprocess.DEVNULL).returncode
        if rc != 0:
            return {"ok": False, "why": "git cat-file rc=%d" % rc}
        with open(tmp, "rb") as fh:
            blob = fh.read()
        digest = hashlib.sha256(blob).hexdigest()
        with io.open(STATE, encoding="utf-8") as f:
            held = json.load(f).get("last_decisions_sha")
        return {"ok": True, "bytes": len(blob), "sha256": digest,
                "held": held, "same": digest == held}
    finally:
        try:
            os.unlink(tmp)
        except OSError:
            pass


def main():
    subprocess.run(["git", "-C", GROUP, "fetch", "origin", "--quiet"],
                   check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    orders = scan_orders()
    dec = decisions_watermark()
    payload = {"round": "r2072", "machine": "bm-c", "orders": orders, "decisions": dec}
    out = os.path.join(REPO, "results", "_r2072bmc_s05_scan.json")
    with io.open(out, "w", encoding="utf-8", newline="\n") as f:
        json.dump(payload, f, ensure_ascii=False, indent=1, sort_keys=True)
        f.write("\n")
    print("S0.5 orders: %(n_files)d files, %(n_acked)d acked, %(n_unacked)d unacked" % orders)
    print("S0.5 unacked in 2026-11: %s" % (", ".join(orders["nov_unacked"]) or "none"))
    if dec.get("ok"):
        print("S0.5 decisions: %d bytes sha=%s same_as_held=%s"
              % (dec["bytes"], dec["sha256"][:12], dec["same"]))
    else:
        print("S0.5 decisions: unreadable -- %s" % dec.get("why"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
