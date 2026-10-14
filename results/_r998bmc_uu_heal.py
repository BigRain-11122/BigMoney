"""r998 bm-c: heal stash-pop UU fleet/machine-health.json (union, r996 c85e806c9 precedent).

Both stages share identical prefix (through 13:36 entry); ours tail = 14:11,
stash side tail = 14:36 (ts-newer). Union = prefix + 14:11 + 14:36.
Text-level surgery preserves PS ConvertTo-Json byte formatting.
"""
import json
import subprocess
import sys

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
GIT = r"C:\Program Files\Git\cmd\git.exe"
PATH = "fleet/machine-health.json"


def blob_text(sha: str) -> str:
    out = subprocess.run([GIT, "-C", REPO, "cat-file", "-p", sha],
                         capture_output=True)
    if out.returncode != 0:
        print("FATAL: cat-file fail", sha, out.stderr.decode("utf-8", "replace"))
        sys.exit(2)
    return out.stdout.decode("utf-8")


def unmerged():
    out = subprocess.run([GIT, "-C", REPO, "ls-files", "-u", "--", PATH],
                         capture_output=True)
    lines = out.stdout.decode("utf-8").strip().splitlines()
    stages = {}
    for ln in lines:
        parts = ln.split("\t")
        meta = parts[0].split()
        stages[int(meta[2])] = meta[1]
    return stages


st = unmerged()
print("stages:", st)
if set(st) != {1, 2, 3}:
    print("FATAL: expected stages 1/2/3, got", sorted(st))
    sys.exit(2)

s1, s2, s3 = blob_text(st[1]), blob_text(st[2]), blob_text(st[3])

# EOL normalization: HEAD side (stage2) carries CRLF, stash side (stage3) LF.
# Content is identical modulo \r (r998 diff-at-byte-1 evidence). Normalize
# stage2 to LF so prefix comparison + union assembly are EOL-consistent;
# union output adopts stage3's LF style (newest live face).
s2 = s2.replace("\r\n", "\n")
s1 = s1.replace("\r\n", "\n")


def split_outer_array(text: str):
    """Split '[\n <elem1>,\n <elem2>\n ]' into (elem1, elem2) text parts.

    Strategy: find the last top-level ',\n    {' boundary at bracket depth 1
    scanning from the start; verified by json round-trip of each part.
    """
    assert text.lstrip().startswith("["), "not array"
    depth = 0
    in_str = False
    esc = False
    tops = []
    for i, ch in enumerate(text):
        if in_str:
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                in_str = False
            continue
        if ch == '"':
            in_str = True
        elif ch in "[{":
            depth += 1
        elif ch in "]}":
            depth -= 1
        elif ch == "," and depth == 1:
            tops.append(i)
    if len(tops) != 1:
        print("FATAL: expected exactly 1 top-level comma, got", len(tops))
        sys.exit(2)
    c = tops[0]
    elem1 = text[1:c].strip()
    rest = text[c + 1:].rstrip()
    assert rest.endswith("]"), "tail malformed"
    elem2 = rest[:-1].strip()
    json.loads("[" + elem1 + "]")
    json.loads("[" + elem2 + "]")
    return elem1, elem2


p1, tail_ours = split_outer_array(s2)
p3, tail_stash = split_outer_array(s3)
if p1 != p3:
    print("FATAL: prefix diverges between stages -- union assumption broken")
    print("prefix len ours:", len(p1), "stash:", len(p3))
    sys.exit(2)

import re


def ts_of(elem: str) -> str:
    m = re.search(r'"ts":\s*"(\d{4}-\d{2}-\d{2} \d{2}:\d{2})"', elem)
    return m.group(1) if m else ""


t_ours, t_stash = ts_of(tail_ours), ts_of(tail_stash)
print("ts ours/stash:", t_ours, "/", t_stash)
if not (t_ours < t_stash):
    print("FATAL: expected ours ts < stash ts (stash = newer live face)")
    sys.exit(2)

union = "[\n    " + p1 + ",\n    " + tail_ours + ",\n    " + tail_stash + "\n]"
parsed = json.loads(union)
assert isinstance(parsed, list) and len(parsed) == 3, "union shape"
union_blob = union.encode("utf-8")

assert "<<<<<<<" not in union and ">>>>>>>" not in union
assert t_ours in union and t_stash in union

with open(REPO + "\\fleet\\machine-health.json", "wb") as f:
    f.write(union_blob)
print("union written:", len(union_blob), "bytes; entries ts", t_ours, "+", t_stash)
