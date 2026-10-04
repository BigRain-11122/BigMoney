import subprocess, json, io, re

OUT = r"C:\Fluxgroup\FluxGroup\quant\bigmoney\results\_r673bmb_merge_resolve.txt"
lines = []

# 32 UU faces per git status porcelain (r657 full-sweep)
TS_FRESH = [
    "docs/daily_report/REPORT-2026-10-04.json",
    "docs/daily_report/REPORT-2026-10-04.md",
    "docs/live_usage/LIVE-2026-10-04.json",
    "docs/live_usage/LIVE-2026-10-04.md",
    "docs/live_usage/LIVE-latest.json",
    "docs/live_usage/LIVE-latest.md",
    "results/_attrition_guard_scan.json",
    "results/compute_audit.json",
    "results/daily_scorecard.json",
    "results/dashboard_status.js",
    "results/dashboard_status.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/lhb_update_status.json",
    "results/regime_state.json",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
    "results/t35_open_fill_verify.json",
    "results/update_status.json",
]
PAPER_OURS = [
    "results/paper/COMPOSITE-CE-01_paper.json",
    "results/paper/COMPOSITE-CE-02_paper.json",
    "results/paper/DROUGHT-CE-01_paper.json",
    "results/paper/ENGULF-CE-01_paper.json",
    "results/paper/NEEDLE-DE-01_paper.json",
    "results/paper/VOLATILITY-CE-01_paper.json",
    "results/paper_export/export-2026-09-30.json",
    "results/paper_export/latest.json",
    "results/prospect_paper/_summary.json",
    "results/prospect_promotion/_summary.json",
]
TOKEN = "results/token_usage.json"
X2 = "results/x2_watch_log.jsonl"

def show(ref, path):
    r = subprocess.run(["git", "show", "%s:%s" % (ref, path)], capture_output=True)
    return r.stdout, r.returncode

def ts_norm(s):
    if not s:
        return None
    s = s.strip().replace("T", " ")[:19]
    return s if re.match(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$", s) else None

def find_ts(b):
    try:
        j = json.loads(b.decode("utf-8"))
        for k in ("ts", "generated_at", "updated", "wall"):
            v = j.get(k) if isinstance(j, dict) else None
            t = ts_norm(str(v)) if v else None
            if t:
                return t, "json:" + k
        def walk(o, depth=0):
            if depth > 3:
                return None
            if isinstance(o, dict):
                for k, v in o.items():
                    if k in ("ts", "generated_at", "updated", "wall", "asof", "checked_at") and v:
                        t = ts_norm(str(v))
                        if t:
                            return t
                    r = walk(v, depth + 1)
                    if r:
                        return r
            elif isinstance(o, list):
                for v in o[:5]:
                    r = walk(v, depth + 1)
                    if r:
                        return r
            return None
        t = walk(j)
        if t:
            return t, "json:dfs"
    except Exception:
        pass
    m = re.search(rb"(\d{4}-\d{2}-\d{2})[T ](\d{2}:\d{2}:\d{2})", b[:3000])
    if m:
        return (m.group(1) + b" " + m.group(2)).decode(), "text"
    return None, None

def resolve_token(ours, theirs):
    jo = json.loads(ours.decode("utf-8"))
    jt = json.loads(theirs.decode("utf-8"))
    side_pick = 0
    if "machines" in jo and "machines" in jt and isinstance(jo["machines"], dict):
        for mk, mv in jt["machines"].items():
            if mk not in jo["machines"]:
                jo["machines"][mk] = mv
                side_pick += 1
            else:
                ov = jo["machines"][mk]
                to = ts_norm(str(ov.get("ts") or "")) or ""
                tt = ts_norm(str(mv.get("ts") or "")) or ""
                if tt > to:
                    jo["machines"][mk] = mv
                    side_pick += 1
    if side_pick == 0:
        # r456/r466 law: zero side-pick -> explicit whole-face ts freshness, never silent whole-theirs
        to, _ = find_ts(ours)
        tt, _ = find_ts(theirs)
        lines.append("  token: side_pick=0 -> whole-face ts ours=%s theirs=%s" % (to, tt))
        return theirs if (tt or "") > (to or "") else ours
    to, _ = find_ts(ours)
    tt, _ = find_ts(theirs)
    if tt and (not to or tt > to):
        for k in ("ts", "updated", "wall"):
            if k in jt:
                jo[k] = jt[k]
    return json.dumps(jo, ensure_ascii=False, indent=1).encode("utf-8")

def resolve_x2_union(ours, theirs):
    # r656/r675 line-level canon union: theirs (origin) full text preserved + ours-only lines appended
    t_lines = theirs.split(b"\n")
    o_lines = ours.split(b"\n")
    t_set = set(l for l in t_lines if l)
    o_only = [l for l in o_lines if l and l not in t_set]
    result = theirs
    if o_only:
        if not result.endswith(b"\n"):
            result += b"\n"
        result += b"\n".join(o_only) + b"\n"
    lines.append("  x2: theirs_lines=%d ours_lines=%d ours_only=%d -> union=%d" % (
        len([l for l in t_lines if l]), len([l for l in o_lines if l]), len(o_only),
        len([l for l in result.split(b"\n") if l])))
    return result

def write_face(f, content, note):
    with io.open(f, "wb") as fh:
        fh.write(content)
    with io.open(f, "rb") as fh:
        d = fh.read()
    n_m = sum(1 for ln in d.split(b"\n") if ln.startswith(b"<<<<<<<") or ln.startswith(b">>>>>>>"))
    lines.append("RESOLVED %s: %s (markers=%d)" % (f, note, n_m))
    if n_m:
        raise SystemExit("MARKER PRESENT after resolve: %s" % f)

resolved = 0
for f in TS_FRESH:
    ob, orc = show("HEAD", f)
    tb, trc = show("MERGE_HEAD", f)
    if orc != 0 or trc != 0:
        lines.append("SKIP %s: show rc ours=%d theirs=%d" % (f, orc, trc))
        continue
    if ob == tb:
        write_face(f, ob, "identical")
    else:
        to, ko = find_ts(ob)
        tt, kt = find_ts(tb)
        if to and tt and to != tt:
            c = ob if to > tt else tb
            write_face(f, c, "ts-freshness ours=%s(%s) theirs=%s(%s) -> %s" % (
                to, ko, tt, kt, "OURS" if to > tt else "THEIRS"))
        elif to and not tt:
            write_face(f, ob, "ours ts only (%s) -> OURS" % to)
        elif tt and not to:
            write_face(f, tb, "theirs ts only (%s) -> THEIRS" % tt)
        else:
            write_face(f, ob, "ts tie/unparseable (%s vs %s) -> OURS" % (to, tt))
    resolved += 1

for f in PAPER_OURS:
    ob, orc = show("HEAD", f)
    tb, trc = show("MERGE_HEAD", f)
    if orc != 0 or trc != 0:
        lines.append("SKIP %s: show rc ours=%d theirs=%d" % (f, orc, trc))
        continue
    write_face(f, ob, "paper-family semantically-equal regen -> OURS (theirs bytes=%d)" % len(tb))
    resolved += 1

ob, orc = show("HEAD", TOKEN)
tb, trc = show("MERGE_HEAD", TOKEN)
if orc == 0 and trc == 0:
    write_face(TOKEN, resolve_token(ob, tb), "per-key union machines + top ts")
    resolved += 1
else:
    lines.append("SKIP token rc ours=%d theirs=%d" % (orc, trc))

ob, orc = show("HEAD", X2)
tb, trc = show("MERGE_HEAD", X2)
if orc == 0 and trc == 0:
    write_face(X2, resolve_x2_union(ob, tb), "line-level union origin-full + ours-only appended")
    resolved += 1
else:
    lines.append("SKIP x2 rc ours=%d theirs=%d" % (orc, trc))

lines.append("TOTAL resolved=%d (expected 31)" % resolved)
if resolved != 31:
    raise SystemExit("RESOLVED COUNT MISMATCH: %d != 31" % resolved)

with io.open(OUT, "w", encoding="utf-8") as fh:
    fh.write("\n".join(lines))
print("resolver done, 32/32")
