# -*- coding: utf-8 -*-
"""r817 bm-c S0.5 group-tree DEC/ORD watermark check (r816 helper mechanism
reused verbatim, zero rewrite of the proven legs): primary leg = git fetch
origin on the group tree, hash docs/decisions.md (SHA-256) + docs/orders.md
(SHA-1, ALGORITHM PIN r537) as raw blob bytes from origin/main; fallback leg
(r805 netpath law, only if the primary fetch resets) = HTTPS fetch into
PRIVATE temp ref refs/tmp/bmc-r817-group (zero origin/main touch, always
deleted in finally). Facts-driven (results/_r817bmc_s05_facts.json, r583
law: close face reads sha from facts json, ZERO literal constants). Compares
with state-bm-c.json watermarks and prints the delta verdict.
Usage: python Tools/_r817bmc_s05.py"""
import subprocess
import hashlib
import json
import os

GROUP = r"K:\Fluxgroup\FluxGroup"
REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
URL = "https://github.com/BigRain-11122/FluxGroup.git"
TMP_REF = "refs/tmp/bmc-r817-group"
CNW = getattr(subprocess, "CREATE_NO_WINDOW", 0)


def git_out(args, timeout=75):
    try:
        p = subprocess.run(["git", "-C", GROUP] + args, capture_output=True,
                           creationflags=CNW, timeout=timeout)
        return p.returncode, p.stdout, p.stderr
    except subprocess.TimeoutExpired:
        return 124, b"", b"timeout"


def blob(ref, path):
    rc, out, err = git_out(["show", ref + ":" + path])
    return (rc, out, err) if rc == 0 else (rc, b"", err)


def main():
    facts = {"round": 817}
    channel = None
    rc, out, err = git_out(["fetch", "origin"])
    facts["ssh_fetch_rc"] = rc
    facts["ssh_fetch_err"] = err.decode("utf-8", "replace")[:300]
    ref = "origin/main"
    if rc == 0:
        channel = "ssh-origin"
    else:
        rc, out, err = git_out(["fetch", URL, "main:" + TMP_REF])
        facts["https_fetch_rc"] = rc
        facts["https_fetch_err"] = err.decode("utf-8", "replace")[:300]
        if rc == 0:
            channel = "https-tmpref"
            ref = TMP_REF
    facts["channel"] = channel
    if channel:
        try:
            rc1, dec, e1 = blob(ref, "docs/decisions.md")
            rc2, ord_, e2 = blob(ref, "docs/orders.md")
            facts["dec_show_rc"] = rc1
            facts["ord_show_rc"] = rc2
            if rc1 == 0 and rc2 == 0:
                facts["dec_sha"] = hashlib.sha256(dec).hexdigest().upper()
                facts["ord_sha"] = hashlib.sha1(ord_).hexdigest().upper()
                facts["dec_bytes"] = len(dec)
                facts["ord_bytes"] = len(ord_)
                with open(os.path.join(REPO, "state-bm-c.json"),
                          encoding="utf-8") as fh:
                    state = json.load(fh)
                facts["prev_dec_sha"] = state.get("last_decisions_sha", "")
                facts["prev_ord_sha"] = state.get("last_orders_sha", "")
                facts["dec_delta"] = (facts["dec_sha"].upper()
                                      != facts["prev_dec_sha"].upper())
                facts["ord_delta"] = (facts["ord_sha"].upper()
                                      != facts["prev_ord_sha"].upper())
                facts["shape_assert"] = bool(
                    len(facts["dec_sha"]) == 64 and len(facts["ord_sha"]) == 40)
                # fleet-local faces for the closing asserts: orders diff + inbox
                hb = json.loads(open(os.path.join(
                    REPO, "fleet", "machines", "bm-c.json"),
                    encoding="utf-8").read())
                ack = set(hb.get("orders_ack", []))
                orders_dir = os.path.join(REPO, "fleet", "orders")
                present = set(f for f in os.listdir(orders_dir)
                              if f.endswith(".md"))
                facts["unacked"] = sorted(present - ack)
                facts["ack_stale"] = sorted(ack - present)
                inbox_dir = os.path.join(REPO, "fleet", "inbox")
                facts["inbox_unread"] = sorted(
                    f for f in os.listdir(inbox_dir)
                    if f.endswith(".md")) if os.path.isdir(inbox_dir) else []
        finally:
            if channel == "https-tmpref":
                git_out(["update-ref", "-d", TMP_REF])
    outp = os.path.join(REPO, "results", "_r817bmc_s05_facts.json")
    with open(outp, "w", encoding="utf-8") as fh:
        json.dump(facts, fh, indent=1)
    compact = {k: facts.get(k) for k in (
        "channel", "ssh_fetch_rc", "dec_sha", "dec_delta", "ord_sha",
        "ord_delta", "shape_assert", "unacked", "ack_stale", "inbox_unread")}
    print(json.dumps(compact, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
