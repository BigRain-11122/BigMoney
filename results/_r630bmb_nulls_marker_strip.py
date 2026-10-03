# r630 bm-b: strip rebase conflict markers from fund_value_p1/nulls.jsonl
# Keeps ours-block + all post->>>>>>> appended rows (burn may append while we work).
# Dedupes by row key (theirs-block duplicates dropped; theirs subset of ours per determinism).
# Atomic tmp+os.replace with retry (burn opens append per batch; window is ms-scale).
import json, os, sys, time

PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                    "fund_value_p1", "nulls.jsonl")

def read_retry(p, n=8):
    for _ in range(n):
        try:
            with open(p, encoding="utf-8") as fh:
                return fh.read().splitlines()
        except PermissionError:
            time.sleep(0.25)
    return None

lines = read_retry(PATH)
if lines is None:
    sys.exit("READ FAIL")
try:
    i_start = next(i for i, l in enumerate(lines) if l.startswith("<<<<<<<"))
    i_mid = next(i for i, l in enumerate(lines) if l == "=======" and i > i_start)
    i_end = next(i for i, l in enumerate(lines) if l.startswith(">>>>>>>") and i > i_mid)
except StopIteration:
    print("NO-MARKERS rows=%d (already clean)" % len(lines))
    sys.exit(0)

ours = lines[:i_start] + lines[i_start + 1:i_mid]
post = lines[i_end + 1:]
theirs_count = i_end - i_mid - 1
result = ours + post

seen, out = set(), []
for ln in result:
    if not ln.strip():
        continue
    k = json.loads(ln)["key"]          # raises on any bad line -> abort, no write
    if k in seen:
        continue
    seen.add(k)
    out.append(ln)

tmp = PATH + ".strip.tmp"
with open(tmp, "w", encoding="utf-8", newline="\n") as fh:
    fh.write("\n".join(out) + "\n")
for _ in range(10):
    try:
        os.replace(tmp, PATH)
        break
    except PermissionError:
        time.sleep(0.25)
else:
    os.unlink(tmp)
    sys.exit("REPLACE FAIL (locked)")
# verify post-write parse (same semantics as runner _done_keys)
with open(PATH, encoding="utf-8") as fh:
    n = 0
    for ln in fh.read().splitlines():
        if ln.strip():
            json.loads(ln)
            n += 1
print("OK rows=%d dropped_theirs=%d kept_post=%d max_k_line_len=%d"
      % (n, theirs_count, len(post), max(len(l) for l in out)))
