# r689 S0 merge resolve: pool_core_samples.jsonl tail-append union (r688 bma precedent)
# r657-2: take both sides via git show HEAD:/MERGE_HEAD: (add-invariant, stage2/3 not used)
# r656: line-level canon multiset containment zero-loss proof (split by \n, not \r\n)
# r675: block-union recipe = theirs full text (order preserved) + our true-new lines appended
import subprocess, json, collections, sys

PATH = "results/pool_core_samples.jsonl"

def git_bytes(rev):
    r = subprocess.run(["git", "show", f"{rev}:{PATH}"], capture_output=True)
    if r.returncode != 0:
        print("FATAL git show", rev, r.stderr.decode("utf-8", "replace"))
        sys.exit(2)
    return r.stdout

ours = git_bytes("HEAD")       # bm-b absorb (daemon tail)
theirs = git_bytes("MERGE_HEAD")  # origin/main via r688 bm-a union

def canon_lines(b):
    # canon = content stripped of trailing CR; keep order
    return [ln.rstrip(b"\r") for ln in b.split(b"\n") if ln.strip()]

o_lines, t_lines = canon_lines(ours), canon_lines(theirs)
o_ms, t_ms = collections.Counter(o_lines), collections.Counter(t_lines)

# true-new = lines ours has beyond theirs count (multiset difference)
ours_new = o_ms - t_ms
theirs_new = t_ms - o_ms
print("ours_lines", len(o_lines), "theirs_lines", len(t_lines))
print("ours_true_new", sum(ours_new.values()), "theirs_true_new", sum(theirs_new.values()))

# sanity: print ts of true-new lines (truncated)
for ln in list(ours_new.elements())[:5]:
    print("OURS_NEW:", ln[:160].decode("utf-8", "replace"))
for ln in list(theirs_new.elements())[:5]:
    print("THEIRS_NEW:", ln[:160].decode("utf-8", "replace"))

# union product: theirs full order preserved + our true-new lines appended in our order
ours_new_seq = [ln for ln in o_lines if ln in ours_new and o_lines.index(ln) is not None]
# build our-new sequence preserving our file order (respecting multiset counts)
remaining = dict(ours_new)
ours_new_seq = []
seen = collections.Counter()
for ln in o_lines:
    if seen[ln] < o_ms[ln] and (o_ms[ln] - t_ms[ln]) > seen.get(ln, 0) and ln in ours_new:
        pass
# simpler correct method: walk ours, count occurrences; keep occurrence-index >= (count of that line in theirs up to same index) ... use multiset remainder queue
rem = collections.Counter(ours_new)
ours_new_seq = []
for ln in o_lines:
    if rem[ln] > 0:
        ours_new_seq.append(ln)
        rem[ln] -= 1

assert sum(ours_new.values()) == len(ours_new_seq), "our-new walk count mismatch"

body = theirs  # keep exact origin bytes as base (order + EOL as-is)
# append our true-new lines with LF terminator
tail = b"".join(ln + b"\n" for ln in ours_new_seq)
product = body.rstrip(b"\n") + b"\n" + tail if ours_new_seq else body
if not product.endswith(b"\n"):
    product += b"\n"

# zero-loss containment proof (line-level multiset)
p_ms = collections.Counter(canon_lines(product))
assert p_ms >= o_ms, "LOST ours lines"
assert p_ms >= t_ms, "LOST theirs lines"
print("containment PASS: product superset of both sides")
# no dup invention: product multiset == ours + theirs union without extra
assert not (p_ms - (o_ms + t_ms)), "INVENTED lines beyond both sides"
print("no-invention PASS")

with open(PATH, "wb") as f:
    f.write(product)
# re-read verify
with open(PATH, "rb") as f:
    rb = f.read()
assert collections.Counter(canon_lines(rb)) >= o_ms
assert collections.Counter(canon_lines(rb)) >= t_ms
print("write-back verify PASS; total_lines", len(canon_lines(rb)))
print("UNION_DONE")
