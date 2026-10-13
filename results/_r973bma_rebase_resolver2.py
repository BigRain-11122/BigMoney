# r973 rebase conflict resolver round-2 (replay of 9ae7cdc3a): 4 UU faces
# canon: update_status=theirs(bm-a 05:50 freshest, verify by ts fields), compute_audit=union history+newer top,
#        token_usage=per-machine merge newer-wins, d19_check=newest ts wins
import json, re, sys

def split_sides(p):
    raw = open(p, encoding="utf-8-sig").read()
    if "<<<<<<<" not in raw:
        return None
    ours_raw = re.sub(r"<<<<<<< HEAD\n(.*?)\n=======\n(.*?)\n>>>>>>> [^\n]*\n?",
                      lambda m: m.group(1) + "\n", raw, flags=re.S)
    theirs_raw = re.sub(r"<<<<<<< HEAD\n(.*?)\n=======\n(.*?)\n>>>>>>> [^\n]*\n?",
                        lambda m: m.group(2) + "\n", raw, flags=re.S)
    return raw, ours_raw, theirs_raw

def find_ts_any(doc):
    # search common ts-ish keys at top level or one level deep
    for k in ("ts", "updated", "updated_at", "generated", "last_run", "asof"):
        if isinstance(doc, dict) and k in doc:
            return str(doc[k])
    return ""

# 1) update_status.json -- freshest wins (expect theirs=bm-a 05:50)
r = split_sides(r"results/update_status.json")
if r:
    _, o_raw, t_raw = r
    o = json.loads(o_raw); t = json.loads(t_raw)
    o_ts, t_ts = find_ts_any(o), find_ts_any(t)
    print("update_status: ours ts=", repr(o_ts), "theirs ts=", repr(t_ts))
    # also compare nested daily cutoff stamps
    def deep_ts(d):
        s = set()
        def walk(x, depth=0):
            if depth > 2: return
            if isinstance(x, dict):
                for k, v in x.items():
                    if k in ("ts", "updated", "cutoff", "generated") and isinstance(v, (str, int, float)):
                        s.add(f"{k}={v}")
                    walk(v, depth + 1)
        walk(d)
        return sorted(s)[:8]
    print(" ours stamps:", deep_ts(o))
    print(" theirs stamps:", deep_ts(t))
    pick_raw, pick = (t_raw, "THEIRS") if t_ts >= o_ts else (o_raw, "OURS")
    if not t_ts and not o_ts:
        pick_raw, pick = t_raw, "THEIRS(no-ts both, bm-a estate face)"
    open(r"results/update_status.json", "w", encoding="utf-8", newline="").write(pick_raw)
    json.loads(open(r"results/update_status.json", encoding="utf-8").read())
    print("update_status resolved:", pick)
else:
    print("update_status: clean")

# 2) compute_audit.json -- union history + newer top
r = split_sides(r"results/compute_audit.json")
if r:
    _, o_raw, t_raw = r
    A = json.loads(o_raw); B = json.loads(t_raw)
    base, other = (A, B) if str(A.get("ts", "")) >= str(B.get("ts", "")) else (B, A)
    def hist(doc):
        return doc.get("history") or []
    seen = set()
    for h in hist(base):
        seen.add((str(h.get("ts")), str(h.get("machine", h.get("machine_id", "")))))
    merged = list(hist(base)); added = 0
    for h in hist(other):
        k = (str(h.get("ts")), str(h.get("machine", h.get("machine_id", ""))))
        if k not in seen:
            seen.add(k); merged.append(h); added += 1
    base["history"] = merged
    print("compute_audit: top ts", base.get("ts"), "| history", len(hist(base)), "+", added, "=", len(merged))
    open(r"results/compute_audit.json", "w", encoding="utf-8", newline="").write(json.dumps(base, ensure_ascii=False, indent=1))
    json.loads(open(r"results/compute_audit.json", encoding="utf-8").read())
    print("compute_audit resolved: union+newer")
else:
    print("compute_audit: clean")

# 3) token_usage.json -- per-machine union newer-wins
r = split_sides(r"results/token_usage.json")
if r:
    _, o_raw, t_raw = r
    A = json.loads(o_raw); B = json.loads(t_raw)
    out = dict(A)
    for k, v in B.items():
        if k not in out:
            out[k] = v
        else:
            # per-key merge: if dict, newer ts wins; else keep ours if equal else take newer str
            if isinstance(v, dict) and isinstance(out[k], dict):
                tv = str(v.get("ts", v.get("updated", "")))
                tk = str(out[k].get("ts", out[k].get("updated", "")))
                if tv >= tk:
                    out[k] = v
            else:
                out[k] = out[k]  # scalar: keep ours (both machines write only own faces)
    print("token_usage keys:", sorted(out.keys())[:12])
    open(r"results/token_usage.json", "w", encoding="utf-8", newline="").write(json.dumps(out, ensure_ascii=False, indent=1))
    json.loads(open(r"results/token_usage.json", encoding="utf-8").read())
    print("token_usage resolved: per-machine union")
else:
    print("token_usage: clean")

# 4) _r686bmb_d19_check.json -- newest run wins
p4 = r"results/_r686bmb_d19_check.json"
r = split_sides(p4)
if r:
    _, o_raw, t_raw = r
    A = json.loads(o_raw); B = json.loads(t_raw)
    a_ts, b_ts = find_ts_any(A), find_ts_any(B)
    print("d19_check: ours ts=", repr(a_ts), "theirs ts=", repr(b_ts))
    pick_raw = o_raw if a_ts >= b_ts else t_raw
    open(p4, "w", encoding="utf-8", newline="").write(pick_raw)
    json.loads(open(p4, encoding="utf-8").read())
    print("d19_check resolved:", "OURS" if a_ts >= b_ts else "THEIRS")
else:
    print("d19_check: clean")
print("RESOLVER-2 DONE rc0")
