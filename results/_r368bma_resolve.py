# r368 bm-a rebase resolve: runnable_pool.json UU (rebase replay of tick self-commit
# 5dc8e159 onto dfa9d2ae). Class = pool-entry-done-union (r312 law): per-entry id
# union both sides, done absorbs, shard-level union, owner transient -> evidence
# gates authoritative. Zero-loss assertion + json.loads verify before write-back.
import json, subprocess

def blob(stage):
    return json.loads(subprocess.run(
        ["git", "show", f":{stage}:results/runnable_pool.json"],
        capture_output=True, check=True).stdout.decode("utf-8"))

ours = blob(2)    # dfa9d2ae (origin/main side)
theirs = blob(3)  # 5dc8e159 (bm-a tick self-commit side)

oe = {e["id"]: e for e in ours["entries"]}
te = {e["id"]: e for e in theirs["entries"]}

def union_shards(a, b):
    bd = next((s for s in b if s.get("status") == "done"), None)
    if bd is not None:
        return [dict(bd)]
    if b:
        return [dict(s) for s in b]
    return [dict(s) for s in a]

out_entries = []
for k in list(oe.keys()) + [k for k in te if k not in oe]:
    if k in oe and k in te:
        e = json.loads(json.dumps(oe[k]))  # ours base
        t = te[k]
        if t.get("status") == "done" or e.get("status") == "done":
            e["status"] = "done"
        e["shards"] = union_shards(e.get("shards", []), t.get("shards", []))
        for f in ("owner", "lane_owner", "entered_at"):
            if f in t and f not in e:
                e[f] = t[f]
    else:
        e = json.loads(json.dumps(oe.get(k) or te.get(k)))
    out_entries.append(e)

# zero-loss assertions: entry id union preserved
assert {e["id"] for e in out_entries} == set(oe) | set(te), "entry id union loss"
for e in out_entries:
    for s in e.get("shards", []):
        assert isinstance(s.get("status"), str) and s.get("status"), f"bad shard {s}"

# envelope: keep ours envelope (origin fresher bookkeeping), updated_at = later ts
env = json.loads(json.dumps(ours))
for f in ("version", "law_ref", "schema"):
    if f not in env and f in theirs:
        env[f] = theirs[f]
env["entries"] = out_entries
ua_o = ours.get("updated_at") or ""
ua_t = theirs.get("updated_at") or ""
env["updated_at"] = max(ua_o, ua_t)

json.dumps(env)  # parse-verify
with open("results/runnable_pool.json", "w", encoding="utf-8", newline="\n") as fh:
    json.dump(env, fh, ensure_ascii=False, indent=1)
    fh.write("\n")
print(f"union ok entries={len(out_entries)} ours={len(oe)} theirs={len(te)} updated_at={env['updated_at']}")
for k in sorted(set(te) - set(oe)):
    print("theirs-only entry:", k)
for k in sorted(set(oe) - set(te)):
    print("ours-only entry:", k)
for k in sorted(set(oe) & set(te)):
    so = {s.get('key'): s.get('status') for s in oe[k].get('shards', [])}
    st = {s.get('key'): s.get('status') for s in te[k].get('shards', [])}
    if so != st:
        print("shard-diff", k, "ours:", so, "theirs:", st)
    if oe[k].get('status') != te[k].get('status'):
        print("status-diff", k, "ours:", oe[k].get('status'), "theirs:", te[k].get('status'))
