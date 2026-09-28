"""r405 bm-a push-storm resolver (vs bm-c r188-189 + bm-b r400 window).

ALL_FACES 7 件已先走 merge_lane_views.py resolve（禁手写 union，r376）:
compute_audit / regime_state / update_status / lhb / futures / token_usage.
本脚本只解非 lane 面剩余 13 件，配方全部照 bigmoney-conflict-resolve SKILL:
- post_review.jsonl / x2_watch_log.jsonl          -> append-log 行级 union 零丢失 (r188/r217)
- daily_scorecard / scorecard_v1 / strategy_scorecard
  / prospect_promotion/_summary
  / fundamental_b_layer_filter                    -> snapshot deep-ts probe take-new (r98/r99/r100/R350)
- dashboard_status.json probe take-new; .js SAME side whole bytes (R209 pair law)
- REPORT-2026-09-29 + LIVE-2026-09-29 twins        -> json probe, md byte-copy SAME side (r327/r329)
- post_review/REPORT-20260929.md                   -> same-day regen md, take-new by 生成 ts line
Stages during rebase replay: :2: = origin side, :3: = local side (r351 law).
"""
import json
import re
import subprocess
import sys

TS_PAT = re.compile(r"20\d{2}-\d{2}-\d{2}[T ]\d{2}:\d{2}(:\d{2})?")
GEN_PAT = re.compile(r"^生成 (20\d{2}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})", re.M)
FAIL = []


def git_blob(stage, path):
    r = subprocess.run(["git", "show", f":{stage}:{path}"], capture_output=True)
    if r.returncode != 0:
        raise RuntimeError(f"blob read fail {stage} {path}: {r.stderr[:200]}")
    return r.stdout


def deep_ts(obj, best=None):
    """Deep-scan nested layers for wall-clock ts values (r311/D-09; time-of-day required per R350)."""
    if best is None:
        best = ""
    if isinstance(obj, dict):
        for k, v in obj.items():
            kn = str(k).replace("_", "").replace("-", "").lower()
            if isinstance(v, str) and TS_PAT.match(v) and ("ts" in kn or "time" in kn or "at" in kn or "date" in kn or "run" in kn or "cutoff" in kn or "updated" in kn):
                if v > best:
                    best = v
            else:
                best = deep_ts(v, best)
    elif isinstance(obj, list):
        for it in obj:
            best = deep_ts(it, best)
    elif isinstance(obj, str) and TS_PAT.match(obj) and len(obj) >= 16:
        if obj > best:
            best = obj
    return best


def take_new_json(path):
    o3 = git_blob(3, path)  # local (mine)
    o2 = git_blob(2, path)  # origin
    try:
        j3 = json.loads(o3)
        j2 = json.loads(o2)
    except Exception as e:
        FAIL.append((path, f"parse fail {e}"))
        return None
    t3 = deep_ts(j3)
    t2 = deep_ts(j2)
    side = 3 if t3 > t2 else 2  # tie -> :2: origin (r140 law)
    ts = max(t3, t2)
    blob = o3 if side == 3 else o2
    with open(path, "wb") as f:
        f.write(blob)
    json.loads(open(path, "rb").read())  # parse-verify written bytes (r185 law)
    print(f"  {path}: take side={side} ({'mine' if side == 3 else 'origin'}) probe mine={t3 or 'NONE'} origin={t2 or 'NONE'} -> {ts or 'NONE'}")
    return side


def union_jsonl(path):
    o2 = git_blob(2, path)  # origin
    o3 = git_blob(3, path)  # mine
    ln2 = o2.split(b"\n")
    ln3 = o3.split(b"\n")
    # strip trailing empty artifact from final newline, re-add on write
    trail2 = ln2 and ln2[-1] == b""
    trail3 = ln3 and ln3[-1] == b""
    if trail2:
        ln2.pop()
    if trail3:
        ln3.pop()
    seen = set(ln2)
    out = list(ln2)
    added = 0
    for ln in ln3:
        if ln not in seen:
            out.append(ln)
            seen.add(ln)
            added += 1
    # zero-loss check: |A∪B| exact (r188 law)
    assert len(out) == len(set(ln2) | set(ln3)), f"union count mismatch {path}"
    data = b"\n".join(out) + (b"\n" if (trail2 or trail3 or out) else b"")
    with open(path, "wb") as f:
        f.write(data)
    print(f"  {path}: line union |A|={len(ln2)} |B|={len(ln3)} -> |A∪B|={len(out)} (mine-only +{added})")
    return len(out)


def twin_md_from_side(md_path, side):
    blob = git_blob(side, md_path)
    with open(md_path, "wb") as f:
        f.write(blob)
    print(f"  {md_path}: byte-copy same side={side} ({len(blob)}B)")


def resolve_post_review_report():
    path = "results/post_review/REPORT-20260929.md"
    o2 = git_blob(2, path).decode("utf-8")
    o3 = git_blob(3, path).decode("utf-8")
    m2 = GEN_PAT.search(o2)
    m3 = GEN_PAT.search(o3)
    assert m2 and m3, "生成 ts line missing on a side"
    side = 3 if m3.group(1) > m2.group(1) else 2  # tie -> origin (r140)
    blob = (o3 if side == 3 else o2).encode("utf-8")
    with open(path, "wb") as f:
        f.write(blob)
    print(f"  {path}: take side={side} 生成 mine={m3.group(1)} origin={m2.group(1)}")


def main():
    print("== append-log line unions (zero loss) ==")
    union_jsonl("results/post_review.jsonl")
    union_jsonl("results/x2_watch_log.jsonl")
    print("== snapshot take-new faces ==")
    for p in (
        "results/daily_scorecard.json",
        "results/scorecard_v1.json",
        "results/strategy_scorecard.json",
        "results/prospect_promotion/_summary.json",
        "results/fundamental_b_layer_filter.json",
    ):
        take_new_json(p)
    print("== dashboard pair (json probe take-new; js whole-bytes SAME side) ==")
    side_dash = take_new_json("results/dashboard_status.json")
    if side_dash is not None:
        blob = git_blob(side_dash, "results/dashboard_status.js")
        with open("results/dashboard_status.js", "wb") as f:
            f.write(blob)
        head = blob[:40].decode("utf-8", errors="replace")
        assert head.lstrip().startswith("window."), f"js wrapper stripped! head={head!r}"
        print(f"  results/dashboard_status.js: whole-bytes side={side_dash} wrapper intact")
    print("== twin regen pairs (probe json, byte-copy md from same side) ==")
    for stem in ("docs/daily_report/REPORT-2026-09-29", "docs/live_usage/LIVE-2026-09-29"):
        side = take_new_json(stem + ".json")
        if side is None:
            continue
        twin_md_from_side(stem + ".md", side)
    print("== post_review regen md (生成 ts take-new) ==")
    resolve_post_review_report()
    if FAIL:
        print("FAILURES:", FAIL)
        sys.exit(2)
    print("resolver OK")


if __name__ == "__main__":
    main()
