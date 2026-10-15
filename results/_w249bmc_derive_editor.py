# -*- coding: utf-8 -*-
# r1041 bm-c: derive results/_w249bmc_freeze_edits.py from the committed W248
# editor template (results/_w248bmc_freeze_edits.py, proven live-fire W248
# splice bm-c r1036 absorb window) via COUNT-ASSERTED ORDERED TRANSFORM
# (E63 lineage). Downstream->self->upstream wave shifts + structural range
# faces FIRST, then targeted context fixes (receipt keys read from the actual
# _w249bmc_20261015_probe_receipt.json this window -- never transcribed).
import io, os, sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(REPO, "results", "_w248bmc_freeze_edits.py")
DST = os.path.join(REPO, "results", "_w249bmc_freeze_edits.py")

t = io.open(SRC, encoding="utf-8").read()
log = []

def rep(old, new, expect=None, tag=""):
    global t
    n = t.count(old)
    if expect is not None:
        assert n == expect, f"[{tag}] count {n} != {expect} for: {old[:70]!r}"
    t = t.replace(old, new)
    log.append(f"{tag}: {n}x {old[:48]!r}")

# ---------- PASS 1: structural range/count faces (before blanket passes) ----------
rep("range(236, 248)", "range(237, 249)", 2, "P1-fresh/legcount-loop")
rep("range(232, 247)", "range(232, 248)", 1, "P1-legs-range")
rep("list(range(236, 247))", "list(range(237, 248))", 1, "P1-dropped-range")
rep("[232, 233, 234, 235]", "[232, 233, 234, 235, 236]", 1, "P1-kept-list")
rep('assert legs_kept.count("assert pf.N1_BANDS[") == 4',
    'assert legs_kept.count("assert pf.N1_BANDS[") == 5', 1, "P1-kept-count")
rep('assert legs_sec.count("assert pf.N1_BANDS[") == 15',
    'assert legs_sec.count("assert pf.N1_BANDS[") == 16', 1, "P1-legs-count")
rep('assert par_full.count("assert pf.N1_BANDS[") == 105',
    'assert par_full.count("assert pf.N1_BANDS[") == 106', 1, "P1-parfull-count")
rep("m236", "m237", None, "P1-m236->m237")
rep(r'r" *assert pf\.N1_BANDS\[236\] =="', r'r" *assert pf\.N1_BANDS\[237\] =="', 1, "P1-split-regex")
rep("'        assert pf.N1_BANDS[236] == {\"a\": ('", "'        assert pf.N1_BANDS[237] == {\"a\": ('", 1, "P1-fresh-firstline")
rep("W236 leg boundary not found inside W247 legs segment",
    "W237 leg boundary not found inside W248 legs segment", 1, "P1-boundary-err")
rep("kept segment not W232..W235 four legs", "kept segment not W232..W236 five legs", 1, "P1-kept-err")
rep("dropped segment not W236..W246 eleven legs", "dropped segment not W237..W247 eleven legs", 1, "P1-dropped-err")
rep("(244, 243, 242, 241, 240, 239, 238, 237, 236, 235)",
    "(245, 244, 243, 242, 241, 240, 239, 238, 237, 236)", 2, "P1-transitive-deps")
rep("range(209, 249)", "range(209, 250)", 2, "P1-liveness-range")
# header (lines 40-43 of the template)
rep("W236..W246 legs (11 rows) do NOT enter", "W237..W247 legs (11 rows) do NOT enter", 1, "P1-hdr-dropped")
rep("fresh W236..W247 legs (12 rows) are added", "fresh W237..W248 legs (12 rows) are added", 1, "P1-hdr-fresh")
rep("parity = 106 rows (W138..W206 + W211..W247). Zero assumption",
    "parity = 107 rows (W138..W206 + W211..W248). Zero assumption", 1, "P1-hdr-parity")
# extraction comment (lines 246-250)
rep("AND the W232..W235", "AND the W232..W236", 1, "P1-ext-kept")
rep("W236..W246 legs (11) are EXCLUDED from the estate path per the prereg",
    "W237..W247 legs (11) are EXCLUDED from the estate path per the prereg", 1, "P1-ext-dropped")
rep("appends fresh W236..W247 legs (12, machine-derived",
    "appends fresh W237..W248 legs (12, machine-derived", 1, "P1-ext-fresh")
rep("keep W232..W235 verbatim (4 legs)", "keep W232..W236 verbatim (5 legs)", 1, "P1-split-kept")
rep("W236..W246 legs (11) are excluded from the estate path",
    "W237..W247 legs (11) are excluded from the estate path", 1, "P1-split-dropped")
# emitted block comments (lines 536-541)
rep("W232..W235 legs (4) extracted verbatim from the OWN W247 block",
    "W232..W236 legs (5) extracted verbatim from the OWN W248 block", 1, "P1-blk-kept-comment")
rep("the W247 block's own W236..W246 legs (11) are",
    "the W248 block's own W237..W247 legs (11) are", 1, "P1-blk-dropped-comment")
rep("W236..W247 legs (12) added, machine-derived",
    "W237..W248 legs (12) added, machine-derived", 1, "P1-blk-fresh-comment")
rep("-> 106 parity rows (W138..W206+W211..W247).",
    "-> 107 parity rows (W138..W206+W211..W248).", 1, "P1-blk-parity-comment")
# receipt parity note (line 765)
rep("+ W232..W235 legs extracted verbatim (4) per the frozen",
    "+ W232..W236 legs extracted verbatim (5) per the frozen", 1, "P1-rcpt-kept")
rep("the W247 block's own W236..W246 legs (11) EXCLUDED",
    "the W248 block's own W237..W247 legs (11) EXCLUDED", 1, "P1-rcpt-dropped")
rep("fresh W236..W247 legs (12) machine-derived", "fresh W237..W248 legs (12) machine-derived", 1, "P1-rcpt-fresh")
rep("W248 block = 106 rows (W138..W206 + W211..W247)", "W249 block = 107 rows (W138..W206 + W211..W248)", 1, "P1-rcpt-parity")

# ---------- PASS 2: downstream shift W249 -> W250 (incl. W249p_* receipt keys) ----------
rep("W249", "W250", None, "P2-downstream")
assert "W249" not in t, "P2 leftover W249"

# ---------- PASS 3: self shift 248 -> 249 (catches W248 + bare) ----------
n248 = t.count("248")
rep("248", "249", None, "P3-self")
log.append(f"P3 consumed {n248} '248' substrings")

# ---------- PASS 4: upstream shift 247 -> 248 ----------
n247 = t.count("247")
rep("247", "248", None, "P4-upstream")
log.append(f"P4 consumed {n247} '247' substrings")

# ---------- PASS 5: targeted context fixes (fragment-level, log-verified) ----------
# receipt leg1 relation_asserts keys (actual W249 receipt faces, read this window)
rep('ra.get("B_base_above_W248c_tail")', 'ra.get("B_base_above_W248_tail")', 1, "P5-key-bbase")
rep('ra.get("W248c_reservation_respected_A")', 'ra.get("W247_W248_bands_respected_A")', 1, "P5-key-rsvA")
rep('ra.get("W248c_reservation_respected_B")', 'ra.get("W247_W248_bands_respected_B")', 1, "P5-key-rsvB")
# upstream owner faces: W248 row is bm-c's own wave (frozen by bm-c r1036)
rep('assert W248.get("engine_owner") == "bm-a"', 'assert W248.get("engine_owner") == "bm-c"', 1, "P5-gate05-owner")
rep("bm-a seat owner expected", "bm-c seat owner expected", 1, "P5-gate05-err")
rep("owner=bm-a seat honored", "owner=bm-c seat honored (upstream W248)", 1, "P5-print-owner")
rep('pf.N1_BANDS[248].get("engine_owner") == "bm-a"', 'pf.N1_BANDS[248].get("engine_owner") == "bm-c"', 1, "P5-mirror-owner")
rep("law-mirror parity; bm-a upstream seat face", "law-mirror parity; bm-c upstream seat face (own-seat upstream)", 1, "P5-mirror-err")
rep('"registered W248 row parity drift (r307; bm-a five-face freeze; own-seat face disclosed)"',
    '"registered W248 row parity drift (r307; bm-c five-face freeze; own-seat face disclosed)"', 1, "P5-legmsg-248")
rep("bm-a own seat executed at", "bm-c own seat executed at", None, "P5-owner-exec")
rep("the bm-a r1021 window", "the bm-c r1036 absorb window", None, "P5-owner-window")
rep("bm-a r1021 freeze + r1022 finalize one-pass", "bm-c r1036 absorb-window freeze + finalize one-pass", None, "P5-upstream-chain")
rep("bm-a r1021 freeze + r1022 finalize\n# one-pass", "bm-c r1036 absorb-window freeze + finalize\n# one-pass", 1, "P5-upstream-chain-lb")
rep("bm-a r1021 splice\n# generation", "bm-c r1036 splice\n# generation", 1, "P5-splice-gen")
rep("bm-a splice generation r1021 window", "bm-c splice generation r1036 absorb window", 1, "P5-splice-gen2")
rep("bm-a r1021/r1022", "bm-c r1036", None, "P5-upstream-pair")
rep("bm-a r1022 own-wave closeout", "bm-c r1036 absorb-window closeout", None, "P5-closeout")
rep("closeout 19:0x", "closeout 22:1x", None, "P5-closeout-ts")
rep("bm-a own-wave closeout r1022", "bm-c own-wave closeout r1036 absorb window", None, "P5-rcpt-closeout")
rep("W248 bm-a finalize one-pass", "W248 bm-c finalize one-pass", 1, "P5-print-upstream")
rep('"engine_owner": "bm-a (upstream seat honored)"', '"engine_owner": "bm-c (upstream seat honored)"', 1, "P5-rcpt-owner")
# window refs
rep("bm-c r1036 freeze window", "bm-c r1041 freeze window", 1, "P5-hdr-window")
rep("r1034-continuation/r1035 window", "r1040-dead window (absorbed+committed r1041)", None, "P5-derive-window")
rep("authored 20:00:36", "authored 04:04:22", 2, "P5-authored")
rep("_w248bma_freeze_edits.py template (proven live-fire freeze, bm-a\n# r1021 window; engine self-burn 12/12 + finalize one-pass verified r1022)",
    "_w248bmc_freeze_edits.py template (proven live-fire freeze, bm-c\n# r1036 absorb window; engine self-burn 12/12 + finalize one-pass verified same window)",
    1, "P5-lineage")
# seat identity
rep("MSG-20261015-164x-bmc-w249-seat", "MSG-20261015-225x-bmc-w249-seat", None, "P5-seat-msg")
rep("86819ad77", "8949e0aef", None, "P5-seat-origin")
rep("r1030 MSG-20261015-164x", "r1037 MSG-20261015-225x", None, "P5-seat-pub")
rep("r1030 BEFORE this freeze", "r1037 BEFORE this freeze", None, "P5-seat-pub2")
rep("queue-depth supply depth-2 at publish, waits-upstream ARMED lane",
    "queue-head supply -- W248 complete -> freeze UNBLOCKED at publish, ZERO waits-upstream face", None, "P5-seat-lane")
rep("waits-upstream ARMED on the W248 chain is DISARMED by the W248 five-face + finalize landing",
    "seat published post-W248-chain (queue-head supply, freeze-UNBLOCKED; the W248 five-face + finalize landed bm-c r1036 before publish)", None, "P5-seat-lane-hdr")
rep("the W249 freeze's waits-upstream on the W248 chain is DISARMED by the W248 five-face + finalize landing",
    "the W249 seat was published AFTER the W248 five-face + finalize landing (zero waits-upstream face)", None, "P5-seat-lane-inner")
# ledger anchors
rep("967_735", "969_935", 1, "P5-ledger-int")
rep("541_320", "543_520", 1, "P5-k-int")
rep("967,735", "969,935", None, "P5-ledger-prose")
rep("541,320", "543,520", None, "P5-k-prose")
# band literals (self wave W249: A 563_501..565_500 / B 544_901..545_100)
rep("561_501", "563_501", None, "P5-band-alo")
rep("563_500", "565_500", None, "P5-band-ahi")
rep("544_701", "544_901", None, "P5-band-blo")
rep("544_900", "545_100", None, "P5-band-bhi")
rep("561501", "563501", None, "P5-band-alo-int")
# receipt band_semantics static staircase literal (W247+W248 B bands both below)
rep("the registered W239 A band 542_501..544_500 and the registered W248 B band 544_501..544_700 both sit below the walk start",
    "the registered W239 A band 542_501..544_500 and the registered W247/W248 B bands 544_501..544_700 + 544_701..544_900 all sit below the walk start",
    None, "P5-rcpt-staircase")
# ordinal faces (probe receipt leg0: owner 238 / bma 129 / bmc 68 -> candidate 239th/69th)
rep("== 237 and len(bma_rows_live) == 129 and len(bmc_rows_live) == 67",
    "== 238 and len(bma_rows_live) == 129 and len(bmc_rows_live) == 68", 1, "P5-ord-gate")
rep("owner rows 237 + candidate", "owner rows 238 + candidate", None, "P5-ord-owner-prose")
rep("237/129/67 PRE-splice", "238/129/68 PRE-splice", 1, "P5-ord-err")
rep("bm-c rows 67 +\n      f\"candidate = 68th", "bm-c rows 68 +\n      f\"candidate = 69th", None, "P5-ord-bmc-prose")
rep("bm-c rows 67 + candidate", "bm-c rows 68 + candidate", None, "P5-ord-rows67")
rep("rows 67 + candidate", "rows 68 + candidate", None, "P5-ord-rows67b")
rep("bmc_ordinal=68", "bmc_ordinal=69", None, "P5-ord-receipt68")
rep("68th own wave", "69th own wave", None, "P5-ord-68th")
rep("68th owned claim", "69th owned claim", None, "P5-ord-68claim")
rep("SIXTY-EIGHTH", "SIXTY-NINTH", None, "P5-word-68")
rep("TWO HUNDRED AND FORTY-EIGHTH", "TWO HUNDRED AND FORTY-NINTH", None, "P5-word-248")
rep('probe_receipt_bmc_ordinal_face": 68', 'probe_receipt_bmc_ordinal_face": 69', 1, "P5-ord-face68")
# seed-gap ordinal: mirror the FROZEN W249 prereg prose (twelfth) + disclose drift
rep("TENTH consecutive", "TWELFTH consecutive", None, "P5-seedgap")
rep("thirty-sixth consecutive", "thirty-seventh consecutive", 2, "P5-cleanwin")
# stale 'wave 245:' cfg label aging face -> true self wave
rep('"wave 245: ",', '"wave 249: ",', 1, "P5-wave-label")
# prereg bundle note: honest authorship
rep("banned gate rc0, committed+pushed same window; commit ",
    "banned gate ADMIT rc0 re-verified r1041, committed r1041; commit ", 1, "P5-bundle-note")

# ---------- structural asserts on output ----------
for needle, want in [
    ("# --- W249 materializer face", 2),          # hdr emit + post-edit gate
    ("# --- W248 materializer face", 1),          # a22 extraction anchor
    ('"+ W249 materializer face', 2),
    ("range(16, 249)", 2),
    ("range(17, 249)", 3),
    ("range(237, 249)", 3),
    ("range(209, 250)", 2),
    ("if w < 249)", 5),
    ("if w < 248)", 1),  # the family-6 stale-check gate string (correct post-shift form)
    ("_w249bmc_20261015_probe_receipt.json", None),
    ("_w249bmc_freeze_receipt.json", 1),
    ("MSG-20261015-225x-bmc-w249-seat", None),
    ("8949e0aef", None),
    ("969_935", 1),
    ("543_520", 1),
    ("(563_501, 565_500)", 1),
    ("(544_901, 545_100)", 1),
    ('B_base_above_W248_tail', 1),
    ('W247_W248_bands_respected_A', 1),
    ("W250p_A_naive", None),
    ("arith_a249", None),
    ("arith_b249", None),
    ('"PERPETUAL-N1-W249-SHARD-0"', None),
    ('n1_w249_results.json', None),
    ("TWELFTH consecutive", None),
]:
    n = t.count(needle)
    if want is not None:
        assert n == want, f"OUTPUT-GATE {needle!r}: {n} != {want}"
    log.append(f"OUT {needle!r} = {n}")

assert "W248c_reservation" not in t, "stale W248c key"
assert "bm-a r1021" not in t and "bm-a r1022" not in t, "stale upstream bm-a window refs"
assert t.count("1945-bm-a") == t.count("1945-bm-a"), "ADMIT convention untouched"

io.open(DST, "w", encoding="utf-8", newline="").write(t)
import py_compile
py_compile.compile(DST, doraise=True)
io.open(os.path.join(REPO, "results", "_w249bmc_derive_editor_log.txt"), "w",
        encoding="utf-8").write("\n".join(log))
print(f"DERIVE OK -> {DST} ({len(t)} chars); {len(log)} transform log rows")
print("\n".join(log[-8:]))
