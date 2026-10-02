import subprocess, os, json, sys

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

def git(args, check=True):
    r = subprocess.run(["git"] + args, cwd=REPO, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if check and r.returncode != 0:
        print("GIT FAIL:", args, r.stdout, r.stderr); sys.exit(1)
    return r

LIVE_PRESERVE = {
    "results/autofill_state.bm-a.json",
    "results/saturation_engine/face_bm-a.json",
    "results/saturation_engine/state_bm-a.json",
    "results/saturation_engine/history_bm-a.jsonl",
    "results/saturation_engine/ledger_bm-a.jsonl",
}
UNION_FILES = ["results/pool_core_samples.jsonl"]

# gather sync list from status porcelain
st = git(["status", "--porcelain"]).stdout.strip().splitlines()
sync = []
for line in st:
    if len(line) < 4: continue
    x, y, path = line[0], line[1], line[3:].strip('"')
    if x == "?" : continue  # untracked: leave (in-flight W104 products)
    if path in LIVE_PRESERVE or path in UNION_FILES: continue
    if y in ("M", "D"):
        sync.append(path)

print("sync checkout count:", len(sync))
# batch checkout via python argv (r580 law)
CH = 40
for i in range(0, len(sync), CH):
    batch = sync[i:i+CH]
    r = git(["checkout", "--"] + batch)
print("checkout done rc:", r.returncode)

# union append-only jsonl per r570/r580 law (blob space LF per r373)
for path in UNION_FILES:
    origin_blob = git(["show", "origin/main:" + path]).stdout
    local_bytes = open(os.path.join(REPO, path), "rb").read()
    # blob space: normalize CRLF->LF for line handling
    otext = origin_blob.replace("\r\n", "\n")
    ltext = local_bytes.decode("utf-8", errors="replace").replace("\r\n", "\n")
    olines = [l for l in otext.split("\n") if l.strip()]
    llines = [l for l in ltext.split("\n") if l.strip()]
    oset = set(olines)
    extra = [l for l in llines if l not in oset]
    non_dict = 0
    for l in extra:
        try:
            if not isinstance(json.loads(l), dict): non_dict += 1
        except Exception: non_dict += 1
    if non_dict:
        print("UNION ABORT: non-dict/non-json extra rows:", non_dict); sys.exit(1)
    merged = olines + extra
    out = "\n".join(merged) + "\n"
    # verify all merged rows parse as dict (r570 double gate)
    for l in merged:
        try:
            assert isinstance(json.loads(l), dict)
        except Exception as e:
            print("MERGED ROW FAIL:", l[:80], e); sys.exit(1)
    open(os.path.join(REPO, path), "wb").write(out.encode("utf-8"))
    print("union", path, "origin:", len(olines), "local_extra:", len(extra), "merged:", len(merged))

# post-verify status
st2 = git(["status", "--porcelain"]).stdout.strip().splitlines()
print("post-sync status:")
for line in st2: print(" ", line[:100])
