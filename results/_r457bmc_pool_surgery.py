"""r457 bm-c pool surgery: FUND-QUALITY-P1-NULLS owner row restore (r637-missed 3rd shard).
Laws: r509 raw-text anchored edit (no re-serialization), r629 comma hygiene,
r400 owner_since=restore action-time, r637 rightful-owner-restore precedent.
Gates: fresh local==origin identity, needle count==1, json.loads reparse,
trio post-state verify, git diff --numstat == +3/-1."""
import datetime
import hashlib
import json
import subprocess

CREATE_NO_WINDOW = 0x08000000
ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
POOL = ROOT + r"\results\runnable_pool.json"
POOL_REL = "results/runnable_pool.json"


def git_raw(args):
    r = subprocess.run(["git"] + args, capture_output=True, cwd=ROOT,
                       creationflags=CREATE_NO_WINDOW)
    return r.returncode, r.stdout or b"", (r.stderr or b"").decode("utf-8", "replace")


def main():
    # freshness: origin must equal local (surgery on stale base = replay-revert hazard)
    rc, blob, err = git_raw(["fetch", "origin"])
    rc, ob, _ = git_raw(["show", "origin/main:" + POOL_REL])
    with open(POOL, "rb") as fh:
        raw = fh.read()
    if raw != ob:
        print("ABORT: local != origin blob (stale base); re-sync first")
        return
    print("GATE1 identity OK (bytes=%d sha16=%s)" % (len(raw), hashlib.sha256(raw).hexdigest()[:16]))

    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    needle = b'keep-block note on crash_fuse"\r\n    }'
    prov = (
        " | rel-bm-c-r457 %s: owner row restored on shared face "
        "(r637 four-face surgery healed VALUE+DIVLOWVOL owner rows but missed 3rd "
        "shard QUALITY -- ownerless since off-caliber-era releases while canonical "
        "burn stayed alive; evidence: burner pid 57116 alive per MSG-0857/0925/2005 "
        "+ nulls row growth 504->510 between 08:47-09:00 bm-b pushes; bm-b daemon "
        "keepalive self-adopts per r288 owner==myid gate; bm-c host_gates fail = "
        "bm-c cannot claim this shard, surgery is observation-heal not self-claim); "
        "owner_since=restore action-time per r400" % now
    ).encode("utf-8")
    replacement = (
        b'keep-block note on crash_fuse' + prov + b'",\r\n'
        b'     "owner": "bm-b",\r\n'
        b'     "owner_since": "' + now.encode("ascii") + b'"\r\n'
        b'    }'
    )
    cnt = raw.count(needle)
    print("GATE2 needle count=%d (need 1)" % cnt)
    if cnt != 1:
        print("ABORT: needle not unique")
        return
    new = raw.replace(needle, replacement)
    # reparse gate
    try:
        d = json.loads(new.decode("utf-8"))
    except ValueError as e:
        print("ABORT: reparse fail %s" % e)
        return
    print("GATE3 reparse OK")
    # trio post-state + pre/post delta (VALUE/DIVLOWVOL must be untouched BY THIS SURGERY)
    def trio(blob_bytes):
        dd = json.loads(blob_bytes.decode("utf-8"))
        out = {}
        for e in dd.get("entries", []):
            if e.get("id", "").endswith("-NULLS") and e.get("id", "").startswith("FUND-"):
                sh = e.get("shards", [{}])[0]
                out[e["id"]] = (sh.get("owner"), sh.get("owner_since"))
        return out
    pre, post = trio(raw), trio(new)
    print("GATE4 trio pre->post:")
    for k in sorted(post):
        print("   %s %s -> %s" % (k, pre.get(k), post.get(k)))
    if post.get("FUND-QUALITY-P1-NULLS", (None,))[0] != "bm-b":
        print("ABORT: QUALITY not restored")
        return
    if post.get("FUND-VALUE-P1-NULLS") != pre.get("FUND-VALUE-P1-NULLS") \
            or post.get("FUND-DIVLOWVOL-P1-NULLS") != pre.get("FUND-DIVLOWVOL-P1-NULLS"):
        print("ABORT: VALUE/DIVLOWVOL face drifted vs pre-surgery base")
        return
    with open(POOL, "wb") as fh:
        fh.write(new)
    print("WROTE bytes=%d (delta %d)" % (len(new), len(new) - len(raw)))
    # numstat assertion
    rc, ns, _ = git_raw(["diff", "--numstat", "--", POOL_REL])
    print("GATE5 numstat: %s" % ns.strip())
    if ns.strip() != "3\t1\t" + POOL_REL:
        print("WARN: numstat mismatch expected 3/1 -- inspect before commit")
        return
    print("ALL GATES PASS")


if __name__ == "__main__":
    main()
