import subprocess, os, shutil, json

GIT = r"C:\Program Files\Git\cmd\git.exe"
ROOT = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"
Q = os.path.join(ROOT, "results", "_quarantine", "r964-estate-20261013")

os.makedirs(Q, exist_ok=True)

def gitb(args):
    return subprocess.run([GIT] + args, cwd=ROOT, capture_output=True).stdout

status = gitb(["status", "--porcelain"]).decode("utf-8", "replace").splitlines()
modified, untracked_on_origin = [], []
for line in status:
    if not line.strip():
        continue
    code = line[:2].strip()
    path = line[3:].strip().strip('"')
    if code == "??":
        r = subprocess.run([GIT, "cat-file", "-e", f"origin/main:{path}"], cwd=ROOT, capture_output=True)
        if r.returncode == 0:
            untracked_on_origin.append(path)
    elif code == "M":
        modified.append(path)

manifest = {"ts": "2026-10-13T21:4x", "why": "FF-to-origin estate preservation: r964-era (10-11 02:5x) worktree regens superseded by origin (bm-c/bm-b chains through 10-13); w17 faces = marker-repair surgery residue; origin = landed canonical 6fe9ef04b", "modified": modified, "untracked_on_origin": untracked_on_origin, "kept_in_place_untracked": ["results/paper/marks/marks-20261012.jsonl", "results/paper/marks/marks-20261013.jsonl"]}
copied = 0
for p in modified + untracked_on_origin:
    src = os.path.join(ROOT, p)
    dst = os.path.join(Q, p.replace("/", "__"))
    if os.path.isfile(src):
        shutil.copy2(src, dst)
        copied += 1
with open(os.path.join(Q, "manifest.json"), "w", encoding="utf-8") as f:
    json.dump(manifest, f, ensure_ascii=False, indent=1)
print(f"backed up {copied} files -> {Q}")
print(f"modified={len(modified)} untracked_on_origin={len(untracked_on_origin)}")
