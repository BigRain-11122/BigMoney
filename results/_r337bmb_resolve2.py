# r337 bm-b resolver-2: 15-face same-window S6 double-run collision at big-commit replay.
# Sides: :2 = ours = upstream (new base), :3 = theirs = my replayed r337 commit. Dynamic probe, no assumption.
# Laws: r185 parse-verify pre-add / r140 tie->HEAD / r311+D-09 deep-scan ts probe / r334 future-sentinel+
# known-producer-path priority / r333 daily_report json-md twin coupling / r188+R208 ledger union zero-loss.
import json, subprocess, sys, re, datetime

NOW = datetime.datetime.now()
TS_KEYS = ("generated", "ts", "updated_at", "asof", "checked_at", "last_run", "updated", "date", "run_ts")

def blob(spec):
    o = subprocess.run(["git", "show", spec], capture_output=True)
    if o.returncode != 0:
        raise SystemExit("BLOB-FAIL " + spec)
    return o.stdout

def norm_ts(s):
    # 19th-batch law: normalize T vs space separator before compare
    s = str(s)
    if len(s) >= 11 and s[10] == "T":
        s = s[:10] + " " + s[11:]
    return s

def deep_ts(obj, acc=None):
    acc = [] if acc is None else acc
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, str) and k in TS_KEYS:
                acc.append(norm_ts(v))
            else:
                deep_ts(v, acc)
    elif isinstance(obj, list):
        for it in obj:
            deep_ts(it, acc)
    return acc

def future_ok(s):
    # future sentinel: ts beyond now+2d = poisoned, ignore (r334)
    try:
        return datetime.datetime.strptime(s[:19], "%Y-%m-%d %H:%M:%S") <= NOW + datetime.timedelta(days=2)
    except Exception:
        return False

def pick_ts(a, b, path):
    ta = [t for t in deep_ts(a) if future_ok(t)]
    tb = [t for t in deep_ts(b) if future_ok(t)]
    ma = max(ta) if ta else ""
    mb = max(tb) if tb else ""
    if mb > ma: return "theirs", ma, mb
    if ma > mb: return "ours", ma, mb
    return "ours(tie)", ma, mb  # r140 tie -> HEAD (ours)

def key(e):
    return json.dumps(e, ensure_ascii=False, sort_keys=True)

def mirror_write(path, data_obj, ref_bytes):
    crlf = b"\r\n" in ref_bytes
    second = ref_bytes.split(b"\n", 2)[1] if b"\n" in ref_bytes else b""
    indent = 0
    for ch in second:
        if ch == 0x20: indent += 1
        else: break
    trail = ref_bytes.endswith(b"\n")
    text = json.dumps(data_obj, ensure_ascii=False, indent=indent or 1)
    if trail: text += "\n"
    if crlf: text = text.replace("\n", "\r\n")
    open(path, "wb").write(text.encode("utf-8"))
    return ("crlf=%s indent=%d trail=%s" % (crlf, indent, trail))

report = []

def resolve_snapshot(path):
    ob, tb_ = blob(":2:" + path), blob(":3:" + path)
    a, b = json.loads(ob), json.loads(tb_)
    side, ma, mb = pick_ts(a, b, path)
    src = b if side == "theirs" else a
    fmt = mirror_write(path, src, ob)
    json.load(open(path, encoding="utf-8"))  # r185
    report.append("%s -> snapshot take-%s (ours_max=%s theirs_max=%s) %s" % (path, side, ma, mb, fmt))

def resolve_ledger(path, ledger_keys):
    ob, tb_ = blob(":2:" + path), blob(":3:" + path)
    a, b = json.loads(ob), json.loads(tb_)
    out = dict(a)
    for lk in ledger_keys:
        la, lb = a.get(lk, []), b.get(lk, [])
        merged = {}
        for e in la + lb:
            merged.setdefault(key(e), e)
        un = [merged[k] for k in merged]
        un.sort(key=lambda e: max(deep_ts(e)) if deep_ts(e) else "")
        out[lk] = un
        report.append("%s.%s union |A|=%d |B|=%d |AuB|=%d written=%d" % (path, lk, len(set(map(key, la))), len(set(map(key, lb))), len(merged), len(un)))
    side, ma, mb = pick_ts({k: v for k, v in a.items() if k not in ledger_keys}, {k: v for k, v in b.items() if k not in ledger_keys}, path)
    src = b if side == "theirs" else a
    for k, v in src.items():
        if k not in ledger_keys:
            out[k] = v
    fmt = mirror_write(path, out, ob)
    json.load(open(path, encoding="utf-8"))
    report.append("%s -> ledger union + state take-%s (ours_max=%s theirs_max=%s) %s" % (path, side, ma, mb, fmt))

def resolve_autofill(path):
    ob, tb_ = blob(":2:" + path), blob(":3:" + path)
    a, b = json.loads(ob), json.loads(tb_)
    la, lb = a.get("launches", []), b.get("launches", [])
    merged = {}
    for e in la + lb: merged.setdefault(key(e), e)
    un = [merged[k] for k in merged]
    un.sort(key=lambda e: str(e.get("ts", "")))
    cap = 0
    if len(un) > 50:
        cap = len(un) - 50
        un = un[-50:]
        un.sort(key=lambda e: str(e.get("ts", "")))
    lk_a, lk_b = a.get("last_tick"), b.get("last_tick")
    ta = lk_a.get("ts", "") if isinstance(lk_a, dict) else ""
    tb2 = lk_b.get("ts", "") if isinstance(lk_b, dict) else ""
    if tb2 > ta: last_tick, side = lk_b, "theirs"
    elif ta > tb2: last_tick, side = lk_a, "ours"
    else: last_tick, side = lk_a, "ours(tie)"
    out = dict(a); out["launches"] = un; out["last_tick"] = last_tick
    assert isinstance(out["last_tick"], dict)
    fmt = mirror_write(path, out, ob)
    v = json.load(open(path, encoding="utf-8"))
    assert isinstance(v["last_tick"], dict)
    report.append("%s -> mixed union=%d(|AuB|=%d cap_drop=%d) last_tick take-%s (%s|%s) %s" % (path, len(un), len(merged), cap, side, ta, tb2, fmt))

# ---- execute all 15 faces ----
resolve_autofill("results/autofill_state.json")
resolve_ledger("results/compute_audit.json", ["history"])
resolve_ledger("results/regime_state.json", ["history", "transitions"])

# js-wrapper: take fresher side WHOLE BYTES (no re-emit)
p = "results/dashboard_status.js"
ob, tb_ = blob(":2:" + p), blob(":3:" + p)
ja = json.loads(ob.decode("utf-8").split("=", 1)[1].strip().rstrip(";"))
jb = json.loads(tb_.decode("utf-8").split("=", 1)[1].strip().rstrip(";"))
side, ma, mb = pick_ts(ja, jb, p)
open(p, "wb").write(tb_ if side == "theirs" else ob)
report.append("%s -> js-wrapper take-%s whole-bytes (ours_max=%s theirs_max=%s)" % (p, side, ma, mb))

for p in ["results/dashboard_status.json", "results/fundamental_b_layer_filter.json",
          "results/futures_update_status.json", "results/heat_update_status.json",
          "results/lhb_update_status.json", "results/update_status.json",
          "results/token_usage.json", "results/scorecard_v1.json",
          "results/strategy_scorecard.json"]:
    resolve_snapshot(p)

# daily_report twins: take-new by embedded ts, SAME side both (r333 coupling)
pj = "docs/daily_report/REPORT-2026-09-27.json"
pm = "docs/daily_report/REPORT-2026-09-27.md"
oj, tj = blob(":2:" + pj), blob(":3:" + pj)
a, b = json.loads(oj), json.loads(tj)
side, ma, mb = pick_ts(a, b, pj)
src_j = tj if side == "theirs" else oj
open(pj, "wb").write(src_j)
json.load(open(pj, encoding="utf-8"))
om, tm = blob(":2:" + pm), blob(":3:" + pm)
open(pm, "wb").write(tm if side == "theirs" else om)
report.append("%s + %s -> twin take-%s coupled (json ours_max=%s theirs_max=%s)" % (pj, pm, side, ma, mb))

print("== RESOLVE-2 REPORT ==")
for r in report: print(r)
print("RESOLVE2-OK faces=%d" % len(report))
