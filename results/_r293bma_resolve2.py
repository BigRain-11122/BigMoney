# _r293bma_resolve2.py -- R293 closure rebase UU x3 resolver (CODELY.md / memory-archive / autofill_state)
# Recipes: memory-union deletion-superset (take-upstream root) + archive ledger union byte-dedup
#          + mixed-dict+ledger (launches union ASC cap50, last_tick take-new-by-ts, LF/no-trailing-newline mirror)
# Law anchors: r208 memory-union, r188 union zero-loss, r203/r245 autofill recipe, r140 tie, r289 full-prefix assert,
#               R293-E1 write-first-assert-after, r291 post-rebase pool done-flip semantic re-verify (printed here for the caller).
import json, subprocess, sys

def stage_blob(stage, path):
    r = subprocess.run(["git", "show", ":%d:%s" % (stage, path)], capture_output=True)
    if r.returncode != 0:
        sys.exit("stage read fail %s %d: %s" % (path, stage, r.stderr[:200]))
    return r.stdout.decode("utf-8")

P_CODELY = "CODELY.md"
P_ARCH = "research/memory-archive/202609.md"
P_AF = "results/autofill_state.json"

log = []

# ---------- 1) autofill_state.json : mixed-dict+ledger ----------
af_base = stage_blob(1, P_AF)
af_ours = stage_blob(2, P_AF)    # upstream (rebase-onto, bm-b face)
af_theirs = stage_blob(3, P_AF)   # my salvage commit (bm-a face)
o = json.loads(af_ours); t = json.loads(af_theirs)
# side identification by content signature (do NOT trust stage numbers blindly - r293 double-colon lesson)
# r140: strictly-newer takes it; same-second tie -> HEAD side (= upstream/ours in a rebase, r292 precedent)
t_ts, o_ts = t.get("last_tick", {}).get("ts", ""), o.get("last_tick", {}).get("ts", "")
mine = t if t_ts > o_ts else o
other = t if mine is o else o
log.append("af sides: last_tick pick=%s machine=%s (tie->HEAD/upstream per r140+r292; other=%s)" % (mine["last_tick"]["ts"], mine["last_tick"].get("machine"), other["last_tick"]["ts"]))

seen = {}
launches = []
for rec in o.get("launches", []) + t.get("launches", []):
    key = json.dumps(rec, sort_keys=True, ensure_ascii=False)
    if key not in seen:
        seen[key] = 1
        launches.append(rec)
launches.sort(key=lambda r: r.get("ts", ""))
before = len(launches)
if len(launches) > 50:
    dropped = launches[:len(launches)-50]
    launches = launches[-50:]
    log.append("af cap50: dropped %d oldest (first dropped ts=%s)" % (len(dropped), dropped[0].get("ts")))
merged = {k: v for k, v in o.items() if k not in ("launches", "last_tick")}
# merge non-recipe keys: prefer upstream face for unknown keys (snapshot semantics), mine for known
for k in t:
    if k not in ("launches", "last_tick") and k not in merged:
        merged[k] = t[k]
merged["launches"] = launches
merged["last_tick"] = mine["last_tick"]  # whole-dict assign (r140: no str()-compare, whole dict)
af_out = json.dumps(merged, indent=1, ensure_ascii=False)
if not af_base.endswith("\n"):
    af_out = af_out.rstrip("\n")  # mirror base: no trailing newline
if "\r\n" in af_base:
    af_out = af_out.replace("\n", "\r\n")
open(P_AF, "w", encoding="utf-8", newline="").write(af_out)

# ---------- 2) CODELY.md : memory-union deletion-superset -> take upstream face ----------
c_base = stage_blob(1, P_CODELY)
c_ours = stage_blob(2, P_CODELY)     # bm-b batch-2 reorg (12 entries out, superset)
c_theirs = stage_blob(3, P_CODELY)    # R293 rebin (11 entries out)
open(P_CODELY, "w", encoding="utf-8", newline="").write(c_ours)
log.append("codely: take-upstream face bytes=%d (theirs-side bytes=%d, base bytes=%d)" % (len(c_ours.encode()), len(c_theirs.encode()), len(c_base.encode())))

# ---------- 3) memory-archive/202609.md : ledger union byte-dedup ----------
a_base = stage_blob(1, P_ARCH)
a_ours = stage_blob(2, P_ARCH)     # bm-b batch-2 section (12 entries incl r290)
a_theirs = stage_blob(3, P_ARCH)    # R293 section (11 dup + 1 unique resolver-E1)
assert a_ours.startswith(a_base), "r289 full-prefix assert FAIL on ours"
assert a_theirs.startswith(a_base), "r289 full-prefix assert FAIL on theirs"
base_lines = a_base.splitlines()
ours_tail = a_ours[len(a_base):]
theirs_tail = a_theirs[len(a_base):]
ours_set = set(l for l in ours_tail.splitlines() if l.strip())
uniq = []
for l in theirs_tail.splitlines():
    if not l.strip():
        continue
    if l in ours_set:
        continue
    if l.startswith("## ") and l in a_theirs:  # section header of R293 window (not in ours)
        uniq.append(l)
        uniq.append("（去重注 2026-09-27 R293-closure：本窗 11 条与 r296 二批节字节同文已并入该节·行级零丢失；本节独有=下 1 条）")
        continue
    if uniq and uniq[-1].endswith("本节独有=下 1 条）"):
        uniq.append(l)
    elif not uniq:
        uniq.append(l)
a_out = a_base
if not a_out.endswith("\n"):
    a_out += "\n"
a_out += ours_tail
if not a_out.endswith("\n"):
    a_out += "\n"
if uniq:
    a_out += "\n" + "\n".join(uniq) + "\n"
open(P_ARCH, "w", encoding="utf-8", newline="").write(a_out)
log.append("archive: ours_tail +%d chars, theirs-unique kept=%d non-blank lines" % (len(ours_tail), len([l for l in uniq if l.strip() and not l.startswith("## ") and "去重注" not in l])))

# ---------- asserts (post-write; E1 law: write-first, assert-after) ----------
fails = []
# af asserts
af_now = json.load(open(P_AF, encoding="utf-8"))
if not isinstance(af_now.get("last_tick"), dict):
    fails.append("af last_tick not dict")
if af_now["last_tick"]["ts"] != mine["last_tick"]["ts"]:
    fails.append("af last_tick ts drift")
n_overlap = len([1 for r in af_now["launches"] if r.get("entry") == "CN-KLINE-PATTERN-P1"])
if n_overlap < 1:
    fails.append("af CN-KLINE launch record lost")
if len(af_now["launches"]) > 50:
    fails.append("af launches cap exceeded")
# codely asserts: <=10KB hard line, no kenglu entry lines left beyond structural
c_bytes = len(open(P_CODELY, "rb").read())
if c_bytes > 10240:
    fails.append("CODELY %d > 10KB hard line" % c_bytes)
# archive zero-loss: every non-blank tail line from BOTH sides present in final
final_arch = open(P_ARCH, encoding="utf-8").read()
fset = set(final_arch.splitlines())
for l in ours_tail.splitlines():
    if l.strip() and l not in fset:
        fails.append("archive zero-loss FAIL (ours side): " + l[:60])
for l in theirs_tail.splitlines():
    if l.strip() and l not in fset:
        fails.append("archive zero-loss FAIL (theirs side): " + l[:60])
if "坑律归档二批 2026-09-27 r296" not in final_arch:
    fails.append("bm-b batch-2 header missing")
if "坑律热冷整编 2026-09-27 R293 窗" not in final_arch:
    fails.append("R293 window header missing")
# codely entry accounting: entries removed by either side must be in archive (already asserted via archive union) ;
# entries remaining in final root = structural only is NOT required (remote face owns content) - count dated kenglu lines left in root
root_left = [l for l in open(P_CODELY, encoding="utf-8").read().splitlines() if l.startswith("- [2026-09-27") and "坑律" in l]
if root_left:
    fails.append("CODELY still carries %d dated kenglu entries" % len(root_left))

for line in log:
    print(line)
print("ASSERTS:", "ALL PASS" if not fails else "FAIL x%d" % len(fails))
for f in fails:
    print("  FAIL:", f)
sys.exit(1 if fails else 0)
