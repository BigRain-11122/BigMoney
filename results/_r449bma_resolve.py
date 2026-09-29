# r449 bm-a push-storm UU resolver -- 25 residual faces (31 UU total, 6 ALL_FACES already
# resolved via scripts/merge_lane_views.py resolve). Recipes per
# .codely-cli/skills/bigmoney-conflict-resolve/SKILL.md + classifier output r449.
# Stage law (r351): :1:=merge-base, :2:=origin/base-side (rebase ours), :3:=local replay side.
# Probe law r100: normalize key stripping '_'/'-' BEFORE prefix-family match; value must be
#   ts-shaped (^20\d{2}-) before max-compare. R350: NO key-name EXCLUDE lists; wall-clock
#   compare requires time-of-day in value (date-only must not feed max); probe STAGED blobs
#   only, never working tree. Tie -> take :2: (HEAD-side, r140).
import subprocess, json, re, sys, difflib
from datetime import datetime

REPO = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"

def blob(stage, path):
    r = subprocess.run(["git", "show", f":{stage}:{path}"], capture_output=True, cwd=REPO)
    if r.returncode != 0:
        raise RuntimeError(f"git show :{stage}:{path} rc={r.returncode} {r.stderr[:200]!r}")
    return r.stdout

def write(path, data: bytes):
    with open(REPO + "\\" + path.replace("/", "\\"), "wb") as f:
        f.write(data)

TS_SHAPE = re.compile(r"^20\d{2}-")
TOD = re.compile(r"[T ]\d{1,2}:\d{2}")

def _to_dt(v):
    s = v.strip()
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    s = s.replace(" ", "T", 1) if ("T" not in s and " " in s) else s
    try:
        d = datetime.fromisoformat(s)
    except Exception:
        try:
            d = datetime.fromisoformat(s + "+08:00")
        except Exception:
            return None
    if d.tzinfo is None:  # normalize naive -> aware (+08:00 local) so max-compare is well-typed
        from datetime import timezone, timedelta
        d = d.replace(tzinfo=timezone(timedelta(hours=8)))
    return d

def deep_wallclock(obj, acc):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, str) and TS_SHAPE.match(v) and TOD.search(v):
                d = _to_dt(v)
                if d is not None:
                    acc.append((d, k, v))
            deep_wallclock(v, acc)
    elif isinstance(obj, list):
        for it in obj:
            deep_wallclock(it, acc)

def probe_side(stage, path):
    b = blob(stage, path)
    try:
        obj = json.loads(b.decode("utf-8"))
    except Exception as e:
        raise RuntimeError(f"{path} stage{stage} not JSON: {e}")
    acc = []
    deep_wallclock(obj, acc)
    if not acc:
        return None, b
    acc.sort(key=lambda x: x[0])
    return acc[-1], b

def take_new(path, log):
    p2, b2 = probe_side(2, path)
    p3, b3 = probe_side(3, path)
    if p2 is None and p3 is None:
        log.append(f"  !! {path}: NO wall-clock probe on either side -> tie-rule :2: (logged, manual eye)")
        write(path, b2); return ":2:"
    if p3 is None or (p2 is not None and p2[0] >= p3[0]):
        side, ts = ":2:", p2
    else:
        side, ts = ":3:", p3
    write(path, b2 if side == ":2:" else b3)
    log.append(f"  {path}: take {side} (max wall-clock {ts[1]}={ts[2]})")
    return side

def twin(json_path, md_path, log):
    side = take_new(json_path, log)
    write(md_path, blob(2 if side == ":2:" else 3, md_path))
    log.append(f"  {md_path}: byte-copy SAME side {side} (twin coupling law r329)")

def js_same_side(js_path, ref_side, log):
    write(js_path, blob(2 if ref_side == ":2:" else 3, js_path))
    log.append(f"  {js_path}: take-side whole bytes {ref_side} (js-wrapper law R209)")

def union_jsonl(path, log):
    a = blob(2, path).decode("utf-8").splitlines()
    b = blob(3, path).decode("utf-8").splitlines()
    from collections import Counter
    ca, cb = Counter(a), Counter(b)
    out, seen = [], Counter()
    for ln in a:
        if seen[ln] < max(ca[ln], cb[ln]):
            out.append(ln); seen[ln] += 1
    for ln in b:
        if seen[ln] < cb[ln]:
            out.append(ln); seen[ln] += 1
    nbad = 0
    for ln in out:
        ln2 = ln.strip()
        if not ln2:
            continue
        try:
            json.loads(ln2)
        except Exception:
            nbad += 1
    total = sum((max(ca[ln], cb[ln]) for ln in set(ca) | set(cb)))
    body = "\n".join(out)
    if blob(2, path).endswith(b"\n") or blob(3, path).endswith(b"\n"):
        body += "\n"
    write(path, body.encode("utf-8"))
    log.append(f"  {path}: line union |A|={len(a)} |B|={len(b)} -> {len(out)} rows (expected {total}); unparseable={nbad}")
    assert len(out) == total, f"{path}: union row mismatch {len(out)} != {total}"

def resolve_codely(log):
    path = "CODELY.md"
    base_b, o_b, t_b = blob(1, path), blob(2, path), blob(3, path)
    base, ours, theirs = base_b.decode("utf-8"), o_b.decode("utf-8"), t_b.decode("utf-8")
    log.append(f"  CODELY.md sizes: base={len(base_b)}B :2:={len(o_b)}B :3:={len(t_b)}B "
               f"(eol base={'CRLF' if b'\\r\\n' in base_b else 'LF'} ours={'CRLF' if b'\\r\\n' in o_b else 'LF'} theirs={'CRLF' if b'\\r\\n' in t_b else 'LF'})")
    if ours.startswith(base) and theirs.startswith(base):
        merged = base + ours[len(base):] + theirs[len(base):]
        mode = "prefix-concat"
    else:
        o_lines = ours.splitlines()
        t_lines = theirs.splitlines()
        sm = difflib.SequenceMatcher(None, o_lines, t_lines, autojunk=False)
        out, ops = [], {"insert": 0, "delete": 0, "replace": 0}
        for tag, i1, i2, j1, j2 in sm.get_opcodes():
            if tag == "equal":
                out.extend(o_lines[i1:i2])
            elif tag == "insert":
                out.extend(t_lines[j1:j2]); ops["insert"] += 1
            elif tag == "delete":
                out.extend(o_lines[i1:i2]); ops["delete"] += 1  # origin-only new entries -- KEEP (zero-loss)
            else:
                out.extend(o_lines[i1:i2]); out.extend(t_lines[j1:j2]); ops["replace"] += 1
        merged = "\n".join(out) + ("\n" if ours.endswith("\n") else "")
        mode = f"entry-splice ops={ops}"
    mtext = merged
    ent = lambda s: [ln for ln in s.splitlines() if ln.strip().startswith("- [")]
    miss_o = [ln for ln in ent(ours) if ln not in mtext]
    miss_t = [ln for ln in ent(theirs) if ln not in mtext]
    drop_o = [ln for ln in ours.splitlines() if ln.strip() and ln not in mtext]
    drop_t = [ln for ln in theirs.splitlines() if ln.strip() and ln not in mtext]
    log.append(f"  CODELY non-entry leftovers: ours-side={len(drop_o)-len(miss_o)} theirs-side={len(drop_t)-len(miss_t)}")
    assert not miss_o, f"CODELY origin entries lost: {len(miss_o)}"
    assert not miss_t, f"CODELY local entries lost: {len(miss_t)}"
    log.append(f"  CODELY.md: {mode}; entries ours={len(ent(ours))} theirs={len(ent(theirs))} "
               f"-> merged={len(ent(mtext))}; lost_o=0 lost_t=0; merged={len(mtext.encode('utf-8'))}B")
    write(path, merged.encode("utf-8"))

def main():
    log = []
    take_new("results/daily_scorecard.json", log)
    ref = take_new("results/dashboard_status.json", log)
    js_same_side("results/dashboard_status.js", ref, log)
    take_new("results/fundamental_b_layer_filter.json", log)
    for p in ["results/paper/COMPOSITE-CE-01_paper.json", "results/paper/COMPOSITE-CE-02_paper.json",
              "results/paper/DROUGHT-CE-01_paper.json", "results/paper/ENGULF-CE-01_paper.json",
              "results/paper/NEEDLE-DE-01_paper.json", "results/paper/VOLATILITY-CE-01_paper.json"]:
        take_new(p, log)
    take_new("results/paper_export/export-2026-09-29.json", log)
    take_new("results/paper_export/latest.json", log)
    take_new("results/prospect_paper/_summary.json", log)
    take_new("results/prospect_promotion/_summary.json", log)
    take_new("results/scorecard_v1.json", log)
    take_new("results/strategy_scorecard.json", log)
    take_new("results/t35_open_fill_verify.json", log)
    twin("docs/daily_report/REPORT-2026-09-29.json", "docs/daily_report/REPORT-2026-09-29.md", log)
    twin("docs/live_usage/LIVE-2026-09-29.json", "docs/live_usage/LIVE-2026-09-29.md", log)
    twin("docs/live_usage/LIVE-latest.json", "docs/live_usage/LIVE-latest.md", log)
    union_jsonl("results/x2_watch_log.jsonl", log)
    resolve_codely(log)
    print("== r449 residual-face resolve ==")
    print("\n".join(log))
    # parse-verify every resolved JSON face (r185 law)
    for p in ["results/daily_scorecard.json", "results/dashboard_status.json",
              "results/fundamental_b_layer_filter.json",
              "results/paper/COMPOSITE-CE-01_paper.json", "results/paper/COMPOSITE-CE-02_paper.json",
              "results/paper/DROUGHT-CE-01_paper.json", "results/paper/ENGULF-CE-01_paper.json",
              "results/paper/NEEDLE-DE-01_paper.json", "results/paper/VOLATILITY-CE-01_paper.json",
              "results/paper_export/export-2026-09-29.json", "results/paper_export/latest.json",
              "results/prospect_paper/_summary.json", "results/prospect_promotion/_summary.json",
              "results/scorecard_v1.json", "results/strategy_scorecard.json",
              "results/t35_open_fill_verify.json",
              "docs/daily_report/REPORT-2026-09-29.json", "docs/live_usage/LIVE-2026-09-29.json",
              "docs/live_usage/LIVE-latest.json"]:
        json.loads(open(REPO + "\\" + p.replace("/", "\\"), "rb").read().decode("utf-8"))
    print("parse-verify: 19 JSON faces OK")

if __name__ == "__main__":
    main()
