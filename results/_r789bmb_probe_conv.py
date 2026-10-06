# r789 bm-b probe: byte conventions for D-06 migration (r783 receipt sha16 convention + line endings)
import hashlib

def read_b(p):
    with open(p, 'rb') as f:
        return f.read()

# 1) line-ending census
for p in ('CODELY.md', 'research/pit-git-resolver.md', 'research/pit-protocol-lane.md', 'knowledge/TREASURE_REGISTRY.md'):
    b = read_b(p)
    crlf = b.count(b'\r\n'); lf = b.count(b'\n') - crlf
    print(f"{p}: bytes={len(b)} crlf={crlf} lf_only={lf} endswith_lf={b.endswith(bytes([10]))}")

# 2) r782 entry in pit-git-resolver.md -> sha16 convention check vs r783 receipt (1129B, 3e36394b1b44e2ae)
res = read_b('research/pit-git-git-resolver.md') if False else read_b('research/pit-git-resolver.md')
i = res.find(b'- [2026-10-06 21:3x r782 bm-b]')
print("r782 entry find@", i)
j = res.find(b'\n', i)
line_no_term = res[i:j]
line_crlf = res[i:j] if res[j-1:j] == b'\r' else line_no_term  # handle
print("line bytes (no term):", len(line_no_term))
for cand, tag in ((line_no_term, 'no-term'), (line_no_term + b'\n', '+LF'), (line_no_term + b'\r\n', '+CRLF')):
    h = hashlib.sha256(cand).hexdigest()[:16]
    print(f"  sha16[{tag}] = {h}")
print("expect 3e36394b1b44e2ae (1129B)")
