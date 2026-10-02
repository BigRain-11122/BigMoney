"""r607 bm-a closeout staging: batch add via python argv (r580 law).
- Stage all M rows (verified bm-a owned/hosted), the paired inbox move (D+A),
  new MSG, round artifacts, r606 dead-session estate, bookkeeping four.
- EXCLUDE in-flight burn products (sens.jsonl, n4_b2/ wave products).
- Verify: staged set contains bookkeeping four; zero unexpected D rows
  (only the paired inbox move); no other-machine faces."""
import subprocess, sys

REPO = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"

def git(*args):
    r = subprocess.run(["git", "-C", REPO, *args], capture_output=True)
    return r.returncode, r.stdout.decode("utf-8", "replace"), r.stderr.decode("utf-8", "replace")

rc, out, _ = git("status", "--porcelain")
lines = [l for l in out.splitlines() if l.strip()]
m_paths, d_paths, u_paths = [], [], []
for l in lines:
    xy, path = l[:2], l[3:]
    if l.startswith("??"):
        u_paths.append(path)
    elif "D" in xy:
        d_paths.append(path)
    elif "M" in xy:
        m_paths.append(path)

# guard: M set must not contain other-machine faces
bad = [p for p in m_paths if (".bm-c." in p or ".bm-b." in p or p.startswith(("round_reports-bm-c", "state-bm-c", "fleet/machines/bm-c", "fleet/machines/bm-b")))]
if bad:
    print("ABORT other-machine M faces:", bad); sys.exit(1)
# guard: D set must be exactly the paired inbox move
if d_paths != ["fleet/inbox/MSG-2026-10-03-0410-bmc-bma.md"]:
    print("ABORT unexpected D rows:", d_paths); sys.exit(1)

explicit_adds = [
    "fleet/inbox/MSG-2026-10-03-0410-bmc-bma.md",           # the move D side
    "fleet/inbox/processed/MSG-2026-10-03-0410-bmc-bma.md", # the move A side
    "fleet/inbox/MSG-2026-10-03-0436-bma-bmc-w14-entry-verdict.md",
    "results/_r606bma_s6_log.txt",
    "results/_r606bma_s6_runner.ps1",
    "results/_r607bma_s0_facets.py",
    "results/_r607bma_s0_fixother.py",
    "results/_r607bma_s6_runner.ps1",
    "results/_r607bma_s6_log.txt",
    "state-bm-a.json",
    "fleet/machines/bm-a.json",
    "round_reports-bm-a.md",
    "CODELY.md",
]
to_add = sorted(set(m_paths) | set(explicit_adds))
print(f"staging {len(to_add)} paths (M={len(m_paths)} + explicit adds)")
rc, _, err = git("add", "--", *to_add)
if rc != 0:
    print("ADD FAIL:", err); sys.exit(1)

# verify staged: bookkeeping four present, D rows only the paired move
rc, out, _ = git("diff", "--cached", "--name-status")
staged = out.splitlines()
staged_d = [l.split("\t")[-1] for l in staged if l.startswith("D")]
need4 = ["state-bm-a.json", "fleet/machines/bm-a.json", "round_reports-bm-a.md", "CODELY.md"]
missing = [f for f in need4 if f not in out]
print("staged rows:", len(staged), "| staged D:", staged_d, "| bookkeeping missing:", missing)
if missing or staged_d != ["fleet/inbox/MSG-2026-10-03-0410-bmc-bma.md"]:
    print("ABORT verify failed"); sys.exit(1)
print("STAGE OK")
