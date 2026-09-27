# -*- coding: utf-8 -*-
"""r120 rebase-wave-2 resolver: my tick commit 96a8caee (stale sleeve claim)
replayed onto bm-a chain (sleeve done-flip r368 + P1 v2-0of1 claim).
- runnable_pool: verify identity-set parity :2 vs :3, then take ORIGIN side
  (bm-a done-flip is the true state; bm-c tick claim on a done shard is a
  stale-model artifact -- discarded with evidence).
- autofill_state: last_tick = max-ts side (r109 law); launches = identity
  union zero-loss (r344/r360)."""
import json, subprocess, os

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
os.chdir(ROOT)


def blob(stage, path):
    r = subprocess.run(["git", "show", ":%d:%s" % (stage, path)],
                       capture_output=True)
    assert r.returncode == 0, (path, stage, r.stderr[:200])
    return json.loads(r.stdout.decode("utf-8"))


# --- runnable_pool: identity parity check then origin side ---
ours = blob(2, "results/runnable_pool.json")
theirs = blob(3, "results/runnable_pool.json")
id_o = [e["id"] for e in ours["entries"]]
id_t = [e["id"] for e in theirs["entries"]]
print("pool ours=%d theirs=%d | same-id-set: %s" % (
    len(id_o), len(id_t), set(id_o) == set(id_t)))
assert set(id_o) == set(id_t), "identity drift -- manual review"
sleeve_o = [e for e in ours["entries"]
            if e["id"] == "DECISION-CHAIN-V2-SLEEVE-EXPORT"][0]
sleeve_t = [e for e in theirs["entries"]
            if e["id"] == "DECISION-CHAIN-V2-SLEEVE-EXPORT"][0]
print("origin sleeve status:", sleeve_o.get("status"),
      "| shards:", [(s.get("key"), s.get("status"), s.get("owner"))
                    for s in sleeve_o.get("shards", [])])
print("mine   sleeve status:", sleeve_t.get("status"),
      "| shards:", [(s.get("key"), s.get("status"), s.get("owner"))
                    for s in sleeve_t.get("shards", [])])
assert sleeve_o.get("status") == "done", "origin side not done-flipped?!"
subprocess.run(["git", "checkout", "--ours", "--", "results/runnable_pool.json"],
               check=True)
subprocess.run(["git", "add", "--", "results/runnable_pool.json"], check=True)
print("pool: origin side taken (bm-a done-flip + P1 v2 claim preserved)")

# --- autofill_state: max-ts last_tick + launches identity union ---
ao = blob(2, "results/autofill_state.json")
at = blob(3, "results/autofill_state.json")
ts_o = (ao.get("last_tick") or {}).get("ts")
ts_t = (at.get("last_tick") or {}).get("ts")
print("autofill last_tick ours=%s theirs=%s" % (ts_o, ts_t))
out = dict(ao) if (ts_o or "") >= (ts_t or "") else dict(at)
lo = ao.get("launches") or []
lt = at.get("launches") or []


def idf(L):
    return (L.get("ts"), L.get("machine"), L.get("entry"), L.get("shard"),
            L.get("pid"))


seen = {idf(L) for L in out.get("launches") or []}
added = 0
for L in (lo + lt):
    if idf(L) not in seen:
        out.setdefault("launches", []).append(L)
        seen.add(idf(L))
        added += 1
print("launches union: base=%d +%d new" % (len(out.get("launches") or []) - added,
                                           added))
raw = json.dumps(out, ensure_ascii=False, indent=1) + "\n"
json.loads(raw)
with open("results/autofill_state.json", "w", encoding="utf-8",
          newline="\n") as f:
    f.write(raw)
subprocess.run(["git", "add", "--", "results/autofill_state.json"], check=True)
print("autofill: last_tick=%s (max-ts law) + launches union written"
      % out["last_tick"].get("ts"))

# marker scan
for p in ("results/runnable_pool.json", "results/autofill_state.json"):
    txt = open(p, encoding="utf-8", errors="replace").read()
    assert "<<<" not in txt and ">>>" not in txt, p
print("marker-scan 2/2 clean")
