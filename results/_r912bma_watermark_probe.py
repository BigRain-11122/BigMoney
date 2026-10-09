"""r912 bm-a: DEC/ORD watermark probe (group origin/main via C: real-path, python raw-bytes canonical).

Follows D-20260930-19/D-20261004-02(3) law: fetch + git show origin blob, SHA-256 over raw bytes.
Read-only vs group tree; zero tree-touch.
"""
import hashlib
import json
import subprocess
import sys

GROUP = r"C:\Users\sjs20\Desktop\FluxGroup"
STATE = r"results\state_probe_r912.json"  # probe output sink (not the state file)


def run(args):
    p = subprocess.run(args, capture_output=True)
    if p.returncode != 0:
        print("CMD_FAIL", args, p.stderr.decode("utf-8", "replace")[:500])
        sys.exit(2)
    return p.stdout


def main():
    run(["git", "-C", GROUP, "fetch", "origin"])
    out = {}
    for key, path in (("decisions", "docs/decisions.md"), ("orders", "docs/orders.md")):
        blob = run(["git", "-C", GROUP, "show", "origin/main:" + path])
        h = hashlib.sha256(blob).hexdigest()
        out[key] = h
    with open(STATE, "w", encoding="ascii") as f:
        json.dump({"decisions_sha": out["decisions"], "orders_sha": out["orders"]}, f, indent=1)
    print(json.dumps(out))

    # tail lines of decisions "dispatch board" + orders CEO physical section, filtered for BigMoney
    dec = run(["git", "-C", GROUP, "show", "origin/main:docs/decisions.md"]).decode("utf-8", "replace")
    lines = dec.splitlines()
    hits = [ln for ln in lines if ("BigMoney" in ln or "bigmoney" in ln or "quant" in ln.lower())]
    print("DEC_BM_LINES_TAIL:")
    for ln in hits[-6:]:
        print("  ", ln[:220])
    print("DEC_TOTAL_LINES", len(lines))

    orders = run(["git", "-C", GROUP, "show", "origin/main:docs/orders.md"]).decode("utf-8", "replace")
    ol = orders.splitlines()
    oh = [ln for ln in ol if ("BigMoney" in ln or "bigmoney" in ln)]
    print("ORD_BM_LINES_TAIL:")
    for ln in oh[-4:]:
        print("  ", ln[:220])
    print("ORD_TOTAL_LINES", len(ol))


if __name__ == "__main__":
    main()
