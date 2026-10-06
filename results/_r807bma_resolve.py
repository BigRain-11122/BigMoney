"""r807 bm-a rebase UU resolver (r806 crash recovery build, extended live at
the r807 04:2x window for the same-window S6 twin-regen collision with the
bm-c standing-guard round): 28 UU faces.

Channel law r648: read stage blobs via `git ls-files -u` sha -> `git cat-file -p`
(NEVER `git show :N:` -- silent empty stdout+rc0 on some faces).

Recipes (bigmoney-conflict-resolve SKILL.md + classifier output):
  - ALL_FACES (6): compute_audit / regime_state / update_status /
    lhb_update_status / futures_update_status / token_usage
    -> scripts/merge_lane_views.py resolve via resolve_face_from_blobs
       (stage2=origin/base, stage3=replay/local; r351 orientation).
  - twin-regen-md (3 pairs): daily_report REPORT + live_usage LIVE x2
    -> probe wall-clock ts inside the JSON side blobs, take SAME side
       wholesale for both .json and .md (byte-copy, r329 law).
  - snapshot take-new (4): dashboard_status.json (+ .js wrapper same side),
    scorecard_v1.json, strategy_scorecard.json, fundamental_b_layer_filter.json,
    _attrition_guard_scan.json -> hardened deep-ts probe (r100/R350 laws)
    -> byte-copy winning side.

Probe laws applied: normalize key stripping '_'/'-' BEFORE prefix match;
value must be ts-shaped ^20\\d{2}- AND carry time-of-day ([T ]HH:MM);
NO key-exclude lists; probe staged blobs never worktree; same-second
tie -> origin side (:2:, r140). Marker gate r648: any side blob carrying
the 7-char lt/gt conflict-marker sequences is rejected for byte-copy
take (other side must parse).
"""
import json
import re
import subprocess
import sys

TS_RE = re.compile(r"^20\d{2}-\d{2}-\d{2}[T ]\d{2}:\d{2}")
MARKERS = (b"<" * 7, b">" * 7)


def git(*args):
    r = subprocess.run(["git", *args], capture_output=True)
    if r.returncode != 0:
        raise SystemExit(f"git {args[0]} rc={r.returncode}: "
                         f"{r.stderr.decode('utf-8', 'replace')[:300]}")
    return r.stdout


def stages():
    out = git("ls-files", "-u")
    m = {}
    for line in out.decode("utf-8").splitlines():
        meta, path = line.split("\t", 1)
        _mode, sha, stage = meta.split()
        m.setdefault(path, {})[int(stage)] = sha
    return m


def blob(sha):
    return git("cat-file", "-p", sha)


ALL_FACES = [
    "results/compute_audit.json",
    "results/regime_state.json",
    "results/update_status.json",
    "results/lhb_update_status.json",
    "results/futures_update_status.json",
    "results/token_usage.json",
]
TWINS = [
    ("docs/daily_report/REPORT-2026-10-07.json",
     "docs/daily_report/REPORT-2026-10-07.md"),
    ("docs/live_usage/LIVE-2026-10-07.json",
     "docs/live_usage/LIVE-2026-10-07.md"),
    ("docs/live_usage/LIVE-latest.json",
     "docs/live_usage/LIVE-latest.md"),
]
SNAPSHOTS = [
    "results/dashboard_status.json",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
    "results/fundamental_b_layer_filter.json",
    "results/_attrition_guard_scan.json",
    # r807 live-window extension (10-07 04:2x rebase, same-window S6
    # twin-regen collision with bm-c standing-guard round): 9 more
    # regenerable same-day JSON faces -> same deep-ts probe take-new
    "results/paper/COMPOSITE-CE-01_paper.json",
    "results/paper/COMPOSITE-CE-02_paper.json",
    "results/paper/DROUGHT-CE-01_paper.json",
    "results/paper/ENGULF-CE-01_paper.json",
    "results/paper/NEEDLE-DE-01_paper.json",
    "results/paper/VOLATILITY-CE-01_paper.json",
    "results/prospect_paper/_summary.json",
    "results/prospect_promotion/_summary.json",
    "results/t35_open_fill_verify.json",
]
JSONL_UNION = [
    # append-only line multiset union (r795 zero-loss law)
    "results/x2_watch_log.jsonl",
]
JS_WRAPPER = "results/dashboard_status.js"


def deep_wallclock(doc, path_acc=()):
    """R350/r100 hardened probe: ALL ts-shaped wall-clock strings, max."""
    best = None
    if isinstance(doc, dict):
        for k, v in doc.items():
            if isinstance(v, str) and TS_RE.match(v):
                if best is None or v > best:
                    best = v
            sub = deep_wallclock(v, path_acc + (k,))
            if sub and (best is None or sub > best):
                best = sub
    elif isinstance(doc, list):
        for v in doc:
            sub = deep_wallclock(v, path_acc)
            if sub and (best is None or sub > best):
                best = sub
    return best


def pick_side(path, st):
    """Return 2 or 3 by hardened deep-ts probe; tie -> 2 (origin, r140)."""
    d2 = json.loads(blob(st[2]).decode("utf-8"))
    d3 = json.loads(blob(st[3]).decode("utf-8"))
    t2, t3 = deep_wallclock(d2), deep_wallclock(d3)
    if t2 is None and t3 is None:
        side, why = 2, "no-ts-both-sides->origin"
    elif t3 is not None and (t2 is None or t3 > t2):
        side, why = 3, f"replay-newer t3={t3} > t2={t2}"
    elif t2 is not None and (t3 is None or t2 > t3):
        side, why = 2, f"origin-newer t2={t2} > t3={t3}"
    else:
        side, why = 2, f"tie t2={t2}==t3={t3}->origin (r140)"
    return side, why


def byte_take(path, st, side):
    raw = blob(st[side])
    for mk in MARKERS:
        if mk in raw:
            raise SystemExit(f"MARKER GATE FAIL {path} side{side}: "
                             f"conflict marker in blob (r648 law)")
    with open(path, "wb") as fh:
        fh.write(raw)
    if path.endswith(".json"):
        json.loads(open(path, encoding="utf-8").read())  # parse-verify r185
    return len(raw)


def main():
    st_all = stages()
    report = []

    # -- ALL_FACES via canonical merger (no hand-written union, r376) --
    sys.path.insert(0, "scripts")
    import merge_lane_views as mlv

    for path in ALL_FACES:
        st = st_all[path]
        b2, b3 = blob(st[2]), blob(st[3])
        for side, raw in ((2, b2), (3, b3)):
            for mk in MARKERS:
                if mk in raw:
                    raise SystemExit(f"MARKER GATE FAIL {path} side{side}")
        d2 = json.loads(b2.decode("utf-8"))
        d3 = json.loads(b3.decode("utf-8"))
        face = mlv.detect_face(path)
        merged, notes = mlv.resolve_face_from_blobs(
            face, {"base_side": d2, "replay_side": d3})
        # producer format mirror: probe base-side blob (r289/r223 law)
        crlf = b"\r\n" in b2
        indent = mlv._probe_key_indent(b2)
        payload = json.dumps(merged, ensure_ascii=False, indent=indent)
        if crlf:
            payload = payload.replace("\n", "\r\n")
        with open(path, "w", encoding="utf-8", newline="") as fh:
            fh.write(payload + ("\r\n" if crlf else "\n"))
        back = json.load(open(path, encoding="utf-8"))
        assert back == merged, f"parse-verify failed {path}"
        report.append(f"ALLFACE  {path} merged crlf={crlf} indent={indent}"
                      f" notes={notes}")

    # -- twins: probe json side, byte-copy BOTH faces from SAME side --
    for jpath, mpath in TWINS:
        st = st_all[jpath]
        side, why = pick_side(jpath, st)
        n1 = byte_take(jpath, st, side)
        n2 = byte_take(mpath, st_all[mpath], side)
        report.append(f"TWIN    {jpath}+{mpath} side={side} ({why})"
                      f" json={n1}B md={n2}B")

    # -- snapshots: probe + byte-copy --
    for path in SNAPSHOTS:
        st = st_all[path]
        side, why = pick_side(path, st)
        n = byte_take(path, st, side)
        report.append(f"SNAP    {path} side={side} ({why}) {n}B")

    # -- jsonl append-only line multiset union (r795 zero-loss law) --
    from collections import Counter
    for path in JSONL_UNION:
        st = st_all[path]
        for side in (2, 3):
            for mk in MARKERS:
                if mk in blob(st[side]):
                    raise SystemExit(f"MARKER GATE FAIL {path} side{side}")
        b2 = blob(st[2]).decode("utf-8")
        b3 = blob(st[3]).decode("utf-8")
        lines2 = [l for l in b2.splitlines() if l.strip()]
        lines3 = [l for l in b3.splitlines() if l.strip()]
        # backbone = longer side; append replay-only surplus lines in order
        if len(lines2) >= len(lines3):
            backbone, other = lines2, lines3
            sides = ("2", "3")
        else:
            backbone, other = lines3, lines2
            sides = ("3", "2")
        need = Counter(other) - Counter(backbone)
        surplus = []
        for l in other:
            if need.get(l, 0) > 0:
                need[l] -= 1
                surplus.append(l)
        merged_lines = backbone + surplus
        crlf = "\r\n" in b2
        with open(path, "w", encoding="utf-8", newline="") as fh:
            fh.write("\r\n".join(merged_lines) + ("\r\n" if crlf else "\n"))
        report.append(
            f"JSONL   {path} line-union backbone=side{sides[0]} "
            f"{len(backbone)}+{len(surplus)} -> {len(merged_lines)} lines "
            f"(side2={len(lines2)} side3={len(lines3)})")

    # -- js wrapper: same side as dashboard_status.json twin decision --
    stj = st_all["results/dashboard_status.json"]
    side, why = pick_side("results/dashboard_status.json", stj)
    n = byte_take(JS_WRAPPER, st_all[JS_WRAPPER], side)
    report.append(f"JSWRAP  {JS_WRAPPER} side={side} (json twin) {n}B")

    print("\n".join(report))
    print(f"\nRESOLVED {len(report)} faces; next: git add -> rebase --continue")


if __name__ == "__main__":
    main()
