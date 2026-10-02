"""r383 bm-c S0 integration: pure-FF surgery to origin (local 0 ahead / 2
behind) over a dirty tree, per r585 (update-ref + reset --mixed + per-face
checkout), r578 (reset --mixed re-anchor), r580 (python argv lists),
r569-3 (CAS full shas), r570/r294 (post_review.jsonl union, dedupe on exact
row identity), r373/r585 (CODELY.md blob-space union, CRLF disk write),
r586 (D+?? same-name move pair = identity proof then delete stray),
r380 (porcelain parse: no whole-output strip).
Fail-closed asserts throughout. Bytes-in/bytes-out only (r530).
"""
import json, os, subprocess, sys

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"

def git(*args):
    r = subprocess.run(["git"] + list(args), cwd=ROOT, capture_output=True,
                       encoding="utf-8", errors="replace",
                       creationflags=0x08000000)
    if r.returncode != 0:
        raise SystemExit(f"git {args[:2]} rc={r.returncode}: {r.stderr[:400]}")
    return r.stdout

def git_bytes(*args):
    r = subprocess.run(["git"] + list(args), cwd=ROOT, capture_output=True,
                       creationflags=0x08000000)
    if r.returncode != 0:
        raise SystemExit(f"git {args[:2]} rc={r.returncode}: {r.stderr[:400]}")
    return r.stdout

head_old = git("rev-parse", "HEAD").strip()
origin_sha = git("rev-parse", "origin/main").strip()
assert len(head_old) == 40 and len(origin_sha) == 40, (head_old, origin_sha)
ahead = int(git("rev-list", "--count", "origin/main..HEAD").strip())
behind = int(git("rev-list", "--count", f"{head_old}..{origin_sha}").strip())
print(f"pre: ahead={ahead} behind={behind} head={head_old[:9]} origin={origin_sha[:9]}")
assert ahead == 0, "not a pure FF window -- ABORT (manual review)"

# --- classify incoming delta vs my old HEAD (r374: --no-renames, tab split)
name_status = git("diff", "--name-status", "--no-renames", head_old, origin_sha)
their = {"M": [], "A": [], "D": []}
for line in name_status.splitlines():
    if not line.strip():
        continue
    parts = line.split("\t")
    st, path = parts[0], parts[1]
    their.setdefault(st, []).append(path)
print("their delta:", {k: len(v) for k, v in their.items()})

# local porcelain (r380: per-line, no whole-output strip)
por = git("status", "--porcelain")
local_mod, local_untracked = [], []
for line in por.splitlines():
    if not line.strip():
        continue
    st, path = line[:2], line[3:]
    if st == "??":
        local_untracked.append(path)
    else:
        local_mod.append(path)
local_mod_set = set(local_mod)

UNION_FILES = ["results/post_review.jsonl", "CODELY.md"]
# shared re-derive faces: take origin now, my S6 re-derives them fresh
TAKE_ORIGIN_OVERLAP = [
    "results/compute_audit.json", "results/lhb_update_status.json",
    "results/post_review/REPORT-20261002.md", "results/regime_state.json",
    "results/scorecard_v1.json", "results/strategy_scorecard.json",
    "results/update_status.json"]

# --- 1) CAS move ref + reset --mixed re-anchor (r578)
git("update-ref", "refs/heads/main", origin_sha, head_old)
git("reset", "--mixed", origin_sha)
print("ref moved + index re-anchored to", origin_sha[:9])

# --- 2) CODELY.md union (r373 blob space; r585 line-set diff)
origin_blob = git_bytes("show", f"{origin_sha}:CODELY.md")
with open(os.path.join(ROOT, "CODELY.md"), "rb") as f:
    local_disk = f.read()
o_lines = origin_blob.replace(b"\r\n", b"\n").split(b"\n")
l_lines = local_disk.replace(b"\r\n", b"\n").split(b"\n")
o_set, l_set = set(o_lines), set(l_lines)
only_local = [x for x in l_lines if x and x not in o_set]
only_origin = [x for x in o_lines if x and x not in l_set]
print(f"CODELY: only_local={len(only_local)} only_origin={len(only_origin)}")
assert len(only_local) == 1, f"expected 1 local-only line, got {len(only_local)}"
# insert local-only line(s) at Project-section tail = just before '### Reference'
ref_idx = next(i for i, x in enumerate(o_lines) if x.startswith(b"### Reference"))
insert_at = ref_idx - 1 if ref_idx > 0 and o_lines[ref_idx - 1] == b"" else ref_idx
merged = o_lines[:insert_at] + only_local + o_lines[insert_at:]
assert len(merged) == len(o_lines) + len(only_local)
assert all(x in merged for x in only_origin), "origin line lost in union"
disk_bytes = b"\r\n".join(merged) + (b"\r\n" if origin_blob.endswith(b"\n") else b"")
with open(os.path.join(ROOT, "CODELY.md"), "wb") as f:
    f.write(disk_bytes)
print("CODELY.md union written (CRLF disk, LF blob)")

# --- 3) post_review.jsonl union (r570: origin bytes verbatim + local dict rows)
pr_path = os.path.join(ROOT, "results", "post_review.jsonl")
origin_pr = git_bytes("show", f"{origin_sha}:results/post_review.jsonl")
with open(pr_path, "rb") as f:
    local_pr = f.read()
o_rows = [x for x in origin_pr.replace(b"\r\n", b"\n").split(b"\n") if x.strip()]
l_rows = [x for x in local_pr.replace(b"\r\n", b"\n").split(b"\n") if x.strip()]
o_row_set = set(o_rows)
local_new = [x for x in l_rows if x not in o_row_set]
# type gate (r570): every appended row must parse to a dict
kept = []
for row in local_new:
    try:
        assert isinstance(json.loads(row.decode("utf-8")), dict)
        kept.append(row)
    except Exception:
        print("dropped non-dict/unparsable local row:", row[:80])
print(f"post_review: origin={len(o_rows)} local_total={len(l_rows)} local_new_kept={len(kept)}")
merged_pr = o_rows + kept
with open(pr_path, "wb") as f:
    f.write(b"\n".join(merged_pr) + b"\n")
print("post_review.jsonl union written")

# --- 4) checkout: origin-changed files not in union/keep set (r580 argv)
co_paths = [p for p in their["M"] + their["A"]
            if p not in UNION_FILES and p not in local_mod_set]
co_paths += [p for p in TAKE_ORIGIN_OVERLAP if p in local_mod_set]
print(f"checkout sync count={len(co_paths)}")
BATCH = 40
for i in range(0, len(co_paths), BATCH):
    git("checkout", "--", *co_paths[i:i + BATCH])

# --- 5) origin-deleted paths: identity-prove then remove stray (r586)
for p in their["D"]:
    fp = os.path.join(ROOT, p)
    if not os.path.exists(fp):
        continue
    h = subprocess.run(["git", "hash-object", fp], cwd=ROOT, capture_output=True,
                       creationflags=0x08000000)
    hsha = h.stdout.decode("utf-8", "replace").strip()
    old_blob_sha = git("rev-parse", f"{head_old}:{p}").strip()
    assert hsha == old_blob_sha, f"{p}: worktree differs from old HEAD -- manual review"
    os.remove(fp)
    print("removed origin-deleted stray:", p)

# --- 6) post-verify
por2 = git("status", "--porcelain")
remaining_mod, remaining_un = [], []
for line in por2.splitlines():
    if not line.strip():
        continue
    (remaining_un if line.startswith("??") else remaining_mod).append(line[3:])
print(f"post: modified={len(remaining_mod)} untracked={len(remaining_un)}")
expected_keep = set(local_mod_set) - set(TAKE_ORIGIN_OVERLAP)
missing_keep = expected_keep - set(remaining_mod)
assert not missing_keep, f"keep-local files lost: {missing_keep}"
with open(os.path.join(ROOT, "CODELY.md"), "rb") as f:
    c_now = f.read()
assert only_local[0] in c_now, "my CODELY line lost"
assert all(x.replace(b"\n", b"\r\n") in c_now for x in only_origin), "origin CODELY line lost"
print("S0 FF surgery COMPLETE -- unions in place, tree synced")
