# -*- coding: utf-8 -*-
"""r326 bm-a rebase resolver -- 30-UU 3-machine same-window S6 mirror batch
(upstream = bm-b r326 + bm-c r83 landed 13:28-13:39; mine r326 chain 13:43-45).

Recipes per bigmoney-conflict-resolve skill (classifier: 13 classified + 16
UNKNOWN hand-adjudicated by frozen deep ts probes):

  CODELY.md                    : memory-union -- merge-base prefix-identity
                                assertion BOTH sides + DIRECT-CONCAT suffixes
                                (bm-c r83 pitlaw suffix + bm-a r326 asi8
                                pitlaw suffix; byte math asserted, r311 law)
  results/autofill_state.json  : mixed-dict+ledger -- launches union ts-desc
                                cap50, write-back re-sorted ts ASC (r245 law);
                                last_tick whole-dict by inner ts, tie->HEAD
  results/compute_audit.json   : history union (ts,machine) composite key +
                                content-identity on collisions (r322 law);
                                latest take-new by deep ts probe
  results/regime_state.json    : history union by asof + content check; state
                                take-new
  results/x2_watch_log.jsonl    : line-level union zero loss
  13 snapshot faces + 16 UNKNOWN ts-snapshot faces : deep ts probe
                                (today-string max, recursive) -> take newer
                                side whole bytes; tie -> HEAD (r140)
"""
import json
import re
import subprocess

TODAY_RE = re.compile(r"2026-09-27T\d{2}:\d{2}(:\d{2})?")


def sh(*args):
    return subprocess.run(list(args), capture_output=True).stdout


def stage_bytes(path, n):
    return sh("git", "show", ":%d:%s" % (n, path))


def deep_today_ts(doc):
    """Max '2026-09-27Thh:mm' string anywhere in the doc (recursive)."""
    best = ""
    stack = [doc]
    while stack:
        x = stack.pop()
        if isinstance(x, dict):
            stack.extend(x.values())
        elif isinstance(x, list):
            stack.extend(x)
        elif isinstance(x, str):
            for m in TODAY_RE.findall(x) or []:
                pass
            m = re.search(TODAY_RE, x)
            if m and m.group(0) > best:
                best = m.group(0)
    return best


def write_bytes(path, b):
    with open(path, "wb") as fh:
        fh.write(b)


def take_newer_side(path, note):
    b2, b3 = stage_bytes(path, 2), stage_bytes(path, 3)
    if b2 == b3:
        write_bytes(path, b3)
        return (path, "identical bytes -> theirs kept (%s)" % note)
    try:
        t2 = deep_today_ts(json.loads(b2.decode("utf-8")))
        t3 = deep_today_ts(json.loads(b3.decode("utf-8")))
    except Exception:
        t2, t3 = None, None
    if t3 and (not t2 or t3 > t2):
        write_bytes(path, b3)
        side = "S3(mine)"
    elif t2 and (not t3 or t2 > t3):
        write_bytes(path, b2)
        side = "S2(upstream)"
    else:
        write_bytes(path, b2)          # tie or no-ts -> HEAD (r140)
        side = "HEAD-side(tie/no-ts)"
    return (path, "ts-diffpick %s vs %s -> %s (%s)" % (t2, t3, side, note))


def resolve_codely():
    p = "CODELY.md"
    base, ours, theirs = stage_bytes(p, 1), stage_bytes(p, 2), stage_bytes(p, 3)
    b = base.rstrip(b"\r\n")
    assert ours.rstrip(b"\r\n").startswith(b), "prefix assert FAILS ours (in-place edit -> manual)"
    assert theirs.rstrip(b"\r\n").startswith(b), "prefix assert FAILS theirs (in-place edit -> manual)"
    suf_a = ours.rstrip(b"\r\n")[len(b):]
    suf_b = theirs.rstrip(b"\r\n")[len(b):]
    merged = b + suf_a + suf_b + b"\r\n"
    assert len(merged) == len(b) + len(suf_a) + len(suf_b) + 2, "byte math"
    write_bytes(p, merged)
    s = open(p, "rb").read().decode("utf-8")           # strict utf-8 verify
    assert "r83 bm-c" in s and "asi8" in s and "r326 bm-a" in s
    return (p, "memory-union direct-concat: base %dB + S2 suffix %dB + S3 suffix "
            "%dB = %dB zero loss; both pitlaws present" %
            (len(b), len(suf_a), len(suf_b), len(merged)))


def resolve_autofill():
    p = "results/autofill_state.json"
    b2, b3 = stage_bytes(p, 2), stage_bytes(p, 3)
    crlf = b"\r\n" in b2 or b"\r\n" in b3
    d2 = json.loads(b2.decode("utf-8"))
    d3 = json.loads(b3.decode("utf-8"))
    doc = dict(d3)
    # launches union by id-key content-identity, ts-asc write-back, cap 50
    l2, l3 = d2.get("launches") or [], d3.get("launches") or []
    pool = {}
    for e in l2 + l3:
        k = json.dumps(e, sort_keys=True, ensure_ascii=False)
        pool[k] = e
    launches = sorted(pool.values(),
                       key=lambda e: str(e.get("ts") or e.get("tick") or ""),
                       reverse=True)[:50]
    launches.sort(key=lambda e: str(e.get("ts") or e.get("tick") or ""))
    doc["launches"] = launches
    lt2, lt3 = d2.get("last_tick"), d3.get("last_tick")
    t2 = str((lt2 or {}).get("ts") or "")
    t3 = str((lt3 or {}).get("ts") or "")
    doc["last_tick"] = lt3 if (not t2 or t3 >= t2) else lt2   # tie -> HEAD side
    assert isinstance(doc["last_tick"], dict)
    s = json.dumps(doc, ensure_ascii=False, indent=1)
    json.loads(s)
    nl = "\r\n" if crlf else "\n"
    write_bytes(p, (s + nl).encode("utf-8"))
    return (p, "launches union %d+%d -> %d (content-identity dedup, cap50, "
            "ts-asc write-back); last_tick ts %s vs %s" %
            (len(l2), len(l3), len(launches), t2, t3))


def resolve_compute_audit():
    p = "results/compute_audit.json"
    d2 = json.loads(stage_bytes(p, 2).decode("utf-8"))
    d3 = json.loads(stage_bytes(p, 3).decode("utf-8"))
    h2, h3 = d2["history"], d3["history"]
    union, collisions = {}, 0
    for e in h2 + h3:
        key = (e.get("ts"), e.get("machine"))
        if key in union:
            collisions += 1
            assert json.dumps(union[key], sort_keys=True) == json.dumps(e, sort_keys=True), \
                "content-diff on collision key %r (r322 composite-key escalation)" % (key,)
        else:
            union[key] = e
    merged = sorted(union.values(), key=lambda e: e.get("ts") or "")
    newer = d3 if deep_today_ts(d3) >= deep_today_ts(d2) else d2
    doc = dict(newer)
    doc["history"] = merged
    s = json.dumps(doc, ensure_ascii=False, indent=1)
    json.loads(s)
    write_bytes(p, s.encode("utf-8"))
    return (p, "history union %d+%d -> %d (collisions %d content-identical); "
            "latest take-new (%s vs %s)" %
            (len(h2), len(h3), len(merged), collisions,
             deep_today_ts(d2), deep_today_ts(d3)))


def resolve_regime():
    p = "results/regime_state.json"
    d2 = json.loads(stage_bytes(p, 2).decode("utf-8"))
    d3 = json.loads(stage_bytes(p, 3).decode("utf-8"))
    h2, h3 = d2.get("history") or [], d3.get("history") or []
    union = {}
    for e in h2 + h3:
        k = e.get("asof")
        if k in union:
            assert json.dumps(union[k], sort_keys=True) == json.dumps(e, sort_keys=True), \
                "content-diff on asof %r" % (k,)
        else:
            union[k] = e
    merged = sorted(union.values(), key=lambda e: str(e.get("asof") or ""))
    newer = d3 if deep_today_ts(d3) >= deep_today_ts(d2) else d2
    doc = dict(newer)
    if merged:
        doc["history"] = merged
    s = json.dumps(doc, ensure_ascii=False, indent=1)
    json.loads(s)
    write_bytes(p, s.encode("utf-8"))
    return (p, "history union %d+%d -> %d (asof dedup); state take-new" %
            (len(h2), len(h3), len(merged)))


def resolve_x2log():
    p = "results/x2_watch_log.jsonl"
    l2 = stage_bytes(p, 2).decode("utf-8").splitlines()
    l3 = stage_bytes(p, 3).decode("utf-8").splitlines()
    seen, out = set(), []
    for line in l2 + l3:
        if line.strip() and line not in seen:
            seen.add(line)
            out.append(line)
    write_bytes(p, ("\n".join(out) + "\n").encode("utf-8"))
    return (p, "line union %d+%d -> %d zero loss" % (len(l2), len(l3), len(out)))


SNAPSHOTS = [
    ("results/dashboard_status.js", "js-wrapper whole bytes"),
    ("results/dashboard_status.json", "snapshot"),
    ("results/fundamental_b_layer_filter.json", "updated-ts snapshot"),
    ("results/futures_update_status.json", "snapshot"),
    ("results/heat_update_status.json", "snapshot"),
    ("results/lhb_update_status.json", "snapshot"),
    ("results/update_status.json", "snapshot"),
    ("results/token_usage.json", "generated-ts snapshot"),
    # -- 16 classifier-UNKNOWNs: hand-adjudicated ts-snapshot faces (same-
    #    family precedents r323/r324/r325: regen twins + ts-diffpick) --
    ("docs/daily_report/REPORT-20260927.json", "same-day regen twin"),
    ("docs/daily_report/REPORT-20260927.md", "same-day regen twin"),
    ("results/daily_scorecard.json", "forward_guard.as_of deep-ts"),
    ("results/paper/COMPOSITE-CE-01_paper.json", "marks ts face"),
    ("results/paper/COMPOSITE-CE-02_paper.json", "marks ts face"),
    ("results/paper/DROUGHT-CE-01_paper.json", "marks ts face"),
    ("results/paper/ENGULF-CE-01_paper.json", "marks ts face"),
    ("results/paper/NEEDLE-DE-01_paper.json", "marks ts face"),
    ("results/paper/VOLATILITY-CE-01_paper.json", "marks ts face"),
    ("results/paper_export/export-2026-09-24.json", "deterministic idempotent face"),
    ("results/paper_export/latest.json", "deterministic idempotent face"),
    ("results/prospect_paper/_summary.json", "summary ts"),
    ("results/prospect_promotion/_summary.json", "summary ts"),
    ("results/scorecard_v1.json", "generated ts"),
    ("results/strategy_scorecard.json", "generated ts"),
    ("results/t35_open_fill_verify.json", "verify-day ts"),
]


def main():
    rep = [resolve_codely(), resolve_autofill(), resolve_compute_audit(),
           resolve_regime(), resolve_x2log()]
    for p, note in SNAPSHOTS:
        rep.append(take_newer_side(p, note))
    for p, msg in rep:
        print("RESOLVED %-46s %s" % (p, msg))
    # stage everything resolved
    for p, _ in rep:
        subprocess.run(["git", "add", p], capture_output=True)
    print("staged %d resolved files" % len(rep))


if __name__ == "__main__":
    main()
