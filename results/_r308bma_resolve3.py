"""R308 bm-a resolver 3: results/runnable_pool.json UU (autofill tick replay
vs bm-b 1bbe7dff). Shard-level claim bookkeeping: same key/owner/status with
differing owner_since -> take the NEWER owner_since (owner machine's own
record of its claim refresh; both sides owner=bm-a). Entry census + id set
must be identical; zero-loss = entry count preserved, only the two
differing shard arrays replaced from theirs.
"""
import json
import subprocess
import sys

PATH = "results/runnable_pool.json"


def blob(st):
    return subprocess.run(["git", "show", st + PATH],
                           capture_output=True, check=True).stdout


def main():
    base_raw = blob(":2:")      # no :1: stage in this conflict; format mirror
    o = json.loads(base_raw.decode("utf-8-sig"))
    t = json.loads(blob(":3:").decode("utf-8-sig"))
    oe = {e["id"]: e for e in o["entries"]}
    te = {e["id"]: e for e in t["entries"]}
    assert set(oe) == set(te), "entry id census mismatch"
    assert len(o["entries"]) == len(t["entries"]), "entry count mismatch"

    merged_ids, replaced = [], []
    for eid in o["entries"]:
        e = dict(eid)
        a, b = oe[eid["id"]], te[eid["id"]]
        if a.get("shards") != b.get("shards"):
            ka = {s["key"]: s for s in a.get("shards", [])}
            kb = {s["key"]: s for s in b.get("shards", [])}
            assert set(ka) == set(kb), f"{eid['id']}: shard key set drift"
            new_shards = []
            for k in ka:
                sa, sb = ka[k], kb[k]
                if (sa.get("owner") == sb.get("owner")
                        and sa.get("status") == sb.get("status")
                        and sa.get("owner_since", "") < sb.get("owner_since",
                                                                "")):
                    sa = dict(sa)
                    sa["owner_since"] = sb["owner_since"]   # newer record
                new_shards.append(sa)
            e["shards"] = new_shards
            replaced.append(eid["id"])
        merged_ids.append(e)
    out = dict(o)
    out["entries"] = merged_ids

    nl = "\r\n" if b"\r\n" in base_raw[:2000] else "\n"
    indent = 1 if base_raw[:200].find(b'\n "') >= 0 else 2
    with open(PATH, "w", encoding="utf-8", newline="") as fh:
        fh.write(json.dumps(out, ensure_ascii=False, indent=indent) + nl)
    chk = json.load(open(PATH, encoding="utf-8-sig"))
    assert len(chk["entries"]) == len(o["entries"]), "entry count loss"
    print(f"r308 resolver3: {len(chk['entries'])} entries preserved; "
          f"shard owner_since newer-record merge on {replaced}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
