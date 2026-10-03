"""r423 bm-c merge resolve: 16 UU runtime-snapshot faces, take-new by embedded
timestamp (r621/r634 ring-merge precedent). token_usage.json verified as an
idempotent regenerating aggregate snapshot (generated-ts head, per-machine
keys inside, delta_vs_prev vs own prev) -- NOT an append-only ledger -- so it
joins the take-new family. Writes a receipt (r634 law).

Usage (from repo root, merge in progress):
  python Tools/_r423bmc_merge_resolve.py
"""
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def git(*a):
    r = subprocess.run(["git", *a], cwd=ROOT, capture_output=True, text=True,
                       encoding="utf-8", errors="replace",
                       creationflags=0x08000000)
    return r.stdout.strip()


def blob_ts(rev, path):
    """Extract the newest embedded timestamp from a blob (top-level ts-ish
    fields + any 'yyyy-mm-dd HH:MM:SS' string anywhere shallow)."""
    r = subprocess.run(["git", "show", f"{rev}:{path}"], cwd=ROOT,
                       capture_output=True, text=True, encoding="utf-8",
                       errors="replace", creationflags=0x08000000)
    if r.returncode != 0:
        return None
    text = r.stdout
    stamps = re.findall(
        r"20\d{2}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2}", text[:4000])
    return max(stamps) if stamps else None


def main():
    out = git("status", "--porcelain")
    uu = [ln[3:] for ln in out.splitlines()
          if ln.startswith("UU ") or ln.startswith("AA ")]
    receipt = {"ts_resolved": [], "union_resolved": [], "other": []}
    for path in uu:
        ours = blob_ts(":2", path)
        theirs = blob_ts(":3", path)
        if ours and theirs:
            winner = ":2" if ours >= theirs else ":3"
            side = "ours" if ours >= theirs else "theirs"
        elif ours:
            winner, side = ":2", "ours"
        elif theirs:
            winner, side = ":3", "theirs"
        else:
            winner, side = ":2", "ours(no-ts)"
        r = subprocess.run(["git", "checkout-index", "-f", "--stage",
                            winner[1:], "--", path], cwd=ROOT,
                           capture_output=True, text=True,
                           creationflags=0x08000000)
        if r.returncode != 0:
            # checkout-index stage form: use git checkout --ours/--theirs
            flag = "--ours" if winner == ":2" else "--theirs"
            git("checkout", flag, "--", path)
        git("add", path)
        receipt["ts_resolved"].append(
            {"path": path, "ours_ts": ours, "theirs_ts": theirs,
             "winner": side})
    rp = os.path.join(ROOT, "results", "_r423bmc_merge_resolve_receipt.json")
    json.dump(receipt, open(rp, "w", encoding="utf-8"), indent=1,
              ensure_ascii=False)
    n = len(receipt["ts_resolved"]) + len(receipt["union_resolved"]) \
        + len(receipt["other"])
    print(f"resolved {n} faces -> {rp}")
    for e in receipt["ts_resolved"]:
        print(f"  take-{e['winner']}: {e['path']} "
              f"(ours {e['ours_ts']} vs theirs {e['theirs_ts']})")
    for e in receipt["union_resolved"]:
        print(f"  union: {e['path']}")


if __name__ == "__main__":
    sys.exit(main())
