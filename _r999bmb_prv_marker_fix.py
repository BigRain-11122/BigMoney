import sys

p = r'results\post_review.jsonl'
data = open(p, 'rb').read()
lines = data.split(b'\n')
assert lines[11895].startswith(b'|||||||'), ('marker not at 11896', lines[11895][:60])
del lines[11895]
bad = [(i + 1, l[:40]) for i, l in enumerate(lines) if l and not l.startswith(b'{')]
out = b'\n'.join(lines)
open(p, 'wb').write(out)
print('marker_removed total_lines', len(lines), 'non_json_lines', bad[:5], 'count', len(bad))

d2 = open(r'_r999_uu.txt', 'rb').read()
print('uu_txt_has_diff3_markers', any(m in d2 for m in (b'<<<<<<<', b'=======', b'>>>>>>>', b'|||||||')))
