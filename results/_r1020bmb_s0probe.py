"""r1020 bm-b: S0.5 probe bundle + O-20261018-0948 window-judgment evidence.

Legs:
  A. orders ack diff: fleet/orders/*.md vs heartbeat orders_ack (bm-b.json).
  B. D-19 dual probe: group repo (C:\\Fluxgroup\\FluxGroup) fresh-read
     docs/decisions.md + docs/orders.md via git show origin/main:<path>
     after fetch; SHA-256 vs heartbeat last_*_sha keys.
  C. O-0948 evidence: ROUND TIMEOUT census post-v2 (since 2026-10-18 10:57
     local v2 first-carrying round r1005), spawning census, and per-round
     closeout evidence (round_reports rows) in the observation window.
Zero writes to shared faces; prints only.
"""
import glob
import hashlib
import json
import os
import re
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HEARTBEAT = os.path.join(ROOT, "fleet", "machines", "bm-b.json")
GROUP = r"C:\Fluxgroup\FluxGroup"


def sh(args, cwd=None, timeout=90):
    p = subprocess.run(
        args, cwd=cwd, capture_output=True, timeout=timeout,
    )
    return p.returncode, p.stdout, p.stderr


def main():
    hb = json.load(open(HEARTBEAT, encoding="utf-8"))
    ack = set(hb.get("orders_ack", []))

    # --- A. orders ack diff ---
    files = sorted(
        os.path.basename(p) for p in glob.glob(os.path.join(ROOT, "fleet", "orders", "*.md"))
    )
    unacked = [f for f in files if f not in ack]
    print(f"A. orders files={len(files)} acked={len(ack & set(files))} unacked={unacked}")

    # --- B. D-19 dual probe (fresh read via git show origin/main) ---
    rc, out, err = sh(["git", "fetch", "origin"], cwd=GROUP, timeout=120)
    print(f"B. group fetch rc={rc} {err.decode(errors='replace').strip()[:120]}")
    for label, path, key in (
        ("DEC", "docs/decisions.md", "last_decisions_sha"),
        ("ORD", "docs/orders.md", "last_orders_sha"),
    ):
        rc, out, err = sh(["git", "show", f"origin/main:{path}"], cwd=GROUP, timeout=60)
        if rc == 0:
            h = hashlib.sha256(out).hexdigest()
            prev = hb.get(key, "")
            print(f"B. {label} sha={h[:16]} prev={prev[:16]} verdict={'UNCHANGED' if h == prev else 'CHANGED'}")
        else:
            print(f"B. {label} show rc={rc} err={err.decode(errors='replace')[:120]}")

    # --- C. O-0948 evidence: v2 adoption was 2026-10-18 10:57 local (r1005) ---
    V2_TS = "20261018_1057"
    logdir = os.path.join(ROOT, "logs", "iteration-loop")
    timeout_hits = []
    spawnings = []
    for p in sorted(glob.glob(os.path.join(logdir, "run_*.log"))):
        base = os.path.basename(p)
        try:
            with open(p, encoding="utf-8", errors="replace") as f:
                for line in f:
                    if "ROUND TIMEOUT" in line:
                        timeout_hits.append(f"{base}: {line.strip()}")
                    if "spawning headless round" in line and "hard-cap" in line:
                        spawnings.append(f"{base}: {line.strip()[:150]}")
        except OSError:
            continue
    post_v2_timeouts = [t for t in timeout_hits if t[:19] >= "run_20261018_1057"] if timeout_hits else []
    # run_YYYYMMDD_HHMMSS naming: compare full prefix
    post_v2_timeouts = [t for t in timeout_hits if t >= f"run_{V2_TS}"]
    print(f"C. TIMEOUT total={len(timeout_hits)} post_v2={len(post_v2_timeouts)}")
    for t in timeout_hits[-3:]:
        print(f"C. last3: {t}")
    for t in post_v2_timeouts:
        print(f"C. POST-V2 HIT: {t}")
    print(f"C. v2 spawning lines={len(spawnings)} (new-phrase carriers)")
    if spawnings:
        print(f"C. first: {spawnings[0]}")
        print(f"C. last: {spawnings[-1]}")

    # closeout continuity: round report rows in the observation window
    rr = os.path.join(logdir, "round_reports.md")
    rows = []
    if os.path.exists(rr):
        with open(rr, encoding="utf-8", errors="replace") as f:
            for line in f:
                m = re.match(r"(2026-10-1[89]T\d{2}:\d{2}:\d{2}\S*) \| (r\d+)", line)
                if m:
                    rows.append((m.group(1), m.group(2)))
    post = [r for r in rows if r[0] >= "2026-10-18T10:57"]
    print(f"C. round-report rows post-v2={len(post)} first={post[0] if post else None} last={post[-1] if post else None}")
    print("C. window rounds:", [r[1] for r in post])


if __name__ == "__main__":
    main()
