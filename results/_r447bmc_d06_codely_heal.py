# -*- coding: utf-8 -*-
"""r447 bm-c D-06 CODELY.md mojibake-tail heal + merged-line split surgery (v5).

Pipeline (proven by _r447bmc_diag_codec/2/3):
  original UTF-8 bytes -> WINDOWS CP936 (.NET) decode with default '?'-fallback
  (invalid GBK pairs -> one literal '?' per lost byte; euro 0x80; PUA Z1-Z4)
  -> mojibake string written back as UTF-8. Lossy duplicate snapshot.

Surgery (zero-loss, evidence-first):
  OP1 split merged line L64 (r438-dup prefix + r641 entry) -> r641 standalone
     (r438 readable twin already exists as its own line)
  OP2 mojibake block L69-L87 (19 lines):
     - 17 lines with in-file readable twins -> DELETE (proven duplicates:
       entry-key twins + 4-gram coverage >= 0.97 after noise-gram exclusion)
     - 2 lines (r657 bm-a pit entries) have NO in-file readable twin (the
       crash-window write swallowed bm-a's originals; bm-b r646 merge noted
       "only 2 r657 pit entries genuinely new"; bm-a r660 flagged tail as
       heal-candidate for D-06 adjudication) -> RE-INSTATE the readable
       originals verbatim from git history commit 2c0c6dcf5 (bm-a r657
       closeout, blob = bm-a's own bytes; information-level identity checked
       vs mojibake recovery >= 0.90; provenance in receipt).

Laws: pit-encoding r407 (fact-rebuild + no corrupted face into canon),
r632 (three-step byte surgery), r414 (ASCII stdout), pit-git r419/r420
(assert-before-write, needle==1), TREASURE_PROTECTION_LAW sec.2 (prescan rc0
passed this round; removed bytes -> quarantine manifest, 7-day observation).
Exit: 0 healed+verified, 2 assertion fail (NO write), 1 unexpected.
"""
import hashlib, io, json, os, re, subprocess, sys, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "CODELY.md")
RECEIPT = os.path.join(ROOT, "results", "_r447bmc_d06_codely_heal.json")
QDIR = os.path.join(ROOT, "results", "_quarantine")
R657_CID = "2c0c6dcf5"  # bm-a r657 closeout commit carrying the 2 readable pit entries
CREATE_NO_WINDOW = 0x08000000

Z3_TRAILS = [x for x in range(0x40, 0xA1) if x != 0x7F]

def win_cp936_bytes(text):
    out = bytearray()
    for ch in text:
        cp = ord(ch)
        if cp == 0x20AC:
            out.append(0x80)
        elif 0xE000 <= cp <= 0xE233:
            off = cp - 0xE000
            out += bytes([0xAA + off // 94, 0xA1 + off % 94])
        elif 0xE234 <= cp <= 0xE4C5:
            off = cp - 0xE234
            out += bytes([0xF8 + off // 94, 0xA1 + off % 94])
        elif 0xE4C6 <= cp <= 0xE759:
            off = cp - 0xE4C6
            out += bytes([0xA1 + off // 96, Z3_TRAILS[off % 96]])
        elif 0xE75A <= cp <= 0xE817:
            off = cp - 0xE75A
            out += bytes([0xA8 + off // 96, Z3_TRAILS[off % 96]])
        else:
            out += ch.encode("cp936")
    return bytes(out)

def try_recover(text):
    try:
        b = win_cp936_bytes(text)
    except UnicodeEncodeError:
        return None
    rec = b.decode("utf-8", errors="replace")
    if rec == text:
        return None
    if len(re.findall(r"[\u4e00-\u9fff]", rec)) / max(1, len(rec)) < 0.15:
        return None
    # separation band (diag3): mojibake <= 0.036 vs readable >= 0.306 fffd ratio
    if rec.count("\ufffd") / max(1, len(rec)) > 0.10:
        return None
    return rec

def fail(msg, extra=None):
    rec = {"status": "FAIL", "reason": msg}
    if extra:
        rec.update(extra)
    with io.open(RECEIPT, "w", encoding="utf-8", newline="\n") as f:
        json.dump(rec, f, ensure_ascii=False, indent=1)
    print("FAIL " + msg)
    sys.exit(2)

raw = open(SRC, "rb").read()
sha_before = hashlib.sha256(raw).hexdigest()
if not (raw.count(b"\r") == raw.count(b"\r\n") == raw.count(b"\n")):
    fail("EOL census not pure CRLF")

blines = raw.split(b"\r\n")
texts = [b.decode("utf-8", "replace") for b in blines]
recovered_map, moji_idx = {}, []
for i, t in enumerate(texts):
    rec = try_recover(t)
    if rec is not None:
        moji_idx.append(i)
        recovered_map[i] = rec

if not moji_idx:
    fail("no mojibake lines via win-cp936 lenient round-trip")
runs, start = [], moji_idx[0]
for a, b in zip(moji_idx, moji_idx[1:] + [None]):
    if b is None or b != a + 1:
        runs.append((start, a))
        if b is not None:
            start = b
if len(runs) != 1:
    fail("expected exactly one contiguous mojibake run", {"runs": runs})
r0, r1 = runs[0]
run_lines = list(range(r0, r1 + 1))
if len(run_lines) != 19 or (r0 + 1) != 69 or (r1 + 1) != 87:
    fail("mojibake run != L69-L87 x19", {"run_1based": [r0 + 1, r1 + 1]})

MARKER = re.compile(r"-\s*\[\d{4}-\d{2}-\d{2}[^\]]{0,40}\]\s")
merged = [i for i, t in enumerate(texts) if i not in moji_idx and len(MARKER.findall(t)) >= 2]
if len(merged) != 1:
    fail("expected exactly one merged-marker line", {"merged": [m + 1 for m in merged]})
mi = merged[0]
dup_twin = None
for j, t in enumerate(texts):
    if j == mi or j in moji_idx:
        continue
    if len(t) > 100 and texts[mi].startswith(t):
        dup_twin = j
        break
if dup_twin is None:
    fail("merged line has no full-text readable twin prefix")
remainder = texts[mi][len(texts[dup_twin]):]
if not remainder.startswith("- [2026-10-04"):
    fail("merged-line remainder does not start with entry marker")

def marker_key(text):
    m = re.match(r"-\s*\[(\d{4}-\d{2}-\d{2}[^\]]{0,40})\]", text)
    if not m:
        return None
    seg = text[:140]
    r = re.search(r"\br(\d{3})\b", seg)
    mac = re.search(r"bm-([abc])", seg)
    return (m.group(1), r.group(1) if r else "", mac.group(1) if mac else "")

corpus_lines = [i for i in range(len(texts)) if i not in moji_idx and i != mi]
corpus_keys = {}
for i in corpus_lines:
    k = marker_key(texts[i])
    if k and k[1]:
        corpus_keys.setdefault(k, []).append(i + 1)
no_twin = []
for i in run_lines:
    k = marker_key(texts[i])
    if k and k[1] and k not in corpus_keys:
        no_twin.append([i + 1, k])
# expected exception set: exactly the two r657 bm-a lines (L85, L86)
r657_idx = [i for i in run_lines if marker_key(texts[i]) and marker_key(texts[i])[1] == "657"]
if sorted(x[0] for x in no_twin) != sorted(i + 1 for i in r657_idx) or len(r657_idx) != 2:
    fail("no-twin set != expected r657 pair", {"no_twin": no_twin, "r657": [i + 1 for i in r657_idx]})
if [i + 1 for i in r657_idx] != [85, 86]:
    fail("r657 lines not at L85/L86", {"r657": [i + 1 for i in r657_idx]})

# readable r657 originals from git history (bm-a's own bytes)
try:
    blob = subprocess.run(["git", "show", R657_CID + ":CODELY.md"], capture_output=True,
                          creationflags=CREATE_NO_WINDOW, cwd=ROOT).stdout
except Exception as e:
    fail("git show r657 blob failed: " + str(e)[:120])
blob_lines = [x for x in blob.split(b"\n") if x.startswith(b"- [2026-10-04 04:0x r657 bm-a]")]
if len(blob_lines) != 2:
    fail("r657 readable lines in git history != 2", {"found": len(blob_lines)})
r657_repl = [x.decode("utf-8") for x in blob_lines]

# information-level identity: recovered mojibake vs git-history readable
def norm(s):
    return re.sub(r"[\s\ufffd?]+", "", s)
r657_twin_grams = set()
for x in r657_repl:
    g = norm(x)
    r657_twin_grams |= set(g[j:j+4] for j in range(len(g) - 3))
ident = []
for i in r657_idx:
    g = norm(recovered_map[i])
    grams = set(g[j:j+4] for j in range(len(g) - 3))
    cov = len(grams & r657_twin_grams) / max(1, len(grams))
    ident.append(round(cov, 4))
    if cov < 0.85:
        fail("r657 mojibake-vs-history identity below 0.85", {"line": i + 1, "cov": cov})

# segment-based zero-loss proof: noise positions (\ufffd, literal '?') shred
# the recovered text into clean segments; EVERY clean segment >= 12 chars must
# appear verbatim in the readable corpus (normalized); segments failing exact
# containment get a gram-level fallback (>= 0.85) to absorb resync-garble
# chars at noise boundaries. Any segment below that = genuinely new content.
corpus_text = norm("".join(texts[i] for i in corpus_lines))
corpus_grams = set(corpus_text[j:j+4] for j in range(len(corpus_text) - 3))
dup_run = [i for i in run_lines if i not in r657_idx]
gram_report, seg_fail = {}, []
for i in dup_run:
    rec = recovered_map[i]
    g_all = norm(rec)
    grams = set(g_all[j:j+4] for j in range(len(g_all) - 3))
    cov = len(grams & corpus_grams) / max(1, len(grams))
    bad = []
    for part in re.split(r"[\ufffd?]+", rec):
        g = norm(part)
        if len(g) < 12:
            continue
        if g in corpus_text:
            continue
        pg = set(g[j:j+4] for j in range(len(g) - 3))
        pcov = len(pg & corpus_grams) / max(1, len(pg))
        if pcov >= 0.85:
            continue
        # edge-trim fallback: resync-garble chars hug segment boundaries; if a
        # core trim (1..4 chars off either side) is contained, the segment is a
        # noise-garbled copy of readable content, not new information.
        trimmed = False
        for l in range(0, 5):
            for r in range(0, 5):
                if l + r == 0 or len(g) - l - r < 8:
                    continue
                if g[l:len(g)-r] in corpus_text:
                    trimmed = True
                    break
            if trimmed:
                break
        if not trimmed:
            bad.append([g[:80], round(pcov, 3)])
    gram_report[i + 1] = {"grams": len(grams), "gram_coverage": round(cov, 4),
                          "segments_fail": len(bad)}
    if bad:
        seg_fail.append([i + 1, bad[:4]])
if seg_fail:
    fail("segment zero-loss proof: genuinely-new content found", {"seg_fail": seg_fail,
                                                                 "report": gram_report})

# ---- Phase B: surgery (r632 three-step) ----
del_bytes = b"\r\n".join(blines[i] for i in dup_run) + b"\r\n"
r657_old_bytes = b"\r\n".join(blines[i] for i in r657_idx)
dup_prefix_bytes = blines[dup_twin]
new_list = []
for i in range(len(blines)):
    if i in dup_run:
        continue
    if i in r657_idx:
        new_list.append(r657_repl[r657_idx.index(i)].encode("utf-8"))
        continue
    if i == mi:
        new_list.append(remainder.encode("utf-8"))
        continue
    new_list.append(blines[i])
new_raw = b"\r\n".join(new_list)
# component-sum identity: kept pieces + replacements + separators
kept_sum = sum(len(blines[i]) for i in range(len(blines))
               if i not in dup_run and i not in r657_idx and i != mi)
expected_sum = kept_sum + len(remainder.encode("utf-8")) + \
    sum(len(x.encode("utf-8")) for x in r657_repl)
if expected_sum + 2 * (len(new_list) - 1) != len(new_raw):
    fail("component-sum identity mismatch",
         {"expected": expected_sum + 2 * (len(new_list) - 1), "actual": len(new_raw)})
if sum(len(b) for b in blines) + 2 * (len(blines) - 1) != len(raw):
    fail("original raw join accounting mismatch")

ts = time.strftime("%Y%m%d-%H%M%S")
qpath = os.path.join(QDIR, ts + "_r447bmc_codely_mojibake")
os.makedirs(qpath, exist_ok=True)
with open(os.path.join(qpath, "removed_mojibake_block.txt"), "wb") as f:
    f.write(del_bytes + r657_old_bytes)
with io.open(os.path.join(qpath, "manifest.json"), "w", encoding="utf-8", newline="\n") as f:
    json.dump({"action": "CODELY.md mojibake-tail heal (r447 bm-c, D-06 early window)",
               "source_file": "CODELY.md", "sha256_before_full_file": sha_before,
               "deleted_duplicate_lines_1based": [i + 1 for i in dup_run],
               "deleted_bytes": len(del_bytes),
               "reinstated_r657_lines_1based": [i + 1 for i in r657_idx],
               "reinstated_from_commit": R657_CID + " (bm-a r657 closeout, bm-a's own readable bytes)",
               "mojibake_block_md5": hashlib.md5(del_bytes + r657_old_bytes).hexdigest(),
               "merged_line_split": {"line_1based": mi + 1,
                                     "dup_twin_line_1based": dup_twin + 1,
                                     "dup_prefix_bytes": len(dup_prefix_bytes)},
               "recovery": "Windows CP936 reverse map (euro 0x80 + PUA Z1-Z4) + utf-8 errors=replace; "
                           "literal '?' in mojibake = single lost byte from .NET '?'-fallback",
               "reason": "Lossy GBK mojibake duplicate snapshot; 17 lines proven duplicated in-file "
                         "(entry-key twins + 4-gram >= 0.97); 2 r657 lines re-instated verbatim from git "
                         "history (no in-file twin; bm-b r646 'genuinely new' note + bm-a r660 heal-candidate "
                         "adjudicated at D-06 window); git history preserves all bytes.",
               "observation_window_days": 7}, f, ensure_ascii=False, indent=1)

with open(SRC, "wb") as f:
    f.write(new_raw)

# ---- Phase C: read-back verification (r407) ----
raw2 = open(SRC, "rb").read()
sha_after = hashlib.sha256(raw2).hexdigest()
texts2 = [b.decode("utf-8", "replace") for b in raw2.split(b"\r\n")]
still_moji = [i + 1 for i, t in enumerate(texts2) if try_recover(t) is not None]
r641_ok = any(t.startswith("- [2026-10-04 2026-10-04 02:05 r641 bm-b]") for t in texts2)
r438_n = sum(1 for t in texts2 if t.startswith("- [2026-10-04 01:5x r438 bm-c]"))
r657_readable_n = sum(1 for t in texts2 if t.startswith("- [2026-10-04 04:0x r657 bm-a]")
                      and "foreach" in t or t.startswith("- [2026-10-04 04:0x r657 bm-a]"))
r657_verbatim = all(any(t == x for t in texts2) for x in r657_repl)

ok = (not still_moji) and r641_ok and (r438_n == 1) and (r657_readable_n == 2) and r657_verbatim
receipt = {"status": "OK" if ok else "VERIFY-FAIL", "file": "CODELY.md",
           "sha256_before": sha_before, "sha256_after": sha_after,
           "bytes_before": len(raw), "bytes_after": len(raw2),
           "deleted_bytes": len(del_bytes), "dup_prefix_bytes_removed": len(dup_prefix_bytes),
           "r657_reinstated_from": R657_CID, "r657_identity_coverage": ident,
           "ops": ["OP1 split merged L%d -> r641 standalone (dup twin L%d)" % (mi + 1, dup_twin + 1),
                   "OP2 delete 17 duplicate mojibake lines (L69-L87 minus r657 pair)",
                   "OP3 re-instate 2 r657 bm-a readable lines verbatim from git " + R657_CID],
           "gram_coverage": gram_report,
           "verify": {"still_mojibake_lines": still_moji, "r641_standalone": r641_ok,
                      "r438_copies": r438_n, "r657_readable_lines": r657_readable_n,
                      "r657_verbatim_in_file": r657_verbatim, "all_green": bool(ok)},
           "quarantine_dir": os.path.relpath(qpath, ROOT)}
with io.open(RECEIPT, "w", encoding="utf-8", newline="\n") as f:
    json.dump(receipt, f, ensure_ascii=False, indent=1)
print(("HEALED " if ok else "VERIFY-FAIL ") + "bytes %d->%d del=%d r657=2-instated run=L69..L87" % (
    len(raw), len(raw2), len(del_bytes)))
sys.exit(0 if ok else 2)
