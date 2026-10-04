"""r685 bm-a: resolve MASS_TRIAL_W3_PREREG.md merge conflict (v2).

ORIGIN (r483 bm-c) = canonical; keep whole, append bm-a chain-integrity line
at the tail of the theirs block (before common sec9 text that follows the
conflict region). Ours side dropped (duplicate backfill).
"""
MARK = (b"<<<<<<<", b"=======", b">>>>>>>")
S7 = "\u00a77".encode()
S8 = "\u00a78".encode()

raw = open(r"research/MASS_TRIAL_W3_PREREG.md", "rb").read()
eol = b"\r\n" if b"\r\n" in raw[:4000] else b"\n"
lines = raw.split(eol)

o = [i for i, l in enumerate(lines) if l.lstrip().startswith(b"<<<<<<<")]
m = [i for i, l in enumerate(lines) if l.lstrip().startswith(b"=======")]
c = [i for i, l in enumerate(lines) if l.lstrip().startswith(b">>>>>>>")]
assert len(o) == len(m) == len(c) == 1, f"markers {len(o)}/{len(m)}/{len(c)}"
oi, mi, ci = o[0], m[0], c[0]
assert oi < mi < ci
theirs = lines[mi + 1:ci]
joined = eol.join(theirs)
assert S7 in joined and S8 in joined, "theirs block missing sec7/8"

extra = (
    "- **\u94fe\u5b8c\u6574\u6027\u6ce8\u8bb0\uff08r685 bm-a \u540c\u7a97\u8865\u5145\uff09**\uff1a"
    "finalize \u9996\u8dd1\u649e dup \u643a\u5e26\u9762\u4ea7\u51fa bogus \u8d26\u672c\u5757\uff08complete=false\u00b7batch_trials 6041\uff09\u2014\u2014"
    "\u672a\u63d0\u4ea4\u672a\u63a8\u9001\uff0c\u4e24\u4ef6 quarantine \u9694\u79bb\uff08bogus+wrongprev\u00b7manifest \u7559\u75d5\uff09\uff1b"
    "science_gates.ledger_head/active_voids \u589e `_quarantine` \u626b\u63cf\u6392\u9664\uff08\u6bb5\u5339\u914d\uff09"
    "+ selftest \u817f 70/70\u2014\u2014\u9694\u79bb\u533a\u8d26\u672c\u7c7b json \u4ef6\u56de\u6d41\u94fe\u5934\u7684 fleet \u7ea7\u5751\u5df2\u7acb\u6cd5"
    "\uff08CODELY r685 \u4e24\u5f8b\uff09\u3002"
).encode()

# strip trailing blank lines from theirs, append extra, re-add one blank
while theirs and not theirs[-1].strip():
    theirs.pop()
theirs_new = theirs + [extra]

new = lines[:oi] + theirs_new + lines[ci + 1:]
assert sum(1 for l in new if l.lstrip().startswith(MARK)) == 0
out = eol.join(new)
open(r"research/MASS_TRIAL_W3_PREREG.md", "wb").write(out)
print("resolved: theirs-canonical + chain-integrity line, markers 0")
