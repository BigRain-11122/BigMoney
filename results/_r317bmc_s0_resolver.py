"""r317 bm-c S0 integration: CODELY.md diff3 conflict union resolver.

r315 entry-extraction law (CODELY union v2): this side's commit carries a tail
append block; peer side appended its own entries on the same base line. Union =
peer(HEAD) section + this-side-only lines, with fail-closed assertions.
Raw-bytes safe: read/write utf-8, splitlines(keepends) preserves per-line EOL.
"""
import sys

PATH = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\CODELY.md"

raw = open(PATH, "rb").read().decode("utf-8")
lines = raw.splitlines(keepends=True)

# line-START markers only (inline mentions inside entry text are legitimate)
marks = [(i, ln) for i, ln in enumerate(lines)
         if ln.startswith(("<<<<<<<", "|||||||", "=======", ">>>>>>>"))]

assert len(marks) == 4, f"expected 4 conflict markers, found {len(marks)}: {[m[1][:40] for m in marks]}"
(m0, l0), (m1, _), (m2, _), (m3, _) = marks
assert l0.startswith("<<<<<<<"), "first marker not <<<<<<<"
assert lines[m1].startswith("|||||||"), "second marker not |||||||"
assert lines[m2].startswith("======="), "third marker not ======="
assert lines[m3].startswith(">>>>>>>"), "fourth marker not >>>>>>>"

head_sec = lines[m0 + 1: m1]
base_sec = lines[m1 + 1: m2]
theirs_sec = lines[m2 + 1: m3]
pre = lines[: m0]
post = lines[m3 + 1:]

assert len(head_sec) == 1, f"HEAD section lines={len(head_sec)} (expected 1)"
assert len(base_sec) == 1, f"BASE section lines={len(base_sec)} (expected 1)"
assert len(theirs_sec) >= 2, f"THEIRS section lines={len(theirs_sec)} (expected >=2)"

# HEAD side must be base + peer append on same line (r315 pattern: peer appended
# its r505 entry onto the shared r315 tail line).
assert head_sec[0].startswith(base_sec[0].rstrip("\r\n")), \
    "HEAD line is not base+append (structure changed, manual review needed)"
# my r315 copy must equal base copy (my side did not modify r315 text itself)
assert theirs_sec[0].rstrip("\r\n") == base_sec[0].rstrip("\r\n"), \
    "THEIRS first line != BASE copy (my r315 text diverged, manual review)"

theirs_only = theirs_sec[1:]
# dedupe fail-closed: my-only entries must not already exist anywhere
for ln in theirs_only:
    t = ln.lstrip()
    if not t:
        continue
    assert ln not in pre and ln not in head_sec, f"dedupe violation: {t[:60]}"
    tag = t[:40]
    assert not any(l.startswith(tag[:28]) for l in pre + head_sec), \
        f"dedupe violation (prefix): {tag}"

union = head_sec + theirs_only
out_lines = pre + union + post
out = "".join(out_lines)

# post-write self-verify: zero line-start markers remain; both new entries present
check = out.splitlines(keepends=True)
bad = [ln[:50] for ln in check if ln.startswith(("<<<<<<<", "|||||||", "=======", ">>>>>>>"))]
assert not bad, f"markers remain after resolve: {bad}"
assert any(l.startswith("- [2026-10-01 13:3x r316 bm-c]") for l in check), "r316 own entry lost"
# r505 peer entry is a mid-line append onto the shared r315 tail line -> substring check
assert "- [2026-10-01 13:2x r505 bm-b]" in out, "r505 peer entry lost"

open(PATH, "wb").write(out.encode("utf-8"))

print(f"OK union: pre={len(pre)} head=1 base=1 theirs={len(theirs_sec)} "
      f"theirs_only={len(theirs_only)} post={len(post)} total={len(check)}")
