# r703 bm-a merge resolver leg-5: fix 3 unresolved-evidence faces + jsonl union correctness re-check
# NOTE: stage blobs already consumed by leg-4 git-add -- sides are HEAD (=ours pre-merge) and origin/main (=theirs)
import subprocess, json, difflib

def blob(rev, path):
    return subprocess.run(["git", "show", f"{rev}:{path}"], capture_output=True).stdout

OURS, THEIRS = "HEAD", "origin/main"

# --- A. compute_audit.json + futures_update_status.json: find ts fields, redo ---
for p in ("results/compute_audit.json", "results/futures_update_status.json"):
    o = json.loads(blob(OURS, p).decode("utf-8", errors="replace"))
    t = json.loads(blob(THEIRS, p).decode("utf-8", errors="replace"))

    def find_ts(d, depth=0):
        found = []
        if isinstance(d, dict):
            for k, v in d.items():
                if isinstance(v, str) and ("2026-10-0" in v) and ("generated" in k or "updated" in k or k == "ts" or "attempt" in k):
                    found.append((k, v))
                elif isinstance(v, (dict,)) and depth < 2:
                    found.extend(find_ts(v, depth + 1))
        return found

    fo, ft = find_ts(o), find_ts(t)
    print(p, "OURS ts fields:", fo[:4])
    print(p, "THEIRS ts fields:", ft[:4])
    # decide by the max common-name ts
    def best(lst):
        return max((v for _, v in lst), default="")
    side = "ours" if best(fo) >= best(ft) else "theirs"
    subprocess.run(["git", "checkout", "--" + side, p], capture_output=True)
    subprocess.run(["git", "add", p], capture_output=True)
    print(f"REDO-RESOLVED {side}: {p} (ours_best={best(fo)} theirs_best={best(ft)})")

# --- B. token_usage: machines sub-dicts identical both sides; whole-face newer-wins (top-level generated) ---
m_ours = json.loads(blob(OURS, "results/token_usage.json").decode("utf-8", errors="replace"))
m_theirs = json.loads(blob(THEIRS, "results/token_usage.json").decode("utf-8", errors="replace"))
ident = m_ours.get("machines") == m_theirs.get("machines")
go, gt = str(m_ours.get("generated", "")), str(m_theirs.get("generated", ""))
print(f"token machines identical={ident}; ours_gen={go} theirs_gen={gt}")
if ident and gt >= go:
    subprocess.run(["git", "checkout", "--theirs", "results/token_usage.json"], capture_output=True)
    subprocess.run(["git", "add", "results/token_usage.json"], capture_output=True)
    print("REDO-RESOLVED theirs (whole-face, machines identical, newer snapshot): results/token_usage.json")

# --- C. post_review.jsonl union correctness: line-level diff census ---
o = blob(OURS, "results/post_review.jsonl").decode("utf-8", errors="replace").splitlines()
t = blob(THEIRS, "results/post_review.jsonl").decode("utf-8", errors="replace").splitlines()
m = open("results/post_review.jsonl", encoding="utf-8").read().splitlines()
so, st, sm = set(o), set(t), set(m)
print(f"post_review.jsonl: ours={len(o)} theirs={len(t)} merged={len(m)}")
print(f"  ours-only lines (not in theirs): {len(so - st)}")
print(f"  merged contains all ours: {so <= sm}; merged contains all theirs: {st <= sm}")
print(f"  merged extra lines vs union: {len(sm - (so | st))}")
