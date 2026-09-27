"""R317 bm-b autostash-pop conflict resolver (third-writer journal faces).

Structural face: autofill ticks (~10min) rewrite results/autofill_state.json
while every cross-machine `git pull --rebase` autostashes the worktree and
pops it back -- the pop conflicts whenever origin advanced the same file.
Hand-slicing conflict markers on nested JSON is fragile (r317 live fire:
one miscounted brace corrupted the whole file before the stage-rebuild
rescue). Canon here: rebuild from the two index stages, never from the
marker text.

Usage (run INSTEAD of hand-editing the UU file):
  python results/_r317bmb_autostash_union.py results/autofill_state.json
Then: git reset -- <file>   (clear UU, keep as unstaged third-writer face)
      git stash drop        (per pop-conflict hint)
      git restore --staged <any incidental staged third-writer file>

Union law (matches committed-face practice, r316/r313 canons):
  - list field "launches": key-dedup on (ts, machine, entry, shard, pid);
    HEAD stage :2: wins on key collision, stash stage :3: adds its
    missing entries; stable-sorted by ts (append-journal semantics).
  - scalar "last_tick": newer ts wins (take-new-on-newer-ts canon).
  - rewrite with indent=1 + CRLF to match the committed face.
Idempotent safety: refuses to run if the file has no conflict stages.
"""
import json
import subprocess
import sys

KEY_FIELDS = ("ts", "machine", "entry", "shard", "pid")
LIST_FIELD = "launches"
SCALAR_NEWEST = "last_tick"


def stage(path, n):
    r = subprocess.run(["git", "show", f":{n}:{path}"],
                       capture_output=True)
    if r.returncode != 0:
        return None
    return json.loads(r.stdout.decode("utf-8"))


def main():
    if len(sys.argv) != 2:
        print("usage: _r317bmb_autostash_union.py < conflicted-file >")
        return 3
    path = sys.argv[1].replace("\\", "/")
    ours = stage(path, 2)          # HEAD face (origin-advanced)
    theirs = stage(path, 3)        # autostash face (local tick)
    if ours is None or theirs is None:
        print("no unmerged stages for this path -- nothing to do")
        return 0
    merged = {}
    merged[LIST_FIELD] = []
    seen = {}
    for src in (ours, theirs):    # HEAD first = wins key collisions
        for e in src.get(LIST_FIELD, []):
            k = tuple(e.get(f) for f in KEY_FIELDS)
            seen.setdefault(k, e)
    merged[LIST_FIELD] = sorted(seen.values(),
                                key=lambda e: str(e.get("ts", "")))
    for k in ours:
        if k == LIST_FIELD:
            continue
        if k == SCALAR_NEWEST:
            faces = [ours.get(SCALAR_NEWEST), theirs.get(SCALAR_NEWEST)]
            faces = [f for f in faces if f]
            merged[k] = max(faces, key=lambda f: str(f.get("ts", ""))) \
                if faces else None
        else:
            merged[k] = ours[k]   # HEAD authoritative on other fields
    text = json.dumps(merged, indent=1, ensure_ascii=False) + "\r\n"
    with open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write(text)
    chk = json.load(open(path, encoding="utf-8"))
    print(f"union written: {len(chk[LIST_FIELD])} entries, "
          f"{SCALAR_NEWEST}.ts={chk[SCALAR_NEWEST]['ts']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
