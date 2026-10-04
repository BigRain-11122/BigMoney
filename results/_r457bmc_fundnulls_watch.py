"""r457 bm-c FUND-NULLS watch: origin pool truth (r489/r513 law) + nulls burn progress
(3 families, target K=2000 each) + local vs origin claim face."""
import json
import os
import subprocess

CREATE_NO_WINDOW = 0x08000000
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FAMS = {
    "VALUE": "results/fund_value_p1/nulls.jsonl",
    "QUALITY": "results/fund_quality_p1/nulls.jsonl",
    "DIVLOWVOL": "results/fund_divlowvol_p1/nulls.jsonl",
}


def git_raw(args):
    r = subprocess.run(["git"] + args, capture_output=True, cwd=ROOT,
                       creationflags=CREATE_NO_WINDOW)
    return r.returncode, r.stdout or b"", (r.stderr or b"").decode("utf-8", "replace")


def shard_state(blob):
    """Extract the three FUND NULLS shard blocks from pool json text."""
    out = {}
    try:
        d = json.loads(blob.decode("utf-8-sig"))
    except Exception as e:
        return {"parse_error": str(e)}
    for e in d.get("entries", []):
        if e.get("id", "").startswith("FUND-") and e.get("id", "").endswith("-NULLS"):
            sh = e.get("shards", [{}])[0]
            out[e["id"]] = {"entry_status": e.get("status"),
                            "shard_status": sh.get("status"),
                            "owner": sh.get("owner"),
                            "owner_since": sh.get("owner_since"),
                            "checkpoint": sh.get("checkpoint")}
    return out


def main():
    print("== LOCAL nulls progress ==")
    for fam, rel in FAMS.items():
        p = os.path.join(ROOT, rel.replace("/", os.sep))
        if not os.path.exists(p):
            print("%s: FILE-MISSING" % fam)
            continue
        ks = set()
        with open(p, encoding="utf-8", errors="replace") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    j = json.loads(line)
                    k = j.get("k", j.get("key"))
                    if k is not None:
                        ks.add(k)
                except ValueError:
                    pass
        print("%s: unique_k=%d / 2000" % (fam, len(ks)))
    print("== ORIGIN pool truth ==")
    rc, blob, err = git_raw(["show", "origin/main:results/runnable_pool.json"])
    if rc != 0:
        print("origin pool read FAIL %s" % err[:160])
        return
    st = shard_state(blob)
    print(json.dumps(st, ensure_ascii=False, indent=1))
    print("== LOCAL pool truth ==")
    with open(os.path.join(ROOT, "results", "runnable_pool.json"), encoding="utf-8-sig") as fh:
        st2 = shard_state(fh.read().encode("utf-8"))
    print(json.dumps(st2, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
