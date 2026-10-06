r"""r775 rebase 14-UU resolver: shared regeneration faces.

Rebase direction note: during `git rebase origin/main`, stage-2 (ours) = the
new base (origin/main side, written by bm-a/bm-c up to 14:39), stage-3
(theirs) = replayed r775 leg3 commit (bm-b S6 chain regen @ ~14:33).

Recipes (bigmoney-conflict-resolve skill / r773 per-face take-newer-by-ts,
r756 mixed-separator normalization, r758 union+ts-stable-sort):
  - snapshot faces: parse ts per side (normalize ' '->'T', naive -> +08:00),
    take newer side wholesale.
  - rolling-ledger faces (compute_audit.json, regime_state.json):
    ledger keys -> entry-level union dedup + ts-stable-sort (zero loss);
    state fields -> newer-side wins.
Probe mode prints per-face verdict; --apply writes resolved bytes + parse-verify.
"""
import json
import subprocess
import sys
from datetime import datetime, timedelta, timezone

FACES = [
    "docs/daily_report/REPORT-2026-10-06.json",
    "docs/daily_report/REPORT-2026-10-06.md",
    "docs/live_usage/LIVE-2026-10-06.json",
    "docs/live_usage/LIVE-2026-10-06.md",
    "docs/live_usage/LIVE-latest.json",
    "docs/live_usage/LIVE-latest.md",
    "results/compute_audit.json",
    "results/fundamental_b_layer_filter.json",
    "results/fundamental_status.json",
    "results/futures_update_status.json",
    "results/lhb_update_status.json",
    "results/regime_state.json",
    "results/token_usage.json",
    "results/update_status.json",
]

LEDGER_KEYS = ("history", "launches", "transitions", "entries", "checks")
LOCAL_TZ = timezone(timedelta(hours=8))


def blob(stage, path):
    r = subprocess.run(["git", "show", ":%d:%s" % (stage, path)],
                       capture_output=True)
    if r.returncode != 0:
        raise RuntimeError("git show :%d:%s rc=%d %r" % (stage, path, r.returncode, r.stderr[:200]))
    return r.stdout


def parse_ts(v):
    if not isinstance(v, str):
        return None
    s = v.strip().replace(" ", "T")
    for fmt in ("%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%S",
                "%Y-%m-%dT%H:%M:%S.%f%z", "%Y-%m-%dT%H:%M:%S.%f"):
        try:
            dt = datetime.strptime(s, fmt)
        except ValueError:
            continue
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=LOCAL_TZ)
        return dt
    return None


def face_ts(data):
    """Max parseable datetime among top-level + depth-1 dict string values
    (covers compute_audit's nested 'latest'; r756 normalize)."""
    if isinstance(data, dict):
        best = None
        best_k = None
        for k, v in data.items():
            if k in LEDGER_KEYS:
                continue
            cands = []
            if isinstance(v, str):
                cands.append((k, v))
            elif isinstance(v, dict):
                cands.extend((k + "." + k2, v2) for k2, v2 in v.items()
                             if isinstance(v2, str))
            for ck, cv in cands:
                t = parse_ts(cv)
                if t and (best is None or t > best):
                    best, best_k = t, ck
        return best, best_k
    # markdown: scan 'YYYY-MM-DD HH:MM:SS' / ISO stamps in first 40 lines
    best = None
    text = data if isinstance(data, str) else data.decode("utf-8", "replace")
    for m in __import__("re").finditer(
            r"\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}(:\d{2})?", "\n".join(text.splitlines()[:40])):
        t = parse_ts(m.group(0))
        if t and (best is None or t > best):
            best = t
    return best, "md-scan"


def entry_ts(e):
    if not isinstance(e, dict):
        return None
    for k, v in e.items():
        if isinstance(v, str) and any(t in k.lower() for t in ("ts", "time", "date", "at")):
            t = parse_ts(v)
            if t:
                return t
    return None


def union_ledger(a, b):
    """Entry-level union dedup + ts-stable sort (r758). Returns merged list."""
    seen = {}
    order = []
    for e in list(a or []) + list(b or []):
        key = json.dumps(e, ensure_ascii=False, sort_keys=True)
        if key not in seen:
            seen[key] = e
            order.append(e)
    def sort_key(e):
        return entry_ts(e) or datetime.min.replace(tzinfo=LOCAL_TZ)
    return sorted([seen[k] for k in seen], key=sort_key)


def resolve_face(path):
    ours_b, theirs_b = blob(2, path), blob(3, path)
    if ours_b == theirs_b:
        return {"path": path, "recipe": "identical", "side": "same", "ts_ours": None, "ts_theirs": None}
    # markdown twins: take newer by scanned stamp, but content is human doc -> prefer newer side wholesale
    if path.endswith(".md") or not path.endswith(".json"):
        to, ko = face_ts(ours_b.decode("utf-8", "replace"))
        tt, kt = face_ts(theirs_b.decode("utf-8", "replace"))
        side = "ours" if (to or datetime.min.replace(tzinfo=LOCAL_TZ)) >= (tt or datetime.min.replace(tzinfo=LOCAL_TZ)) else "theirs"
        return {"path": path, "recipe": "md-take-newer", "side": side,
                "ts_ours": str(to), "ts_theirs": str(tt)}
    try:
        ours, theirs = json.loads(ours_b), json.loads(theirs_b)
    except Exception as exc:
        return {"path": path, "recipe": "ERROR-unparseable", "err": str(exc)}
    to, ko = face_ts(ours)
    tt, kt = face_ts(theirs)
    has_ledger = any(isinstance(ours.get(k), list) and k in LEDGER_KEYS for k in LEDGER_KEYS)
    merged = {}
    if has_ledger:
        base = theirs if (tt or datetime.min.replace(tzinfo=LOCAL_TZ)) >= (to or datetime.min.replace(tzinfo=LOCAL_TZ)) else ours
        other = ours if base is theirs else theirs
        merged = dict(base)
        for k in LEDGER_KEYS:
            if isinstance(base.get(k), list) or isinstance(other.get(k), list):
                merged[k] = union_ledger(base.get(k), other.get(k))
        return {"path": path, "recipe": "union-ledger+newer-state", "side": "newer=%s" % ("theirs" if base is theirs else "ours"),
                "ts_ours": "%s(%s)" % (to, ko), "ts_theirs": "%s(%s)" % (tt, kt),
                "merged": merged}
    side = "ours" if (to or datetime.min.replace(tzinfo=LOCAL_TZ)) >= (tt or datetime.min.replace(tzinfo=LOCAL_TZ)) else "theirs"
    return {"path": path, "recipe": "snapshot-take-newer", "side": side,
            "ts_ours": "%s(%s)" % (to, ko), "ts_theirs": "%s(%s)" % (tt, kt),
            "merged": ours if side == "ours" else theirs}


def main():
    apply = "--apply" in sys.argv
    for path in FACES:
        info = resolve_face(path)
        merged = info.pop("merged", None)
        side = info.get("side", "?")
        print("[%(path)s] %(recipe)s -> %(side)s | ours=%(ts_ours)s theirs=%(ts_theirs)s" % {
            "path": info["path"], "recipe": info["recipe"], "side": side,
            "ts_ours": info.get("ts_ours"), "ts_theirs": info.get("ts_theirs")})
        if "err" in info:
            print("  ERROR:", info["err"])
        if apply and merged is not None:
            data = json.dumps(merged, ensure_ascii=False, indent=2).encode("utf-8")
            json.loads(data.decode("utf-8"))  # parse-verify before write (r185)
            with open(path, "wb") as f:
                f.write(data)
        elif apply and info["recipe"] == "md-take-newer":
            src = blob(2 if side == "ours" else 3, path)
            with open(path, "wb") as f:
                f.write(src)
        elif apply and info["recipe"] == "snapshot-take-newer":
            src = blob(2 if side == "ours" else 3, path)
            json.loads(src.decode("utf-8"))  # parse-verify (r185)
            with open(path, "wb") as f:
                f.write(src)
    print("APPLY" if apply else "PROBE-ONLY (pass --apply to write)")


if __name__ == "__main__":
    main()
