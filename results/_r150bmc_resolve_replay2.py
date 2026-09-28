# -*- coding: utf-8 -*-
"""r150 bm-c rebase-replay storm resolver v2 (second wave: bma r394 close
faces).  stage2=ours=69448ad3 (bma r394 close, fresher ~09:1x),
stage3=theirs=my round-150 commit (08:4x writes).
Laws: compute_audit history ts-key union (zero-loss); C-family derived
faces (dashboard_status.js/.json, scorecard_v1, strategy_scorecard) =
take ours (bma = r378 canonical host, fresher derive supersedes my
stale-takeover derive); status faces = take-new by ts (r109 law)."""
import io
import json
import subprocess


def side(path, n):
    r = subprocess.run(["git", "show", f":{n}:{path}"], capture_output=True)
    assert r.returncode == 0, f"stage {n} missing for {path}"
    return r.stdout.decode("utf-8")


def write(path, text):
    io.open(path, "w", encoding="utf-8", newline="\n").write(text)


TS_KEYS = ("ts", "asof", "updated_at", "updated", "generated",
           "generated_at")


def ts_of(obj):
    for k in TS_KEYS:
        if isinstance(obj, dict) and k in obj and obj[k]:
            return str(obj[k])
    return ""


# [1] compute_audit.json: history ts-key union
ca2 = json.loads(side("results/compute_audit.json", 2))
ca3 = json.loads(side("results/compute_audit.json", 3))
by = {}
for row in ca2.get("history", []) + ca3.get("history", []):
    k = row.get("ts")
    if k not in by or str(row) > str(by[k]):
        by[k] = row
res = dict(ca2)
res["history"] = [by[k] for k in sorted(by)]
write("results/compute_audit.json",
      json.dumps(res, ensure_ascii=False, indent=1) + "\n")
json.load(io.open("results/compute_audit.json", encoding="utf-8"))
print(f"[1] compute_audit union: "
      f"{len(ca2.get('history', []))}|{len(ca3.get('history', []))} -> "
      f"{len(res['history'])}")

# [2] C-family derived faces: ours (bma canonical host, fresher)
for f in ("results/dashboard_status.json", "results/dashboard_status.js",
          "results/scorecard_v1.json", "results/strategy_scorecard.json"):
    o = side(f, 2)
    if f.endswith(".json"):
        json.loads(o)                      # parse guard
    write(f, o)
    print(f"[2] {f}: ours (bma r378 host derive)")

# [3] status faces: take-new by ts
for f in ("results/fundamental_b_layer_filter.json",
          "results/futures_update_status.json",
          "results/lhb_update_status.json",
          "results/update_status.json",
          "results/regime_state.json",
          "results/token_usage.json"):
    o = json.loads(side(f, 2))
    t = json.loads(side(f, 3))
    pick = o if ts_of(o) >= ts_of(t) else t
    write(f, json.dumps(pick, ensure_ascii=False, indent=1) + "\n")
    json.load(io.open(f, encoding="utf-8"))
    print(f"[3] {f}: take-new ours={ts_of(o)[:19]!r} theirs={ts_of(t)[:19]!r}")

print("resolver v2 OK")
