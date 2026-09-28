import subprocess, json

def stage(n):
    r = subprocess.run(["git", "show", f":{n}:results/runnable_pool.json"],
                       capture_output=True)
    return json.loads(r.stdout.decode("utf-8"))

for n, label in ((2, "ours(=origin/main during rebase)"), (3, "theirs(=my replay)")):
    try:
        d = stage(n)
        e = {x["id"]: x for x in d["entries"]}
        j = e.get("TRIAL-LABOR-W6-JUDGE", {})
        print(f"stage{n} [{label}]: n={len(d['entries'])} updated_at={d.get('updated_at')} "
              f"W6JUDGE_owner={j.get('shards', [{}])[0].get('owner')} "
              f"V3={e.get('DECISION-CHAIN-V3-TOURNAMENT', {}).get('status')} "
              f"W6S={e.get('TRIAL-LABOR-W6-SCREEN', {}).get('status')}")
    except Exception as ex:
        print(f"stage{n}: ERR {ex}")
