# r370 bm-a: D-20260928-03(1) lane-file migration -- S1 measurement census (L1 deterministic, zero network).
# Single-pass git walk (one `git log --name-only` over last 3000 commits) aggregated per file;
# multi-machine co-writers (>=2 bm-* writers) = lane-migration candidates. Consumer face: basename grep.
import subprocess, json, re, os, glob, collections

OUT = "results/_r370bma_lane_census.json"

def writer_of(msg):
    m = re.search(r"\[(?:via )?(?:r\d+ )?(bm-[abc])\]", msg.strip())
    if m:
        return m.group(1)
    return "tick/other"

log = subprocess.run(["git", "log", "-n", "3000", "--format=%h|%s", "--name-only", "results/"],
                     capture_output=True, text=True, encoding="utf-8", errors="replace").stdout
per_file = collections.defaultdict(collections.Counter)
commit_count = 0
cur_writer = None
for line in log.splitlines():
    if "|" in line and line.index("|") <= 42 and not line.startswith(" "):
        h, msg = line.split("|", 1)
        if re.fullmatch(r"[0-9a-f]{7,40}", h.strip()):
            commit_count += 1
            cur_writer = writer_of(msg)
            continue
    f = line.strip()
    if f and cur_writer and f.startswith("results/") and f.endswith((".json", ".js")):
        per_file[f][cur_writer] += 1

census = {}
for f, w in per_file.items():
    machines = {m for m in w if m.startswith("bm-")}
    if len(machines) >= 2:
        census[f] = {"commits": sum(w.values()), "machines": sorted(machines),
                     "per_machine": {k: v for k, v in w.items() if k.startswith("bm-")}}

consumers = {}
script_face = glob.glob("scripts/*.py") + glob.glob("*.py") + glob.glob("*.html") + glob.glob("monitor/*.py")
for f in census:
    base = os.path.basename(f)
    consumers[f] = [s for s in script_face
                    if os.path.exists(s) and base in open(s, encoding="utf-8", errors="replace").read()]

json.dump({"generated_by": "r370 bm-a D-20260928-03(1) S1 census",
           "walk_commits": commit_count, "hits": census, "consumers": consumers},
          open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("walk commits:", commit_count, "| multi-machine co-writer files:", len(census))
for f, c in sorted(census.items(), key=lambda kv: -kv[1]["commits"])[:40]:
    print(f"{c['commits']:>4}  {','.join(c['machines']):>12}  {f}  consumers={len(consumers[f])}")
