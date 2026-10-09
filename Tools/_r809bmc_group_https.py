# -*- coding: utf-8 -*-
"""r809 bm-c group-tree HTTPS freshness fallback: the group-tree SSH fetch
reset (port 22, same 20.205.243.166 face) left the S0.5 DEC/ORD hashes on a
stale origin/main base. This helper fetches the group repo over HTTPS (r805
netpath law: HTTPS face is the reliable channel when SSH resets) into a
PRIVATE temp ref refs/tmp/bmc-r809-group (zero touch of origin/main), hashes
docs/decisions.md (SHA-256) + docs/orders.md (SHA-1, ALGORITHM PIN r537) as
raw bytes, compares with state-bm-c.json watermarks, reports staleness of
the origin/main ref, and ALWAYS deletes the temp ref (finally block).
Usage: python Tools/_r809bmc_group_https.py"""
import subprocess
import hashlib
import json
import os

GROUP = r"K:\Fluxgroup\FluxGroup"
REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
URL = "https://github.com/BigRain-11122/FluxGroup.git"
TMP_REF = "refs/tmp/bmc-r809-group"
CNW = getattr(subprocess, "CREATE_NO_WINDOW", 0)


def git_out(args, timeout=75):
    try:
        p = subprocess.run(["git", "-C", GROUP] + args, capture_output=True,
                           creationflags=CNW, timeout=timeout)
        return p.returncode, p.stdout, p.stderr
    except subprocess.TimeoutExpired:
        return 124, b"", b"timeout"


def main():
    facts = {"round": 809, "channel": "https", "url": URL}
    rc, out, err = git_out(["fetch", URL, "main:" + TMP_REF])
    facts["fetch_rc"] = rc
    facts["fetch_err"] = err.decode("utf-8", "replace")[:300]
    if rc == 0:
        try:
            rc1, dec, _ = git_out(["show", TMP_REF + ":docs/decisions.md"])
            rc2, ord_, _ = git_out(["show", TMP_REF + ":docs/orders.md"])
            facts["dec_sha"] = hashlib.sha256(dec).hexdigest().upper()
            facts["ord_sha"] = hashlib.sha1(ord_).hexdigest().upper()
            facts["dec_bytes"] = len(dec)
            facts["ord_bytes"] = len(ord_)
            with open(os.path.join(REPO, "state-bm-c.json"),
                      encoding="utf-8") as fh:
                state = json.load(fh)
            facts["prev_dec_sha"] = state.get("last_decisions_sha", "")
            facts["prev_ord_sha"] = state.get("last_orders_sha", "")
            facts["dec_delta_https"] = (facts["dec_sha"].upper()
                                        != facts["prev_dec_sha"].upper())
            facts["ord_delta_https"] = (facts["ord_sha"].upper()
                                        != facts["prev_ord_sha"].upper())
            # is the local origin/main ref stale vs the fresh https tip?
            rc3, tip, _ = git_out(["rev-parse", TMP_REF])
            rc4, omtip, _ = git_out(["rev-parse", "origin/main"])
            facts["https_tip"] = tip.decode().strip()
            facts["origin_main_tip"] = omtip.decode().strip()
            facts["origin_main_stale"] = (facts["https_tip"]
                                          != facts["origin_main_tip"])
            facts["shape_assert"] = bool(
                len(facts["dec_sha"]) == 64 and len(facts["ord_sha"]) == 40)
        finally:
            git_out(["update-ref", "-d", TMP_REF])
    outp = os.path.join(REPO, "results", "_r809bmc_group_https.json")
    with open(outp, "w", encoding="utf-8") as fh:
        json.dump(facts, fh, indent=1)
    compact = {k: facts.get(k) for k in (
        "fetch_rc", "dec_sha", "dec_delta_https", "ord_sha",
        "ord_delta_https", "origin_main_stale", "https_tip",
        "origin_main_tip", "shape_assert")}
    print(json.dumps(compact, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
