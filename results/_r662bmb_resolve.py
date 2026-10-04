# -*- coding: utf-8 -*-
# r662 bm-b merge resolver: 18 UU per bigmoney-conflict-resolve skill classification
# Laws: r657(2) raw bytes via git show HEAD:/MERGE_HEAD:; r100 normalized-key ts probe;
# R350 wall-clock requires time-of-day, no key-EXCLUDE lists; r140 same-second tie -> HEAD;
# r188/R208 rolling-ledger union zero-loss; twins take same side (json authoritative);
# r185 reparse-before-write; r456 side-pick>0 assertion for union legs.
import json, subprocess, io, re, sys

def git_bytes(rev, path):
    p = subprocess.run(["git", "show", "%s:%s" % (rev, path)], capture_output=True)
    if p.returncode != 0:
        raise RuntimeError("git show %s:%s rc=%d %s" % (rev, path, p.returncode, p.stderr[-200:]))
    return p.stdout

TS_SHAPE = re.compile(r"^20\d{2}-")
HAS_TOD = re.compile(r"[T ]\d{2}:\d{2}")

def deep_ts_probe(obj, path_seen=""):
    """R350/r100 hardened probe: normalize keys (strip _ -), value must be ts-shaped
    AND carry time-of-day. Returns (max_ts_str, evidence_key)."""
    best = (None, None)
    if isinstance(obj, dict):
        for k, v in obj.items():
            nk = re.sub(r"[_\-]", "", str(k)).lower()
            if isinstance(v, str) and TS_SHAPE.match(v) and HAS_TOD.search(v):
                if any(t in nk for t in ("ts", "asof", "updated", "generated", "time", "clock", "seen", "written")):
                    if best[0] is None or v > best[0]:
                        best = (v, path_seen + "/" + str(k))
            r = deep_ts_probe(v, path_seen + "/" + str(k))
            if r[0] is not None and (best[0] is None or r[0] > best[0]):
                best = r
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            r = deep_ts_probe(v, path_seen + "/%d" % i)
            if r[0] is not None and (best[0] is None or r[0] > best[0]):
                best = r
    return best

def load_json(b):
    return json.loads(b.decode("utf-8-sig", "replace"))

def take_new(path, side_hint=None):
    h, t = git_bytes("HEAD", path), git_bytes("MERGE_HEAD", path)
    try:
        jh, jt = load_json(h), load_json(t)
        ph, pt = deep_ts_probe(jh), deep_ts_probe(jt)
    except Exception as e:
        # non-json or probe fail: fall back to mtime-less byte take of MERGE_HEAD if unparseable
        return {"path": path, "side": "HEAD", "why": "probe-fail-fallback-HEAD %s" % e, "blob": h}
    if pt[0] is not None and (ph[0] is None or pt[0] > ph[0]):
        side, blob, why = "MERGE_HEAD", t, "theirs-newer %s>vs>%s" % (pt[0], ph[0])
    elif pt[0] is not None and ph[0] is not None and pt[0] == ph[0]:
        side, blob, why = "HEAD", h, "tie->HEAD %s" % ph[0]
    elif ph[0] is not None:
        side, blob, why = "HEAD", h, "ours-newer %s>vs>%s" % (ph[0], pt[0])
    else:
        side, blob, why = "HEAD", h, "no-ts-both->HEAD"
    return {"path": path, "side": side, "why": why, "blob": blob}

def rolling_union(path):
    h, t = git_bytes("HEAD", path), git_bytes("MERGE_HEAD", path)
    jh, jt = load_json(h), load_json(t)
    ph, pt = deep_ts_probe(jh), deep_ts_probe(jt)
    base, other = (jh, jt) if (ph[0] and (pt[0] is None or ph[0] >= pt[0])) else (jt, jh)
    base_name = "HEAD" if base is jh else "MERGE_HEAD"
    side_picks = 0
    sets_equal = True
    for k in list(base.keys()):
        if isinstance(base.get(k), list) and isinstance(other.get(k), list):
            canon = set(json.dumps(e, sort_keys=True, ensure_ascii=False) for e in base[k])
            ocanon = set(json.dumps(e, sort_keys=True, ensure_ascii=False) for e in other[k])
            if canon != ocanon:
                sets_equal = False
            for e in other[k]:
                c = json.dumps(e, sort_keys=True, ensure_ascii=False)
                if c not in canon:
                    base[k].append(e); canon.add(c); side_picks += 1
            # chronological re-sort when entries carry a ts key (format face, r188 zero-loss)
            if base[k] and all(isinstance(e, dict) and any(
                    isinstance(v, str) and TS_SHAPE.match(v) for v in e.values()) for e in base[k]):
                def _ek(e):
                    cands = [v for v in e.values() if isinstance(v, str) and TS_SHAPE.match(v) and HAS_TOD.search(v)]
                    return max(cands) if cands else ""
                base[k].sort(key=_ek)
    if side_picks == 0:
        # r456 law: zero per-key pick -> EXPLICIT whole-face freshness adjudication;
        # zero-loss precondition = both sides' ledger sets identical (verified above)
        assert sets_equal, "zero picks but ledger sets differ on %s -- real loss risk, halt" % path
        winner, wname = (jh, "HEAD") if (ph[0] and (pt[0] is None or ph[0] >= pt[0])) else (jt, "MERGE_HEAD")
        blob = json.dumps(winner, ensure_ascii=False, indent=1).encode("utf-8")
        return {"path": path, "side": "whole-face-%s" % wname,
                "why": "sets-equal zero-pick -> freshness whole-take (ours=%s theirs=%s)" % (ph[0], pt[0]),
                "blob": blob}
    blob = json.dumps(base, ensure_ascii=False, indent=1).encode("utf-8")
    return {"path": path, "side": "union-base-%s" % base_name, "why": "ours=%s theirs=%s picks=%d" % (ph[0], pt[0], side_picks), "blob": blob}

log = []
def write_out(r):
    with io.open(r["path"], "wb") as f:
        f.write(r["blob"])
    log.append({"path": r["path"], "side": r["side"], "why": r["why"]})

# --- twin groups: json twin decides, all group files take that side (byte copy) ---
grp_report = take_new("docs/daily_report/REPORT-2026-10-04.json")
side_report = grp_report["side"]
for p in ("docs/daily_report/REPORT-2026-10-04.json", "docs/daily_report/REPORT-2026-10-04.md"):
    write_out({"path": p, "side": side_report, "why": grp_report["why"],
               "blob": git_bytes("HEAD" if side_report == "HEAD" else "MERGE_HEAD", p)})

grp_live = take_new("docs/live_usage/LIVE-2026-10-04.json")
side_live = grp_live["side"]
for p in ("docs/live_usage/LIVE-2026-10-04.json", "docs/live_usage/LIVE-2026-10-04.md",
          "docs/live_usage/LIVE-latest.json", "docs/live_usage/LIVE-latest.md"):
    write_out({"path": p, "side": side_live, "why": grp_live["why"],
               "blob": git_bytes("HEAD" if side_live == "HEAD" else "MERGE_HEAD", p)})

# --- dashboard twins: json decides; js byte-copies same side ---
grp_dash = take_new("results/dashboard_status.json")
side_dash = grp_dash["side"]
for p in ("results/dashboard_status.json", "results/dashboard_status.js"):
    write_out({"path": p, "side": side_dash, "why": grp_dash["why"],
               "blob": git_bytes("HEAD" if side_dash == "HEAD" else "MERGE_HEAD", p)})

# --- rolling ledgers (union zero-loss) ---
for p in ("results/compute_audit.json", "results/regime_state.json"):
    write_out(rolling_union(p))

# --- plain snapshots (incl. UNKNOWN->manual snapshot _attrition_guard_scan.json) ---
for p in ("results/fundamental_b_layer_filter.json", "results/futures_update_status.json",
          "results/lhb_update_status.json", "results/scorecard_v1.json",
          "results/strategy_scorecard.json", "results/token_usage.json",
          "results/update_status.json", "results/_attrition_guard_scan.json"):
    write_out(take_new(p))

# --- reparse validation gate (r185): every resolved json must json.loads ---
resolved_jsons = [e["path"] for e in log if e["path"].endswith(".json")]
for p in resolved_jsons:
    json.loads(io.open(p, encoding="utf-8-sig").read())

# --- conflict-marker residue check (line-start law r453/r657): no resolved file may carry markers ---
for e in log:
    with io.open(e["path"], "rb") as f:
        content = f.read()
    for marker in (b"<<<<<<<", b">>>>>>>", b"======="):
        assert not any(l.startswith(marker) for l in content.splitlines()), \
            "marker residue in %s" % e["path"]

with io.open("results/_r662bmb_resolve.json", "w", encoding="utf-8") as f:
    json.dump({"round": 662, "machine": "bm-b", "resolved": log,
               "note": "18 UU per classifier; _attrition_guard_scan.json manually classified snapshot (per-run scan evidence, take-new by internal ts)"}, f, ensure_ascii=False, indent=1)
for e in log:
    print("%-52s -> %-14s %s" % (e["path"], e["side"], e["why"][:60]))
print("REPARSE+MARKER GATES: ALL PASS, files resolved:", len(log))
