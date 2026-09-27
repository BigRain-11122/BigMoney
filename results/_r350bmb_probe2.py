# -*- coding: utf-8 -*-
import subprocess, json

for path in ("results/compute_audit.json", "results/regime_state.json"):
    raw = subprocess.run(["git", "show", ":2:" + path], capture_output=True).stdout
    d = json.loads(raw.decode("utf-8-sig"))
    print(path, "| top keys:", list(d.keys()))
    for k, v in d.items():
        if isinstance(v, list):
            print("  list key:", k, "len:", len(v))
            if v and isinstance(v[0], dict):
                print("    row0 keys:", list(v[0])[:6])
        if isinstance(v, dict) and k == "latest":
            print("  latest ts:", v.get("ts"))
    raw3 = subprocess.run(["git", "show", ":3:" + path], capture_output=True).stdout
    d3 = json.loads(raw3.decode("utf-8-sig"))
    for k, v in d3.items():
        if isinstance(v, list):
            print("  [mine] list key:", k, "len:", len(v))
        if isinstance(v, dict) and k == "latest":
            print("  [mine] latest ts:", v.get("ts"))
