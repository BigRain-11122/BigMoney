# -*- coding: utf-8 -*-
"""r120 rebase-storm resolution: 14-UU shared-JSON set (bm-c r119 2ab490fe
replayed onto bm-a r367 4756eca2; both sides ran parallel S6 chains in the
00:42-00:47 window).

Laws applied:
- r344/r360: history faces = identity union |A u B|, NO resolver cap,
  zero-loss vs base asserted fail-closed.
- r366: identity key probed per-face over the union of all sides (no
  hardcode); twins same-side; ties -> HEAD(ours = origin-pushed side).
- r116: content-based churn judgment; LF-normalized write face.
- r113: origin side wins for derived snapshots (every snapshot face is
  re-derived by this round's S6 chain anyway).
"""
import json, subprocess, os

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
os.chdir(ROOT)

SNAPSHOTS = [
    "docs/daily_report/REPORT-2026-09-28.json",
    "docs/daily_report/REPORT-2026-09-28.md",
    "results/dashboard_status.js",
    "results/dashboard_status.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/heat_update_status.json",
    "results/lhb_update_status.json",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
    "results/token_usage.json",
    "results/update_status.json",
]
UNION_FACES = {
    "results/compute_audit.json": ["history"],
    "results/regime_state.json": ["history", "transitions"],
}


def sh(*args):
    r = subprocess.run(list(args), capture_output=True)
    if r.returncode != 0:
        raise RuntimeError("%s -> rc=%s: %s" % (
            args, r.returncode, r.stderr.decode("utf-8", "replace")[:300]))
    return r.stdout


def blob(stage, path):
    return sh("git", "show", ":%d:%s" % (stage, path)).decode("utf-8")


def probe_keys(ours, theirs, base, label):
    # r366 law: identity key probed per-face; uniqueness required WITHIN
    # each parent side (cross-side dups = the common rows union dedupes)
    for cand in (("machine", "ts"), ("ts",), ("asof",),
                 ("machine", "asof"), ("id",)):
        ok = True
        for rows in (ours, theirs, base):
            seen = set()
            for r in rows:
                if not all(k in r for k in cand):
                    ok = False
                    break
                t = tuple(r[k] for k in cand)
                if t in seen:
                    ok = False
                    break
                seen.add(t)
            if not ok:
                break
        if ok:
            print("  [%s] identity key: %s" % (label, cand))
            return cand
    raise SystemExit("no unique identity key for %s -- manual review" % label)


def union_rows(ours, theirs, base, label):
    cand = probe_keys(ours, theirs, base, label)
    idf = lambda r: tuple(r[k] for k in cand)
    id_o = {idf(r) for r in ours}
    id_t = {idf(r) for r in theirs}
    id_b = {idf(r) for r in base}
    union = list(ours)                      # ours order first (origin side)
    add_t = [r for r in theirs if idf(r) not in id_o]
    add_b = [r for r in base if idf(r) not in id_o and idf(r) not in id_t]
    union += add_t + add_b
    ids_u = [idf(r) for r in union]
    assert len(ids_u) == len(set(ids_u)), "dup identities post-union"
    # hard zero-loss (r344/r360): |A u B| complete, no resolver cap
    assert id_o <= set(ids_u), "ours loss"
    assert id_t <= set(ids_u), "theirs loss"
    # base identities absent from BOTH sides = producer rolling-window
    # write-back face (r360: window belongs to producer, not resolver) --
    # report only, do not resurrect
    rolled = id_b - set(ids_u)
    if rolled:
        print("  [%s] NOTE base rows legally rolled out by producer "
              "windows on both sides: %d" % (label, len(rolled)))
    print("  [%s] ours=%d theirs=%d base=%d -> union=%d "
          "(+theirs-unique %d, +base-unique %d)" % (
              label, len(ours), len(theirs), len(base), len(union),
              len(add_t), len(add_b)))
    return union


print("== snapshot faces: take origin/ours side (S6 re-derives) ==")
for p in SNAPSHOTS:
    sh("git", "checkout", "--ours", "--", p)
    sh("git", "add", "--", p)
    print("  ours-side:", p)

print("== history faces: three-way identity union ==")
for p, faces in UNION_FACES.items():
    base_d = json.loads(blob(1, p))
    ours_d = json.loads(blob(2, p))
    theirs_d = json.loads(blob(3, p))
    out = dict(ours_d)                      # top-level = ours (origin side)
    for face in faces:
        out[face] = union_rows(list(ours_d.get(face) or []),
                                list(theirs_d.get(face) or []),
                                list(base_d.get(face) or []),
                                "%s:%s" % (p, face))
    with open(p, "w", encoding="utf-8", newline="\n") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
    sh("git", "add", "--", p)
    print("  union written:", p)

print("== marker scan across all 14 faces ==")
ALL = SNAPSHOTS + list(UNION_FACES)
for p in ALL:
    txt = open(p, encoding="utf-8", errors="replace").read()
    for mk in ("<<<<<<<", "=======", ">>>>>>>"):
        assert mk not in txt, "marker %s still in %s" % (mk, p)
print("  14/14 marker-free")

st = sh("git", "status", "--porcelain").decode("utf-8")
uu = [l for l in st.splitlines() if l.startswith("UU")]
assert not uu, "still-unmerged: %s" % uu
print("OK: all 14 resolved and staged; no UU remains.")
