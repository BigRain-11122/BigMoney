# -*- coding: utf-8 -*-
# r651 bm-c rebase resolver: results/compute_audit.json (shared append-only
# history face; upstream round vs my S6 row same-window). Laws: r648 sha
# channel (ls-files -u -> cat-file, NEVER :N:); marker hard-gate both sides
# (r806); ts-union resolution per r650 merge precedent; add+continue atomic
# (r787); EDITOR blunted (r765). Machine JSON face: ANY marker substring =
# pollution (not a pit-doc quoting face).
import subprocess, json, sys, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def git(*args):
    p = subprocess.run(["git", "-C", ROOT] + list(args), capture_output=True)
    if p.returncode != 0:
        raise RuntimeError("git %s rc=%d %s" % (args, p.returncode, p.stderr.decode("utf-8", "replace")))
    return p.stdout

def main():
    ls = git("ls-files", "-u").decode().strip().splitlines()
    shas = {}
    for line in ls:
        parts = line.split()
        # git ls-files -u columns: <mode> <sha> <stage> <path>
        shas[int(parts[2])] = parts[1]
    assert set(shas) == {1, 2, 3}, "unexpected stage set: %s" % sorted(shas)

    blobs = {}
    for stage, sha in shas.items():
        b = git("cat-file", "-p", sha)
        for m in (b"<<<<<<<", b">>>>>>>", b"|||||||"):
            assert m not in b, "marker pollution in stage %d blob %s" % (stage, sha)
        obj = json.loads(b.decode("utf-8-sig"))
        assert "history" in obj, "no history face in stage %d" % stage
        blobs[stage] = obj
    print("stages ok: base=%d ours(onto)=%d theirs(mine)=%d rows" % (
        len(blobs[1]["history"]), len(blobs[2]["history"]), len(blobs[3]["history"])))

    def key(r):
        return (r.get("ts", ""), r.get("machine", ""))

    union = {}
    for st in (2, 3):
        for r in blobs[st]["history"]:
            k = key(r)
            if k in union:
                # same key both sides: keep the newer-ts-equal face deterministic (ours-onto wins ties)
                continue
            union[k] = r
    rows = sorted(union.values(), key=key)
    # every row from both sides must survive
    k2 = {key(r) for r in blobs[2]["history"]}
    k3 = {key(r) for r in blobs[3]["history"]}
    assert k2 | k3 == set(union.keys()), "union key loss"

    # top-level: take stage-2 (upstream onto-side) non-history keys, override history
    out = dict(blobs[2])
    out["history"] = rows
    # format mirror: try to match upstream serialization (indent=1, LF)
    text = json.dumps(out, indent=1, ensure_ascii=False) + "\n"
    rb = open(os.path.join(ROOT, "results", "compute_audit.json"), "rb").read()
    if rb.startswith(b"\xef\xbb\xbf"):
        text = "\ufeff" + text
    with open(os.path.join(ROOT, "results", "compute_audit.json"), "wb") as f:
        f.write(text.encode("utf-8"))
    # re-verify from disk
    chk = json.loads(open(os.path.join(ROOT, "results", "compute_audit.json"), "rb").read().decode("utf-8-sig"))
    assert {key(r) for r in chk["history"]} == k2 | k3
    assert len(chk["history"]) == len(rows)
    print("resolved rows=%d (union %d+%d, overlap %d)" % (
        len(rows), len(k2), len(k3), len(k2 & k3)))

if __name__ == "__main__":
    main()
