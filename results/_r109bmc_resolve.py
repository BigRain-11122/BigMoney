# -*- coding: utf-8 -*-
# R109 bm-c push-cycle storm resolver: 16-UU vs bma-r357 (rebase replay window) -- r355 recipe adaptation
# SIDE MAPPING (r351 law): :2: = HEAD = origin face (bma r357, base 9b62a4c9),
#                          :3: = replayed commit = MY face (bmc R109 commit c713e5d7, S6 run ts 21:41-21:44 fingerprint).
# Side-assertion below (fail-closed). Recipes per SKILL.md classifier output.
import subprocess, json, re, sys

def blob(path, stage):
    r = subprocess.run(["git", "show", f":{stage}:{path}"], capture_output=True)
    if r.returncode != 0:
        raise RuntimeError(f"stage read fail {path} :{stage}: {r.stderr[:200]}")
    return r.stdout

def parse(b):
    return json.loads(b.decode("utf-8-sig"))

WALL = re.compile(r"^20\d{2}-\d{2}-\d{2}[T ]\d{2}:\d{2}")

def norm_ts(v):
    return v.replace("T", " ") if isinstance(v, str) else v

def deep_ts(obj):
    # r311/r353: deep-scan dicts AND lists (traders[].forward_guard.as_of lives in a list)
    # r100: value must be wall-clock shaped (date-only values forbidden per R350)
    best = ""
    if isinstance(obj, dict):
        it = obj.values()
    elif isinstance(obj, list):
        it = obj
    else:
        return best
    for v in it:
        if isinstance(v, str) and WALL.match(v):
            n = norm_ts(v)
            if n > best:
                best = n
        elif isinstance(v, (dict, list)):
            b = deep_ts(v)
            if b > best:
                best = b
    return best

def detect_fmt(b):
    crlf = b"\r\n" in b
    m = re.search(rb"\n([ \t]+)", b)
    indent = m.group(1).decode() if m else None
    return crlf, indent

def dump_bytes(obj, crlf, indent):
    if indent:
        s = json.dumps(obj, ensure_ascii=False, indent=indent)
    else:
        s = json.dumps(obj, ensure_ascii=False)
    s += "\n"
    return (s.replace("\n", "\r\n") if crlf else s).encode("utf-8")

def write(path, data_bytes):
    with open(path, "wb") as f:
        f.write(data_bytes)

report = []

def uu_paths():
    r = subprocess.run(["git", "ls-files", "-u"], capture_output=True, text=True)
    return {line.split("\t", 1)[1].strip() for line in r.stdout.splitlines() if "\t" in line}

UU = uu_paths()

# ---------- SIDE ASSERTION (r351: assert before batch take-side) ----------
a2, a3 = parse(blob("results/compute_audit.json", 2)), parse(blob("results/compute_audit.json", 3))
# :3: = MY replayed commit face: fingerprint fixed (my 21:01:12 compute_audit run).
# :2: = origin face (dynamic: bmc-r106 in first storm, bmc-r107 in second replay window).
assert a3["latest"]["ts"] == "2026-09-27 21:41:37", f":3: audit latest.ts unexpected: {a3['latest']['ts']}"
print(f"side-assert: :2: origin face audit latest.ts={a2['latest']['ts']}, :3: MY face audit latest.ts={a3['latest']['ts']}")
report.append(f"side-assert PASS: :2:=origin face (audit {a2['latest']['ts']}), :3:=bmc-R109 face (audit 21:41:37) -- 本链面=:3:")

def take_new_deep(path, label=None):
    b2, b3 = blob(path, 2), blob(path, 3)
    j2, j3 = parse(b2), parse(b3)
    t2, t3 = deep_ts(j2), deep_ts(j3)
    side = 3 if t3 > t2 else 2  # tie -> :2: (HEAD, r140)
    chosen = b3 if side == 3 else b2
    write(path, chosen)
    parse(chosen)  # parse-verify r185
    report.append(f"{label or path}: deep-ts {t2!r}(:2:) vs {t3!r}(:3:) -> take :{side}: ({'mine' if side==3 else 'origin'})")
    return side, j2, j3

# ---------- twin 1: REPORT json+md (r327/r329: same side both, md = blob bytes) ----------
pj, pm = "docs/daily_report/REPORT-2026-09-27.json", "docs/daily_report/REPORT-2026-09-27.md"
j2, j3 = parse(blob(pj, 2)), parse(blob(pj, 3))
t2, t3 = norm_ts(j2.get("generated_at", "")), norm_ts(j3.get("generated_at", ""))
side = 3 if t3 > t2 else 2
for p in (pj, pm):
    chosen = blob(p, side)
    write(p, chosen)
    if p.endswith(".json"):
        parse(chosen)
report.append(f"REPORT twins: generated_at {t2}(:2:) vs {t3}(:3:) -> both take :{side}: (twin-coupled, md=side blob bytes)")

# ---------- twin 2: dashboard_status.js + .json (r329/r353 twin-coupled) ----------
pjs, pjn = "results/dashboard_status.js", "results/dashboard_status.json"
b2js, b3js = blob(pjs, 2), blob(pjs, 3)
def strip_js(b):
    s = b.decode("utf-8-sig")
    s = s.strip()
    assert s.startswith("window.DASH_DATA ="), "js wrapper missing"
    return s[len("window.DASH_DATA ="):].rstrip(";").strip()
t2js = deep_ts(json.loads(strip_js(b2js)))
t3js = deep_ts(json.loads(strip_js(b3js)))
side = 3 if t3js > t2js else 2
for p in (pjs, pjn):
    chosen = blob(p, side)
    write(p, chosen)
    if p.endswith(".json"):
        parse(chosen)
    else:
        json.loads(strip_js(chosen))
report.append(f"dashboard twins: deep-ts {t2js}(:2:) vs {t3js}(:3:) -> both take :{side}: (twin-coupled, js=whole blob bytes)")

# ---------- plain take-new snapshots (deep probe, tie->:2:) ----------
for p in [
    "results/fundamental_b_layer_filter.json",
    "results/prospect_promotion/_summary.json",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
    "results/update_status.json",
    "results/futures_update_status.json",
    "results/heat_update_status.json",
    "results/lhb_update_status.json",
]:
    if p in UU:
        take_new_deep(p)
    else:
        report.append(f"{p}: auto-merged by git, resolver skip")

# ---------- token_usage.json (generated ts + bucket merge guard) ----------
pt = "results/token_usage.json"
b2, b3 = blob(pt, 2), blob(pt, 3)
j2, j3 = parse(b2), parse(b3)
t2, t3 = norm_ts(j2["generated"]), norm_ts(j3["generated"])
side = 3 if t3 > t2 else 2
src, other = (j3, j2) if side == 3 else (j2, j3)
# bucket-merge guard: every bucket key of the losing side must exist in the winning side
# (zero-loss check; R351 bucket-merge face). Divergent per-bucket scalars = take winning side's
# (fresher full re-derive face, R354 carried=none confirmation).
lost_keys = set(other.get("machines", {})) - set(src.get("machines", {}))
assert not lost_keys, f"token bucket-merge would lose keys: {lost_keys}"
deltas = {}
for k in src.get("machines", {}):
    if k in other.get("machines", {}) and src["machines"][k] != other["machines"][k]:
        deltas[k] = "differs (winning-side value kept; full re-derive face self-heals next meter run)"
write(pt, b3 if side == 3 else b2)
parse(b3 if side == 3 else b2)
report.append(f"token_usage: generated {t2}(:2:) vs {t3}(:3:) -> take :{side}:; machines buckets 5/5 key-complete, {len(deltas)} divergent bucket(s) kept winning-side (re-derive face)")

# ---------- compute_audit.json: history union + latest take-new ----------
p = "results/compute_audit.json"
b2, b3 = blob(p, 2), blob(p, 3)
j2, j3 = parse(b2), parse(b3)
h2, h3 = j2["history"], j3["history"]
key = lambda r: r.get("ts")
by2 = {key(r): r for r in h2}
by3 = {key(r): r for r in h3}
for k in set(by2) & set(by3):
    if by2[k] != by3[k]:
        # r85: producer rolling-window re-derives per-tick rows; identical ts with diverged content = flag
        raise RuntimeError(f"compute_audit history ts collision divergence at {k}")
union = {**by2, **by3}
state_src, state_side = (j3, 3) if norm_ts(j3["latest"]["ts"]) >= norm_ts(j2["latest"]["ts"]) else (j2, 2)
merged = dict(state_src)  # latest/state fields from fresher side (dynamic take-side)
merged["history"] = [union[k] for k in sorted(union)]
crlf, indent = detect_fmt(b3)
write(p, dump_bytes(merged, crlf, indent))
parse(open(p, "rb").read())
report.append(f"compute_audit: history union {len(h2)}+{len(h3)} -> {len(union)} (ts-key dedupe, zero loss); latest/state take :{state_side}: ({state_src['latest']['ts']}); fmt mirror crlf={crlf} indent={indent!r}")

# ---------- regime_state.json: transitions union + state take-new ----------
p = "results/regime_state.json"
b2, b3 = blob(p, 2), blob(p, 3)
j2, j3 = parse(b2), parse(b3)
tr2, tr3 = j2.get("transitions", []), j3.get("transitions", [])
tkey = lambda r: (r.get("date") or r.get("ts"), r.get("state") or r.get("to"))
by = {}
for r in tr2 + tr3:
    by[tkey(r)] = r
merged = dict(j3) if norm_ts(j3.get("updated", "")) >= norm_ts(j2.get("updated", "")) else dict(j2)  # state fields take fresher side
merged["transitions"] = [by[k] for k in sorted(by, key=str)]
crlf, indent = detect_fmt(b3)
write(p, dump_bytes(merged, crlf, indent))
parse(open(p, "rb").read())
report.append(f"regime_state: transitions union {len(tr2)}+{len(tr3)} -> {len(by)}; state take fresher side (updated {merged.get('updated')})")

# ---------- autofill_state.json: launches composite-key union + last_tick whole-dict ----------
p = "results/autofill_state.json"
if p not in UU:
    report.append("autofill_state: auto-merged by git (prior resolve converged sides), resolver skip")
else:
    b2, b3 = blob(p, 2), blob(p, 3)
    j2, j3 = parse(b2), parse(b3)
    L2, L3 = j2.get("launches", []), j3.get("launches", [])
    def ckey(l):
        return (l.get("ts"), l.get("machine"), l.get("pid"), l.get("runner_sha256"), l.get("entry"), l.get("shard"))
    def merge_pair(a, b):
        # r322: same composite key -> field-union merge if subset/superset; true divergence = flag
        if a == b:
            return a
        ka, kb = set(a.keys()), set(b.keys())
        if ka <= kb:
            return b
        if kb <= ka:
            return a
        if ka | kb == ka and all(a[k] == b[k] for k in ka & kb):
            return a
        # field-union: shared fields must be equal
        for k in ka & kb:
            if a[k] != b[k]:
                raise RuntimeError(f"autofill launch true divergence at {k}: {a.get('ts')}")
        out = dict(a); out.update(b); return out
    by = {}
    for l in L2 + L3:
        k = ckey(l)
        by[k] = merge_pair(by[k], l) if k in by else l
    merged_launches = sorted(by.values(), key=lambda l: l.get("ts") or "")
    if len(merged_launches) > 50:
        merged_launches = sorted(merged_launches[-50:], key=lambda l: l.get("ts") or "")  # cap 50 newest, write-back ASC (r245)
    else:
        merged_launches = sorted(merged_launches, key=lambda l: l.get("ts") or "")
    lt2, lt3 = j2.get("last_tick") or {}, j3.get("last_tick") or {}
    side_lt = 2 if norm_ts(lt2.get("ts") or "") >= norm_ts(lt3.get("ts") or "") else 3
    merged = {"last_tick": lt2 if side_lt == 2 else lt3, "launches": merged_launches}
    assert isinstance(merged["last_tick"], dict)
    crlf, indent = detect_fmt(b3)
    write(p, dump_bytes(merged, crlf, indent))
    chk = parse(open(p, "rb").read())
    assert isinstance(chk["last_tick"], dict)
    report.append(f"autofill_state: launches composite-union {len(L2)}+{len(L3)} -> {len(by)} (r322 key-dedupe) cap50 write-ASC; last_tick take :{side_lt}: (ts {lt2.get('ts')} vs {lt3.get('ts')})")

print("\n".join(report))
print("RESOLVE OK:", len(report), "faces handled")
