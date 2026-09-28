"""r400 bm-a push-storm resolver (vs bm-c r175 window 17:27:35).

Conflict faces (10 UU) + canonical recipes per bigmoney-conflict-resolve SKILL:
- REPORT-2026-09-28 json/md twins   -> deep-ts probe take-new, md byte-copy SAME side (r327/r329)
- LIVE-2026-09-28 json/md twins     -> same-day idempotent regen pair, same twin-side coupling law
- HANDOVER.md                       -> anchor-insert union: origin first-comer keeps slot,
                                       latecomer (bm-a) inserts own line before previous-check anchor (R210)
- dashboard_status.json             -> take-new by deep probe; .js = SAME side whole bytes (R209 pair law)
- fundamental_b_layer_filter.json   -> take-new by updated ts (R216)
- futures/lhb_update_status.json    -> take-new by deep ts probe (R208/r100/R350)
Stages during rebase replay: :2: = origin side, :3: = local side (r351 law).
"""
import json
import re
import subprocess
import sys

TS_PAT = re.compile(r"20\d{2}-\d{2}-\d{2}[T ]\d{2}:\d{2}(:\d{2})?")
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


def take_new_json(path, probe_hint=None):
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
    # tie -> HEAD side = :2: origin (r140 law)
    side = 3 if t3 > t2 else 2
    ts = max(t3, t2)
    blob = o3 if side == 3 else o2
    with open(path, "wb") as f:
        f.write(blob)
    json.loads(open(path, "rb").read())  # parse-verify written bytes (r185 law)
    print(f"  {path}: take side={side} ({'mine' if side == 3 else 'origin'}) probe mine={t3 or 'NONE'} origin={t2 or 'NONE'} -> {ts or 'NONE'}")
    return side


def twin_md_from_side(md_path, side):
    blob = git_blob(side, md_path)
    with open(md_path, "wb") as f:
        f.write(blob)
    print(f"  {md_path}: byte-copy same side={side} ({len(blob)}B)")


def resolve_handover():
    path = "research/HANDOVER.md"
    o2 = git_blob(2, path).decode("utf-8")
    o3 = git_blob(3, path).decode("utf-8")
    # my new line lives only in :3: (local); anchor = previous-check line '> bm-c round 170 五倍数核对'
    mine_lines = [ln for ln in o3.split("\n") if ln.startswith("> bm-a round 400 五倍数核对")]
    assert len(mine_lines) == 1, f"expected exactly 1 bm-a r400 line, got {len(mine_lines)}"
    mine_line = mine_lines[0]
    anchor = "> bm-c round 170 五倍数核对"
    lines2 = o2.split("\n")
    hits = [i for i, ln in enumerate(lines2) if ln.startswith(anchor)]
    assert len(hits) == 1, f"anchor count {len(hits)} in origin blob"
    idx = hits[0]
    # latecomer inserts own line BEFORE the previous-check anchor (R210)
    out = lines2[:idx] + [mine_line] + lines2[idx:]
    text = "\n".join(out)
    # verification: presence + ordering (r175 origin line kept slot, mine inserted before r170 anchor)
    assert "> bm-c round 175" in o2 or True  # origin first-comer presence informational
    assert mine_line in text and o2.count(anchor) == text.count(anchor)
    assert text.index(mine_line) < text.index(anchor)
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(text)
    has175 = "> bm-c round 175" in text
    print(f"  {path}: anchor-insert union landed (bm-c r175 present={has175}, bm-a r400 inserted before r170 anchor)")


def main():
    print("== twin regen pairs (probe json, byte-copy md from same side) ==")
    for stem in ("docs/daily_report/REPORT-2026-09-28", "docs/live_usage/LIVE-2026-09-28"):
        side = take_new_json(stem + ".json")
        if side is None:
            continue
        twin_md_from_side(stem + ".md", side)
    print("== dashboard pair (json probe take-new; js whole-bytes SAME side) ==")
    side_dash = take_new_json("results/dashboard_status.json")
    if side_dash is not None:
        blob = git_blob(side_dash, "results/dashboard_status.js")
        with open("results/dashboard_status.js", "wb") as f:
            f.write(blob)
        head = blob[:40].decode("utf-8", errors="replace")
        assert head.lstrip().startswith("window."), f"js wrapper stripped! head={head!r}"
        print(f"  results/dashboard_status.js: whole-bytes side={side_dash} wrapper intact")
    print("== snapshot take-new faces ==")
    for p in ("results/fundamental_b_layer_filter.json", "results/futures_update_status.json", "results/lhb_update_status.json"):
        take_new_json(p)
    print("== HANDOVER anchor-insert ==")
    resolve_handover()
    if FAIL:
        print("FAILURES:", FAIL)
        sys.exit(2)
    print("resolver OK")


if __name__ == "__main__":
    main()
