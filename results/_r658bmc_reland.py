# -*- coding: utf-8 -*-
# r658 bm-c close re-land -- the pool_worker piggyback commit 908b13017
# (containing the full r658 close set) diverged from origin/main when bm-a's
# r811 wave (06:09..06:15) landed first. ZERO hand-merge (bm-b r796 lesson):
# reset to origin tip; restore ONLY this round's unique files byte-exact
# from 908b13017; shared concurrently-derived faces stay at origin's newer
# versions (deep-ts newer-wins by construction); x2_watch_log.jsonl
# (append-only ledger in the overlap) healed via line-level union.
import subprocess, os, json, datetime

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
NO_WINDOW = 0x08000000
MINE_SHA = "908b13017"
BASE = "e6b9acfc2"

def git(args, binary=False):
    r = subprocess.run(["git", "-C", ROOT] + args, capture_output=True,
                       creationflags=NO_WINDOW)
    out = r.stdout if binary else r.stdout.decode("utf-8", "replace")
    if r.returncode != 0:
        raise RuntimeError("git %s rc=%d %s" % (" ".join(args), r.returncode, r.stderr.decode()[:200]))
    return out

def markers_in(path):
    with open(path, "rb") as f:
        t = f.read().decode("utf-8", "replace")
    return sum(1 for l in t.split("\n") if l.startswith("<<<<<<< ") or l.startswith(">>>>>>> "))

origin = git(["rev-parse", "origin/main"]).strip()
mine_files = set(git(["diff", "--name-only", MINE_SHA + "^", MINE_SHA]).split())
their_files = set(git(["diff", "--name-only", BASE, "origin/main"]).split())
overlap, unique = sorted(mine_files & their_files), sorted(mine_files - their_files)

# sanity: bm-a's wave built on my heal base
anc = subprocess.run(["git", "-C", ROOT, "merge-base", "--is-ancestor", BASE, "origin/main"],
                     capture_output=True, creationflags=NO_WINDOW)

# stash the piggyback's x2 ledger content BEFORE reset (for the union step)
x2 = "results/x2_watch_log.jsonl"
x2_mine_bytes = git(["show", MINE_SHA + ":" + x2], binary=True) if x2 in overlap else None

git(["reset", "--hard", "origin/main"])

# restore unique files byte-exact from the piggyback commit
for i in range(0, len(unique), 20):
    git(["checkout", MINE_SHA, "--"] + unique[i:i + 20])

# append-only union for the overlapping ledger face (r446 line-level union law)
x2_union_info = None
if x2_mine_bytes is not None:
    mine_lines = [l for l in x2_mine_bytes.decode("utf-8", "replace").split("\n") if l.strip()]
    with open(os.path.join(ROOT, x2), encoding="utf-8", errors="replace") as f:
        origin_lines = [l for l in f.read().split("\n") if l.strip()]
    origin_set = set(origin_lines)
    added = [l for l in mine_lines if l not in origin_set]
    merged = origin_lines + added
    with open(os.path.join(ROOT, x2), "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(merged) + ("\n" if merged else ""))
    x2_union_info = {"origin_lines": len(origin_lines), "mine_lines": len(mine_lines),
                     "appended_unique": len(added)}

# validation gate: every restored file marker-free; .json faces parse
bad = []
for rel in unique:
    p = os.path.join(ROOT, rel.replace("/", os.sep))
    if not os.path.exists(p):
        bad.append(("missing", rel)); continue
    if markers_in(p) != 0:
        bad.append(("markers", rel))
    if rel.endswith(".json"):
        try:
            json.load(open(p, encoding="utf-8-sig"))
        except ValueError as e:
            bad.append(("json:" + str(e)[:50], rel))
# spot-check origin's overlapping faces for marker contamination (bm-a wave sanity)
spot = [f for f in overlap if f.endswith(".json")][:6] + \
       [f for f in ("results/strategy_scorecard.json", "results/dashboard_status.json") if f in overlap]
for rel in spot:
    p = os.path.join(ROOT, rel.replace("/", os.sep))
    if os.path.exists(p) and markers_in(p) != 0:
        bad.append(("origin-face-markers", rel))

receipt = {"asof": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
           "probe": "r658 bm-c close re-land", "origin_main": origin,
           "heal_base_is_ancestor": anc.returncode == 0,
           "unique_restored": len(unique), "overlap_left_to_origin": len(overlap),
           "x2_union": x2_union_info, "bad_faces": bad, "files": {
               "unique": unique, "overlap": overlap}}
assert not bad, "validation gate failed: " + repr(bad)
with open(os.path.join(ROOT, "results", "_r658bmc_reland_receipt.json"), "w", encoding="utf-8") as f:
    json.dump(receipt, f, indent=1, ensure_ascii=False)
print(json.dumps({k: receipt[k] for k in ("origin_main", "heal_base_is_ancestor",
      "unique_restored", "overlap_left_to_origin", "x2_union", "bad_faces")}))
