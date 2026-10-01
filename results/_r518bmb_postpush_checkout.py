import subprocess

EXCLUDE = {
    "results/saturation_engine/face_bm-b.json",
    "results/saturation_engine/history_bm-b.jsonl",
    "results/saturation_engine/state_bm-b.json",
    "results/pool_core_samples.jsonl",
}
out = subprocess.check_output(["git", "status", "--porcelain=v1"], text=True)
paths = []
for line in out.splitlines():
    st = line[:2]
    p = line[3:].strip()
    if st == "??":
        continue
    if line.startswith("R ") or line.startswith("C "):
        p = line[3:].split("\t")[-1].strip()
    if p in EXCLUDE:
        continue
    paths.append(p)
print(len(paths), "paths to checkout")
subprocess.check_call(["git", "checkout", "HEAD", "--"] + paths)
print("checkout OK")
