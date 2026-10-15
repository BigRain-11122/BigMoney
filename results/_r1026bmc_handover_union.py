# r1026 S0 rebase-conflict heal: research/HANDOVER.md line-level union
# ours (stage2 4c37fbd6b) = bm-b r965/r970/r975 rows; theirs (stage3 e3581d89b) = + bm-c r1025 row
# treasure_guard rc3 carve-out path: line-level union only
import subprocess, sys

def blob(sh):
    r = subprocess.run(['git', 'show', sh], capture_output=True)
    if r.returncode != 0:
        print("BLOB-FAIL", sh, r.stderr.decode('utf-8', 'replace')); sys.exit(2)
    return r.stdout

ours = blob('4c37fbd6b0a643f7b54568daca3fc66a5158359e')
theirs = blob('e3581d89ba4d6e63e1112c4b99ce454c355f5b23')

marker = b'> bm-c round 1025 '
tgt = [l for l in theirs.splitlines(keepends=True) if l.startswith(marker)]
assert len(tgt) == 1, "expected exactly 1 bm-c r1025 line, got %d" % len(tgt)
assert marker not in ours, "ours already contains bm-c r1025 row (double-union)"

if not ours.endswith(b'\n'):
    ours += b'\n'
merged = ours + tgt[0]

with open('research/HANDOVER.md', 'wb') as f:
    f.write(merged)

# verify read-back
back = open('research/HANDOVER.md', 'rb').read()
assert back == merged, "read-back mismatch"
assert b'round 975 bm-b' in back and marker in back, "union missing required rows"
print("UNION-OK bytes=%d added_line_bytes=%d" % (len(back), len(tgt[0])))
