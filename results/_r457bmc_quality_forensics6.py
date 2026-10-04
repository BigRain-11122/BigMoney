"""r457 bm-c QUALITY forensics6: bm-b autofill launch ledger tail (in-flight trio) +
bm-c host_gates check (p1c_stock presence) + bm-a autofill posture on origin."""
import glob
import json
import subprocess

CREATE_NO_WINDOW = 0x08000000
ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
FLEET_ROOT = r"K:\Fluxgroup"


def git_raw(args):
    r = subprocess.run(["git"] + args, capture_output=True, cwd=ROOT,
                       creationflags=CREATE_NO_WINDOW)
    return r.returncode, r.stdout or b"", (r.stderr or b"").decode("utf-8", "replace")


def main():
    rc, blob, _ = git_raw(["show", "origin/main:results/autofill_state.bm-b.json"])
    if rc == 0:
        d = json.loads(blob.decode("utf-8-sig"))
        launches = d.get("launches", [])
        print("== bm-b autofill launches TAIL-15 (of %s) ==" % len(launches))
        for v in launches[-15:]:
            print("  ", json.dumps(v, ensure_ascii=False)[:260])
    rc, blob, _ = git_raw(["show", "origin/main:results/autofill_state.bm-a.json"])
    if rc == 0:
        d = json.loads(blob.decode("utf-8-sig"))
        print("== bm-a autofill last_tick ==")
        print("  ", json.dumps(d.get("last_tick", {}), ensure_ascii=False)[:300])
        launches = d.get("launches", [])
        print("== bm-a launches TAIL-5 (of %s) ==" % len(launches))
        for v in launches[-5:]:
            print("  ", json.dumps(v, ensure_ascii=False)[:240])
    print("== bm-c host_gates: p1c_stock presence ==")
    for base in (FLEET_ROOT, ROOT):
        p = base + "\\Money02\\data\\cache\\p1c_stock"
        n = len(glob.glob(p + "\\*.npy"))
        print("  %s -> *.npy count %d" % (p, n))
    # fund_history presence (T-152 source was bm-c)
    for base in (FLEET_ROOT, ROOT):
        for cand in ("Money02\\t18_fund_history", "Money02\\data\\fund_history"):
            p = base + "\\" + cand
            n = len(glob.glob(p + "\\*"))
            print("  %s -> files %d" % (p, n))


if __name__ == "__main__":
    main()
