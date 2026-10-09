# -*- coding: utf-8 -*-
"""r801 bm-c S0.5 facts probe (1-gen clone of _r801bmc_s05.py canon):
repo status/tip log/ahead-behind, orphan-face probe (read-only, round-zero law
O-20261008-1300 knife-2), pool/watermark live reads (D-20261009-01 (iii) SLA
face), group-tree origin DEC/ORD raw-blob hashes (SHA-256 / SHA-1 ALGORITHM
PIN per r537 law; hex-case compare normalized per r711 law), fleet orders ack
diff (basename-with-.md canon), inbox scan.
Usage: python Tools/_r801bmc_s05.py [start|closing]
  start   -> results/_r801bmc_s05_facts.json (round-start sweep)
  closing -> results/_r801bmc_s0_facts.json (S7 closing double-sweep)
Every subprocess passes CREATE_NO_WINDOW (zero-desktop-flash defense-in-depth,
U060/2026-10-01 silence law)."""
import subprocess
import hashlib
import json
import glob
import os
import re
import sys

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
GROUP = r"K:\Fluxgroup\FluxGroup"
ROUND = 801
CNW = getattr(subprocess, "CREATE_NO_WINDOW", 0)


def git_out(cwd, args):
    p = subprocess.run(["git", "-C", cwd] + args, capture_output=True,
                       creationflags=CNW)
    return p.returncode, p.stdout, p.stderr


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "start"
    tag = "s05" if mode == "start" else "s0"
    facts = {"round": ROUND, "mode": mode}

    # --- repo state (post-rebase record; no pull here) ---
    rc, out, _ = git_out(REPO, ["status", "--porcelain"])
    st = out.decode("utf-8", "replace")
    facts["dirty"] = st.strip()
    facts["dirty_n"] = len(st.strip().splitlines()) if st.strip() else 0
    rc, out, _ = git_out(REPO, ["log", "-3", "--oneline"])
    facts["tip_log"] = out.decode("utf-8", "replace").strip()
    rc, out, _ = git_out(REPO, ["rev-list", "--left-right", "--count",
                                "HEAD...origin/main"])
    cnt = out.decode().split()
    facts["ahead"] = int(cnt[0]) if len(cnt) == 2 else None
    facts["behind"] = int(cnt[1]) if len(cnt) == 2 else None

    # --- orphan face probe (read-only; round report carries the count) ---
    p = subprocess.run(["python", "Tools/orphan_face_probe.py"],
                       cwd=REPO, capture_output=True, creationflags=CNW)
    facts["orphan_probe_rc"] = p.returncode
    ot = p.stdout.decode("utf-8", "replace")
    facts["orphan_probe_tail"] = ot.strip().splitlines()[-6:] if ot.strip() else []
    m = re.search(r"(?i)orphan[s]?\D{0,20}(\d+)", ot)
    facts["orphan_n"] = int(m.group(1)) if m else None

    # --- pool + watermark live reads (SLA face) ---
    try:
        with open(os.path.join(REPO, "results", "runnable_pool.json"),
                  encoding="utf-8") as fh:
            pool = json.load(fh)
        entries = pool.get("entries", pool if isinstance(pool, list) else [])
        stat = {}
        for e in entries:
            s = e.get("status", "?")
            stat[s] = stat.get(s, 0) + 1
        facts["pool_total"] = len(entries)
        facts["pool_status"] = stat
        facts["pool_claimable"] = stat.get("ready", 0) + stat.get("open", 0)
        w17 = [e for e in entries if "W17" in str(e.get("id", ""))]
        facts["w17_faces"] = ["%s:%s" % (e.get("id"), e.get("status"))
                              for e in w17]
    except Exception as ex:
        facts["pool_err"] = repr(ex)[:200]
    try:
        with open(os.path.join(REPO, "results", "watermark_red.json"),
                  encoding="utf-8") as fh:
            wm = json.load(fh)
        facts["wm_red"] = wm.get("red")
        facts["wm_verdict"] = str(wm.get("verdict") or "")[:200]
        facts["wm_next_pick"] = str(wm.get("next_pick") or "")[:200]
    except Exception as ex:
        facts["wm_err"] = repr(ex)[:200]

    # --- group-tree S0.5 (verbatim s05 canon) ---
    rc, _, err = git_out(GROUP, ["fetch", "origin"])
    facts["group_fetch_rc"] = rc
    if rc != 0:
        facts["group_fetch_err"] = err.decode("utf-8", "replace")[:300]
    rc, dec_bytes, _ = git_out(GROUP, ["show", "origin/main:docs/decisions.md"])
    facts["dec_bytes"] = len(dec_bytes)
    facts["dec_sha"] = hashlib.sha256(dec_bytes).hexdigest().upper()
    rc, ord_bytes, _ = git_out(GROUP, ["show", "origin/main:docs/orders.md"])
    facts["ord_bytes"] = len(ord_bytes)
    facts["ord_sha"] = hashlib.sha1(ord_bytes).hexdigest().upper()

    with open(os.path.join(REPO, "state-bm-c.json"), encoding="utf-8") as fh:
        state = json.load(fh)
    facts["prev_dec_sha"] = state.get("last_decisions_sha", "")
    facts["prev_ord_sha"] = state.get("last_orders_sha", "")
    facts["dec_delta"] = facts["dec_sha"].upper() != facts["prev_dec_sha"].upper()
    facts["ord_delta"] = facts["ord_sha"].upper() != facts["prev_ord_sha"].upper()

    facts["ord_delta_rows"] = None
    if facts["ord_delta"]:
        rc, hist, _ = git_out(GROUP, ["rev-list", "-15", "origin/main",
                                       "--", "docs/orders.md"])
        prev_commit = None
        for c in hist.decode("utf-8", "replace").split():
            rc2, blob, _ = git_out(GROUP, ["show", "%s:docs/orders.md" % c])
            if hashlib.sha1(blob).hexdigest().upper() == facts["prev_ord_sha"].upper():
                prev_commit = c
                break
        facts["ord_prev_commit"] = prev_commit
        if prev_commit:
            rc3, diff, _ = git_out(GROUP, ["diff", "--unified=0",
                                            "%s:docs/orders.md" % prev_commit,
                                            "origin/main:docs/orders.md"])
            dtxt = diff.decode("utf-8", "replace")
            with open(os.path.join(REPO, "results",
                                   "_r801bmc_ord_delta.txt"),
                      "w", encoding="utf-8") as fh:
                fh.write(dtxt)
            added = [l for l in dtxt.splitlines() if l.startswith("+") and not l.startswith("+++")]
            removed = [l for l in dtxt.splitlines() if l.startswith("-") and not l.startswith("---")]
            facts["ord_delta_rows"] = {"added": len(added), "removed": len(removed)}
            facts["ord_delta_added_rows"] = added[:40]
        with open(os.path.join(REPO, "results", "_r801bmc_ord_blob.md"),
                  "wb") as fh:
            fh.write(ord_bytes)
    if facts["dec_delta"]:
        rc, dlog, _ = git_out(GROUP, ["log", "-8", "--oneline", "origin/main",
                                       "--", "docs/decisions.md"])
        with open(os.path.join(REPO, "results", "_r801bmc_dec_log.txt"),
                  "w", encoding="utf-8") as fh:
            fh.write(dlog.decode("utf-8", "replace"))
        with open(os.path.join(REPO, "results", "_r801bmc_dec_blob.md"),
                  "wb") as fh:
            fh.write(dec_bytes)

    order_files = sorted(glob.glob(os.path.join(REPO, "fleet", "orders", "O-*.md")))
    facts["fleet_orders_total"] = len(order_files)
    hb_path = os.path.join(REPO, "fleet", "machines", "bm-c.json")
    with open(hb_path, encoding="utf-8") as fh:
        hb = json.load(fh)
    ack = set(hb.get("orders_ack", []))
    unacked = []
    for f in order_files:
        base = os.path.basename(f)   # canon: full basename WITH .md suffix
        if base not in ack:
            unacked.append(base)
    facts["unacked"] = unacked

    inbox_dir = os.path.join(REPO, "fleet", "inbox")
    unread = []
    for f in sorted(glob.glob(os.path.join(inbox_dir, "*.md"))):
        try:
            txt = open(f, encoding="utf-8", errors="replace").read()
        except Exception:
            unread.append(os.path.basename(f))
            continue
        if re.search(r"(?im)(bm-c|all)", txt[:800]):
            unread.append(os.path.basename(f))
    facts["inbox_unread"] = unread

    facts["shape_assert"] = bool(
        re.fullmatch(r"[0-9A-F]{64}", facts["dec_sha"])
        and re.fullmatch(r"[0-9A-F]{40}", facts["ord_sha"]))

    out = os.path.join(REPO, "results", "_r801bmc_%s_facts.json" % tag)
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(facts, fh, indent=1)
    print(json.dumps(facts, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
