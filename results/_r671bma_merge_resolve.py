"""r671 bm-a merge resolver v2 for CODELY.md: strip blank padding, anchor on stripped, union append theirs-new."""
import subprocess, sys

REPO = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"

def git_show_bytes(ref, path):
    r = subprocess.run(["git", "-C", REPO, "show", f"{ref}:{path}"], capture_output=True)
    if r.returncode != 0:
        raise SystemExit(f"git show rc={r.returncode}")
    return r.stdout

def norm(l: bytes) -> bytes:
    return l.rstrip(b"\r\n")

p = "CODELY.md"
ours = git_show_bytes("HEAD", p)
their = git_show_bytes("MERGE_HEAD", p)

crlf = ours.count(b"\r\n"); lf_only = ours.count(b"\n") - crlf
eol = b"\r\n" if crlf > lf_only else b"\n"
print("eol form:", "CRLF" if eol == b"\r\n" else "LF")

def strip_blanks(ls):
    pad = 0
    while ls and norm(ls[-1]) == b"":
        ls.pop(); pad += 1
    return ls, pad

ours_l, ours_pad = strip_blanks(ours.splitlines())
their_l, their_pad = strip_blanks(their.splitlines())
print("ours content lines:", len(ours_l), "pad:", ours_pad, "| theirs:", len(their_l), "pad:", their_pad)

their_set = set(norm(l) for l in their_l)
anchor_idx = None
for i in range(len(ours_l) - 1, -1, -1):
    if norm(ours_l[i]) != b"" and norm(ours_l[i]) in their_set:
        anchor_idx = i
        break
print("anchor at ours line idx:", anchor_idx, "of", len(ours_l))
if anchor_idx is None:
    raise SystemExit("no common anchor line found")
anchor_line = norm(ours_l[anchor_idx])
if not anchor_line.startswith(b"- ["):
    raise SystemExit(f"anchor not an entry line: {anchor_line[:60]!r}")

# same anchor position in theirs (last occurrence)
t_anchor = None
for i in range(len(their_l) - 1, -1, -1):
    if norm(their_l[i]) == anchor_line:
        t_anchor = i
        break

ours_set = set(norm(l) for l in ours_l)
their_new = [l for l in their_l[t_anchor+1:] if norm(l) not in ours_set]
seen = set(); their_dd = []
for l in their_new:
    n = norm(l)
    if n in seen: continue
    seen.add(n); their_dd.append(l)
print("their-new unique:", len(their_dd))

merged = list(ours_l) + ([b""] if their_dd and norm(ours_l[-1]) != b"" else []) + their_dd
out = eol.join(norm(l) for l in merged) + (eol * max(ours_pad, 2))
with open(REPO + "\\" + p, "wb") as f:
    f.write(out)

mc = sum(1 for l in out.split(b"\n") if l.lstrip(b"\r").startswith((b"<<<<<<<", b">>>>>>>", b"=======")))
print("markers:", mc, "| merged lines:", len(merged), "| bytes:", len(out))
assert mc == 0 and len(their_dd) > 0, "union must carry their entries and zero markers"
print("RESOLVER V2 OK")
