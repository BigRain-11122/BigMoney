"""r457 bm-c QUALITY-claim forensics: when did FUND-QUALITY-P1-NULLS owner row vanish?
Walk origin log for runnable_pool.json, extract QUALITY shard owner state per commit
(binary search over last ~20 touching commits)."""
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
    rc, out, _ = git(["log", "--format=%h %ci %s", "-25", "--follow",
                      "--", "results/runnable_pool.json"])
    lines = [l for l in out.strip().splitlines() if l.strip()]
    print("pool-touching commits (last 25):")
    for l in lines:
        print(" ", l[:150])
    print("--- QUALITY shard state per commit (newest 25) ---")
    for l in lines:
        rev = l.split()[0]
        st = owner_state(rev)
        print("%s | %s" % (rev, st))
        if st and str(st).startswith("owner=None"):
            # found first commit where owner vanished
            print(">>> FIRST owner=None at %s: %s" % (rev, l[:150]))
            break


if __name__ == "__main__":
    main()
