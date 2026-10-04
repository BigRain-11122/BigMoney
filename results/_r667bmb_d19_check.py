# r667 bm-b D-19 group freshness check (decisions.md SHA-256 + orders.md SHA-1)
# Laws: r660 (subprocess raw-bytes git show, no PS pipe, no on-disk hash),
#       r631 (sparse clone fallback when K:/local group tree absent),
#       r458/r672 (per-key hash caliber by value length: 64-hex=SHA-256, 40-hex=SHA-1),
#       r446 (probe as file, output to file, no console CJK print)
import json
import hashlib
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

REPO = r"https://github.com/BigRain-11122/FluxGroup.git"
STATE = Path(r"C:\Fluxgroup\FluxGroup\quant\bigmoney\state.json")
OUT = Path(r"C:\Fluxgroup\FluxGroup\quant\bigmoney\results\_r667bmb_d19_check.json")

def main():
    st = json.loads(STATE.read_text(encoding="utf-8"))
    exp_dec = st.get("last_decisions_sha", "").strip().upper()
    exp_ord = st.get("last_orders_sha", "").strip().upper()
    result = {
        "probe": "r667bmb_d19_check",
        "ts": time.strftime("%Y-%m-%dT%H:%M:%S+08:00"),
        "exp_decisions_sha256": exp_dec,
        "exp_orders_sha1": exp_ord,
        "caliber": {"decisions": f"sha256 (len={len(exp_dec)})",
                    "orders": f"sha1 (len={len(exp_ord)})"},
    }
    tmp = Path(tempfile.mkdtemp(prefix="bmb-d19-r667-"))
    try:
        def git(*args, cwd=None):
            return subprocess.run(["git", *args], cwd=cwd or str(tmp),
                                  capture_output=True, timeout=300)
        c = git("clone", "--depth", "1", "--filter=blob:none", "--sparse", REPO, ".")
        if c.returncode != 0:
            result["status"] = "CLONE_FAIL"
            result["stderr"] = c.stderr.decode("utf-8", "replace")[-800:]
            OUT.write_text(json.dumps(result, ensure_ascii=True, indent=1), encoding="utf-8")
            print("CLONE_FAIL")
            return 1
        s = git("sparse-checkout", "set", "--skip-checks", "docs/decisions.md", "docs/orders.md")
        if s.returncode != 0:
            result["status"] = "SPARSE_FAIL"
            result["stderr"] = s.stderr.decode("utf-8", "replace")[-800:]
            OUT.write_text(json.dumps(result, ensure_ascii=True, indent=1), encoding="utf-8")
            print("SPARSE_FAIL")
            return 1
        # raw blob bytes via git show from object db (no working-tree translation)
        d = git("show", "origin/main:docs/decisions.md")
        o = git("show", "origin/main:docs/orders.md")
        if d.returncode != 0 or o.returncode != 0:
            result["status"] = "SHOW_FAIL"
            result["stderr"] = (d.stderr + b" | " + o.stderr).decode("utf-8", "replace")[-800:]
            OUT.write_text(json.dumps(result, ensure_ascii=True, indent=1), encoding="utf-8")
            print("SHOW_FAIL")
            return 1
        got_dec = hashlib.sha256(d.stdout).hexdigest().upper()
        got_ord = hashlib.sha1(o.stdout).hexdigest().upper()
        result["got_decisions_sha256"] = got_dec
        result["got_orders_sha1"] = got_ord
        result["decisions_match"] = (got_dec == exp_dec)
        result["orders_match"] = (got_ord == exp_ord)
        result["status"] = "OK"
        OUT.write_text(json.dumps(result, ensure_ascii=True, indent=1), encoding="utf-8")
        print("DECISIONS", "MATCH" if result["decisions_match"] else "CHANGED")
        print("ORDERS", "MATCH" if result["orders_match"] else "CHANGED")
        return 0
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

if __name__ == "__main__":
    sys.exit(main())
