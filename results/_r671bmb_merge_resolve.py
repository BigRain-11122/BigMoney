import subprocess, json, io, re, sys

OUT = r"C:\Fluxgroup\FluxGroup\quant\bigmoney\results\_r671bmb_merge_resolve.txt"
FACES = [
    "docs/daily_report/REPORT-2026-10-04.json",
    "docs/daily_report/REPORT-2026-10-04.md",
    "docs/live_usage/LIVE-2026-10-04.json",
    "docs/live_usage/LIVE-2026-10-04.md",
    "docs/live_usage/LIVE-latest.json",
    "docs/live_usage/LIVE-latest.md",
    "results/_attrition_guard_scan.json",
    "results/compute_audit.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/lhb_update_status.json",
    "results/regime_state.json",
    "results/token_usage.json",
    "results/update_status.json",
]
lines = []

def show(ref, path):
    r = subprocess.run(["git", "show", "%s:%s" % (ref, path)], capture_output=True)
    return r.stdout, r.returncode

def ts_norm(s):
    if not s:
        return None
    s = s.strip().replace("T", " ")[:19]
    return s if re.match(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$", s) else None

def find_ts(b):
    # try JSON first
    try:
        j = json.loads(b.decode("utf-8"))
        for k in ("ts", "generated_at", "updated", "wall"):
            v = j.get(k) if isinstance(j, dict) else None
            t = ts_norm(str(v)) if v else None
            if t:
                return t, "json:" + k
        # nested first ts (dfs shallow)
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
    # md/text: first ISO timestamp in first 3000 bytes
    m = re.search(rb"(\d{4}-\d{2}-\d{2})[T ](\d{2}:\d{2}:\d{2})", b[:3000])
    if m:
        return (m.group(1) + b" " + m.group(2)).decode(), "text"
    return None, None

def resolve_token(ours, theirs):
    jo = json.loads(ours.decode("utf-8"))
    jt = json.loads(theirs.decode("utf-8"))
    side_pick = 0
    # per-key union on machines dict
    if "machines" in jo and "machines" in jt and isinstance(jo["machines"], dict):
        for mk, mv in jt["machines"].items():
            if mk not in jo["machines"]:
                jo["machines"][mk] = mv
                side_pick += 1
            else:
                # per-machine: take newer ts inside
                ov = jo["machines"][mk]; tv = mv
                to = ts_norm(str(ov.get("ts") or "")) or ""
                tt = ts_norm(str(tv.get("ts") or "")) or ""
                if tt > to:
                    jo["machines"][mk] = tv
                    side_pick += 1
    if side_pick == 0:
        # r456/r466 law: zero side-pick -> explicit whole-face freshness
        to, _ = find_ts(ours)
        tt, _ = find_ts(theirs)
        lines.append("  token: side_pick=0 -> whole-face ts ours=%s theirs=%s" % (to, tt))
        return theirs if (tt or "") > (to or "") else ours
    # top-level: keep ours ts if newer else theirs ts
    to, _ = find_ts(ours)
    tt, _ = find_ts(theirs)
    if tt and (not to or tt > to):
        for k in ("ts", "updated", "wall"):
            if k in jt:
                jo[k] = jt[k]
    return json.dumps(jo, ensure_ascii=False, indent=1).encode("utf-8")

for f in FACES:
    ob, orc = show("HEAD", f)
    tb, trc = show("MERGE_HEAD", f)
    if orc != 0 or trc != 0:
        lines.append("SKIP %s: show rc ours=%d theirs=%d" % (f, orc, trc))
        continue
    if ob == tb:
        lines.append("IDENTICAL %s -> either" % f)
        content = ob
    elif f == "results/token_usage.json":
        content = resolve_token(ob, tb)
        lines.append("RESOLVED %s: per-key union" % f)
    else:
        to, ko = find_ts(ob)
        tt, kt = find_ts(tb)
        if to and tt and to != tt:
            content = ob if to > tt else tb
            lines.append("RESOLVED %s: ts-freshness ours=%s(%s) theirs=%s(%s) -> %s" % (
                f, to, ko, tt, kt, "OURS" if to > tt else "THEIRS"))
        elif to and not tt:
            content = ob; lines.append("RESOLVED %s: ours ts only (%s) -> OURS" % (f, to))
        elif tt and not to:
            content = tb; lines.append("RESOLVED %s: theirs ts only (%s) -> THEIRS" % (f, tt))
        else:
            content = ob
            lines.append("RESOLVED %s: ts tie/unparseable (%s vs %s) -> OURS + byte-diff=%s" % (
                f, to, tt, ob != tb))
    with io.open(f, "wb") as fh:
        fh.write(content)
    # marker check on written file
    with io.open(f, "rb") as fh:
        d = fh.read()
    n_m = sum(1 for ln in d.split(b"\n") if ln.startswith(b"<<<<<<<") or ln.startswith(b">>>>>>>"))
    lines.append("  markers=%d" % n_m)

with io.open(OUT, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))
print("resolved; see log")
