"""r531 bm-a: W18 freeze surgical replay onto moved origin (commit-tree law).

Temp-index on origin/main -> hash-object merged/mine files -> write-tree ->
commit-tree -p origin/main -> push <sha>:main. Zero working-tree touch.
"""
import subprocess, os, sys

REPO = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"
FILES = [
    "scripts/perpetual_faces.py",
    "scripts/perpetual_faces_n1.py",
    "research/PERPETUAL_FACES.md",
    "research/PERPETUAL_N1_W18_PREREG.md",
    "results/_r530bma_w18_band_gate.py",
    "results/_r531bma_w18_admit_reverify.py",
    "results/_r531bma_w18_surgical_merge.py",
    "results/_r531bma_w18_constructive_n1.py",
]
MSG = """round 531: W18 FREEZE replay onto moved origin 23667218e (bm-b W19 v3 re-band) -- constructive union, DISJOINT bands chain-verified

- W18 (bm-a): A 78_001..80_000 / B exit 38_300..38_499, rotation slot W18=bm-a,
  both tails arithmetic (W17 ends +1), ADMIT receipt _r530bma_w18_band_gate.py
  (r530 crashed-session draft adopted per r314 after independent re-verify
  _r531bma_w18_admit_reverify.py vs HEAD 15-row pre-W18 table, incl. r529
  N3-R1 actual-seed-set leg); prereg anchored on W17 finalize (K=35,320,
  ledger 401,948); law sec.4 W18 row + canon row + N1_BANDS + WAVE_CONFIGS.
- W19 (bm-b, 18:54:28 commit EARLIER): re-band v3 A 80_001..82_000 /
  B 38_500..38_699 re-based past W18's published projection (their leg) --
  the two waves pack CONTIGUOUS 76_001..82_000 with zero overlap; both stand.
- Merge method: mechanical hunk-union produced interleaved frankenstein
  (n1) -> constructive merge (theirs base + my 3 anchored blocks; receipts
  _r531bma_w18_surgical_merge.py + _r531bma_w18_constructive_n1.py).
- Sole cross-side edit (disclosed): bm-b W19 leg prior-wave pin updated
  [no 15/18 -> +18 registered by this W18 freeze; derive-from-keys law
  unchanged]; all bm-b text otherwise verbatim (their EIGHTH ordinal + 
  18-unfrozen notes were written pre-W18-freeze under the 18-as-gap
  assumption; by wave-number succession W18=8th, W19=9th).
- Selftests on merged tree: n1 PASS (W18+W19 materializer faces + T-141
  exemption), pf 8/8, engine 7 legs. Banned gate ADMIT (pre-replay).
- W18 burn IN FLIGHT: engine ignited n1w18-1of12 pid 104756, queue 10,
  shards_done_total 20, ledger_flush=1 (product-face evidence).
"""

def g(*args, **kw):
    return subprocess.run(["git", "-C", REPO] + list(args), capture_output=True, **kw)

their = g("rev-parse", "origin/main").stdout.decode().strip()
idx = os.path.join(REPO, "results", "_r531bma_tmp_index")
env = dict(os.environ, GIT_INDEX_FILE=idx)
if os.path.exists(idx):
    os.remove(idx)
r = subprocess.run(["git", "-C", REPO, "read-tree", their], env=env, capture_output=True)
assert r.returncode == 0, r.stderr
for f in FILES:
    b = subprocess.check_output(["git", "-C", REPO, "hash-object", "-w", f])
    sha = b.decode().strip()
    mode = "100755" if f.endswith(".py") and False else "100644"
    r = subprocess.run(["git", "-C", REPO, "update-index", "--add", "--cacheinfo",
                        f"{mode},{sha},{f}"], env=env, capture_output=True)
    assert r.returncode == 0, (f, r.stderr)
    print("staged:", f, sha[:12])
tree = subprocess.check_output(["git", "-C", REPO, "write-tree"], env=env).decode().strip()
msgfile = os.path.join(os.environ["TEMP"], "r531_msg.txt")
with open(msgfile, "w", encoding="utf-8", newline="\n") as f:
    f.write(MSG)
commit = subprocess.check_output(
    ["git", "-C", REPO, "commit-tree", tree, "-p", their, "-F", msgfile],
    env=env).decode().strip()
print("commit-tree:", commit, "parent:", their[:12])
r = subprocess.run(["git", "-C", REPO, "push", "origin", f"{commit}:refs/heads/main"],
                   capture_output=True)
out = (r.stdout + r.stderr).decode()
print("push rc:", r.returncode)
print(out.strip().splitlines()[-2:] if out.strip() else "(no output)")
if r.returncode != 0:
    sys.exit(1)
r = subprocess.run(["git", "-C", REPO, "update-ref", "refs/heads/main", commit],
                   capture_output=True)
assert r.returncode == 0, r.stderr
print("local main updated ->", commit[:12])
os.remove(idx)
