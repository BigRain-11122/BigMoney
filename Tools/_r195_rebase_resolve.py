"""R195 push-retry rebase resolver: S6 mirror family conflicts (r185/r186/r188/r201 recipes).

Per-file rules (all via git index stages :2=ours[origin/bm-b side] :3=theirs[replayed r195 side]):
- CODELY.md            text union (both machines' new lines, order: ours-unique + theirs-unique)
- autofill_state.json   r188 union: launches list union-dedupe by record ts (tail 50), last_tick/ts newer
- compute_audit.json    r185: history ts-union + latest-run fields newer-wins
- token_usage.json      R193: per-key union, cumulative counters max
- everything else (whole-file rewrites): newer real-time key wins (ts / meta.generated_at);
  parse-fail side discarded honestly; missing ts -> theirs (newer commit side)
"""
import io, json, subprocess, sys

def stage(idx, path):
    out = subprocess.run(["git", "show", f":{idx}:{path}"], capture_output=True)
    if out.returncode != 0:
        return None
    return out.stdout.decode("utf-8", errors="replace")

def jload(txt):
    try:
        return json.loads(txt)
    except Exception:
        return None

def find_ts(obj):
    if isinstance(obj, dict):
        for k in ("ts", "updated_at", "generated_at"):
            v = obj.get(k)
            if isinstance(v, str) and len(v) >= 10:
                return v
        meta = obj.get("meta")
        if isinstance(meta, dict):
            v = meta.get("generated_at") or meta.get("ts")
            if isinstance(v, str):
                return v
    return None

def whole_file_newer(path):
    ours, theirs = stage(2, path), stage(3, path)
    if ours is None:
        return theirs
    if theirs is None:
        return ours
    jo, jt = jload(ours), jload(theirs)
    if jo is None and jt is None:
        return theirs
    if jo is None:
        return theirs
    if jt is None:
        return ours
    to, tt = find_ts(jo), find_ts(jt)
    if to and tt:
        return theirs if tt >= to else ours
    return theirs  # newer commit side wins when ts keys absent

def write(path, text):
    with io.open(path, "w", encoding="utf-8", newline="") as f:
        f.write(text)

def resolve_codely():
    ours, theirs = stage(2, "CODELY.md"), stage(3, "CODELY.md")
    o_lines = ours.splitlines()
    t_lines = theirs.splitlines()
    o_set = set(o_lines)
    uniq_t = [l for l in t_lines if l not in o_set]
    out = ours.rstrip("\n")
    if uniq_t:
        out += "\n" + "\n".join(uniq_t)
    out += "\n"
    write("CODELY.md", out)
    return f"CODELY.md union: +{len(uniq_t)} theirs-unique lines"

def resolve_autofill():
    ours, theirs = stage(2, "results/autofill_state.json"), stage(3, "results/autofill_state.json")
    jo, jt = jload(ours), jload(theirs)
    if jo is None or jt is None:
        write("results/autofill_state.json", ours if jo else theirs)
        return "autofill: one side unparseable -> parseable side"
    base = dict(jt)  # start from newer commit side
    ol, tl = jo.get("launches") or [], jt.get("launches") or []
    union = {}
    for rec in ol + tl:
        key = json.dumps(rec, sort_keys=True, ensure_ascii=False)
        union[key] = rec
    merged = sorted(union.values(),
                    key=lambda r: str(r.get("ts") or r.get("launched_at") or ""))
    base["launches"] = merged[-50:]  # rolling window cap (r188 design)
    for k in ("last_tick", "ts"):
        ov, tv = jo.get(k), jt.get(k)
        if isinstance(ov, dict) and isinstance(tv, dict):
            base[k] = tv if str(tv.get("ts", "")) >= str(ov.get("ts", "")) else ov
        elif tv is not None:
            base[k] = tv
    write("results/autofill_state.json",
          json.dumps(base, ensure_ascii=False, indent=1))
    return f"autofill union: launches {len(ol)}+{len(tl)} -> {len(base['launches'])}"

def resolve_compute_audit():
    path = "results/compute_audit.json"
    ours, theirs = stage(2, path), stage(3, path)
    jo, jt = jload(ours), jload(theirs)
    if jo is None or jt is None:
        write(path, ours if jo else theirs)
        return "compute_audit: parseable-side"
    base = dict(jt)
    ho, ht = jo.get("history") or [], jt.get("history") or []
    seen, union = set(), []
    for rec in ho + ht:
        key = json.dumps(rec, sort_keys=True, ensure_ascii=False)
        if key not in seen:
            seen.add(key)
            union.append(rec)
    union.sort(key=lambda r: str(r.get("ts") or ""))
    base["history"] = union
    write(path, json.dumps(base, ensure_ascii=False, indent=1))
    return f"compute_audit: history union {len(ho)}+{len(ht)} -> {len(union)}"

def resolve_token():
    path = "results/token_usage.json"
    ours, theirs = stage(2, path), stage(3, path)
    jo, jt = jload(ours), jload(theirs)
    if jo is None or jt is None:
        write(path, ours if jo else theirs)
        return "token: parseable-side"
    base = dict(jo)
    for k, v in jt.items():
        ov = base.get(k)
        if isinstance(ov, dict) and isinstance(v, dict):
            merged = dict(ov)
            merged.update(v)
            base[k] = merged
        elif isinstance(ov, (int, float)) and isinstance(v, (int, float)):
            base[k] = max(ov, v)
        else:
            base[k] = v
    write(path, json.dumps(base, ensure_ascii=False, indent=1))
    return "token: per-key union, counters max"

WholeFile = [
    "results/dashboard_status.js", "results/dashboard_status.json",
    "results/fundamental_b_layer_filter.json", "results/futures_update_status.json",
    "results/heat_update_status.json", "results/lhb_update_status.json",
    "results/regime_state.json", "results/update_status.json",
]

notes = [resolve_codely(), resolve_autofill(), resolve_compute_audit(), resolve_token()]
for p in WholeFile:
    write(p, whole_file_newer(p))
    notes.append(f"{p}: whole-file newer-side")
for n in notes:
    print(n)
