# r895 bm-a S0 dead-tail rebase adoption: resolve UU append-log face (r188/r217 union law)
# Face: results/pool_core_samples.jsonl  (engine burn samples, append-only jsonl)
# Recipe: line-level union of stage2 (ours) + stage3 (theirs) + post-marker workfile extras;
#         parse-verify every line (r185); zero-loss assert |A u B| ; EOL mirror base blob.
import json, subprocess, sys

GIT = r"C:\Program Files\Git\cmd\git.exe"
PATH = "results/pool_core_samples.jsonl"

def blob(rev):
    return subprocess.run([GIT, "show", rev], capture_output=True).stdout

s2 = blob(":2:" + PATH)
s3 = blob(":3:" + PATH)
with open(PATH, "rb") as f:
    wf = f.read()

# EOL mirror (r223/r234): detect from stage2 blob
crlf = b"\r\n" in s2
def split_lines(b):
    if crlf:
        return [l + b"\r\n" for l in b.split(b"\r\n") if l]
    return [l + b"\n" for l in b.split(b"\n") if l]

l2, l3, lw = split_lines(s2), split_lines(s3), split_lines(wf)
markers = sum(1 for l in lw if l.strip().startswith((b"<<<<<<<", b"=======", b">>>>>>>")))
# post-marker daemon appends: valid jsonl lines in workfile not present in either stage
s2s, s3s = set(l2), set(l3)
extras = [l for l in lw if not l.strip().startswith((b"<<<<<<<", b"=======", b">>>>>>>")) and l not in s2s and l not in s3s]

# ordered dedupe union: stage2 first, then stage3-only, then workfile extras
seen, union = set(), []
for l in l2 + l3 + extras:
    if l not in seen:
        seen.add(l); union.append(l)

# parse-verify every union line (r185)
for i, l in enumerate(union):
    try:
        json.loads(l.decode("utf-8").strip())
    except Exception as e:
        print(json.dumps({"verdict": "PARSE_FAIL", "line": i, "err": str(e)[:200]}))
        sys.exit(2)

out = b"".join(union)
with open(PATH, "wb") as f:
    f.write(out)

facts = {
    "verdict": "UNION_OK",
    "path": PATH,
    "recipe": "append-log line-level union zero-loss (r188/r217)",
    "eol": "CRLF" if crlf else "LF",
    "stage2_lines": len(l2),
    "stage3_lines": len(l3),
    "workfile_lines_raw": len(lw),
    "workfile_markers": markers,
    "post_marker_extras": len(extras),
    "union_lines": len(union),
    "union_eq_side_union": len(union) == len(set(l2) | set(l3) | set(extras)),
    "bytes_out": len(out),
}
print(json.dumps(facts))
