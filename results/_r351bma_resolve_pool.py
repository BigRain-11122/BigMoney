"""R351 bm-a fold-landing runnable_pool resolver (pool-entry-done-union).

Skill canon: per entry id union both sides; done-absorption (either side done -> done, shard
fields from done side = completing machine's record); same-state -> shard-level union; single-
side entry -> keep; pre-write done-absorption assert + json.loads (r312).
Usage: python results/_r351bma_resolve_pool.py <path>
"""
import json, subprocess, sys

def blob(rev, path):
    out = subprocess.run(["git", "show", f"{rev}:{path}"], capture_output=True)
    if out.returncode != 0:
        raise RuntimeError(f"git show {rev}:{path} rc={out.returncode}")
    return out.stdout

def merge_entry(a, b):
    # done absorption: done side wins for shard/status fields
    if a.get("status") == "done" and b.get("status") != "done":
        base = dict(b); base.update({k: v for k, v in a.items() if k in ("status", "result_ref", "done_at", "shards", "done_by") or k.endswith("_at") and k in a}); return base
    if b.get("status") == "done" and a.get("status") != "done":
        base = dict(a); base.update({k: v for k, v in b.items() if k in ("status", "result_ref", "done_at", "shards", "done_by")}); return base
    # same-state: shard-level union
    out = dict(a)
    sa, sb = a.get("shards"), b.get("shards")
    if isinstance(sa, list) and isinstance(sb, list):
        keyf = lambda s: s if isinstance(s, str) else json.dumps(s, sort_keys=True, ensure_ascii=False)
        pool = {}
        for s in sa + sb:
            pool[keyf(s)] = s
        out["shards"] = list(pool.values())
    for k, v in b.items():
        out.setdefault(k, v)
    return out

def main(path):
    ours_b = blob(":2", path)
    theirs_b = blob(":3", path)
    ours = json.loads(ours_b.decode("utf-8-sig"))
    theirs = json.loads(theirs_b.decode("utf-8-sig"))
    oE = {e["id"]: e for e in ours.get("entries", [])}
    tE = {e["id"]: e for e in theirs.get("entries", [])}
    merged = {}
    for eid in oE.keys() | tE.keys():
        if eid in oE and eid in tE:
            merged[eid] = merge_entry(oE[eid], tE[eid])
        else:
            merged[eid] = oE.get(eid) or tE[eid]
    entries = [merged[e] for e in oE] + [merged[e] for e in tE if e not in oE]  # ours order + theirs-only appended
    out = dict(ours)
    out["entries"] = entries
    for k, v in theirs.items():
        if k not in out and k != "entries":
            out[k] = v
    # updated_at: take newer
    if str(theirs.get("updated_at", "")) > str(ours.get("updated_at", "")):
        out["updated_at"] = theirs["updated_at"]

    # done-absorption assert (r312): no entry regressed from done
    for e in entries:
        was_done = (e["id"] in oE and oE[e["id"]].get("status") == "done") or (e["id"] in tE and tE[e["id"]].get("status") == "done")
        assert not (was_done and e.get("status") != "done"), f"done-regression on {e['id']}"

    crlf = b"\r\n" in ours_b
    text = json.dumps(out, ensure_ascii=False, indent=1)
    if crlf:
        text = text.replace("\n", "\r\n")
    if ours_b.endswith(b"\n"):
        text += "\r\n" if crlf else "\n"
    with open(path, "wb") as f:
        f.write(text.encode("utf-8"))
    json.loads(open(path, encoding="utf-8").read())
    print(json.dumps({"ours": len(oE), "theirs": len(tE), "union": len(entries)}, ensure_ascii=False))

if __name__ == "__main__":
    main(sys.argv[1])
