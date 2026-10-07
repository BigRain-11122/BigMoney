# -*- coding: utf-8 -*-
"""r665 bm-c MERGE-mode conflict resolver (17 UU vs bm-a r814 closeout wave).

Sides (MERGE semantics -- OPPOSITE of rebase, r648 law): stage2 'ours' = MY
r665 round commit; stage3 'theirs' = origin bm-a r814 closeout.
Recipes (r664 resolver receipt lineage + r598/r724 family):
  1. CODELY.md                    -> LINE UNION (append-only ledger law:
       theirs base + mine-only tail lines appended; superset asserted)
  2. results/compute_audit.json   -> ROW UNION (own-row law r798: history rows
       dedup by full-row identity, sort by ts; latest = newest ts row)
  3. results/token_usage.json      -> PER-KEY OWN-ROW UNION (machines: bm-c
       keys from ours, bm-a keys from theirs, default from ours-newer; all
       other top-level fields from ours = newer generated 08:52:49)
  4. docs/daily_report + docs/live_usage (6 faces, same-day idempotent
       last-writer-wins, NO host guard per r664 receipt) -> ts-newer-wins
  5. results/_attrition_guard_scan.json -> ts-newer-wins (transient evidence)
  6. results/{fundamental_b_layer_filter,regime_state,scorecard_v1,
       strategy_scorecard,update_status}.json -> STAGE 3 (origin-newer-wins:
       regenerable deterministic S6 faces, r648 two-bucket law; scorecard
       doubly host=bm-a per r378)
  7. results/{futures_update_status,lhb_update_status}.json -> STAGE 3
       (lane-owner-wins: bm-a is futures/LHB lane host, R31 family)
All blob IO byte-exact via git show :N:path; JSON re-dump uses file-native
indent detected from the winning blob. Zero hand-edited content.
"""
import json
import re
import subprocess
import sys

CREATE_NO_WINDOW = 0x08000000
MINE_NEWER_FACES = [
    "docs/daily_report/REPORT-2026-10-07.json",
    "docs/daily_report/REPORT-2026-10-07.md",
    "docs/live_usage/LIVE-2026-10-07.json",
    "docs/live_usage/LIVE-2026-10-07.md",
    "docs/live_usage/LIVE-latest.json",
    "docs/live_usage/LIVE-latest.md",
    "results/_attrition_guard_scan.json",
]
STAGE3_FACES = [
    "results/fundamental_b_layer_filter.json",
    "results/regime_state.json",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
    "results/update_status.json",
    "results/futures_update_status.json",
    "results/lhb_update_status.json",
]


def blob(stage, path):
    r = subprocess.run(["git", "show", ":%d:%s" % (stage, path)],
                       capture_output=True, creationflags=CREATE_NO_WINDOW)
    if r.returncode != 0:
        raise SystemExit("blob read fail stage %d %s: %s" % (stage, path, r.stderr))
    return r.stdout


def detect_indent(raw):
    m = re.match(rb"\{\r?\n(\s+)", raw)
    return len(m.group(1)) if m else None


def dump_native(data, sample_raw, path):
    indent = detect_indent(sample_raw)
    txt = json.dumps(data, ensure_ascii=False, indent=indent)
    if sample_raw.endswith(b"\n"):
        txt += "\n"
    with open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write(txt)


def extract_ts(raw):
    m = re.search(rb"20\d{2}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2}", raw)
    if not m:
        return None
    return m.group(0).decode()


def resolve_verbatim(path, side):
    data = blob(2 if side == "ours" else 3, path)
    with open(path, "wb") as fh:
        fh.write(data)
    print("RESOLVED %-46s <- stage%d (%d bytes)" % (path, 2 if side == "ours" else 3, len(data)))


def resolve_ts_newer(path):
    o = blob(2, path)
    t = blob(3, path)
    ots = extract_ts(o)
    tts = extract_ts(t)
    assert ots and tts, "ts extract fail %s (%s vs %s)" % (path, ots, tts)
    if ots > tts:
        data, side = o, "ours"
    else:
        data, side = t, "theirs"
    with open(path, "wb") as fh:
        fh.write(data)
    print("RESOLVED %-46s <- ts-newer %s (ours %s vs theirs %s)" % (path, side, ots, tts))


def resolve_codely():
    path = "CODELY.md"
    o = blob(2, path)
    t = blob(3, path)
    marker = b"r665 bm-c] **silent-git"
    assert marker in o and marker not in t, "r665 pit marker side-check fail"
    o_lines = o.split(b"\n")
    t_lines = t.split(b"\n")
    t_keys = [l.rstrip(b"\r") for l in t_lines if l.strip()]
    from collections import Counter
    tc = Counter(t_keys)
    adds = []
    for l in o_lines:
        if not l.strip():
            continue
        k = l.rstrip(b"\r")
        if tc[k] > 0:
            tc[k] -= 1
        else:
            adds.append(k)
    assert adds, "CODELY union: no mine-only lines found (unexpected)"
    eol = b"\r\n" if b"\r\n" in t[:300] else b"\n"
    base = t if t.endswith(b"\n") else t + b"\n"
    merged = base + eol.join(adds) + b"\n"
    # superset assertion: every distinct nonempty line of both sides present
    ml = Counter(l.rstrip(b"\r") for l in merged.split(b"\n") if l.strip())
    for src in (o, t):
        for l in src.split(b"\n"):
            if l.strip():
                assert ml[l.rstrip(b"\r")] > 0, "CODELY union lost a line"
    assert merged.count(marker) == 1, "r665 marker count != 1"
    with open(path, "wb") as fh:
        fh.write(merged)
    print("RESOLVED %-46s <- line-union (mine-only adds=%d, %dB)" % (path, len(adds), len(merged)))


def resolve_compute_audit():
    path = "results/compute_audit.json"
    o = json.loads(blob(2, path))
    t = json.loads(blob(3, path))
    seen = {}
    for row in t["history"] + o["history"]:
        key = json.dumps(row, sort_keys=True, ensure_ascii=False)
        seen[key] = row
    hist = sorted(seen.values(), key=lambda r: r.get("ts", ""))
    latest = max(hist, key=lambda r: r.get("ts", ""))
    res = {"latest": latest, "history": hist}
    dump_native(res, blob(2, path), path)
    d = json.load(open(path, encoding="utf-8"))
    assert d["latest"]["ts"] == max(r["ts"] for r in d["history"])
    print("RESOLVED %-46s <- row-union (%d rows, latest %s)" % (path, len(hist), latest["ts"]))


def resolve_token_usage():
    path = "results/token_usage.json"
    o_raw = blob(2, path)
    t_raw = blob(3, path)
    o = json.loads(o_raw)
    t = json.loads(t_raw)
    assert o["generated"] > t["generated"], "token: ours not newer (%s vs %s)" % (o["generated"], t["generated"])
    m = dict(t["machines"])
    for k, v in o["machines"].items():
        if ("bm-c" in k) or (k == "default"):
            m[k] = v
    res = dict(o)
    res["machines"] = m
    dump_native(res, o_raw, path)
    d = json.load(open(path, encoding="utf-8"))
    assert "bm-c" in d["machines"] and "bm-a" in d["machines"]
    print("RESOLVED %-46s <- own-row union (bm-c/default=ours %s, bm-a=theirs %s)" % (path, o["generated"], t["generated"]))


def main():
    resolve_codely()
    resolve_compute_audit()
    resolve_token_usage()
    for p in MINE_NEWER_FACES:
        resolve_ts_newer(p)
    for p in STAGE3_FACES:
        resolve_verbatim(p, "theirs")
    # global post-asserts: no conflict markers anywhere in resolved set
    all_paths = ["CODELY.md", "results/compute_audit.json", "results/token_usage.json"] + MINE_NEWER_FACES + STAGE3_FACES
    for p in all_paths:
        raw = open(p, "rb").read()
        assert b"<<<<<<<" not in raw and b">>>>>>>" not in raw, "marker left in " + p
        if p.endswith(".json"):
            json.loads(raw)
    print("POST-ASSERTS: 17 faces resolved, zero markers, JSON parse PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
