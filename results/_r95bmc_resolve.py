import json, subprocess, sys

def side(rev, path):
    out = subprocess.run(["git", "show", f"{rev}{path}"], capture_output=True)
    if out.returncode != 0:
        return None
    return out.stdout.decode("utf-8-sig")

def put(path, data):
    with open(path, "w", encoding="utf-8", newline="") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)

uu = subprocess.run(["git", "diff", "--name-only", "--diff-filter=U"],
                    capture_output=True).stdout.decode().split()

report = {}
for path in uu:
    ours = side(":2:", path)
    theirs = side(":3:", path)
    if path.endswith((".md", ".js")):
        # raw-text payload: same-day regen faces -> origin side fresher (deterministic, next regen overwrites)
        with open(path, "w", encoding="utf-8", newline="") as f:
            f.write(theirs if theirs else ours)
        report[path] = f"raw-text take-{'theirs' if theirs else 'ours'}"
        continue
    o = json.loads(ours) if ours else None
    t = json.loads(theirs) if theirs else None
    if o is None and t is None:
        report[path] = "BOTH-EMPTY skip"
        continue

    def ts_of(d):
        if not isinstance(d, dict):
            return ""
        for k in ("ts", "generated", "generated_at", "updated_at", "last_run", "asof"):
            v = d.get(k)
            if isinstance(v, str) and v:
                return v
        return ""

    if path == "results/compute_audit.json":
        # rolling history ledger: ts+machine composite key union (r85/r89 law)
        hist = []
        seen = set()
        for src in (o, t):
            for row in (src or {}).get("history", []):
                key = (str(row.get("ts")), str(row.get("machine")))
                if key not in seen:
                    seen.add(key)
                    hist.append(row)
        hist.sort(key=lambda r: str(r.get("ts")))
        # keep trailing window same as producer (rolling ~201-233 rows observed); cap at max(len_o,len_t)+recent growth
        cap = max(len((o or {}).get("history", [])), len((t or {}).get("history", [])))
        # union may exceed cap; producers observed union growth is legitimate (new rounds appended)
        base = t if t is not None else o
        base["history"] = hist
        put(path, base)
        report[path] = f"union history {len(hist)} (o={len((o or {}).get('history',[]))} t={len((t or {}).get('history',[]))})"
        continue

    if path == "results/token_usage.json":
        # L2 legs rolling ledger: union by day+cmd identity keys; take-new envelope
        base = t if t is not None else o
        o_days = (o or {}).get("days", {})
        t_days = (t or {}).get("days", {})
        for dkey, o_rec in (o_days or {}).items():
            if dkey not in t_days:
                t_days[dkey] = o_rec
            else:
                # merge per-day records: keep max counts per cmd key
                trec = t_days[dkey]
                for k, v in (o_rec or {}).items():
                    if k not in trec or (isinstance(v, (int, float)) and isinstance(trec.get(k), (int, float)) and v > trec.get(k, 0)):
                        trec[k] = v
        if isinstance(base, dict) and base.get("days") is None:
            base["days"] = t_days
        else:
            base["days"] = t_days
        put(path, base)
        report[path] = "token_usage day-union"
        continue

    # snapshot mirrors: deterministic regen faces -> take fresher ts side, tie -> theirs
    ts_o, ts_t = ts_of(o), ts_of(t)
    winner = "theirs" if ts_t >= ts_o else "ours"
    data = t if winner == "theirs" else o
    # byte-preserving write for non-dict payloads (js twins handled below separately)
    if path.endswith(".js"):
        with open(path, "w", encoding="utf-8", newline="") as f:
            f.write(theirs if winner == "theirs" else ours)
    else:
        put(path, data)
    report[path] = f"take-{winner} (ts_o={ts_o} ts_t={ts_t})"

print(json.dumps(report, ensure_ascii=False, indent=1))
