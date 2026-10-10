# r826 bm-b pick2 resolver — 4 daemon faces: pick2 (lane-sync 09:0x snapshot) vs HEAD side
# (= live daemon state absorbed into pick1-close f51a73f99 at ~09:2x). Live-wins per lane law
# (r917/r685-3): stage2 is the absorbed live face, strictly newer than the stale pick snapshot.
# history jsonl = line-level union zero-loss (r188). r648 sha channel. r185 parse-verify.
import io, json, subprocess

uu = {}
for ln in subprocess.run(["git", "ls-files", "-u"], capture_output=True).stdout.decode("utf-8", "replace").splitlines():
    meta, path = ln.split("\t")
    _, sha, stage = meta.split()
    uu.setdefault(path, {})[int(stage)] = sha

def blob(sha):
    b = subprocess.run(["git", "cat-file", "-p", sha], capture_output=True).stdout
    assert b, "EMPTY BLOB r648: " + sha
    return b

receipt = {"round": "r826-pick2", "faces": {}}
for p in ["results/p1d_gates.json", "results/saturation_engine/face_bm-b.json", "results/saturation_engine/state_bm-b.json"]:
    b2 = blob(uu[p][2])
    assert b"<<<<<<<" not in b2
    json.loads(b2.decode("utf-8"))            # r185
    io.open(p, "wb").write(b2)
    receipt["faces"][p] = {"recipe": "daemon live-wins: take stage2 (absorbed live > stale pick snapshot)"}

p = "results/saturation_engine/history_bm-b.jsonl"
l2 = blob(uu[p][2]).decode("utf-8").splitlines()
l3 = blob(uu[p][3]).decode("utf-8").splitlines()
seen, out = set(), []
for ln in l2 + l3:
    if ln not in seen:
        seen.add(ln); out.append(ln)
assert set(l3) <= set(out) and set(l2) <= set(out), "union loss"
superset = set(l3) <= set(l2)
eol = "\r\n" if b"\r\n" in blob(uu[p][2]) else "\n"
io.open(p, "w", encoding="utf-8", newline="").write(eol.join(out) + (eol if out else ""))
receipt["faces"][p] = {"recipe": "jsonl line-union zero-loss", "s2_lines": len(l2), "s3_lines": len(l3), "union_lines": len(out), "s2_superset_of_s3": superset}

bad = []
for p in receipt["faces"]:
    b = io.open(p, "rb").read()
    if b"<<<<<<<" in b or b">>>>>>>" in b: bad.append(p)
assert not bad, "MARKERS: " + repr(bad)
with io.open("results/_r826bmb_rebase_resolver_p2.json", "w", encoding="utf-8", newline="\n") as f:
    json.dump(receipt, f, ensure_ascii=False, indent=1)
print("PICK2 RESOLVED", len(receipt["faces"]), "faces; superset:", superset, "jsonl union:", len(out))
