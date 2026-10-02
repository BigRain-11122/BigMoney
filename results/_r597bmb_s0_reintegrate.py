"""r597 bm-b S0 re-integration surgery (r589 unwind-FF-recommit loop + r595 E-08 curation).

Context: r597 claim commit (T-146 claim + r596 posthumous estate) push was claw-rejected
because origin advanced (bm-c r385 232ff349e + bm-a r595 f54b87cef) -> r374 diverged-base
artifact (origin-new file _r595bma_s6_chain2.py mis-read as local deletion). Tree holds
tracked live-write lane faces -> rebase forbidden (r532) -> unwind-FF-recommit loop:
  1. extract my unique CODELY r596 row from the unpushed commit (blob space, bytes)
  2. reset --mixed to execution-time fresh origin/main (r593 fresh-read law)
  3. checkout ALL origin-gain faces EXCEPT the 2 union faces (CODELY.md, T-147 ticket)
     -> foreign/shared derived faces take origin verbatim (r595 19-keep/69-origin law)
  4. union CODELY.md = origin verbatim + my 1 unique row appended at tail (pure-append
     row; origin's own -34 restructure untouched per r585 no-union-revert law)
  5. union T-147 ticket = origin verbatim (bm-c claim-first wins path) + bm_b_yield_record
     field (sec.4 commit-time yield + full estate handover pointers)
  6. probe: zero " D" faces before any add (E-08), staged/unstaged census
ASCII-only comments per pit law.
"""
import json
import subprocess
import sys

R = r"C:\Fluxgroup\FluxGroup\quant\bigmoney"
UNION_FACES = {"CODELY.md", "fleet/tasks/T-2026-10-02-147-P1.json"}
OG_LIST = r"C:\Users\Administrator\AppData\Local\Temp\o_gain.txt"


def git(*args, binary=False):
    p = subprocess.run(["git", *args], cwd=R, capture_output=True)
    if binary:
        return p.returncode, p.stdout, p.stderr
    return p.returncode, p.stdout.decode("utf-8", errors="replace"), p.stderr.decode("utf-8", errors="replace")


def die(msg):
    print("ABORT:", msg)
    sys.exit(1)


def read_any(path):
    raw = open(path, "rb").read()
    if raw.startswith(b"\xff\xfe") or raw.startswith(b"\xfe\xff"):
        return raw.decode("utf-16")
    return raw.decode("utf-8", errors="replace")


# --- 1. my unique CODELY row from the dangling r597 commit (blob bytes) ---
rc, out, err = git("rev-parse", "HEAD@{1}")
if rc != 0:
    die("rev-parse HEAD@{1} failed: " + err)
DANGLING = out.strip()
rc, mine_blob, _ = git("cat-file", "blob", DANGLING + ":CODELY.md", binary=True)
if rc != 0:
    die("cat-file HEAD:CODELY.md failed")
lines = mine_blob.split(b"\n")
row = None
for ln in reversed(lines):
    if ln.strip():
        row = ln
        break
if row is None or b"r596 bm-b" not in row:
    die("unique r596 row not found in HEAD:CODELY.md tail")
print("[1] my unique CODELY row bytes:", len(row), "starts:", row[:60])

# --- 2. reset --mixed to fresh origin/main (idempotent on re-run) ---
rc, out, err = git("rev-parse", "origin/main")
if rc != 0:
    die("rev-parse origin/main failed: " + err)
new = out.strip()
rc, head_sha, _ = git("rev-parse", "HEAD")
if head_sha.strip() != new:
    rc, out, err = git("reset", "--mixed", new)
    if rc != 0:
        die("reset --mixed failed: " + err)
    print("[2] reset --mixed ->", new[:10])
else:
    print("[2] HEAD already at origin/main", new[:10], "(re-run pass)")

# --- 3. checkout all origin-gain faces except union faces ---
og = [l.strip() for l in read_any(OG_LIST).splitlines() if l.strip()]
todo = [f.replace("\\", "/") for f in og]
done = 0
for i in range(0, len(todo), 40):
    batch = todo[i:i + 40]
    rc, out, err = git("checkout", "--", *batch)
    if rc != 0:
        die("checkout batch failed @%d: %s" % (i, err[:300]))
    done += len(batch)
print("[3] checkout origin-verbatim faces (incl. union bases):", done, "of", len(todo))

# --- 4. union CODELY.md: disk is now ORIGIN version; append my unique row, EOL-matched ---
with open(R + r"\CODELY.md", "rb") as fh:
    cur = fh.read()
if b"r596 bm-b" in cur:
    print("[4] CODELY union: row already present, no-op")
else:
    eol = b"\r\n" if b"\r\n" in cur else b"\n"
    body = cur
    if not body.endswith(eol):
        body += eol
    body += row + eol
    with open(R + r"\CODELY.md", "wb") as fh:
        fh.write(body)
    print("[4] CODELY union: appended r596 row, eol", repr(eol))

# --- 5. union T-147 ticket: origin verbatim + yield_record field ---
tp = R + r"\fleet\tasks\T-2026-10-02-147-P1.json"
with open(tp, "rb") as fh:
    raw = fh.read()
if b"bm_b_yield_record" in raw:
    print("[5] T-147 union: yield field already present, no-op")
else:
    try:
        doc = json.loads(raw.decode("utf-8"))
    except Exception as e:
        die("T-147 origin blob not json: %s" % e)
    if doc.get("claimed_by", "").startswith("bm-c") is False:
        die("T-147 at disk is not the bm-c origin version: claimed_by=%r" % doc.get("claimed_by"))
    yield_text = (
        "bm-b YIELDS per sec.4 commit-time order: parallel claim 22:05 local (board scan "
        "pre-visibility saw zero open deep-axis tickets; origin fresh only to O-2135/T-146), "
        "your claim landed at origin first via 232ff349e -> ticket + judgment face ownership "
        "stays bm-c. ESTATE HANDOVER (built in parallel by bm-b r596 pre-visibility, ADOPT per "
        "r471/r302 -- verify then continue s3->finalize+E1 under your ownership, zero re-draft "
        "needed): (1) research/LOWAMP-DEEP-P1.md frozen at main-exam rank = s1+s2 DONE (headline "
        "LAD-EDGE 67-trade deep face per O-2115 verbatim; 4 judged cells incl 2 TRUE-eq "
        "first-measured; 2000 deep same-mask hold-through nulls; sens 500; exit-axis dual gate "
        "params-4+ExitPatch-2+law-A census 20%; E1 four-leg declared; deterministic reproduction "
        "assert vs P3 deep artifacts). (2) scripts/lowamp_deep_p1.py runner (P3 sizing dead-letter "
        "bug FIXED + F3b hermetic regression leg, selftest 22/22; probe PASS: G-CENSUS deep 1506 "
        "exact, D6 max|corr| 0.1719 admit, sizing differentiates 3126/3126 real-panel days, headline "
        "reproduces P3 artifact bit-for-bit). (3) seeds lowamp_deep_p1_params/nulls 20337000/20337500 "
        "in scripts/science_gates.py SEED_REGISTRY (disjoint-verified). (4) 10 pool units registered "
        "in results/runnable_pool.json (audit.machine=bm-b; burns in flight on bm-b = deep-panel "
        "data-locality; per-machine entries machine-agnostic per pool law). If your independent "
        "draft differs your frozen version wins the judgment face (r483); sizing-bug detail = CODELY "
        "r596 row + knowledge/METHODOLOGY_ASSETS.md E09. Full handover note = fleet/inbox/MSG-2026-10-02-2215-bmb."
    )
    doc["bm_b_yield_record"] = yield_text
    # byte-stable insert: string surgery before final closing brace, preserve foreign formatting
    txt = raw.decode("utf-8")
    idx = txt.rstrip().rfind("}")
    if idx < 0:
        die("T-147 closing brace not found")
    field = ' "bm_b_yield_record": ' + json.dumps(yield_text, ensure_ascii=False)
    new_txt = txt[:idx].rstrip().rstrip(",") + ",\n" + field + "\n}\n"
    with open(tp, "wb") as fh:
        fh.write(new_txt.encode("utf-8"))
    # verify parseable
    json.loads(open(tp, "rb").read().decode("utf-8"))
    print("[5] T-147 union: bm_b_yield_record appended, json re-parse OK")

# --- 6. probe: zero D faces, census ---
rc, out, err = git("status", "--porcelain")
d_faces = [l for l in out.splitlines() if l.startswith(" D") or l.startswith("D ")]
if d_faces:
    print("ACTIVE D FACES (E-08 violation, must restore before add):")
    for l in d_faces:
        print("  ", l)
    sys.exit(2)
mod = [l for l in out.splitlines() if l.startswith(" M")]
unt = [l for l in out.splitlines() if l.startswith("??")]
print("[6] porcelain: %d modified, %d untracked, 0 D-faces" % (len(mod), len(unt)))
print("SURGERY OK")
