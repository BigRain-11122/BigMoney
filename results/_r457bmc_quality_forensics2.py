"""r457 bm-c QUALITY-claim forensics2: find LAST commit where QUALITY shard owner non-None.
Walk up to 80 pool-touching commits; print state transitions only."""
import json
import subprocess

CREATE_NO_WINDOW = 0x08000000
ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"


def git(args):
    r = subprocess.run(["git"] + args, capture_output=True, cwd=ROOT,
                       creationflags=CREATE_NO_WINDOW)
    return r.returncode, (r.stdout or b"").decode("utf-8", "replace"), \
        (r.stderr or b"").decode("utf-8", "replace")


def owner_state(rev):
    rc, blob, _ = git(["show", "%s:results/runnable_pool.json" % rev])
    if rc != 0:
        return None
    try:
        d = json.loads(blob)
    except ValueError:
        return "PARSE-FAIL"
    for e in d.get("entries", []):
        if e.get("id") == "FUND-QUALITY-P1-NULLS":
            sh = e.get("shards", [{}])[0]
            return "owner=%s since=%s shard_status=%s entry=%s" % (
                sh.get("owner"), sh.get("owner_since"),
                sh.get("status"), e.get("status"))
    return "ENTRY-MISSING"


def main():
    rc, out, _ = git(["log", "--format=%h|%ci|%s", "-80", "--follow",
                      "--", "results/runnable_pool.json"])
    lines = [l for l in out.strip().splitlines() if l.strip()]
    prev = None
    for l in lines:
        rev = l.split("|")[0]
        st = owner_state(rev)
        if st != prev:
            print("STATE-CHANGE %s | %s | %s" % (rev, l.split("|")[1], st))
            prev = st
    print("--- also check origin crash_fuse QUALITY sigs + autofill_state.bm-b launch ledger ---")
    rc, blob, _ = git(["show", "origin/main:results/autofill_state.bm-b.json"])
    if rc == 0:
        try:
            d = json.loads(blob)
            txt = json.dumps(d)
            print("autofill_state.bm-b keys:", list(d.keys())[:12])
            for kw in ("quality", "fund_quality", "QUALITY"):
                print("  contains '%s': %s" % (kw, kw.lower() in txt.lower()))
        except ValueError as e:
            print("autofill_state.bm-b parse fail", e)
    else:
        print("autofill_state.bm-b read fail")
    rc, blob, _ = git(["show", "origin/main:results/crash_fuse.json"])
    if rc == 0:
        try:
            d = json.loads(blob)
            for k in d:
                if "quality" in k.lower():
                    print("fuse sig:", k[:100])
        except ValueError as e:
            print("crash_fuse parse fail", e)


if __name__ == "__main__":
    main()
