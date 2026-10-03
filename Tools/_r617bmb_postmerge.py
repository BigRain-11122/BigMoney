"""r617 bm-b: S0 post-merge legs.

1) pool_core_samples.jsonl origin-union (r570 law): origin-verbatim base +
   local snapshot rows appended if byte-absent; dict-only gate; atomic write.
2) D-19 watermark: hash origin/main:docs/decisions.md (python bytes, r617 law)
   vs state.json last_decisions_sha; if changed, print dispatch-board lines
   involving BigMoney/quant + bm-b.
3) docs/orders.md CEO physical-items scan for BigMoney rows.
Prints PASS/FAIL markers per leg.
"""
import hashlib
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PCS = os.path.join(ROOT, "results", "pool_core_samples.jsonl")
LOCAL_SNAP = os.path.join(os.environ.get("TEMP", "."), "pcs_local_r617.jsonl")
STATE = os.path.join(ROOT, "state.json")


def leg_pcs_union():
    with open(PCS, encoding="utf-8") as fh:
        origin_lines = [ln.rstrip("\n") for ln in fh if ln.strip()]
    origin_set = set(origin_lines)
    added = 0
    if os.path.exists(LOCAL_SNAP):
        with open(LOCAL_SNAP, encoding="utf-8") as fh:
            local_lines = [ln.rstrip("\n") for ln in fh if ln.strip()]
        for ln in local_lines:
            if ln not in origin_set:
                origin_lines.append(ln)
                origin_set.add(ln)
                added += 1
    merged = origin_lines
    bad = 0
    for ln in merged:
        try:
            if not isinstance(json.loads(ln), dict):
                bad += 1
        except Exception:
            bad += 1
    if bad:
        print("PCS-UNION FAIL: %d non-dict lines" % bad)
        return 1
    tmp = PCS + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as fh:
        for ln in merged:
            fh.write(ln + "\n")
    os.replace(tmp, PCS)
    print("PCS-UNION PASS: origin=%d local_added=%d total=%d" % (
        len(merged) - added, added, len(merged)))
    return 0


def git_show_bytes(path):
    r = subprocess.run(
        ["git", "-C", ROOT, "show", "origin/main:" + path],
        capture_output=True)
    if r.returncode != 0:
        return None
    return r.stdout


def leg_d19():
    blob = git_show_bytes("docs/decisions.md")
    if blob is None:
        print("D19 FAIL: git show docs/decisions.md rc!=0")
        return 1
    sha = hashlib.sha256(blob).hexdigest()
    with open(STATE, encoding="utf-8") as fh:
        st = json.load(fh)
    prev = st.get("last_decisions_sha", "")
    if sha == prev:
        print("D19 UNCHANGED %s" % sha[:8])
        return 0
    print("D19 CHANGED prev=%s new=%s" % (prev[:8], sha[:8]))
    text = blob.decode("utf-8", errors="replace")
    board = False
    hits = 0
    for ln in text.splitlines():
        if "派工通告板" in ln:
            board = True
        if board and any(k in ln for k in ("BigMoney", "bigmoney", "quant", "bm-b")):
            print("D19-DISPATCH: " + ln.strip()[:200])
            hits += 1
    if hits == 0:
        print("D19-DISPATCH: zero lines involving BigMoney/quant/bm-b")
    return 0


def leg_orders_md():
    blob = git_show_bytes("docs/orders.md")
    if blob is None:
        print("ORDERSMD: absent or fetch fail (non-blocking)")
        return 0
    text = blob.decode("utf-8", errors="replace")
    hits = 0
    for ln in text.splitlines():
        if any(k in ln for k in ("BigMoney", "bigmoney", "quant")):
            print("ORDERSMD-HIT: " + ln.strip()[:200])
            hits += 1
    if hits == 0:
        print("ORDERSMD: zero BigMoney/quant rows")
    return 0


if __name__ == "__main__":
    rc = leg_pcs_union()
    rc |= leg_d19()
    rc |= leg_orders_md()
    sys.exit(rc)
