# -*- coding: utf-8 -*-
"""r402 bm-c mechanical surgery (three faces, assert-all-before-write):

1. T-147 done-flip: status claimed->done + result_ref + r402 progress note
   (json.loads verify; format-fingerprint round-trip guard).
2. r393 pool-domain pit sweep: CODELY.md hot layer -> research/pit-pool.md
   tail append (verbatim bytes, r401 missed-entry backfill), with
   accounting line in pit-pool header + CODELY pool-pointer r402 note.
3. New r402 pit entry append to CODELY hot layer (landed-instrument
   readout must self-certify completion state).

All edits computed in memory; every assert must pass before ANY write
(zero-partial-write law). Byte-level ops only (no transcoding).
"""
import hashlib
import json
import os
import sys

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
CODELY = os.path.join(ROOT, "CODELY.md")
PITPOOL = os.path.join(ROOT, "research", "pit-pool.md")
T147 = os.path.join(ROOT, "fleet", "tasks", "T-2026-10-02-147-P1.json")


def die(msg):
    print(f"SURGERY ABORT: {msg}")
    sys.exit(1)


def md5(b):
    return hashlib.md5(b).hexdigest()


def load(p):
    with open(p, "rb") as fh:
        return fh.read()


def save(p, data):
    tmp = p + ".tmp_r402"
    with open(tmp, "wb") as fh:
        fh.write(data)
    os.replace(tmp, p)


def line_bounds(raw, idx):
    """Full line bounds (excluding terminator) + terminator bytes."""
    start = raw.rfind(b"\n", 0, idx) + 1
    end = raw.find(b"\n", idx)
    if end < 0:
        return start, len(raw), b""
    term = b"\r\n" if raw[end - 1:end] == b"\r" else b"\n"
    return start, end, term


# ---------------- phase 1: T-147 done-flip ----------------
orig_t = load(T147)
try:
    j = json.loads(orig_t.decode("utf-8"))
except Exception as ex:
    die(f"T-147 json parse: {ex}")
if j.get("status") != "claimed":
    die(f"T-147 status unexpected: {j.get('status')!r}")
if j.get("id") != "T-2026-10-02-147":
    die("T-147 id mismatch")

RESULT_REF = ("results/lowamp_p3/lowamp_p3_results.json + "
              "results/lowamp_p3/e1_three_leg.json (judged-negative verdict; "
              "face complete r398: s1 extract r386 + frozen prereg "
              "LOWAMP-DEEP-P1 + burn 10/10 bm-b data-locality + finalize+E1 "
              "r397 exec/r398 delivery bm-c; CLOSED_FAMILIES #8 "
              "lowamp_deep_xs dual-registered)")
j["status"] = "done"
j["result_ref"] = RESULT_REF
j["progress_r402_bmc"] = ("r402: bookkeeping done-flip only (face complete "
                          "since r398 delivery; zero new work) -- "
                          "verdict=judged-negative, no WATCHLIST flip, "
                          "born-main-exam satisfied by full judgment per "
                          "O-2115")

cand = (json.dumps(j, ensure_ascii=False, indent=1) + "\n").encode("utf-8")
# format-fingerprint: round-trip of the ORIGINAL must be byte-stable,
# else fall back to text surgery (refuse silent reformat)
rt = (json.dumps(json.loads(orig_t.decode("utf-8")), ensure_ascii=False,
                 indent=1) + "\n").encode("utf-8")
if rt == orig_t:
    new_t = cand
    print(f"T-147: dict path, new size {len(orig_t)}->{len(new_t)}B")
else:
    # text surgery fallback (mixed CRLF/LF file -- dict path would
    # reformat 30 CRLF lines): status line + result_ref after
    # claimed_at (matching that line's own terminator) + progress note
    # before the closing brace
    txt = orig_t.decode("utf-8")
    if txt.count('"status": "claimed"') != 1:
        die("T-147 status string not unique")
    txt = txt.replace('"status": "claimed"', '"status": "done"')
    anchor = '"claimed_at": "2026-10-02T22:00:00+08:00",'
    if txt.count(anchor) != 1:
        die("T-147 claimed_at anchor not unique")
    ai = txt.find(anchor) + len(anchor)
    term = "\r\n" if txt[ai:ai + 2] == "\r\n" else "\n"
    txt = (txt[:ai] + term + ' "result_ref": '
           + json.dumps(RESULT_REF, ensure_ascii=False) + "," + txt[ai:])
    prog_note = ('"progress_r402_bmc": ' + json.dumps(
        "r402: bookkeeping done-flip only (face complete since r398 "
        "delivery; zero new work) -- verdict=judged-negative, no "
        "WATCHLIST flip, born-main-exam satisfied by full judgment per "
        "O-2115", ensure_ascii=False))
    if txt.count("\n}") != 1:
        die("T-147 closing-brace anchor not unique")
    txt = txt.replace("\n}", ",\n " + prog_note + "\n}")
    new_t = txt.encode("utf-8")
    try:
        json.loads(new_t.decode("utf-8"))
    except Exception as ex:
        die(f"T-147 fallback json verify: {ex}")
    print(f"T-147: text path, new size {len(orig_t)}->{len(new_t)}B")
# final verify both paths
jj = json.loads(new_t.decode("utf-8"))
assert jj["status"] == "done" and jj.get("result_ref") and \
    jj.get("progress_r402_bmc"), "T-147 verify failed"

# ---------------- phase 2: r393 pit sweep ----------------
codely = load(CODELY)
pitpool = load(PITPOOL)

ANCH = b"[2026-10-03 02:34:29 r393 bm-c]"
hits = []
i = codely.find(ANCH)
while i >= 0:
    hits.append(i)
    i = codely.find(ANCH, i + 1)
if len(hits) != 1:
    die(f"CODELY r393 anchor hits={len(hits)} (expect 1)")
s, e, term = line_bounds(codely, hits[0])
if codely[s:s + 2] != b"- ":
    die("r393 entry not in dash form")
entry_full = codely[s:e + len(term)]
entry_no_term = codely[s:e]
if entry_no_term in pitpool:
    die("r393 entry already in pit-pool (idempotence guard)")
# preceding/following blank-line layout
prev_start = codely.rfind(b"\n", 0, s - 1) + 1
prev_line = codely[prev_start:s - 1]
next_start = e + len(term)
ne = codely.find(b"\n", next_start)
next_line = codely[next_start:ne if ne >= 0 else len(codely)]
remove_span = entry_full
removed_blanks = 0
if prev_line == b"" and next_line == b"":
    # double-blank after removal -> also take one blank line
    bs = codely.rfind(b"\n", 0, prev_start - 1) + 1
    remove_start = bs
    remove_span = codely[bs:e + len(term)]
    removed_blanks = 1
else:
    remove_start = s
print(f"r393 entry: {len(entry_no_term)}B md5={md5(entry_no_term)} "
      f"term={term!r} prev_blank={prev_line == b''} "
      f"next_blank={next_line == b''}")

# pit-pool tail append (recent-batch style: blank line + entry)
if not pitpool.endswith(b"\n"):
    pitpool += b"\n"
appendix = b"\n" + entry_no_term + b"\n"
# accounting line inserted after the r401 accounting header line
acc_anchor = "\uff08r401 bm-c\u00b7T-2026-10-02-144(c)\uff09".encode("utf-8")
ah = pitpool.find(acc_anchor)
if ah < 0:
    die("pit-pool r401 accounting line anchor missing")
as_, ae, aterm = line_bounds(pitpool, ah)
entry_lf = entry_no_term.replace(b"\r\n", b"\n")
acc_line = ("> \u589e\u91cf\u56de\u626b\u884c\uff08r402 bm-c\u00b7"
            "T-2026-10-02-144(c)\uff09\uff1a\u70ed\u5c42\u6c60\u57df\u6761"
            "\u76ee 1 \u6761 verbatim \u8ffd\u52a0\uff0810-03 02:34:29 "
            "r393 \u6279\u00b7r401 \u6f0f\u626b\u8865\u5f55\uff09\u00b7\u8ffd"
            "\u52a0\u6838 " + str(len(entry_lf)) + " B\uff08LF blob \u9762\u00b7"
            "md5=" + md5(entry_lf) +
            "\uff09\u00b7\u96f6\u4e22\u5931\u65ad\u8a00 PASS\uff08\u9010"
            "\u884c verbatim \u5728\u573a+\u6e90\u4ef6\u96f6\u6b8b\u7559\u00b7"
            "\u673a\u68b0\u8fc1\u79fb\u975e\u624b\u6284\u00b7r401 \u8303"
            "\u5f0f\u540c\u6e90\uff09\u3002").encode("utf-8")
new_pitpool = (pitpool[:ae + len(aterm)] + acc_line + aterm
               + pitpool[ae + len(aterm):])
new_pitpool += appendix
# accounting insertion shifts nothing we still need; verify entry present
assert entry_no_term in new_pitpool and acc_line in new_pitpool

# CODELY pool-pointer line r402 note (scoped to the pool pointer line only)
pp_anchor = b"research/pit-pool.md"
ph = codely.find(pp_anchor)
if ph < 0:
    die("CODELY pool pointer line missing")
ps, pe, pterm = line_bounds(codely, ph)
ptr_line = codely[ps:pe]
if b"r401" not in ptr_line:
    die("CODELY pool pointer line lacks r401 note (layout drift)")
tail_seg = "\u5df2\u5165\u4ef6\uff08\u4ef6\u5185\u5bf9\u8d26\u884c\u4e3a"
tail_seg += "\u51c6\uff09\u3002"
tail_b = tail_seg.encode("utf-8")
if ptr_line.count(tail_b) < 1:
    die("pool pointer line tail segment missing")
last_pos = ptr_line.rfind(tail_b)
new_ptr = (ptr_line[:last_pos]
           + ptr_line[last_pos:].replace(
               tail_b,
               ("\u5df2\u5165\u4ef6\uff08\u4ef6\u5185\u5bf9\u8d26\u884c"
                "\u4e3a\u51c6\uff09\uff1br402 bm-c \u589e\u91cf\u56de"
                "\u626b 1 \u6761\uff08r393 crash fuse \u673a\u961f\u70b9"
                "\u706b\u95e8\u00b7r401 \u6f0f\u626b\u8865\u5f55\uff09"
                "\u5df2\u5165\u4ef6\uff08\u4ef6\u5185\u5bf9\u8d26\u884c"
                "\u4e3a\u51c6\uff09\u3002").encode("utf-8"), 1))
print(f"pool pointer line: {len(ptr_line)}->{len(new_ptr)}B")

# remove r393 entry from CODELY (after pointer edit, coordinates are
# independent -- pointer edit is inside its own slice)
codely_mid = codely[:ps] + new_ptr + codely[pe:]
# re-locate r393 in the edited buffer (pointer edit may shift offsets)
h2 = codely_mid.find(ANCH)
if h2 < 0 or codely_mid.find(ANCH, h2 + 1) >= 0:
    die("r393 re-locate failed after pointer edit")
s2, e2, term2 = line_bounds(codely_mid, h2)
ent2 = codely_mid[s2:e2 + len(term2)]
if ent2.replace(b"\r\n", b"\n") != entry_full.replace(b"\r\n", b"\n"):
    die("r393 span drift after pointer edit")
# blank-collapse decision recomputed
prev2_start = codely_mid.rfind(b"\n", 0, s2 - 1) + 1
prev2 = codely_mid[prev2_start:s2 - 1]
n2s = e2 + len(term2)
n2e = codely_mid.find(b"\n", n2s)
next2 = codely_mid[n2s:n2e if n2e >= 0 else len(codely_mid)]
if prev2 == b"" and next2 == b"":
    rm_start = codely_mid.rfind(b"\n", 0, prev2_start - 1) + 1
    removed_blanks = 1
else:
    rm_start = s2
    removed_blanks = 0
codely_after = codely_mid[:rm_start] + codely_mid[e2 + len(term2):]
# verify removal: anchor gone, size delta == entry bytes (+ blank)
if ANCH in codely_after:
    die("r393 still present after removal")
expected_delta = len(entry_full) + (removed_blanks and
                                    (len(term2) * 1 + 0) or 0)
# (blank line removal = its own terminator only)
if len(codely_after) != len(codely_mid) - expected_delta:
    die(f"removal delta mismatch {len(codely_mid) - len(codely_after)}"
        f" vs {expected_delta}")

# ---------------- phase 3: new r402 pit entry append ----------------
NEW_PIT = (
    "- [2026-10-03 07:25 r402 bm-c] \u5df2\u843d\u5730\u4eea\u5668\u7684"
    "\u95e8\u8bfb\u51fa\u5fc5\u987b\u81ea\u8bc1\u5b8c\u6210\u6001\u5751"
    "\uff08dualrun flip \u95e8 r401 \u8bef\u8bfb\u5b9e\u5f39\u00b7\u96f6"
    "\u6267\u884c\u635f\u5931\u6838\u9a8c\u62e6\uff09\uff1apool_dualrun"
    "_reconcile status \u7684\u300cwave-1 flip gate: READY\u300d\u4e3a "
    "r203 flip \u843d\u5730\u524d\u8bbe\u8ba1\u7684\u95e8\u5224\u8bfb\u51fa"
    "\u2014\u2014flip \u5df2\u843d\u5730\uff08r203 commit 298c4796b\uff09"
    "+s4 \u5df2 CLOSED\uff08r204 option a\uff09\u540e\u8bfb\u51fa\u6052"
    "\u6253 READY \u6c38\u4e0d\u81ea\u8bc1\u5b8c\u6210\uff0cr401 \u4e0b"
    "\u8f6e\u6307\u9488\u636e\u6b64\u8bef\u63d0\u300cflip \u8ba1\u5212"
    "\u63d0\u5448\u9762\u300d\uff08r402 \u5f00\u5de5 git log -S "
    "_pool_merged_view \u4e09\u8bfb\u70b9\u6838\u9a8c\u5f53\u573a\u62e6"
    "\u00b7\u96f6\u91cd\u590d\u6267\u884c\uff09\u3002\u4fee\u6cd5=\u4eea"
    "\u5668\u843d\u5730\u611f\u77e5\u5e38\u91cf\uff08FLIP_LANDED_COMMIT/"
    "FLIP_RECEIPT_REL\uff09+status \u6458\u8981\u884c\u6539 LANDED \u8bfb"
    "\u51fa+per-machine \u884c\u53bb\u95e8\u5224\u8bed+cmd_run streak "
    "\u884c\u53bb /3 \u76ee\u6807\u8bed+selftest E1-E3 \u4e09\u817f"
    "\uff0813/13 PASS\uff09\u3002How to apply\uff1a\u4e00\u5207\u300c"
    "\u95e8\u5224\u540e\u6267\u884c\u300d\u7c7b\u4eea\u5668\u5b8c\u6210"
    "\u6001\u5fc5\u987b\u5199\u56de\u4eea\u5668\u672c\u4f53\u8bfb\u51fa"
    "\uff08\u5b8c\u6210\u4e0d\u81ea\u8bc1=\u6c38\u60ac\u95e8=\u6bcf\u8f6e"
    "\u91cd\u626b\u540c\u4e00\u7b49\u5f85\u5bf9\u8c61\u8fdd\u4ea7\u54c1"
    "\u5f8b\uff09\uff1b\u63a5\u300c\u62df\u6267\u884c flip/\u8fc1\u79fb"
    "\u300d\u7c7b\u4e0b\u8f6e\u6307\u9488\u5148 git log -S \u67e5\u843d"
    "\u5730\u53f2\u52ff\u4fe1\u8bfb\u51fa\u9762\u3002"
).encode("utf-8")
if NEW_PIT[:40] in codely_after:
    die("new pit already present (idempotence)")
# insert after the r605 entry line (last hot-layer pit entry)
r605_anchor = b"[2026-10-03 03:4x r605 bm-a]"
rh = codely_after.find(r605_anchor)
if rh < 0:
    die("r605 anchor missing for insertion point")
rs, re_, rterm = line_bounds(codely_after, rh)
insert_at = re_ + len(rterm)
codely_final = (codely_after[:insert_at] + NEW_PIT + rterm
                + codely_after[insert_at:])
if codely_final.count(r605_anchor) != 1 or \
        codely_final.find(NEW_PIT[:40]) != insert_at:
    die("new pit insertion verify failed")

# ---------------- final accounting ----------------
print(f"CODELY.md: {len(codely)}B -> {len(codely_final)}B "
      f"(r393 out -{len(entry_full)}B+{removed_blanks}blank, ptr +"
      f"{len(new_ptr) - len(ptr_line)}B, new pit +{len(NEW_PIT) + len(rterm)}B)")
print(f"pit-pool.md: {len(pitpool)}B -> {len(new_pitpool)}B "
      f"(entry +{len(entry_no_term)}B, acc +{len(acc_line) + len(aterm)}B)")
print(f"entry md5={md5(entry_no_term)} lf_md5={md5(entry_lf)}")
assert entry_no_term in new_pitpool
assert ANCH not in codely_final
assert NEW_PIT in codely_final
assert acc_line in new_pitpool

# ---------------- writes (all asserts passed) ----------------
save(T147, new_t)
save(PITPOOL, new_pitpool)
save(CODELY, codely_final)
print("WRITES OK: T-147 done-flip + pit-pool r393 sweep + CODELY new pit")
