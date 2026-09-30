# r469 bm-b S7 stash-pop UU resolver (r467 canon verbatim lineage; r462 stash-pop law)
# Wave-1 conflict: replay of 4ece8eddb (r466 base, writes ~14:15-16) onto origin/main
# d7bd079b3 (bm-a r475 + bm-c r273 re-derives ~14:22-25) -> 30 UU.
# Direction law (r461): NEVER assume by rebase common sense -- per-file ts probe BOTH
# staged blobs, take strictly newer (tie -> :2 HEAD per r140). Probe laws r100/R208/R350:
# deep-scan nested, value must be ts-shaped WITH time-of-day, staged-blob only.
# Recipes: snapshot=take-new whole bytes (+twin same-side forced); rolling-ledger
# (compute_audit/regime_state)=union zero-loss + state take-newer; append-log=superset
# take / else line union; paper accounts=months_detail union-by-month + state take-newer;
# autofill mixed-dict+ledger=launches union cap50 re-sort asc + last_tick ts-compare;
# single-writer mine (state.json, fleet/machines/bm-b.json)=take :3; memory CODELY.md=
# line union dedupe (r208/r212); js-wrapper whole-bytes (R209); parse-validate (r185).
# Re-runnable for subsequent replay waves + stash-pop UU (r462): re-classifies whatever
# UU set exists at invocation time. Fail-closed: unmatched path -> report, no write.
import json
import re
import subprocess
import sys

TS_RE = re.compile(r"20\d{2}-\d{2}-\d{2}[T ]\d{2}:\d{2}(?::\d{2})?")
TS_FULL_RE = re.compile(r"^20\d{2}-\d{2}-\d{2}[T ]\d{2}:\d{2}(:\d{2}(\.\d+)?)?(\+\d{2}:\d{2})?$")

PAPER_ACCOUNTS = [f"results/paper/{t}_paper.json" for t in
                  ["COMPOSITE-CE-01", "COMPOSITE-CE-02", "DROUGHT-CE-01",
                   "ENGULF-CE-01", "NEEDLE-DE-01", "VOLATILITY-CE-01"]]
TWIN_GROUPS = {
    "REPORT": ["docs/daily_report/REPORT-2026-09-30.json", "docs/daily_report/REPORT-2026-09-30.md"],
    "LIVE": ["docs/live_usage/LIVE-2026-09-30.json", "docs/live_usage/LIVE-2026-09-30.md",
             "docs/live_usage/LIVE-latest.json", "docs/live_usage/LIVE-latest.md"],
    "DASH": ["results/dashboard_status.js", "results/dashboard_status.json"],
    "SCORECARD": ["results/strategy_scorecard.json", "results/scorecard_v1.json"],
}
MINE_ALWAYS = {"state.json", "fleet/machines/bm-b.json"}


def sh(args):
    return subprocess.run(args, capture_output=True)


def stage_bytes(stage, path):
    r = sh(["git", "show", f":{stage}:{path}"])
    if r.returncode != 0:
        sys.exit(f"stage read fail {stage} {path}: {r.stderr[:200]}")
    return r.stdout


def uu_paths():
    out = sh(["git", "ls-files", "-u"]).stdout.decode("utf-8")
    seen = []
    for ln in out.splitlines():
        parts = ln.split()
        if len(parts) >= 4 and parts[3] not in seen:
            seen.append(parts[3])
    return seen


def deep_ts(obj, best=""):
    if isinstance(obj, dict):
        for v in obj.values():
            best = deep_ts(v, best)
    elif isinstance(obj, list):
        for v in obj:
            best = deep_ts(v, best)
    elif isinstance(obj, str):
        for m in TS_RE.finditer(obj):
            c = m.group(0)
            if len(c) >= 16 and c > best:
                best = c
    return best


def probe(stage, path):
    b = stage_bytes(stage, path)
    if path.endswith(".json"):
        try:
            return deep_ts(json.loads(b.decode("utf-8")))
        except Exception:
            pass
    m = TS_RE.findall(b.decode("utf-8", errors="replace"))
    return max(m) if m else ""


def take_whole(path, side, log, note=""):
    b = stage_bytes(side, path)
    assert b"<<<<<<<" not in b, f"{path}: s{side} blob has markers"
    if path.endswith(".json"):
        json.loads(b.decode("utf-8"))  # parse-validate before write (r185)
    with open(path, "wb") as f:
        f.write(b)
    sh(["git", "add", path])
    log.append(f"{path}: take-s{side} whole-bytes {len(b)}B {note}")


def detect_fmt(raw_text):
    nl = "\r\n" if "\r\n" in raw_text else "\n"
    m = re.search(r"\n( +)\"", raw_text)
    indent = len(m.group(1)) if m else 2
    return nl, indent


def write_json(path, obj, raw_ref, log):
    nl, indent = detect_fmt(raw_ref)
    with open(path, "w", encoding="utf-8", newline="") as f:
        json.dump(obj, f, ensure_ascii=False, indent=indent)
        f.write(nl)
    json.loads(open(path, "r", encoding="utf-8").read())  # roundtrip validate
    sh(["git", "add", path])


def union_jsonl(path, log):
    b2 = stage_bytes(2, path).decode("utf-8")
    b3 = stage_bytes(3, path).decode("utf-8")
    l2 = [x for x in b2.splitlines() if x.strip()]
    l3 = [x for x in b3.splitlines() if x.strip()]
    s2, s3 = set(l2), set(l3)
    if not (s2 - s3):  # :3 strict superset -> wholesale take (r461 superset law)
        take_whole(path, 3, log, note=f"strict-superset :2={len(l2)}<:3={len(l3)}")
        return
    if not (s3 - s2):
        take_whole(path, 2, log, note=f"strict-superset :3={len(l3)}<:2={len(l2)}")
        return
    # dual-sided unique lines -> ts-sorted line union zero loss (r188)
    rows = []
    for ln in l2 + [x for x in l3 if x not in s2]:
        obj = json.loads(ln)  # validate each row (r185)
        ts = obj.get("ts", "") if isinstance(obj, dict) else ""
        rows.append((ts, ln))
    rows.sort(key=lambda r: r[0])
    union = [r[1] for r in rows]
    assert set(union) == (s2 | s3), f"{path} union loss"
    assert len(union) >= max(len(l2), len(l3))
    nl = "\r\n" if "\r\n" in b2 else "\n"
    with open(path, "wb") as f:
        f.write((nl.join(union) + nl).encode("utf-8"))
    sh(["git", "add", path])
    log.append(f"{path}: union {len(l2)}+{len(l3)} only2={len(s2-s3)} only3={len(s3-s2)} -> {len(union)} zero-loss")


def union_paper_account(path, log):
    a = json.loads(stage_bytes(2, path).decode("utf-8"))
    b = json.loads(stage_bytes(3, path).decode("utf-8"))
    t2, t3 = deep_ts(a), deep_ts(b)
    base, other = (b, a) if t3 > t2 else (a, b)  # take-new state, tie->:2(a)
    res = dict(base)
    md_b = base.get("months_detail") or []
    md_o = other.get("months_detail") or []
    seen, union = {e.get("month") for e in md_b}, list(md_b)
    for e in md_o:
        if e.get("month") not in seen:
            seen.add(e.get("month"))
            union.append(e)
    union.sort(key=lambda e: e.get("month", ""))
    assert len(union) >= max(len(md_b), len(md_o)), f"{path} months union loss"
    res["months_detail"] = union
    newer = 3 if t3 > t2 else 2
    write_json(path, res, stage_bytes(newer, path).decode("utf-8"), log)
    log.append(f"{path}: state take-s{newer} (ts {t2!r} vs {t3!r}), months_detail union {len(md_b)}+{len(md_o)}->{len(union)}")


def union_ledger(path, list_specs, log):
    """list_specs: {key: ident_getter}; state fields take-newer side."""
    a = json.loads(stage_bytes(2, path).decode("utf-8"))
    b = json.loads(stage_bytes(3, path).decode("utf-8"))
    t2, t3 = deep_ts(a), deep_ts(b)
    newer = 3 if t3 > t2 else 2
    base = b if newer == 3 else a
    res = dict(base)
    rep = []
    for k, ident in list_specs.items():
        la = a.get(k) or []
        lb = b.get(k) or []
        ka = {ident(e): e for e in la}
        kb = {ident(e): e for e in lb}
        merged = dict(ka)
        merged.update(kb)
        hist = sorted(merged.values(), key=ident)
        assert len(hist) >= max(len(la), len(lb)), f"{path}.{k} union loss"
        assert len(hist) == len(set(ka) | set(kb)), f"{path}.{k} union key mismatch"
        res[k] = hist
        rep.append(f"{k}:{len(la)}+{len(lb)}->{len(hist)}")
    write_json(path, res, stage_bytes(newer, path).decode("utf-8"), log)
    log.append(f"{path}: union[{' '.join(rep)}] state-take-s{newer} (ts {t2!r} vs {t3!r})")


def union_autofill(path, log):
    a = json.loads(stage_bytes(2, path).decode("utf-8"))
    b = json.loads(stage_bytes(3, path).decode("utf-8"))
    la = a.get("launches") or []
    lb = b.get("launches") or []
    key = lambda e: e.get("ts") or ""
    ka = {key(e): e for e in la}
    kb = {key(e): e for e in lb}
    merged = dict(ka)
    merged.update(kb)
    union = sorted(merged.values(), key=key, reverse=True)[:50]  # cap=newest 50 (bm-b r245)
    union.sort(key=key)  # write-back order = ts ASC (producer append order)
    t2 = (a.get("last_tick") or {}).get("ts", "")
    t3 = (b.get("last_tick") or {}).get("ts", "")
    last_tick = b.get("last_tick") if t3 >= t2 else a.get("last_tick")  # ts-compare, no str() (r140)
    res = dict(a if t3 < t2 else b)
    res["launches"] = union
    res["last_tick"] = last_tick
    assert isinstance(last_tick, dict), f"{path} last_tick not dict"
    write_json(path, res, stage_bytes(3 if t3 >= t2 else 2, path).decode("utf-8"), log)
    log.append(f"{path}: launches union {len(la)}+{len(lb)}->cap50={len(union)}, last_tick ts-compare -> {last_tick.get('ts')}")


def union_memory(path, log):
    t2 = stage_bytes(2, path).decode("utf-8").splitlines()
    t3 = stage_bytes(3, path).decode("utf-8").splitlines()
    out, seen = [], set()
    for ln in t2 + [x for x in t3 if x not in set(t2)]:
        if ln in seen:
            continue
        seen.add(ln)
        out.append(ln)
    nl = "\r\n" if "\r\n" in stage_bytes(2, path).decode("utf-8", errors="replace") else "\n"
    with open(path, "wb") as f:
        f.write((nl.join(out) + nl).encode("utf-8"))
    sh(["git", "add", path])
    log.append(f"{path}: memory line-union {len(t2)}+{len(t3)}->{len(out)}")


def main():
    paths = uu_paths()
    log = []
    unresolved = []
    handled = set()
    # 1) twin groups: probe json member, force whole group same side
    for gname, members in TWIN_GROUPS.items():
        hits = [p for p in paths if p in members]
        if not hits:
            continue
        t2, t3 = probe(2, members[0]), probe(3, members[0])
        assert TS_FULL_RE.match(t2) or t2 == "", f"{members[0]} s2 probe bad {t2!r}"
        side = 3 if t3 > t2 else 2  # tie -> :2 (r140)
        for p in hits:
            take_whole(p, side, log, note=f"twin-{gname} probe s2={t2!r} s3={t3!r}")
            handled.add(p)
    for p in paths:
        if p in handled:
            continue
        if p in MINE_ALWAYS:
            take_whole(p, 3, log, note="single-writer-mine")
        elif p.endswith(".jsonl"):
            union_jsonl(p, log)
        elif p == "results/compute_audit.json":
            union_ledger(p, {"history": lambda e: e.get("ts") or ""}, log)
        elif p == "results/regime_state.json":
            union_ledger(p, {"history": lambda e: e.get("asof") or "",
                             "transitions": lambda e: (e.get("ts") if isinstance(e, dict) else str(e)) or ""},
                         log)
        elif p in PAPER_ACCOUNTS:
            union_paper_account(p, log)
        elif "autofill_state" in p and p.endswith(".json"):
            union_autofill(p, log)
        elif p == "CODELY.md":
            union_memory(p, log)
        elif p.endswith(".json"):
            t2, t3 = probe(2, p), probe(3, p)
            assert TS_FULL_RE.match(t2) and TS_FULL_RE.match(t3), f"{p}: probe not ts-shaped ({t2!r} vs {t3!r})"
            side = 3 if t3 > t2 else 2
            take_whole(p, side, log, note=f"probe s2={t2!r} s3={t3!r}")
        else:
            unresolved.append(p)
    for ln in log:
        print(f"[resolved] {ln}")
    if unresolved:
        print("UNRESOLVED (fail-closed, no write):", unresolved)
        return 2
    leftover = sh(["git", "ls-files", "-u"]).stdout.decode("utf-8").strip()
    print("leftover-UU:", leftover or "NONE")
    return 0 if not leftover else 2


if __name__ == "__main__":
    sys.exit(main())

