"""r908 bm-b S0 rebase resolver-2: pick 5/5 (ab9d8129c absorb snapshot) self-overlap.

The absorb commit (23:44 snapshot of satengine/ext_slots/p1d_gates faces) is a
STALE snapshot of faces already absorbed NEWER into pick 2/5 (914004bad, 23:47+).
Law r685-3: stale daemon-snapshot pick may be dropped WITH PROOF -- here the
proof = per-face ts comparison (json: max ISO ts in stage2 >= stage3) or
line-superset (jsonl: stage2 lines superset of stage3). Take stage2 (HEAD side),
fail-closed if any assertion breaks. Receipt appended to
results/_r908bmb_rb_resolver.json under key "resolver2".
"""
import json
import os
import re
import subprocess
import sys

REPO = os.path.dirname(os.path.abspath(__file__))
RECEIPT = os.path.join(REPO, "results", "_r908bmb_rb_resolver.json")
ISO_RE = re.compile(r"\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}(:\d{2})?")


def git(args):
    r = subprocess.run(["git"] + args, capture_output=True)
    if r.returncode != 0:
        raise RuntimeError("git %s rc=%d: %s" % (args, r.returncode, r.stderr[:300]))
    return r.stdout


def main():
    out = git(["ls-files", "-u"]).decode("utf-8", "replace")
    faces = {}
    for line in out.strip().splitlines():
        meta, path = line.split("\t", 1)
        mode, sha, stage = meta.split()
        faces.setdefault(path, {})[int(stage)] = sha
    expected = {
        "results/ext_slots_pull_status.json",
        "results/p1d_gates.json",
        "results/saturation_engine/face_bm-b.json",
        "results/saturation_engine/history_bm-b.jsonl",
        "results/saturation_engine/state_bm-b.json",
    }
    if set(faces) != expected:
        raise RuntimeError("UU set mismatch: %s" % sorted(faces))

    log = []
    for path in sorted(expected):
        st = faces[path]
        for s in (2, 3):
            if s not in st:
                raise RuntimeError("%s missing stage %d" % (path, s))
        s2 = git(["cat-file", "-p", st[2]]).decode("utf-8", "replace")
        s3 = git(["cat-file", "-p", st[3]]).decode("utf-8", "replace")
        if path.endswith(".jsonl"):
            l2, l3 = set(s2.splitlines()), set(s3.splitlines())
            if not l2 >= l3:
                raise RuntimeError("%s: stage2 NOT superset (s2=%d s3=%d)" %
                                   (path, len(l2), len(l3)))
            log.append("%s: stage2 superset of stage3 (s2=%d s3=%d) -> take HEAD" %
                       (path, len(l2), len(l3)))
        else:
            t2 = ISO_RE.findall(s2)
            t3 = ISO_RE.findall(s3)
            m2 = max(t2) if t2 else ""
            m3 = max(t3) if t3 else ""
            if not (m2 and m3 and m2 >= m3):
                raise RuntimeError("%s: ts proof failed s2max=%r s3max=%r" %
                                   (path, m2, m3))
            log.append("%s: stage2 max-ts %s >= stage3 max-ts %s -> take HEAD" %
                       (path, m2, m3))
        for ln in s2.splitlines():
            if ln.startswith(("<<<<<<<", ">>>>>>>", "=======")):
                raise RuntimeError("%s: marker in stage2 blob" % path)
        with open(os.path.join(REPO, path), "w", encoding="utf-8", newline="") as f:
            f.write(s2)

    with open(RECEIPT, encoding="utf-8") as f:
        receipt = json.load(f)
    receipt["resolver2"] = {"stage": "pick 5/5 (ab9d8129c stale absorb self-overlap)",
                            "recipe": "drop stale pick-side snapshot (r685-3 with proof)",
                            "decisions": log}
    with open(RECEIPT, "w", encoding="utf-8") as f:
        json.dump(receipt, f, ensure_ascii=True, indent=1)
    print("RESOLVER2 OK: 5 faces took HEAD side (stale snapshot dropped with proof)")
    for line in log:
        print("DEC " + line)
    return 0


if __name__ == "__main__":
    sys.exit(main())
