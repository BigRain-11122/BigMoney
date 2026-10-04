# D-19 decisions watermark probe (bm-b round 661)
# Law: r631 sparse-clone fallback (no K:/no local .git group tree), r660 subprocess original-bytes hash (no PS pipe, no disk-copy hash)
import json, subprocess, hashlib, os, sys, tempfile, shutil

REPO = "https://github.com/BigRain-11122/FluxGroup.git"
STATE = "state.json"

def main():
    s = json.load(open(STATE, encoding="utf-8"))
    last_sha = s.get("last_decisions_sha", "")
    tmp = tempfile.mkdtemp(prefix="fg-d19-r661-")
    try:
        # sparse clone: zero resident tree impact on any existing group checkout
        r = subprocess.run(["git", "clone", "--depth", "1", "--filter=blob:none",
                            "--sparse", REPO, tmp],
                           capture_output=True, timeout=120)
        if r.returncode != 0:
            print(json.dumps({"verdict": "CLONE_FAIL", "stderr": r.stderr.decode("utf-8", "replace")[-400:]}))
            return 2
        r = subprocess.run(["git", "-C", tmp, "sparse-checkout", "set", "--skip-checks",
                            "docs/decisions.md"], capture_output=True, timeout=60)
        if r.returncode != 0:
            print(json.dumps({"verdict": "SPARSE_FAIL", "stderr": r.stderr.decode("utf-8", "replace")[-400:]}))
            return 2
        # r660 law: git show origin bytes via subprocess capture (no disk-copy hash)
        r = subprocess.run(["git", "-C", tmp, "show", "origin/main:docs/decisions.md"],
                           capture_output=True, timeout=60)
        if r.returncode != 0:
            print(json.dumps({"verdict": "SHOW_FAIL", "stderr": r.stderr.decode("utf-8", "replace")[-400:]}))
            return 2
        content = r.stdout
        new_sha = hashlib.sha256(content).hexdigest().upper()
        changed = (new_sha != last_sha)
        out = {"verdict": "CHANGED" if changed else "MATCH",
               "last_sha": last_sha, "new_sha": new_sha,
               "bytes": len(content)}
        print(json.dumps(out))
        # also read orders.md CEO physical-items section (same-law per protocol step)
        r2 = subprocess.run(["git", "-C", tmp, "show", "origin/main:docs/orders.md"],
                            capture_output=True, timeout=60)
        if r2.returncode == 0:
            orders_txt = r2.stdout.decode("utf-8", "replace")
            # pit-encoding family: console GBK cannot print CJK/symbols -> write hits to file instead
            hits = [ln for ln in orders_txt.splitlines()
                    if ("BigMoney" in ln or "quant" in ln or "bm-b" in ln)]
            with open("results/_r661bmb_d19_orders_hits.json", "w", encoding="utf-8") as f:
                json.dump({"orders_doc_lines": len(orders_txt.splitlines()),
                          "relevant_hits": hits[-40:]}, f, ensure_ascii=False, indent=1)
            print(json.dumps({"orders_doc": "OK", "hits_file": "results/_r661bmb_d19_orders_hits.json", "hits_count": len(hits)}))
        else:
            print(json.dumps({"orders_doc": "READ_FAIL"}))
        return 0
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

if __name__ == "__main__":
    sys.exit(main())
