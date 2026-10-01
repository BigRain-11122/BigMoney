# r552 bm-a surgical lane-files push (r512/r530 net path; r330 script-file law)
# Payload = 6 bm-a single-writer lane files; parent = fresh origin/main; FF by construction.
import subprocess, os, sys, json, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # results/ -> repo root
os.chdir(ROOT)

def g(*args, **kw):
    r = subprocess.run(["git", *args], capture_output=True, **kw)
    if r.returncode != 0:
        sys.exit(f"GIT FAIL {args}: {r.stderr.decode(errors='replace')[:400]}")
    return r.stdout

CARRY = [
    "results/autofill_state.bm-a.json",
    "results/runnable_pool.bm-a.json",
    "results/saturation_engine/face_bm-a.json",
    "results/saturation_engine/history_bm-a.jsonl",
    "results/saturation_engine/ledger_bm-a.jsonl",
    "results/saturation_engine/state_bm-a.json",
]

g("fetch", "origin")
base = g("rev-parse", "origin/main").decode().strip()
print("base:", base[:12])

tmp_index = os.path.join(tempfile.gettempdir(), "r552bma_surg.index")
env = dict(os.environ, GIT_INDEX_FILE=tmp_index)
if os.path.exists(tmp_index):
    os.remove(tmp_index)

def ge(*args):
    r = subprocess.run(["git", *args], capture_output=True, env=env)
    if r.returncode != 0:
        sys.exit(f"GIT FAIL {args}: {r.stderr.decode(errors='replace')[:400]}")
    return r.stdout

ge("read-tree", base)

changed = []
for path in CARRY:
    origin_blob = subprocess.run(["git", "show", f"{base}:{path}"], capture_output=True).stdout
    work = open(path, "rb").read()
    # EOL canon = origin blob's dominant EOL; convert working bytes to match canon
    if origin_blob.count(b"\r\n") * 2 > origin_blob.count(b"\n"):
        canon_crlf = True
    else:
        canon_crlf = False
    work_crlf = work.count(b"\r\n") * 2 > work.count(b"\n")
    if canon_crlf and not work_crlf:
        work = work.replace(b"\n", b"\r\n")
    elif (not canon_crlf) and work_crlf:
        work = work.replace(b"\r\n", b"\n")
    # content sanity: json/jsonl parse (fail-closed)
    if path.endswith((".json", ".jsonl")):
        txt = work.decode("utf-8")
        if path.endswith(".jsonl"):
            n = 0
            for line in txt.splitlines():
                if line.strip():
                    json.loads(line); n += 1
            assert n > 0, f"{path}: zero jsonl rows"
        else:
            json.loads(txt)
    if work != origin_blob:
        tmpf = tempfile.NamedTemporaryFile(delete=False)
        tmpf.write(work); tmpf.close()
        blob = ge("hash-object", "-w", "--no-filters", tmpf.name).decode().strip()
        os.remove(tmpf.name)
        ge("update-index", "--cacheinfo", f"100644,{blob},{path}")
        changed.append((path, blob))
    else:
        print("identical to origin (no change needed):", path)

if not changed:
    print("NOTHING TO PUSH - all lane files already byte-equal to origin")
    sys.exit(0)

tree = ge("write-tree").decode().strip()
msgfile = tempfile.NamedTemporaryFile(mode="w", delete=False, encoding="utf-8", newline="\n")
msgfile.write(
    "round 552 S0 surgical: bm-a lane files carry (autofill nulls claim_lost_yield self-heal per r297 ladder "
    "+ engine tick state/face/history/ledger + lane pool view; supersedes unpushed 0baee35d8 chain whose rebase "
    "base 76bc3edfe was an r519-family transient-deletion commit; pool contribution zero vs origin bm-c r345 "
    "restores) [via bm-a]\n"
)
msgfile.close()
sha = subprocess.run(["git", "commit-tree", tree, "-p", base, "-F", msgfile.name],
                     capture_output=True, env=env).stdout.decode().strip()
os.remove(msgfile.name)
print("new commit:", sha[:12])

# payload assertions (r331/r343): exactly the carry set changed; zero deletions
name_status = g("diff-tree", "-r", "--name-status", "--no-renames", base, sha).decode()
lines = [l for l in name_status.splitlines() if l.strip()]
mods = [l.split("\t") for l in lines]
payload = {m[1] for m in mods}
assert payload == {p for p, _ in changed}, f"payload mismatch: {payload}"
assert all(m[0] == "M" for m in mods), f"non-M status in payload: {mods}"
deletions = [m for m in mods if m[0].startswith("D")]
assert not deletions, f"DELETION SET non-empty: {deletions}"
print("payload OK:", len(payload), "files, zero deletions")

r = subprocess.run(["git", "push", "origin", f"{sha}:main"], capture_output=True)
if r.returncode != 0:
    print("PUSH REJECTED:", r.stderr.decode(errors='replace')[:300])
    sys.exit(2)
print("pushed FF:", sha[:12])

# post-push delivery check (r344 three-face): fetch + ls-tree blob equality
g("fetch", "origin")
head = g("rev-parse", "origin/main").decode().strip()
assert head == sha, f"origin moved after push: {head[:12]} != {sha[:12]}"
for path, blob in changed:
    got = g("ls-tree", head, path).decode().split()[2].split("\t")[0]
    assert got == blob, f"blob mismatch on origin for {path}"
print("delivery verified: ls-tree blob equality", len(changed), "files")
print("SURGICAL OK", sha)
