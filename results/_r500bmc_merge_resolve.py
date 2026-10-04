# r500 bm-c merge resolver: UU line-union for both-sides-append jsonl faces
# Law chain: r657-2 (HEAD:/MERGE_HEAD: raw blobs, immune to add pollution),
# r453/r499 (exact-line dedup keep-first union), r656 (line-level canon zero-loss containment),
# r446 (probe-as-file), r489 (output to file, no console dependence).
import json, subprocess, sys

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"

def blob(rev, path):
    return subprocess.check_output(["git", "-C", REPO, "show", "%s:%s" % (rev, path)])

def canon_lines(raw):
    txt = raw.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    lines = txt.split(b"\n")
    if lines and lines[-1] == b"":
        lines = lines[:-1]
    return lines

faces = ["results/pool_core_samples.jsonl", "results/pool_red_flags.jsonl"]
receipt = {}
for path in faces:
    raw_ours = blob("HEAD", path)
    raw_theirs = blob("MERGE_HEAD", path)
    ours = canon_lines(raw_ours)
    theirs = canon_lines(raw_theirs)
    ours_set = set(ours)
    theirs_set = set(theirs)
    theirs_only = [ln for ln in theirs if ln not in ours_set]
    union = ours + theirs_only
    union_set = set(union)
    # zero-loss assertions (fail-closed)
    assert ours_set <= union_set, "ours loss in %s" % path
    assert theirs_set <= union_set, "theirs loss in %s" % path
    # conflict-marker absence in final bytes
    eol = b"\r\n" if b"\r\n" in raw_ours else b"\n"
    out = eol.join(union) + eol
    assert b"<<<<<<<" not in out and b">>>>>>>" not in out
    with open(REPO + "\\" + path.replace("/", "\\"), "wb") as f:
        f.write(out)
    receipt[path] = {
        "ours_lines": len(ours),
        "theirs_lines": len(theirs),
        "theirs_only_appended": len(theirs_only),
        "union_lines": len(union),
        "dup_lines_dropped": len(theirs) - len(theirs_only),
        "eol": "CRLF" if eol == b"\r\n" else "LF",
        "zero_loss": True,
    }

with open(REPO + r"\results\_r500bmc_merge_resolve.json", "w", encoding="utf-8") as f:
    json.dump(receipt, f, ensure_ascii=False, indent=1)
print("RESOLVE-OK " + json.dumps(receipt))
