"""r448 bm-c merge resolver: single UU face research/pit-encoding.md.

Form = line-level union (allowed form for registered/ledger-class faces per
S0-restore classification gate): keeps BOTH sides' appended entries verbatim,
removes ONLY git conflict markers. Zero content-line loss is asserted
(ours-entry present + theirs-entry present + pre/post segments verbatim).
Then: staged-set marker sweep (r644 content law) + JSON reparse of key
auto-merged shared faces (pool/fuse/attrition/criteria/audit/token/readiness).
"""
import json
import os
import subprocess
import sys

RB = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
CREATE = 0x08000000
FACE = "research/pit-encoding.md"
FULL = os.path.join(RB, FACE.replace("/", os.sep))


def git(*a):
    p = subprocess.run(["git", "-C", RB] + list(a), capture_output=True,
                       creationflags=CREATE)
    return p.returncode, (p.stdout or b""), (p.stderr or b"")


# ---------- 1) pit-encoding.md marker-strip union surgery ----------
data = open(FULL, "rb").read()
M1 = b"<<<<<<< HEAD"
M4 = b">>>>>>> origin/main"
assert data.count(M1) == 1, "expect exactly 1 conflict block, got %d" % data.count(M1)
s = data.find(M1)
# EOL probe BEFORE any needle surgery (r657 law: conflict faces land CRLF under autocrlf)
m1_line_nl = data.find(b"\n", s)
eol = b"\r\n" if data[m1_line_nl - 1:m1_line_nl] == b"\r" else b"\n"
EL = len(eol)
s_body = m1_line_nl + 1
p_pipe = data.find(b"|||||||", s_body)
assert p_pipe > s_body, "diff3 base marker not found"
assert data[p_pipe - EL:p_pipe] == eol, "pipe marker not at line start"
ours = data[s_body:p_pipe - EL]
pipe_line_nl = data.find(b"\n", p_pipe)  # end of "||||||| <base>" line
assert data[pipe_line_nl + 1:pipe_line_nl + 1 + 7 + EL] == b"=======" + eol, "======= not right after base section"
theirs_start = pipe_line_nl + 1 + 7 + EL
p_theirs_end = data.find(eol + M4, theirs_start)
assert p_theirs_end > theirs_start, "closing marker not found"
theirs = data[theirs_start:p_theirs_end]
post_start = p_theirs_end + EL + len(M4) + EL  # EOL before marker + marker + EOL after
post = data[post_start:]

assert ours.startswith(b"- ") and b"r447" in ours, "ours block shape"
assert b"r662 bm-a" in theirs, "theirs block shape"

result = data[:s] + ours + eol + theirs + eol + post
# zero-marker assertion (conflict-shaped only, r644 law)
for m in (b"<<<<<<< HEAD", b">>>>>>> origin/main", b"|||||||"):
    assert m not in result, "marker residue: %r" % m
# zero-loss assertions: both entries in result, flanking bytes verbatim
assert ours in result and theirs.strip() in result, "entry loss"
assert result.startswith(data[:s]) and result.endswith(post), "flank drift"
result.decode("utf-8")  # strict utf-8 self-verify
open(FULL, "wb").write(result)
import hashlib
sha16 = hashlib.sha256(result).hexdigest()[:16]
print("PIT-ENCODING-UNION-OK eol=%s sha16=%s ours=%dB theirs=%dB total=%dB" % (repr(eol), sha16, len(ours), len(theirs), len(result)))

# ---------- 2) staged-set conflict-marker sweep ----------
rc, out, _ = git("diff", "--cached", "--name-only")
staged = [ln for ln in out.decode("utf-8", "replace").splitlines() if ln.strip()]
bad = []
for rel in staged:
    ap = os.path.join(RB, rel.replace("/", os.sep))
    if not os.path.isfile(ap):
        continue
    raw = open(ap, "rb").read()
    if b"<<<<<<< HEAD" in raw or b"\n>>>>>>> " in raw or b"\n|||||||" in raw:
        bad.append(rel)
assert not bad, "conflict marker residue in staged: %r" % bad
print("STAGED-MARKER-SWEEP CLEAN (%d files)" % len(staged))

# ---------- 3) JSON reparse of key auto-merged shared faces ----------
JSON_FACES = [
    "results/runnable_pool.json",
    "results/crash_fuse.json",
    "results/gate_attrition.json",
    "results/post_review_criteria.json",
    "results/compute_audit.json",
    "results/token_usage.json",
    "results/finalize_trio_readiness.json",
    "state.json",
    "state-bm-a.json",
    "fleet/machines/bm-a.json",
    "fleet/machines/bm-b.json",
    "results/autofill_state.bm-a.json",
    "results/autofill_state.bm-b.json",
    "results/saturation_engine/state_bm-a.json",
    "results/saturation_engine/state_bm-b.json",
]
for rel in JSON_FACES:
    ap = os.path.join(RB, rel.replace("/", os.sep))
    json.loads(open(ap, "rb").read().decode("utf-8"))
print("JSON-REPARSE %d/%d PASS" % (len(JSON_FACES), len(JSON_FACES)))
for rel in ("results/fund_value_p1/nulls.jsonl", "results/fund_quality_p1/nulls.jsonl", "results/fund_divlowvol_p1/nulls.jsonl"):
    ap = os.path.join(RB, rel.replace("/", os.sep))
    n = 0
    for ln in open(ap, "rb").read().splitlines():
        if ln.strip():
            json.loads(ln.decode("utf-8"))
            n += 1
    print("JSONL-REPARSE %s lines=%d PASS" % (rel, n))
pool_raw = open(os.path.join(RB, "results", "runnable_pool.json"), "rb").read()
assert b"bm-b" in pool_raw, "pool lost bm-b owner visibility"
print("ALL-CHECKS-PASS")
