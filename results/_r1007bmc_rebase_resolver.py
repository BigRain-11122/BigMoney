# r1007 rebase conflict resolver: shared regenerable faces (r991 family union law)
# token_usage: per-machine sub-key union; compute_audit: history union-by-ts + newer scalars;
# small dicts: newer-wins by ts; daily_report pair: newer side wins both faces consistently
import json, io, os, sys

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"

def load(p):
    return json.load(io.open(os.path.join(ROOT, p), encoding="utf-8"))

def dump(p, obj):
    io.open(os.path.join(ROOT, p), "w", encoding="utf-8", newline="").write(
        json.dumps(obj, ensure_ascii=False, indent=1))

def ts_of(d, keys=("ts", "generated", "generated_at", "updated", "now", "epoch")):
    for k in keys:
        v = d.get(k)
        if v is not None:
            return str(v)
    return ""

report = []

# 1) token_usage.json -- per-machine sub-key union, scalars newer-wins
p = "results/token_usage.json"
def stage_fp(i, fp):
    out = os.popen('cd /d "%s" && "C:\\Program Files\\Git\\cmd\\git.exe" show :%d:"%s"' % (ROOT, i, fp)).read()
    return json.loads(out)

def stage2(fp):
    return stage_fp(2, fp)

def stage3(fp):
    return stage_fp(3, fp)

p = "results/token_usage.json"
try:
    ours, theirs = stage2(p), stage3(p)
    merged = dict(theirs)
    om, tm = ours.get("machines", {}), theirs.get("machines", {})
    for mid, mv in om.items():
        if mid not in tm or str(mv.get("ts", "")) >= str(tm.get(mid, {}).get("ts", "")):
            merged.setdefault("machines", {})[mid] = mv
    for k, v in ours.items():
        if k != "machines" and (k not in merged or str(v) >= str(merged.get(k, ""))):
            merged[k] = v
    dump(p, merged)
    report.append((p, "machines-union newer-wins", "ok"))
except Exception as e:
    report.append((p, "FALLBACK theirs", repr(e)[:80]))
    dump(p, d if "<<<<<<<" not in json.dumps(d) else {})

# 2) compute_audit.json -- history union-by-ts + newer scalars
p = "results/compute_audit.json"
try:
    ours, theirs = stage2(p), stage3(p)
    merged = dict(theirs)
    oh, th = ours.get("history", []), theirs.get("history", [])
    seen = {str(r.get("ts")) for r in th}
    for r in oh:
        if str(r.get("ts")) not in seen:
            merged.setdefault("history", []).append(r)
    merged["history"].sort(key=lambda r: str(r.get("ts")))
    if str(ours.get("ts", "")) >= str(theirs.get("ts", "")):
        for k, v in ours.items():
            if k != "history":
                merged[k] = v
    dump(p, merged)
    report.append((p, "history-union-by-ts", "ok"))
except Exception as e:
    report.append((p, "FALLBACK theirs", repr(e)[:80]))

# 3) small ts-dicts: newer-wins
for p in ("results/regime_state.json", "results/update_status.json",
          "results/_attrition_guard_scan.json", "results/_r686bmb_d19_check.json"):
    try:
        ours, theirs = stage2(p), stage3(p)
        win = ours if str(ts_of(ours)) >= str(ts_of(theirs)) else theirs
        dump(p, win)
        report.append((p, "newer-wins " + ("ours" if win is ours else "theirs"), ts_of(win)[:19]))
    except Exception as e:
        report.append((p, "FALLBACK theirs", repr(e)[:80]))

# 4) daily_report pair: JSON decides (newer generated ts), md follows JSON side
pj = "docs/daily_report/REPORT-2026-10-14.json"
pm = "docs/daily_report/REPORT-2026-10-14.md"
try:
    ours, theirs = stage2(pj), stage3(pj)
    ours_newer = str(ts_of(ours)) >= str(ts_of(theirs))
    dump(pj, ours if ours_newer else theirs)
    side = 2 if ours_newer else 3
    md = os.popen('cd /d "%s" && git show :%d:"%s"' % (ROOT, side, pm)).read()
    io.open(os.path.join(ROOT, pm), "w", encoding="utf-8", newline="").write(md)
    report.append((pj, "newer-wins side%d" % side, ts_of(ours if ours_newer else theirs)[:19]))
except Exception as e:
    report.append((pj, "FALLBACK theirs", repr(e)[:80]))

for r in report:
    print(r)
