"""r457 bm-c QUALITY forensics3: lane mirror claims + full trio state at two revs."""
import json
import subprocess

CREATE_NO_WINDOW = 0x08000000
ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"


def git_raw(args):
    r = subprocess.run(["git"] + args, capture_output=True, cwd=ROOT,
                       creationflags=CREATE_NO_WINDOW)
    return r.returncode, r.stdout or b"", (r.stderr or b"").decode("utf-8", "replace")


def trio_state(blob):
    try:
        d = json.loads(blob.decode("utf-8-sig"))
    except ValueError as e:
        return {"parse_fail": str(e)}
    out = {}
    for e in d.get("entries", []):
        if e.get("id", "").startswith("FUND-") and e.get("id", "").endswith("-NULLS"):
            sh = e.get("shards", [{}])[0]
            out[e["id"]] = {"owner": sh.get("owner"), "since": sh.get("owner_since"),
                            "shard": sh.get("status"), "entry": e.get("status")}
    return out


def main():
    for rev in ("f10dc1ffd", "8b24a0dd0"):
        rc, blob, _ = git_raw(["show", "%s:results/runnable_pool.json" % rev])
        print("== shared face @%s ==" % rev)
        print(json.dumps(trio_state(blob), ensure_ascii=False, indent=1))
    rc, blob, _ = git_raw(["show", "origin/main:results/runnable_pool.bm-b.json"])
    if rc == 0:
        print("== bm-b LANE mirror @origin ==")
        print(json.dumps(trio_state(blob), ensure_ascii=False, indent=1))
    else:
        print("lane mirror read fail:", _[:120])
    # QUALITY SENS entry too (separate family ticket)
    rc, blob, _ = git_raw(["show", "origin/main:results/runnable_pool.json"])
    d = json.loads(blob.decode("utf-8-sig"))
    print("== all FUND-* entries on origin shared face ==")
    for e in d.get("entries", []):
        if e.get("id", "").startswith("FUND-"):
            sh = e.get("shards", [{}])[0] if e.get("shards") else {}
            print("%s entry=%s shard=%s owner=%s since=%s" % (
                e.get("id"), e.get("status"), sh.get("status"),
                sh.get("owner"), sh.get("owner_since")))


if __name__ == "__main__":
    main()
