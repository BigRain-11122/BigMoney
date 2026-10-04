import difflib
PATH = r"results/runnable_pool.json"
raw = open(PATH, "rb").read()
eol = b"\r\n" if b"\r\n" in raw[:5000] else b"\n"
lines = raw.split(eol)
start = next(i for i, ln in enumerate(lines) if b'"key": "w3-screen-3of4"' in ln)
end = next(j for j in range(start + 1, len(lines)) if lines[j].strip() == b"}")
window = lines[start:end + 1]
window = [ln.replace(b'"status": "ready"', b'"status": "done"') if b'"status"' in ln else ln for ln in window]
oi = next(k for k, ln in enumerate(window) if b'"owner_since"' in ln)
indent = window[oi][: len(window[oi]) - len(window[oi].lstrip())]
window[oi] = window[oi].rstrip() + b","
window[oi + 1:oi + 1] = [
    indent + b'"claimed_since": "2026-10-04 15:53:07",',
    indent + b'"done_at": "X",',
    indent + b'"harvested_by": "bm-a",',
    indent + b'"harvest_claim": "w3-screen-3of4.bm-a.json"',
]
lines[start:end + 1] = window
out = eol.join(lines)
for l in difflib.unified_diff(raw.decode("utf-8").splitlines(),
                              out.decode("utf-8").splitlines(), lineterm="", n=0):
    print(l)
