# -*- coding: utf-8 -*-
"""r687 bm-a D-19 sparse-clone raw-blob watermark (r631 recipe; r677 ssh-first
dual URL + mkdtemp unique dir; r660 subprocess raw-bytes sha256 law).
Zero persistent tree. Writes results/_r687bma_d19_check.json.
"""
import json, subprocess, tempfile, shutil, hashlib, os, io, sys

OUT = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney\results\_r687bma_d19_check.json"
URLS = ["git@github.com:BigRain-11122/FluxGroup.git",
        "https://github.com/BigRain-11122/FluxGroup.git"]

def sha256(b):
    return hashlib.sha256(b).hexdigest()

def main():
    out = {}
    tmp = tempfile.mkdtemp(prefix="d19_r687_")
    try:
        cloned = False
        for url in URLS:
            r = subprocess.run(["git", "clone", "--depth", "1",
                                "--filter=blob:none", "--sparse", url, tmp],
                               capture_output=True, timeout=180)
            if r.returncode == 0:
                out["clone_url"] = url
                cloned = True
                break
            out.setdefault("clone_errors", []).append(
                url + " :: " + r.stderr.decode("utf-8", "replace")[-200:])
        if not cloned:
            out["error"] = "ALL CLONE URLS FAILED"
        else:
            sp = subprocess.run(["git", "-C", tmp, "sparse-checkout", "set",
                                 "--skip-checks", "docs/decisions.md",
                                 "docs/orders.md"], capture_output=True, timeout=60)
            out["sparse_rc"] = sp.returncode
            for name, path in (("decisions", "docs/decisions.md"),
                               ("group_orders", "docs/orders.md")):
                b = subprocess.run(["git", "-C", tmp, "show", "HEAD:" + path],
                                   capture_output=True, timeout=60)
                if b.returncode == 0:
                    out[name + "_sha256"] = sha256(b.stdout)
                    out[name + "_bytes"] = len(b.stdout)
                else:
                    out[name + "_error"] = b.stderr.decode("utf-8", "replace")[:200]
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    # state watermark keys for comparison
    sp2 = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney\state-bm-a.json"
    st = json.load(open(sp2, encoding="utf-8"))
    out["state_last_decisions_sha"] = st.get("last_decisions_sha")
    out["state_last_orders_sha"] = st.get("last_orders_sha")
    out["decisions_match"] = (out.get("decisions_sha256") ==
                              st.get("last_decisions_sha"))
    out["group_orders_match"] = (out.get("group_orders_sha256") ==
                                 st.get("last_orders_sha"))
    with io.open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print("WROTE", OUT)
    return 0

if __name__ == "__main__":
    sys.exit(main())
