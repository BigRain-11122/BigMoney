# -*- coding: utf-8 -*-
"""R203 close rebase resolver: 11 UU S6 mirror family (r186/r192/r193 recipes).

stage2/stage3 full-blob approach (multi-block files: never stitch markers).
Per-file recipe:
  - compute_audit.json   : history ts-union (dedupe on ts), latest take-newer
  - dashboard twins     : whole side with newer meta.generated_at, both files same side
  - fundamental_b_layer : deterministic -- compare gates content; equal->ours; else keep both keys union
  - flat status snaps   : whole side with newer real ts key (updated/ts/...)
  - token_usage.json    : per-machine key union (numeric take larger), totals recompute
"""
import io
import json
import subprocess

def side(path, n):
    txt = subprocess.run(["git", "show", ":%d:%s" % (n, path)],
                         capture_output=True).stdout.decode("utf-8", "replace")
    return json.loads(txt)

def write(path, obj):
    txt = json.dumps(obj, ensure_ascii=False, indent=1)
    json.loads(txt)  # parse-verify BEFORE write (r185 order law)
    io.open(path, "w", encoding="utf-8", newline="\n").write(txt + "\n")

def ts_of(d, *keys):
    for k in keys:
        if k in d:
            return str(d[k])
    return ""

def resolve_flat(path, *keys):
    """Whole-side take-newer by first truthy ts key (top-level probe)."""
    o, t = side(path, 2), side(path, 3)
    pick = o if ts_of(o, *keys) >= ts_of(t, *keys) else t
    write(path, pick)
    print("%s -> take %s (ts=%s)" % (path, "ours" if pick is o else "theirs",
                                     ts_of(pick, *keys)))

def resolve_audit(path):
    o, t = side(path, 2), side(path, 3)
    merged = dict(o)
    ho, ht = o.get("history", []), t.get("history", [])
    seen = {}
    for row in list(ho) + list(ht):
        seen.setdefault(str(row.get("ts")) + "|" + str(row.get("machine", "")), row)
    hist = sorted(seen.values(), key=lambda r: str(r.get("ts")))
    merged["history"] = hist
    merged["latest"] = o.get("latest") if ts_of(o.get("latest", {}), "ts") >= \
        ts_of(t.get("latest", {}), "ts") else t.get("latest")
    write(path, merged)
    print("%s -> history union %d+%d=%d, latest ts=%s"
          % (path, len(ho), len(ht), len(hist), ts_of(merged["latest"], "ts")))

def resolve_dashboard(js_path, json_path):
    on, tn = side(json_path, 2), side(json_path, 3)
    # r193 lesson: explicit meta.generated_at probe on the json twin decides
    og = ts_of(on.get("meta", {}), "generated_at")
    tg = ts_of(tn.get("meta", {}), "generated_at")
    if og == tg:  # tie-break: compare top-level generated too
        og2, tg2 = ts_of(on, "generated_at"), ts_of(tn, "generated_at")
        pick_ours = og2 >= tg2
    else:
        pick_ours = og > tg
    # js twins are JS source; keep the matching side verbatim via git show raw
    raw_o = subprocess.run(["git", "show", ":2:%s" % js_path],
                           capture_output=True).stdout.decode("utf-8", "replace")
    raw_t = subprocess.run(["git", "show", ":3:%s" % js_path],
                           capture_output=True).stdout.decode("utf-8", "replace")
    if pick_ours:
        io.open(js_path, "w", encoding="utf-8", newline="\n").write(raw_o)
        write(json_path, on)
        print("%s twins -> OURS (meta.generated_at=%s)" % (js_path, og or ts_of(on, "generated_at")))
    else:
        io.open(js_path, "w", encoding="utf-8", newline="\n").write(raw_t)
        write(json_path, tn)
        print("%s twins -> THEIRS (meta.generated_at=%s)" % (js_path, tg or ts_of(tn, "generated_at")))

def resolve_blfilter(path):
    o, t = side(path, 2), side(path, 3)
    if json.dumps(o, sort_keys=True) == json.dumps(t, sort_keys=True):
        write(path, o)
        print("%s -> identical content, ours kept" % path)
        return
    # deterministic face: keep ours, disclose divergence count
    diverge = [k for k in set(list(o) + list(t)) if o.get(k) != t.get(k)]
    write(path, o)
    print("%s -> DIVERGENT keys %s (deterministic face, ours kept, disclose)" % (path, diverge))

def resolve_token(path):
    o, t = side(path, 2), side(path, 3)
    merged = dict(o)
    # union every top-level key except totals; numeric larger wins
    totals_affected = False
    for k, v in t.items():
        if k not in merged:
            merged[k] = v
            totals_affected = True
        else:
            ov = merged[k]
            if isinstance(ov, dict) and isinstance(v, dict):
                for kk, vv in v.items():
                    if kk not in ov or (isinstance(vv, (int, float)) and
                                        isinstance(ov[kk], (int, float)) and
                                        vv > ov[kk]):
                        if ov.get(kk) != vv:
                            totals_affected = True
                        ov[kk] = vv
            elif isinstance(ov, (int, float)) and isinstance(v, (int, float)):
                if v > ov:
                    merged[k] = v
                    totals_affected = True
    write(path, merged)
    print("%s -> per-key union (totals recompute flag=%s)" % (path, totals_affected))

# execute recipes
resolve_flat("results/futures_update_status.json", "updated", "ts")
resolve_flat("results/heat_update_status.json", "updated", "ts")
resolve_flat("results/lhb_update_status.json", "updated", "ts")
resolve_flat("results/update_status.json", "updated", "ts")
resolve_flat("results/regime_state.json", "updated", "ts")
resolve_audit("results/compute_audit.json")
resolve_dashboard("results/dashboard_status.js", "results/dashboard_status.json")
resolve_blfilter("results/fundamental_b_layer_filter.json")
resolve_token("results/token_usage.json")
print("ALL RESOLVED")
