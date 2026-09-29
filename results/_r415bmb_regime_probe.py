import subprocess, json
for s, t in ((2, "origin"), (3, "bmb")):
    j = json.loads(subprocess.run(["git", "show", ":%d:results/regime_state.json" % s], capture_output=True).stdout)
    h = j["history"]; tr = j["transitions"]
    print(t, "hist", len(h), "entrykeys", sorted(h[0].keys()) if h else None)
    print(t, "trans", len(tr), "transkeys", sorted(tr[0].keys()) if tr and isinstance(tr[0], dict) else (type(tr[0]) if tr else None))
    print(t, "hist ts head/tail:", h[0].get("ts") or h[0].get("date"), "/", h[-1].get("ts") or h[-1].get("date"))
    if tr: print(t, "trans first:", json.dumps(tr[0])[:200])
