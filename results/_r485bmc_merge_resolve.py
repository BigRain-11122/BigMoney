"""r485 bm-c merge-window resolver (canon lineage: r484 resolver + honest
two-side ts probing -- NO a-priori direction; r505 one-convergence law for
ts-less faces = majority direction of probed ts faces; token per-key union
r456 + r466 fallback; jsonl line-union r462/r656; CODELY block-union
r675 + r479 containment). Fail-closed on unexpected probe results."""
import json
import os
import re
import subprocess

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
CNW = getattr(subprocess, "CREATE_NO_WINDOW", 0)
OUTLOG = os.path.join(REPO, "results", "_r485bmc_merge_resolve_out.txt")
lines = []


def show(ref, path):
    r = subprocess.run(["git", "show", f"{ref}:{path}"], capture_output=True,
                       cwd=REPO, creationflags=CNW)
    if r.returncode != 0:
        raise SystemExit(f"RESOLVER-FAIL: git show {ref}:{path} rc={r.returncode}")
    return r.stdout


def face_ts(raw):
    """Top-level freshness field for S6 regenerable JSON faces."""
    try:
        d = json.loads(raw)
    except Exception:
        return None
    for k in ("ts", "generated", "updated", "written_at", "as_of",
              "updated_at"):
        v = d.get(k)
        if isinstance(v, str) and ":" in v:
            return v
    return None


def norm_ts(v):
    """r461 law: normalize ts before comparing (T->space, first 19 chars)."""
    if not v:
        return None
    v = v.strip().replace("T", " ")
    return v[:19]


EMBED_TS = re.compile(r"20\d\d-\d\d-\d\d[T ]\d\d:\d\d:\d\d")


def embed_ts(raw):
    """First embedded wall-clock ts in head of md/js/other faces."""
    m = EMBED_TS.search(raw[:600].decode("utf-8", "replace"))
    return norm_ts(m.group(0)) if m else None


# ---- UU face sets ----
S6_FACES = [
    "docs/daily_report/REPORT-2026-10-04.json",
    "docs/daily_report/REPORT-2026-10-04.md",
    "docs/live_usage/LIVE-2026-10-04.json",
    "docs/live_usage/LIVE-2026-10-04.md",
    "docs/live_usage/LIVE-latest.json",
    "docs/live_usage/LIVE-latest.md",
    "results/_attrition_guard_scan.json",
    "results/compute_audit.json",
    "results/daily_scorecard.json",
    "results/dashboard_status.js",
    "results/dashboard_status.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/lhb_update_status.json",
    "results/paper/COMPOSITE-CE-01_paper.json",
    "results/paper/COMPOSITE-CE-02_paper.json",
    "results/paper/DROUGHT-CE-01_paper.json",
    "results/paper/ENGULF-CE-01_paper.json",
    "results/paper/NEEDLE-DE-01_paper.json",
    "results/paper/VOLATILITY-CE-01_paper.json",
    "results/paper_export/export-2026-09-30.json",
    "results/paper_export/latest.json",
    "results/prospect_paper/_summary.json",
    "results/prospect_promotion/_summary.json",
    "results/regime_state.json",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
    "results/t35_open_fill_verify.json",
    "results/update_status.json",
]
JSONL_FACES = [
    "results/pool_core_samples.jsonl",
    "results/x2_watch_log.jsonl",
]
TOKEN_FACE = "results/token_usage.json"
CODELY = "CODELY.md"

# ---- 1. S6 regenerable faces: honest two-side probe, newer-wins ----
ours_wins, theirs_wins, tsless = [], [], []
for p in S6_FACES:
    o_raw, t_raw = show("HEAD", p), show("MERGE_HEAD", p)
    o_ts = norm_ts(face_ts(o_raw)) or embed_ts(o_raw)
    t_ts = norm_ts(face_ts(t_raw)) or embed_ts(t_raw)
    if o_ts and t_ts:
        if o_ts >= t_ts:
            ours_wins.append(p)
        else:
            theirs_wins.append(p)
            lines.append(f"FACE_THEIRS_NEWER {p} ours={o_ts} theirs={t_ts}")
    else:
        tsless.append(p)
        lines.append(f"FACE_TS_EXTRACT_MISS {p} ours={o_ts} theirs={t_ts}")

probed = ours_wins + theirs_wins
assert len(probed) >= 8, \
    f"RESOLVER-FAIL: ts-probe floor not met ({len(probed)} probed)"
# r505 one-convergence: majority direction applies to ts-less faces
majority_ours = len(ours_wins) >= len(theirs_wins)
lines.append(f"S6 probe: ours={len(ours_wins)} theirs={len(theirs_wins)} "
             f"tsless={len(tsless)} -> tsless default "
             f"{'ours' if majority_ours else 'theirs'}")
for p in tsless:
    (ours_wins if majority_ours else theirs_wins).append(p)
    lines.append(f"FACE_TSLESS_DEFAULT_{'OURS' if majority_ours else 'THEIRS'} {p}")
for p in ours_wins:
    with open(os.path.join(REPO, p.replace("/", os.sep)), "wb") as f:
        f.write(show("HEAD", p))
for p in theirs_wins:
    with open(os.path.join(REPO, p.replace("/", os.sep)), "wb") as f:
        f.write(show("MERGE_HEAD", p))
lines.append(f"S6 faces resolved: ours={len(ours_wins)} theirs={len(theirs_wins)}")

# ---- 2. jsonl append-only faces: line-level union (r462/r656) ----
for p in JSONL_FACES:
    o_raw, t_raw = show("HEAD", p), show("MERGE_HEAD", p)
    o_lines = [l for l in o_raw.decode("utf-8").splitlines() if l.strip()]
    t_lines = [l for l in t_raw.decode("utf-8").splitlines() if l.strip()]
    base = o_lines[:]
    seen = set(base)
    added = 0
    for l in t_lines:
        if l not in seen:
            base.append(l)
            seen.add(l)
            added += 1
    # zero-loss assertions: every side's line set is contained in union
    assert set(o_lines) <= set(base) and set(t_lines) <= set(base)
    # every line is valid json
    for l in base:
        json.loads(l)
    eol = "\r\n" if b"\r\n" in o_raw[:2000] else "\n"
    with open(os.path.join(REPO, p.replace("/", os.sep)), "w",
              encoding="utf-8", newline="") as f:
        f.write(eol.join(base) + (eol if base else ""))
    lines.append(f"JSONL union {p}: ours={len(o_lines)} theirs={len(t_lines)} "
                 f"-> union={len(base)} (+{added} theirs-only)")

# ---- 3. token_usage.json: per-key union (r456) w/ r466 fallback ----
o_raw, t_raw = show("HEAD", TOKEN_FACE), show("MERGE_HEAD", TOKEN_FACE)
o, t = json.loads(o_raw), json.loads(t_raw)
o_m, t_m = o.get("machines", {}), t.get("machines", {})
side_pick = 0
union_m = {}
for k in sorted(set(o_m) | set(t_m)):
    ov, tv = o_m.get(k), t_m.get(k)
    if ov == tv:
        union_m[k] = ov
    elif k not in t_m or k not in o_m:
        union_m[k] = ov if k not in t_m else tv
        side_pick += 1
    else:
        o_ts = ov.get("ts") if isinstance(ov, dict) else None
        t_ts = tv.get("ts") if isinstance(ov, dict) else None
        if o_ts and t_ts:
            union_m[k] = ov if norm_ts(o_ts) >= norm_ts(t_ts) else tv
        else:
            union_m[k] = ov if str(ov) >= str(tv) else tv
        side_pick += 1
o_gen, t_gen = norm_ts(o.get("generated")), norm_ts(t.get("generated"))
assert o_gen and t_gen, "RESOLVER-FAIL: token faces lack generated ts"
if side_pick == 0:
    winner = o if o_gen >= t_gen else t
    lines.append(f"token: per-key zero side-pick -> whole-face freshness "
                 f"ours={o_gen} theirs={t_gen} -> "
                 f"{'ours' if o_gen >= t_gen else 'theirs'} (r466 fallback)")
else:
    winner = dict(o if o_gen >= t_gen else t)
    winner["machines"] = union_m
    lines.append(f"token: per-key union side_pick={side_pick} base="
                 f"{'ours' if o_gen >= t_gen else 'theirs'}")
with open(os.path.join(REPO, "results", "token_usage.json"), "wb") as f:
    f.write(json.dumps(winner, ensure_ascii=False, indent=1).encode("utf-8"))
json.load(open(os.path.join(REPO, "results", "token_usage.json"),
               encoding="utf-8"))

# ---- 4. CODELY.md block-union (r675 + r479 containment) ----
o_raw, t_raw = show("HEAD", CODELY), show("MERGE_HEAD", CODELY)
o_txt, t_txt = o_raw.decode("utf-8"), t_raw.decode("utf-8")
o_lines = o_txt.splitlines()
missing = [ln for ln in o_lines if ln.strip() and ln not in t_txt]
true_new = [ln for ln in missing if ln not in t_txt]
assert len(true_new) == 1 and "r485 bm-c" in true_new[0], \
    f"RESOLVER-FAIL: CODELY true-new != 1 ({len(true_new)}) [missing=" \
    f"{[m[:60] for m in missing]}]"
base = t_txt if t_txt.endswith("\n") else t_txt + "\n"
union = base + true_new[0] + "\n"
assert union.startswith(t_txt.rstrip("\n") + "\n") or union.startswith(t_txt), \
    "RESOLVER-FAIL: CODELY theirs-prefix identity broken"
assert union.count(true_new[0]) == 1
assert not any(ln.startswith(("<<<<<<<", "=======", ">>>>>>>"))
               for ln in union.splitlines()), "RESOLVER-FAIL: markers present"
with open(os.path.join(REPO, "CODELY.md"), "wb") as f:
    f.write(union.encode("utf-8"))
lines.append(f"CODELY union: theirs-preserved + 1 true-new (r485 ser() EOL pit), "
             f"marker-scan clean, result_lines={len(union.splitlines())}")

# ---- 5. final marker sweep across all resolved faces (r644 content check) ----
for p in S6_FACES + JSONL_FACES + [TOKEN_FACE, CODELY]:
    fp = os.path.join(REPO, p.replace("/", os.sep))
    body = open(fp, "rb").read().decode("utf-8", "replace")
    for ln in body.splitlines():
        if ln.startswith(("<<<<<<<", ">>>>>>>")):
            raise SystemExit(f"RESOLVER-FAIL: marker at line start in {p}: {ln[:80]}")
lines.append("final marker sweep: clean")

with open(OUTLOG, "w", encoding="utf-8", newline="\n") as f:
    f.write("\n".join(lines))
print("RESOLVE_DONE_WROTE", OUTLOG)
