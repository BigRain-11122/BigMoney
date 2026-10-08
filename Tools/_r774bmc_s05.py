"""r774 bm-c S0.5 facts probe (immediate generation, source=_r770bmc_s05.py
1-gen clone): group-tree origin DEC/ORD raw-blob hashes
(SHA-256 / SHA-1 ALGORITHM PIN per r537 law; hex-case compare normalized per
r711 law), state watermark comparison, fleet orders ack diff
(basename-with-.md canon), inbox unread scan.
r774 extension (canon-safe, facts-driven): on ORD delta, enumerate changed
rows by locating the prev blob sha in recent history of docs/orders.md and
writing a unified diff to results/_r774bmc_ord_delta.txt; on either delta,
dump the new raw blob to results/_r774bmc_{ord,dec}_blob.md for consumption.
Facts-driven JSON -> results/_r774bmc_s05_facts.json. Pattern credit:
Tools/_r770bmc_s05.py (canonical clone chain)."""
import subprocess
import hashlib
import json
import glob
import os
import re

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
GROUP = r"K:\Fluxgroup\FluxGroup"
ROUND = 774


def git_out(cwd, args):
    p = subprocess.run(["git", "-C", cwd] + args, capture_output=True)
    return p.returncode, p.stdout, p.stderr


def main():
    facts = {"round": ROUND}
    rc, _, err = git_out(GROUP, ["fetch", "origin"])
    facts["fetch_rc"] = rc
    if rc != 0:
        facts["fetch_err"] = err.decode("utf-8", "replace")[:300]

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

    # r774 extension: locate prev ORD blob in recent history, diff rows.
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
            with open(os.path.join(REPO, "results", "_r774bmc_ord_delta.txt"),
                      "w", encoding="utf-8") as fh:
                fh.write(dtxt)
            added = [l for l in dtxt.splitlines() if l.startswith("+") and not l.startswith("+++")]
            removed = [l for l in dtxt.splitlines() if l.startswith("-") and not l.startswith("---")]
            facts["ord_delta_rows"] = {"added": len(added), "removed": len(removed)}
        with open(os.path.join(REPO, "results", "_r774bmc_ord_blob.md"),
                  "wb") as fh:
            fh.write(ord_bytes)
    if facts["dec_delta"]:
        with open(os.path.join(REPO, "results", "_r774bmc_dec_blob.md"),
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

    out = os.path.join(REPO, "results", "_r774bmc_s05_facts.json")
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(facts, fh, indent=1)
    print(json.dumps(facts, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
