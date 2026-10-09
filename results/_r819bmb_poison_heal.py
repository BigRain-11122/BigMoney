# r819 bm-b poison-heal resolver (cycle 2, 12 UU):
# origin/main tip (3e276eba4) carries CONFLICT MARKERS in 9+ shared faces
# (bm-c fe60f9773..3e276eba4 absorbed a dead predecessor session's
# mid-rebase worktree -- all four commits poisoned). Last VALID origin
# state = f2f770b62 (bm-a r944). Heal = reconstruct both halves of each
# marker blob (git's own two sides of bm-c's internal conflict), validate,
# then apply canonical recipes across ALL valid candidates:
#   ledger faces (compute_audit/regime_state history): row-union zero-loss
#   snapshot/twin faces: take-new by content max-ts
# Candidates per face: {f2f770b62, poison-half-A, poison-half-B, MINE}.
import json
import re
import subprocess
import sys

VALID_ORIGIN = "f2f770b62"   # last marker-free origin state
POISON_TIP = "3e276eba4"     # current origin/main tip (marker-poisoned)
MINE = "2df8f0a03"           # replayed bm-b r819 round commit (valid)
TS = re.compile(r"20\d{2}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}")


def blob(rev, path):
    r = subprocess.run(["git", "show", "%s:%s" % (rev, path)],
                       capture_output=True)
    if r.returncode != 0:
        return None
    return r.stdout


def split_marker_halves(data):
    """Reconstruct the two sides of a conflict-marker blob (line-wise)."""
    a, b, state = [], [], 0  # 0 common, 1 A(HEAD), 2 B
    for raw in data.decode("utf-8", "replace").splitlines(keepends=True):
        s = raw.strip()
        if s.startswith("<<<<<<<"):
            state = 1
        elif s == "=======" and state == 1:
            state = 2
        elif s.startswith(">>>>>>>") and state == 2:
            state = 0
        else:
            if state in (0, 1):
                a.append(raw)
            if state in (0, 2):
                b.append(raw)
    return "".join(a).encode("utf-8"), "".join(b).encode("utf-8")


def max_ts_text(text):
    m = TS.findall(text.decode("utf-8", "replace"))
    return max(m) if m else ""


def candidates(path):
    """All valid candidate blobs for a face, newest-ts first."""
    cands = []
    v = blob(VALID_ORIGIN, path)
    if v is not None and b"<<<<<<<" not in v:
        cands.append(("valid_origin", v))
    p = blob(POISON_TIP, path)
    if p is not None:
        if b"<<<<<<<" in p:
            for i, half in enumerate(split_marker_halves(p)):
                cands.append(("poison_half_%s" % chr(ord("A") + i), half))
        else:
            cands.append(("poison_tip_clean", p))
    m = blob(MINE, path)
    if m is not None and b"<<<<<<<" not in m:
        cands.append(("mine", m))
    return cands


def resolve_ledger(path, ledger_key):
    cands = candidates(path)
    parsed = []
    for tag, data in cands:
        try:
            parsed.append((tag, json.loads(data.decode("utf-8")), data))
        except Exception as e:
            print("  [warn] %s %s unparseable: %r" % (path, tag, e))
    assert parsed, "no valid candidate for %s" % path
    seen, union = set(), []
    for tag, d, _ in parsed:
        for row in d.get(ledger_key, []):
            k = json.dumps(row, sort_keys=True, ensure_ascii=False)
            if k not in seen:
                seen.add(k)
                union.append(row)
    def _sk(r):
        return str(r.get("ts") or r.get("asof") or r.get("date") or "")
    union.sort(key=_sk)
    base = max(parsed, key=lambda t: max_ts_text(t[2]))[1]
    merged = dict(base)
    merged[ledger_key] = union
    assert len(union) >= max(len(d.get(ledger_key, [])) for _, d, _ in parsed), \
        "union lost rows"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(merged, f, ensure_ascii=False, indent=1)
    return {"path": path, "recipe": "poison_heal_union",
            "candidates": [t for t, _, _ in parsed],
            "union_rows": len(union),
            "state_from": max(parsed, key=lambda t: max_ts_text(t[2]))[0]}


def resolve_take_new(path):
    cands = candidates(path)
    if path.endswith((".json",)):
        parsed = []
        for tag, data in cands:
            try:
                parsed.append((tag, data, json.loads(data.decode("utf-8"))))
            except Exception as e:
                print("  [warn] %s %s unparseable: %r" % (path, tag, e))
        assert parsed, "no valid candidate for %s" % path
        best = max(parsed, key=lambda t: (max_ts_text(t[1]), t[0] == "mine"))
        with open(path, "wb") as f:
            f.write(best[1])
        return {"path": path, "recipe": "poison_heal_take_new",
                "candidates": [t for t, _, _ in parsed], "picked": best[0],
                "picked_ts": max_ts_text(best[1])}
    # markdown twins: text take-new by max-ts
    best = max(cands, key=lambda c: (max_ts_text(c[1]), c[0] == "mine"))
    with open(path, "wb") as f:
        f.write(best[1])
    return {"path": path, "recipe": "poison_heal_take_new_md",
            "candidates": [t for t, _ in cands], "picked": best[0],
            "picked_ts": max_ts_text(best[1])}


out = {"incident": "origin tip 3e276eba4 marker-poisoned faces (bm-c fe60f9773..3e276eba4 dead-session absorb); last valid origin=f2f770b62; heal=half-reconstruction union",
       "resolved": []}
out["resolved"].append(resolve_ledger("results/compute_audit.json", "history"))
out["resolved"].append(resolve_ledger("results/regime_state.json", "history"))
for p in (
    "results/token_usage.json",
    "results/futures_update_status.json",
    "results/lhb_update_status.json",
    "results/fundamental_b_layer_filter.json",
    "docs/daily_report/REPORT-2026-10-10.json",
    "docs/live_usage/LIVE-2026-10-10.json",
    "docs/live_usage/LIVE-latest.json",
    "docs/daily_report/REPORT-2026-10-10.md",
    "docs/live_usage/LIVE-2026-10-10.md",
    "docs/live_usage/LIVE-latest.md",
):
    out["resolved"].append(resolve_take_new(p))

# zero-marker residue assertion over all resolved paths
for r in out["resolved"]:
    body = open(r["path"], "rb").read()
    assert b"<<<<<<<" not in body and b">>>>>>>" not in body, \
        "markers left in %s" % r["path"]

with open("results/_r819bmb_poison_heal_out.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=True, indent=1)
print(json.dumps(out, indent=1)[:2000])
print("POISON_HEAL_OK %d files" % len(out["resolved"]))
