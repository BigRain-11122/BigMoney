# -*- coding: utf-8 -*-
"""r687 bm-a S0.5: orders ack set-diff (same-form full filenames both sides,
r477 law) + D-19 decisions/orders raw-blob sha256 watermark (r660 subprocess
raw-bytes law). Writes results/_r687bma_s05_scan.json, zero console CJK.
"""
import json, os, subprocess, hashlib, io, sys

REPO = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"
GROUP = r"K:\Fluxgroup\FluxGroup"
OUT = REPO + r"\results\_r687bma_s05_scan.json"

def sha256(b):
    return hashlib.sha256(b).hexdigest()

def main():
    out = {"orders": {}, "d19": {}}
    # ---- orders set-diff (local FS both sides, full .md names) ----
    odir = os.path.join(REPO, "fleet", "orders")
    files = sorted(f for f in os.listdir(odir)
                   if f.startswith("O-") and f.endswith(".md"))
    hb_path = os.path.join(REPO, "fleet", "machines", "bm-a.json")
    hb = json.load(open(hb_path, encoding="utf-8"))
    ack = set(hb.get("orders_ack", []))
    unacked = [f for f in files if f not in ack]
    extra = sorted(ack - set(files))
    out["orders"]["files_total"] = len(files)
    out["orders"]["ack_total"] = len(ack)
    out["orders"]["unacked"] = unacked
    out["orders"]["ack_extra"] = extra
    # ---- D-19 watermark (group tree raw blob) ----
    try:
        if os.path.isdir(GROUP):
            subprocess.run(["git", "-C", GROUP, "fetch", "origin"],
                           capture_output=True, timeout=120)
            dec = subprocess.run(["git", "-C", GROUP, "show",
                                  "origin/main:docs/decisions.md"],
                                 capture_output=True, timeout=60)
            orders_g = subprocess.run(["git", "-C", GROUP, "show",
                                        "origin/main:docs/orders.md"],
                                       capture_output=True, timeout=60)
            dec_sha = sha256(dec.stdout) if dec.returncode == 0 else None
            ord_sha = sha256(orders_g.stdout) if orders_g.returncode == 0 else None
            out["d19"]["decisions_sha256"] = dec_sha
            out["d19"]["group_orders_sha256"] = ord_sha
            out["d19"]["decisions_bytes"] = len(dec.stdout)
        else:
            out["d19"]["error"] = "GROUP TREE ABSENT (S4U fallback path)"
    except Exception as e:
        out["d19"]["error"] = repr(e)[:300]
    # state watermark keys
    sp = os.path.join(REPO, "state-bm-a.json")
    if os.path.exists(sp):
        st = json.load(open(sp, encoding="utf-8"))
        out["d19"]["state_keys"] = {k: st.get(k) for k in sorted(st)
                                    if "sha" in k.lower() or "watermark" in k.lower()}
    with io.open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print("WROTE", OUT)
    return 0

if __name__ == "__main__":
    sys.exit(main())
