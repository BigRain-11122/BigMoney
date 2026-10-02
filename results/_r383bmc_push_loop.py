"""r383 bm-c W113 finalize push window: r589 reset-FF-reland loop over the
mid-window origin advance (bm-a r593, which parked W114 freeze awaiting this
finalize). Corrections vs first attempt:
- post_review.jsonl: TAKE-ORIGIN verbatim (id-twin verdict -- 49 content
  variants carry ids already in origin; r294 id-dedupe law, bm-a r593
  cross-confirmed 'id-set identical both sides')
- CODELY.md: re-union after FF (new origin verbatim + my 1 local-only pit
  line, insert before '### Reference'; r373/r585 laws)
- execution-time rev-parse for all shas (bm-a r593 new pit law)
- attrition scan re-run post-FF (derive face, fresh overwrite)
Then: re-add payload, commit -F, push, delivery self-proof (fetch + 0/0 +
ls-tree per O-20261001-1108 door)."""
import json, os, subprocess, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
CN = 0x08000000

def git(*args, check=True):
    r = subprocess.run(["git", "-C", ROOT] + list(args), capture_output=True,
                       encoding="utf-8", errors="replace", creationflags=CN)
    if check and r.returncode != 0:
        raise SystemExit(f"git {args[:2]} rc={r.returncode}: {r.stderr[:400]}")
    return r

def git_bytes(*args):
    r = subprocess.run(["git", "-C", ROOT] + list(args), capture_output=True,
                       creationflags=CN)
    if r.returncode != 0:
        raise SystemExit(f"git {args[:2]} rc={r.returncode}: "
                         f"{r.stderr.decode('utf-8', 'replace')[:400]}")
    return r.stdout

# --- 0) state snapshot
head = git("rev-parse", "HEAD").stdout.strip()
origin_sha = git("rev-parse", "origin/main").stdout.strip()
head_subject = git("log", "-1", "--format=%s").stdout.strip()[:60]
print(f"HEAD={head[:9]} ({head_subject}...) origin={origin_sha[:9]}")
assert head_subject.startswith("W113 finalize landed"), \
    f"HEAD is not my finalize commit: {head_subject}"

# --- 1) uncommit my finalize (files stay on disk)
git("reset", "--mixed", "HEAD~1")
base = git("rev-parse", "HEAD").stdout.strip()
print("uncommitted; base =", base[:9])

# --- 2) take-origin post_review.jsonl (id-twin verdict, r294 law)
origin_pr = git_bytes("show", f"{origin_sha}:results/post_review.jsonl")
with open(os.path.join(ROOT, "results", "post_review.jsonl"), "wb") as f:
    f.write(origin_pr)
n_pr = len([x for x in origin_pr.replace(b"\r\n", b"\n").split(b"\n") if x.strip()])
print(f"post_review.jsonl = origin verbatim ({n_pr} rows, 49 twin variants dropped)")

# --- 3) CODELY: extract my local-only line, then checkout clean for FF
with open(os.path.join(ROOT, "CODELY.md"), "rb") as f:
    local_codely = f.read()
origin_codely = git_bytes("show", f"{origin_sha}:CODELY.md")
o_lines = origin_codely.replace(b"\r\n", b"\n").split(b"\n")
l_lines = local_codely.replace(b"\r\n", b"\n").split(b"\n")
only_local = [x for x in l_lines if x and x not in set(o_lines)]
print(f"CODELY local-only lines vs NEW origin: {len(only_local)}")
assert len(only_local) == 1, only_local

# --- 4) clean the FF-blocker files (worktree = current HEAD versions)
git("checkout", "--", "CODELY.md", "results/post_review.jsonl",
    "results/_attrition_guard_scan.json")
print("blocker files restored to base versions")

# --- 5) FF to origin (execution-time sha)
r = git("merge", "--ff-only", origin_sha, check=False)
if r.returncode != 0:
    raise SystemExit(f"FF refused: {r.stderr[:400]}")
print("FF ->", git("rev-parse", "HEAD").stdout.strip()[:9])
assert git("rev-parse", "HEAD").stdout.strip() == origin_sha

# --- 6) re-apply CODELY union (new origin + my 1 line before ### Reference)
ref_idx = next(i for i, x in enumerate(o_lines) if x.startswith(b"### Reference"))
insert_at = ref_idx - 1 if ref_idx > 0 and o_lines[ref_idx - 1] == b"" else ref_idx
merged = o_lines[:insert_at] + only_local + o_lines[insert_at:]
assert len(merged) == len(o_lines) + 1
assert all(x in merged for x in o_lines)
with open(os.path.join(ROOT, "CODELY.md"), "wb") as f:
    f.write(b"\r\n".join(merged) + (b"\r\n" if origin_codely.endswith(b"\n") else b""))
print("CODELY union re-applied (origin verbatim + 1 local pit line)")

# --- 7) re-run attrition scan post-FF (fresh derive face)
r = subprocess.run(["python", os.path.join(ROOT, "scripts",
                     "attrition_ledger_guard.py"), "scan"],
                    cwd=ROOT, capture_output=True, encoding="utf-8",
                    errors="replace", creationflags=CN)
print("attrition scan rc:", r.returncode,
      "|", (r.stdout or "").strip().splitlines()[-1][:120])
assert r.returncode == 0, "ACTIVE LOSS -- abort"

# --- 8) re-add payload + commit + push
payload = ["results/perpetual_faces/n1_w113_results.json",
           "scripts/perpetual_faces_n1.py",
           "research/PERPETUAL_N1_W113_PREREG.md",
           "results/_r383bmc_w113_refix.py", "results/_r383bmc_w113_gates.py",
           "results/_r383bmc_w113_verify.py", "results/_r383bmc_s78_backfill.py",
           "results/_r383bmc_ledger_scan.py"]
git("add", *payload)
staged = git("diff", "--cached", "--name-only").stdout.split()
assert set(staged) == set(payload), staged
print("staged:", len(staged), "files")
git("commit", "-F",
    r"K:\Fluxgroup\FluxGroup\quant\.codely-cli\scratch\msg_r383_w113_finalize.txt")
print("commit:", git("log", "-1", "--format=%h").stdout.strip())

r = git("push", check=False)
print("push rc:", r.returncode, "|", (r.stdout or r.stderr).strip()[:300])
if r.returncode != 0:
    raise SystemExit("PUSH FAILED -- manual follow-up needed (r589 re-loop)")

# --- 9) delivery self-proof (O-20261001-1108 door)
git("fetch", "origin")
ahead = int(git("rev-list", "--count", "origin/main..HEAD").stdout.strip())
behind = int(git("rev-list", "--count", "HEAD..origin/main").stdout.strip())
print(f"post-push: ahead={ahead} behind={behind}")
assert ahead == 0 and behind == 0, "not settled"
head_now = git("rev-parse", "HEAD").stdout.strip()
assert git("rev-parse", "origin/main").stdout.strip() == head_now
ls = git_bytes("ls-tree", "origin/main",
               "results/perpetual_faces/n1_w113_results.json").decode()
assert "blob" in ls, "results file missing on origin"
print("DELIVERY VERIFIED: origin/main == HEAD ==", head_now[:9],
      "| n1_w113_results.json on origin")
