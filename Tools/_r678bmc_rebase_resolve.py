# -*- coding: utf-8 -*-
"""r678 bm-c rebase-conflict per-face resolver (18-UU, push-race window vs
bm-a r825 estate wave; first push claw-blocked on behind-signal phantom
deletions per MSG-0612 family, zero --no-verify).

Blood lineage: Tools/_r672bmc_rebase_resolve.py (same-window family), with
four law upgrades:
  * r648 channel: stage blobs read via ls-files -u sha -> cat-file -p
    (NEVER git show :N: -- empty-stdout rc0 trap), len>100 gate (r710B);
    marker scan hard gate on every chosen blob (origin side may carry
    unresolved markers, r648/r804 family) -> polluted side swaps, both
    polluted = abort.
  * r711/r756 normalization: every extracted stamp parsed via
    datetime.fromisoformat (space/T both accepted) before comparing; raw
    string max is forbidden (dict-order T>space poison).
  * r708 twin same-side law: REPORT md follows REPORT json; LIVE-2026-10-07
    md + LIVE-latest json/md follow LIVE-2026-10-07 json decision.
  * r794 targeted adds only (no add -u loops); daemon churn absorbed by the
    caller's atomic add -A + rebase --continue (r787).
Classes: compute_audit/regime_state -> rolling history union (scalars newer
side, rows identity-dedup, r758); token_usage -> per-key max-union (r758/
r456); everything else -> normalized ts-duel newer-wins, tie -> stage2
origin (r140 per r794).
Stage semantics: REBASE window -> stage2=onto(origin bm-a estate),
stage3=replayed commit(mine r678) -- opposite of merge (r782-bma law).
Receipt -> results/_r678bmc_rebase_resolve.json."""
import datetime as _dt
import json
import os
import re
import subprocess
import sys

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
CREATE_NO_WINDOW = 0x08000000
RECEIPT = os.path.join(ROOT, "results", "_r678bmc_rebase_resolve.json")
UNION_HISTORY_FACES = {"results/compute_audit.json", "results/regime_state.json"}
UNION_MAX_FACES = {"results/token_usage.json"}
TWIN_GROUPS = [
    ("docs/daily_report/REPORT-2026-10-07.json", [
        "docs/daily_report/REPORT-2026-10-07.json",
        "docs/daily_report/REPORT-2026-10-07.md"]),
    ("docs/live_usage/LIVE-2026-10-07.json", [
        "docs/live_usage/LIVE-2026-10-07.json",
        "docs/live_usage/LIVE-2026-10-07.md",
        "docs/live_usage/LIVE-latest.json",
        "docs/live_usage/LIVE-latest.md"]),
]
TS_PAT = re.compile(
    r'"(?:generated|ts|updated_at|updated|last_run_at|generated_at|asof'
    r'|scan_ts|cutoff|written_at)"\s*:\s*"?(\d{4}-\d{2}-\d{2}[T ][\d:.]+'
    r'(?:[+-]\d{2}:?\d{2})?)')
MARKER_PAT = re.compile(r"^(<{7}|>{7} |={7}$)", re.M)


def _git(args):
    r = subprocess.run(["git", "-C", ROOT] + args, capture_output=True,
                       creationflags=CREATE_NO_WINDOW)
    return r.returncode, (r.stdout or b""), (r.stderr or b"")


def _stage_blobs(path):
    """r648 channel: ls-files -u shas -> cat-file -p; len>100 gate."""
    rc, out, err = _git(["ls-files", "-u", "--", path])
    assert rc == 0, "ls-files fail %s: %s" % (path, err.decode(errors="replace"))
    blobs = {}
    for line in out.decode("utf-8", "replace").splitlines():
        parts = line.split("\t")
        meta = parts[0].split()
        if len(parts) >= 2 and len(meta) >= 3:
            blobs[int(meta[2])] = meta[1]
    assert 2 in blobs and 3 in blobs, "stage 2/3 missing for %s (r405 guard)" % path
    res = {}
    for stage, sha in ((2, blobs[2]), (3, blobs[3])):
        rc, out, err = _git(["cat-file", "-p", sha])
        assert rc == 0, "cat-file fail %s" % sha
        assert len(out) > 100, "stage blob too small %s stage %d (r710B gate)" % (path, stage)
        res[stage] = out
    return res[2], res[3]


def _norm_ts(stamp):
    try:
        return _dt.datetime.fromisoformat(stamp)
    except ValueError:
        try:
            return _dt.datetime.fromisoformat(stamp.replace(" ", "T", 1))
        except ValueError:
            return None


def _max_ts(blob):
    if blob is None:
        return None
    txt = blob.decode("utf-8", errors="replace")
    parsed = [t for t in (_norm_ts(s) for s in TS_PAT.findall(txt)) if t]
    return max(parsed) if parsed else None


def _marker_clean(blob):
    return not MARKER_PAT.search(blob.decode("utf-8", errors="replace"))


def _pick(path, b2, b3):
    """Return (blob, why). Only called for non-union, non-twin-follower faces."""
    ts2, ts3 = _max_ts(b2), _max_ts(b3)
    if ts3 is not None and (ts2 is None or ts3 > ts2):
        blob, why = b3, "ts-duel local newer (%s > %s)" % (ts3, ts2)
    elif ts2 is not None and (ts3 is None or ts2 > ts3):
        blob, why = b2, "ts-duel origin newer (%s > %s)" % (ts2, ts3)
    else:
        blob, why = b2, "tie/no-ts -> stage2 origin (r140 per r794)"
    if not _marker_clean(blob):
        other = b3 if blob is b2 else b2
        assert _marker_clean(other), "both sides marker-polluted %s (abort)" % path
        blob = other
        why += " | marker-polluted side swapped (r648 gate)"
    return blob, why, ts2, ts3


def _union_history(b2, b3):
    ts2, ts3 = _max_ts(b2), _max_ts(b3)
    if ts3 is not None and (ts2 is None or ts3 >= ts2):
        base, other, newer = json.loads(b3), json.loads(b2), "local"
    else:
        base, other, newer = json.loads(b2), json.loads(b3), "origin"
    hist_key = None
    for k in ("history",):
        if k in base or k in other:
            hist_key = k
            break
    if hist_key:
        seen = set()
        merged = []
        for row in list(base.get(hist_key) or []) + list(other.get(hist_key) or []):
            ident = json.dumps(row, sort_keys=True, ensure_ascii=False)
            if ident not in seen:
                seen.add(ident)
                merged.append(row)
        base[hist_key] = merged
    return json.dumps(base, ensure_ascii=False, indent=1).encode("utf-8"), \
        "rolling history union (scalars newer=%s, rows identity-dedup zero-loss, r758)" % newer


def _num_max(a, b):
    if isinstance(a, dict) and isinstance(b, dict):
        out = dict(a)
        for k, v in b.items():
            out[k] = _num_max(out[k], v) if k in out else v
        return out
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return max(a, b)
    return a


def _max_union(b2, b3):
    ts2, ts3 = _max_ts(b2), _max_ts(b3)
    if ts3 is not None and (ts2 is None or ts3 >= ts2):
        base, other = json.loads(b3), json.loads(b2)
    else:
        base, other = json.loads(b2), json.loads(b3)
    for key in ("machines", "l2_local_llm"):
        if key in base and key in other:
            merged = dict(other[key])
            for k, v in base[key].items():
                merged[k] = _num_max(merged[k], v) if k in merged else v
            base[key] = merged
    return json.dumps(base, ensure_ascii=False, indent=1).encode("utf-8"), \
        "per-key max-union (r758/r456 canon, counters recursive max)"


def main():
    rc, out, _ = _git(["diff", "--name-only", "--diff-filter=U"])
    files = sorted(f.strip() for f in out.decode("utf-8", "replace").splitlines()
                   if f.strip())
    assert files, "no UU files -- wrong context"
    blobs = {p: _stage_blobs(p) for p in files}
    decisions = []
    decided = {}

    def emit(path, blob, why, ts2=None, ts3=None):
        assert path not in decided, "double decision %s" % path
        if not _marker_clean(blob):
            b2, b3 = blobs[path]
            other = b3 if blob is b2 else b2
            assert _marker_clean(other), "both sides polluted %s" % path
            blob, why = other, why + " | marker swap (r648)"
        full = os.path.join(ROOT, path.replace("/", os.sep))
        with open(full, "wb") as fh:
            fh.write(blob)
        if path.endswith(".json"):
            json.loads(open(full, "rb").read().decode("utf-8"))  # reparse gate
        rca, _, erra = _git(["add", "--", path])
        assert rca == 0, "add fail %s: %s" % (path, erra.decode(errors="replace"))
        decided[path] = True
        decisions.append({"path": path, "rule": why,
                          "ts_origin": str(ts2), "ts_local": str(ts3)})
        print("RESOLVED %-46s (%s)" % (path, why))

    # 1) union classes (marker pre-gate: single polluted side -> whole clean
    #    side per r648; both polluted -> abort)
    for path in files:
        if path in UNION_HISTORY_FACES or path in UNION_MAX_FACES:
            b2, b3 = blobs[path]
            c2, c3 = _marker_clean(b2), _marker_clean(b3)
            if c2 and not c3:
                emit(path, b2, "origin clean, local polluted -> origin whole-side (r648)")
                continue
            if c3 and not c2:
                emit(path, b3, "local clean, origin polluted -> local whole-side (r648)")
                continue
            assert c2 and c3, "both sides marker-polluted %s (abort)" % path
            if path in UNION_HISTORY_FACES:
                blob, why = _union_history(b2, b3)
            else:
                blob, why = _max_union(b2, b3)
            emit(path, blob, why)

    # 2) twin groups: primary ts-duel decides, members follow (r708)
    for primary, members in TWIN_GROUPS:
        if primary in decided:
            continue
        group_present = [m for m in members if m in blobs]
        if primary not in blobs:
            continue
        b2, b3 = blobs[primary]
        blob, why, ts2, ts3 = _pick(primary, b2, b3)
        side = 3 if blob is b3 else 2
        emit(primary, blob, why + " | twin-primary", ts2, ts3)
        for m in group_present:
            if m in decided:
                continue
            mb = blobs[m][side - 2]
            emit(m, mb, "twin same-side follows %s (r708, side=%s)" % (primary, "local" if side == 3 else "origin"))

    # 3) everything else: normalized ts-duel
    for path in files:
        if path in decided:
            continue
        b2, b3 = blobs[path]
        blob, why, ts2, ts3 = _pick(path, b2, b3)
        emit(path, blob, why, ts2, ts3)

    with open(RECEIPT, "w", encoding="utf-8", newline="\n") as fh:
        json.dump({"round": 678, "machine": "bm-c",
                   "context": "push-race 18-UU rebase window vs bm-a r825 estate (first push claw-blocked behind-signal phantom deletions, zero --no-verify)",
                   "n_faces": len(decisions), "faces": decisions},
                  fh, ensure_ascii=False, indent=1)
    print("receipt:", os.path.relpath(RECEIPT, ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
