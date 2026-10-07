# -*- coding: utf-8 -*-
"""r815 bm-a W171 freeze edits: four insertions (pf N1_BANDS[171] row +
n1 WAVE_CONFIGS[171] entry + n1 W171 materializer block refresh +
n1 PASS snippet claim insertion). DRY flag: --dry = zero-write simulation
(r781 verify-separation law + r811 dry-run precedent: full stale+prose+
AST asserts in memory BEFORE any write).

Bloodline: r813 _r813bma_w170_freeze_edits.py machinery (r773 pit law
freeze-editor compliance + r776 fragment-needle law + r781
verify-separation law), W171 facts live-registry-driven:
  - pre-seat probe results/_r814bma_w171_probe_receipt.json rc0 ADMIT
    (A 391_004..393_003 staircase THIRTIETH instance E36 hops=1 past
    the registered W170 B band 390_804..391_003; naive 390_804..392_803
    refused at its own start by the W170 B band; B 393_004..393_203
    own-A mutual exclusion hops=1, naive 391_004..391_203);
  - face probe results/_r815bma_w171_face_probe_receipt.json rc0 (all
    four W170 faces dumped + needle counts; this TOK is built from the
    PHYSICAL probe-dumped shapes, r776 law);
  - seat MSG-2026-10-07-0843-bma-w171-seat published (r814 seat push
    3290e586b machine-derived via git log origin/main -- <path>; the
    state file carried 1aab5daf7 = stale pre-rebase artifact, r812
    honest-note precedent), r565 law: on origin BEFORE this freeze
    commit; seat MSG still in fleet/inbox/ at freeze time = honest
    DEFERRED state (self-ack move deferred to the W171 finalize window
    -- NO direction fixup needed this window, the W170-era DEFERRED
    prose rolls true);
  - 3-item payload honesty FIXUP (this window): the W171 seat push
    carried seat MSG + probe script + probe receipt ONLY (the W170
    finalize product was already on origin since r813, not re-shipped;
    seat MSG-0843 discloses the 3-item truth) -- the rolled W170-era
    "4-item, W146 same-push precedent" prose is corrected per-face;
  - per-wave prereg research/PERPETUAL_N1_W171_PREREG.md (r815 build
    via _r815bma_w171_prereg_build.py, banned gate ADMIT 0);
  - W170 finalize one-pass landed in the r813-labeled takeover window:
    ledger head 779,412, merged pool K=371,920 (n1_w170_results.json
    machine-read);
  - W170 freeze registered sha machine-derived = cb7314d64 (git log
    origin/main --grep "W170 FREEZE");
  - lineage constants disclosed (r795 precedent, passed through):
    (a) the "wave N-1:" entry label + "wave N-1 = first free number"
    mat-header label ride the vmap verbatim (off-by-one lineage quirk
    since the W165 r795 band-facts template); (b) "law sec.4 W170 row,
    r795" band-facts template stamp keeps its r795; (c) "r813 sec8
    succession" does NOT roll (the W170 sec8 succession face was
    backfilled in the r813-labeled takeover window); (d) "single-window
    derive (r812 merged the gate legs INTO the pre-seat probe..." stays
    (historical merge citation, the structure persists); (e) the
    bm-a-owned ordinal word rolls eighty-fifth -> eighty-sixth (the
    lineage pattern: ordinal word = prior-row count, rows 86 + candidate
    = 87th owned per probe leg0).

r773 pit law compliance:
  (1) full string-face inventory empirically probed BEFORE TOK
      (_r815bma_w171_face_probe.py -- four face dumps + needle-count
      receipt, rc0);
  (2) composite band strings tokenized WHOLE (every dotted band /
      seed-base row / jump phrase / projection pair is a single token;
      bare numerals run LAST);
  (3) post-edit full-file start>end malformed-window regex scan on BOTH
      touched files;
  (4) every projection value re-derived FROM the on-disk probe receipt
      (r587 never-transcribe law);
  (5) r776 fragment-needle law: all needles taken from the PHYSICAL
      probe-dumped shapes (the pf "r810 gate\\r\\n    # leg3" split form
      carried by @GATEPF@ + @LEG3PF@; the entry "re-derive on the "
      fragment split carried by @FR1@/@FR2@);
  (6) r560 insert-after-last-registered-row + pre-edit live registry
      parity + origin anti-collision pre-check (r530/r687: fetch +
      origin carries no W171 registration before this freeze);
  (7) AST gate after every edit batch (r580/r781)."""
import ast
import io
import json
import os
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
DRY = "--dry" in sys.argv
PF = r"scripts/perpetual_faces.py"
N1 = r"scripts/perpetual_faces_n1.py"
CRLF = "\r\n"

# --- machine-derived facts (r587: read from on-disk receipts) ----------------
probe = json.load(open(r"results/_r814bma_w171_probe_receipt.json", encoding="utf-8"))
assert probe["verdict"] == "ADMIT", probe["verdict"]
assert probe["bands"] == {"A": "391004_393003", "B": "393004_393203"}, probe["bands"]
leg0, leg1 = probe["legs"]["leg0"], probe["legs"]["leg1"]
leg2, leg3, leg4 = probe["legs"]["leg2"], probe["legs"]["leg3"], probe["legs"]["leg4"]
assert leg1["A"] == [391004, 393003] and leg1["B"] == [393004, 393203], leg1
assert leg1["hops_A"] == 1 and leg1["hops_B"] == 1, leg1
assert leg1["ARITH_A"] == [390804, 392803], leg1["ARITH_A"]
assert leg1["ARITH_B"] == [391004, 391203], leg1["ARITH_B"]
assert leg1["B_naive_first_clean"] == [391004, 391203], leg1
assert leg1["B_hop_chain"][0]["jump_to"] == 393004, leg1["B_hop_chain"]
assert leg2["conflicts"] == 0, leg2
assert leg3["origin_vacancy"] is True, leg3
assert leg0["rows"] == 168 and leg0["tail"] == "W170" and leg0["ordinal"] == 161 \
    and leg0["bma_ordinal"] == 87 and leg0["owner_rows"] == 160 \
    and leg0["bma_rows"] == 86 and leg0["w170_ledger_head"] == 779412, leg0
W172p_A = "393_004..395_003"
W172p_B = "393_204..393_403"
assert leg4["W172p_A"] == "393004..395003" and leg4["W172p_B"] == "393204..393403", leg4
assert leg4["hops_A"] == 0 and leg4["hops_B"] == 0, leg4
assert leg4["W172p_B_lands_inside_W172p_A"] is True, leg4
w170res = json.load(open(r"results/perpetual_faces/n1_w170_results.json", encoding="utf-8"))
assert w170res["null_pool_cumulative"]["merged"]["n_values"] == 371920, "W170 merged K drift"
assert w170res["null_pool_cumulative"]["merged"]["n_values"] + 2200 == 374120, \
    "W171 K projection arithmetic"
assert os.path.exists(os.path.join("research", "PERPETUAL_N1_W171_PREREG.md")), \
    "W171 per-wave prereg missing on disk"
_r = subprocess.run(["git", "log", "origin/main", "--format=%h", "--grep=W170 FREEZE", "-1"],
                    capture_output=True, text=True)
W170_SHA = _r.stdout.strip()
assert W170_SHA == "cb7314d64", W170_SHA
_r2 = subprocess.run(["git", "log", "origin/main", "--format=%h", "-1", "--",
                      "fleet/inbox/MSG-2026-10-07-0843-bma-w171-seat.md"],
                     capture_output=True, text=True)
SEAT_SHA = _r2.stdout.strip()
assert SEAT_SHA == "3290e586b", SEAT_SHA
# honesty precondition: the W171 seat MSG sits in fleet/inbox/ at freeze
# time (DEFERRED self-ack state; the mover would be THIS machine at the
# W171 finalize window) -- the rolled W170-era DEFERRED prose rides true.
assert os.path.exists(os.path.join("fleet", "inbox",
                                   "MSG-2026-10-07-0843-bma-w171-seat.md")), \
    "W171 seat MSG not in fleet/inbox/ (DEFERRED prose would be wrong)"
assert not os.path.exists(os.path.join("fleet", "inbox", "processed",
                                        "MSG-2026-10-07-0843-bma-w171-seat.md")), \
    "W171 seat MSG already processed (landed direction would be TRUE -- prose wrong)"


def u(s):
    return re.sub(r"(\d)(?=(\d{3})+$)", r"\1_", s)


# --- ordered value-map (tokens first, then back-substitution) ---------------
TOK = [
    # seat / push / payload carriers (composites FIRST)
    ('MSG-2026-10-07-0738-bma-w170-seat', "@SEAT@"),
    ('0f00fa424', "@SEATSHA@"),
    ('r812 pre-seat push', "@PSP@"),
    ('r812 pre-seat', "@PSPPF@"),           # pf split fragment (after @PSP@)
    ('W169 finalize product', "@FWPROD@"),
    # seed-base rows (entry comment face; bands + ordinal carried WHOLE)
    ('"a_seed_base": 388_804,        # law sec.4 W170 A: 388_804..390_803 (FIRST-CLEAN past the registered W169 B band; arithmetic 388_604..390_603 REFUSED at own start by the W169 B band; hops=1; A-hops-prior-B staircase twenty-ninth instance, E36 card)', "@ASROW@"),
    ('"b_exit_seed_base": 390_804,   # law sec.4 W170 B: 390_804..391_003 (FIRST-CLEAN past the own-wave A window; arithmetic 388_804..389_003 lands inside own-A, same-freeze mutual exclusion W141 precedent; reserved walk hops=1; B base == own-A tail+1)', "@BSROW@"),
    # registered-prior-row citations (machine-verified sha pairing)
    ('W169 row bm-a r811 freeze', "@PROW1@"),
    ('9c2271baf, SINGLE STATE zero seat gap W2..W169 all', "@PROW2@"),
    ('bm-a r811 freeze 9c2271baf', "@REGROW@"),
    # freeze-session composites (this window: bm-a r815 freeze)
    ('bm-a r813 freeze', "@FZH@"),
    ('r813 bm-a freeze', "@MFZH@"),
    ('r813 bm-a] ', "@CLMS@"),
    # prior-finalize citations (W170 finalize one-pass r813 takeover window)
    ('W169 finalize landed same-window r812', "@FW@"),
    ('W169 finalize one-pass bm-a r812', "@FOPW@"),
    ('W169 bm-a r812 one-pass', "@FOP@"),
    ('finalize one-pass bm-a r812', "@FOPM2@"),
    # probe receipt carrier
    ('_r812bma_w170_probe_receipt.json', "@PRC@"),
    ('MSG-0738', "@MSGS@"),
    # gate / projection citations: W170-era W171+ projection faces
    ('r810 gate leg3', "@GATEL3@"),
    ('r810 gate', "@GATEPF@"),              # pf split fragment (after @GATEL3@)
    ('leg3', "@LEG3PF@"),                   # pf split fragment tail
    ('W169 seat W170+ projection', "@SEATPROJ@"),
    ('W170+ projection', "@WPN@"),
    ('gate-derived r812', "@GDR@"),
    ('W170 B band 390_804..391_003 will refuse the naive', "@FR0@"),
    ('W171 A window; W171 freezer MUST re-derive on the ', "@FR1@"),
    ('post-W170 universe', "@FR2@"),
    # W172+ projection bands (probe leg4 verbatim, WHOLE; BEFORE all band
    # tokens and seed backstops -- r773 pit law)
    ('390_804..392_803', "@PA@"),
    ('391_004..391_203', "@PB@"),
    # jump phrases (longest first; BEFORE @BB@ which shares the B-band substring)
    ('jumps to 390_804, first-clean 390_804..391_003 hops=1', "@JN@"),
    ('jumps to 390_804 -> 390_804..391_003,', "@JP@"),
    ('390_804 and lands 390_804..391_003', "@JAND@"),
    ('own-wave A window reserved jumps to 390_804, first-clean ', "@JB@"),
    # assert composites
    ('== 388_804 == 388_803 + 1', "@ASB@"),
    ('== 390_804 == 390_803 + 1', "@BSB@"),
    ('set(range(388_804, 390_804))', "@ARITHA@"),
    ('set(range(390_804, 391_004))', "@ARB@"),
    # dotted band geometry
    ('388_604..390_603', "@NA@"),
    ('388_604..388_803', "@OB@"),
    ('388_804..390_803', "@AB@"),
    ('388_804..389_003', "@NB@"),
    ('390_804..391_003', "@BB@"),
    # base-relation composites
    ('388_803+1', "@ABASE@"),
    ('390_803+1', "@BBASE@"),
    # identity / stats / ordinals
    ('PERPETUAL_N1_W170_PREREG.md', "@PF@"),
    ('PERPETUAL-N1-W170', "@B@"),
    ('n1_w170_results.json', "@OD@"),
    ('n1_w170', "@SD@"),
    ('n1w170', "@SD2@"),
    ('777,212', "@LEDG@"),
    ('369,720', "@KOLD@"),
    ('ONE HUNDRED-AND-SIXTIETH', "@ORDW@"),
    ('engine_owner rows 159', "@R154@"),
    ('rows 85 + candidate', "@ROWS80@"),
    ('eighty-fifth', "@SVN@"),
    ('twenty-ninth', "@ST24@"),
    ('W17..W169', "@W17TO@"),
    ('W2..W169', "@W2TO@"),
    ('W1..W169', "@W1TO@"),
    ('range(17, 170)', "@DEPW@"),
    ('range(16, 170)', "@R16@"),
    ('if w < 170', "@WPREV@"),
    ('170: {"a": (388_804, 390_803), "b_exit": (390_804, 391_003),', "@RROW@"),
    ('170: {"batch"', "@RENTRY@"),
    # wave numbers (higher first: W171 projection -> W172; then W170->W171,
    # W169->W170)
    ('W171', "@WN2@"),
    ('W170', "@WN@"),
    ('W169', "@W@"),
    # bare numerals LAST
    ('170', "@IDX@"),
    ('169', "@IDX2@"),
]
BACK = [
    ("@SEAT@", "MSG-2026-10-07-0843-bma-w171-seat"),
    ("@SEATSHA@", SEAT_SHA),
    ("@PSP@", "r814 pre-seat push"),
    ("@PSPPF@", "r814 pre-seat"),
    ("@FWPROD@", "W170 finalize product"),
    ("@ASROW@", '"a_seed_base": 391_004,        # law sec.4 W171 A: 391_004..393_003 (FIRST-CLEAN past the registered W170 B band; arithmetic 390_804..392_803 REFUSED at own start by the W170 B band; hops=1; A-hops-prior-B staircase thirtieth instance, E36 card)'),
    ("@BSROW@", '"b_exit_seed_base": 393_004,   # law sec.4 W171 B: 393_004..393_203 (FIRST-CLEAN past the own-wave A window; arithmetic 391_004..391_203 lands inside own-A, same-freeze mutual exclusion W141 precedent; reserved walk hops=1; B base == own-A tail+1)'),
    ("@PROW1@", "W170 row bm-a r813 freeze"),
    ("@PROW2@", f"cb7314d64, SINGLE STATE zero seat gap W2..W170 all"),
    ("@REGROW@", f"bm-a r813 freeze {W170_SHA}"),
    ("@FZH@", "bm-a r815 freeze"),
    ("@MFZH@", "r815 bm-a freeze"),
    ("@CLMS@", "r815 bm-a] "),
    ("@FW@", "W170 finalize landed same-window r813"),
    ("@FOPW@", "W170 finalize one-pass bm-a r813"),
    ("@FOP@", "W170 bm-a r813 one-pass"),
    ("@FOPM2@", "finalize one-pass bm-a r813"),
    ("@PRC@", "_r814bma_w171_probe_receipt.json"),
    ("@MSGS@", "MSG-0843"),
    ("@GATEL3@", "r812 probe leg4"),
    ("@GATEPF@", "r812 probe"),
    ("@LEG3PF@", "leg4"),
    ("@SEATPROJ@", "W170 seat W171+ projection"),
    ("@WPN@", "W171+ projection"),
    ("@GDR@", "gate-derived r814"),
    ("@FR0@", "W171 B band 393_004..393_203 will refuse the naive"),
    ("@FR1@", "W172 A window; W172 freezer MUST re-derive on the "),
    ("@FR2@", "post-W171 universe"),
    ("@PA@", W172p_A),
    ("@PB@", W172p_B),
    ("@JN@", "jumps to 393_004, first-clean 393_004..393_203 hops=1"),
    ("@JP@", "jumps to 393_004 -> 393_004..393_203,"),
    ("@JAND@", "393_004 and lands 393_004..393_203"),
    ("@JB@", "own-wave A window reserved jumps to 393_004, first-clean "),
    ("@ASB@", "== 391_004 == 391_003 + 1"),
    ("@BSB@", "== 393_004 == 393_003 + 1"),
    ("@ARITHA@", "set(range(391_004, 393_004))"),
    ("@ARB@", "set(range(393_004, 393_204))"),
    ("@NA@", "390_804..392_803"),
    ("@OB@", "390_804..391_003"),
    ("@AB@", "391_004..393_003"),
    ("@NB@", "391_004..391_203"),
    ("@BB@", "393_004..393_203"),
    ("@ABASE@", "391_003+1"),
    ("@BBASE@", "393_003+1"),
    ("@PF@", "PERPETUAL_N1_W171_PREREG.md"),
    ("@B@", "PERPETUAL-N1-W171"),
    ("@OD@", "n1_w171_results.json"),
    ("@SD@", "n1_w171"),
    ("@SD2@", "n1w171"),
    ("@LEDG@", "779,412"),
    ("@KOLD@", "371,920"),
    ("@ORDW@", "ONE HUNDRED-AND-SIXTY-FIRST"),
    ("@R154@", "engine_owner rows 160"),
    ("@ROWS80@", "rows 86 + candidate"),
    ("@SVN@", "eighty-sixth"),
    ("@ST24@", "thirtieth"),
    ("@W17TO@", "W17..W170"),
    ("@W2TO@", "W2..W170"),
    ("@W1TO@", "W1..W170"),
    ("@DEPW@", "range(17, 171)"),
    ("@R16@", "range(16, 171)"),
    ("@WPREV@", "if w < 171"),
    ("@RROW@", '171: {"a": (391_004, 393_003), "b_exit": (393_004, 393_203),'),
    ("@RENTRY@", '171: {"batch"'),
    ("@WN2@", "W172"),
    ("@WN@", "W171"),
    ("@W@", "W170"),
    ("@IDX@", "171"),
    ("@IDX2@", "170"),
]
# r587 belt-and-braces: the projection BACK values equal probe leg4 verbatim
assert ("@PA@", W172p_A) in BACK and ("@PB@", W172p_B) in BACK

# per-face expected TOK counts (from the r815 face-probe receipt; r745 law)
FCOUNT = {
    "pf": {"@WN@": None, "@W@": None, "@ASROW@": 0, "@BSROW@": 0,
           "@SEAT@": 1, "@SEATSHA@": 1, "@PSP@": 0, "@PSPPF@": 2, "@FWPROD@": 1,
           "@SEATPROJ@": 1, "@WPN@": 1, "@GDR@": 1, "@GATEL3@": 0, "@GATEPF@": 1,
           "@LEG3PF@": 1, "@FR0@": 1, "@FR1@": 1, "@FR2@": 0, "@PA@": 1, "@PB@": 1,
           "@JN@": 0, "@JP@": 1, "@JAND@": 0, "@JB@": 0, "@ASB@": 0, "@BSB@": 0,
           "@ARITHA@": 0, "@ARB@": 0, "@NA@": 1, "@OB@": 1, "@AB@": 1, "@NB@": 1,
           "@BB@": 0, "@ABASE@": 1, "@BBASE@": 1, "@PF@": 0, "@B@": 0, "@OD@": 0,
           "@SD@": 0, "@SD2@": 0, "@LEDG@": 0, "@KOLD@": 0, "@ORDW@": 0,
           "@R154@": 0, "@ROWS80@": 0, "@SVN@": 0, "@ST24@": 1, "@W17TO@": 0,
           "@W2TO@": 0, "@W1TO@": 0, "@DEPW@": 0, "@R16@": 0, "@WPREV@": 0,
           "@RROW@": 1, "@RENTRY@": 0, "@WN2@": 0, "@IDX@": 0, "@IDX2@": 0,
           "@MSGS@": 0,
           "@FW@": 0, "@FOPW@": 0, "@FOP@": 0, "@FOPM2@": 0, "@PRC@": 1,
           "@PROW1@": 0, "@PROW2@": 0, "@REGROW@": 0, "@FZH@": 1, "@MFZH@": 0,
           "@CLMS@": 0},
    "entry": {"@WN@": None, "@W@": None, "@ASROW@": 1, "@BSROW@": 1,
              "@SEAT@": 1, "@SEATSHA@": 1, "@PSP@": 1, "@PSPPF@": 0, "@FWPROD@": 1,
              "@SEATPROJ@": 2, "@WPN@": 1, "@GDR@": 0, "@GATEL3@": 2, "@GATEPF@": 0,
              "@LEG3PF@": 0, "@FR0@": 1, "@FR1@": 1, "@FR2@": 1, "@PA@": 1,
              "@PB@": 1, "@JN@": 1, "@JP@": 0, "@JAND@": 0, "@JB@": 0, "@ASB@": 0,
              "@BSB@": 0, "@ARITHA@": 0, "@ARB@": 0, "@NA@": 1, "@OB@": 1,
              "@AB@": 1, "@NB@": 1, "@BB@": 0, "@ABASE@": 0, "@BBASE@": 0,
              "@PF@": 1, "@B@": 1, "@OD@": 1, "@SD@": 1, "@SD2@": 0, "@LEDG@": 2,
              "@KOLD@": 2, "@ORDW@": 1, "@R154@": 1, "@ROWS80@": 0, "@SVN@": 0,
              "@ST24@": 1, "@W17TO@": 0, "@W2TO@": 0, "@W1TO@": 1, "@DEPW@": 0,
              "@R16@": 0, "@WPREV@": 0, "@RROW@": 0, "@RENTRY@": 1, "@WN2@": 0,
              "@IDX@": 0, "@IDX2@": 1, "@MSGS@": 0, "@FW@": 1, "@FOPW@": 0, "@FOP@": 0,
              "@FOPM2@": 1, "@PRC@": 1, "@PROW1@": 1, "@PROW2@": 1, "@REGROW@": 0,
              "@FZH@": 0, "@MFZH@": 0, "@CLMS@": 0},
    "mat": {"@WN@": None, "@W@": None, "@ASROW@": 0, "@BSROW@": 0,
            "@SEAT@": 1, "@SEATSHA@": 1, "@PSP@": 1, "@PSPPF@": 0, "@FWPROD@": 0,
            "@SEATPROJ@": 3, "@WPN@": 0, "@GDR@": 0, "@GATEL3@": 3, "@GATEPF@": 0,
            "@LEG3PF@": 0, "@FR0@": 0, "@FR1@": 0, "@FR2@": 0, "@PA@": 0,
            "@PB@": 0, "@JN@": 0, "@JP@": 0, "@JAND@": 1, "@JB@": 1, "@ASB@": 1,
            "@BSB@": 1, "@ARITHA@": 1, "@ARB@": 1, "@NA@": 2, "@OB@": 2,
            "@AB@": 1, "@NB@": 2, "@BB@": 1, "@ABASE@": 2, "@BBASE@": 2,
            "@PF@": 1, "@B@": 2, "@OD@": 1, "@SD@": 1, "@SD2@": 2, "@LEDG@": 2,
            "@KOLD@": 1, "@ORDW@": 1, "@R154@": 1, "@ROWS80@": 1, "@SVN@": 1,
            "@ST24@": 2, "@W17TO@": 1, "@W2TO@": 3, "@W1TO@": 1, "@DEPW@": 1,
            "@R16@": 1, "@WPREV@": 3, "@RROW@": 0, "@RENTRY@": 0, "@WN2@": 0,
            "@IDX@": 5, "@IDX2@": 20, "@MSGS@": 1, "@FW@": 0, "@FOPW@": 1, "@FOP@": 1,
            "@FOPM2@": 0, "@PRC@": 1, "@PROW1@": 0, "@PROW2@": 0, "@REGROW@": 1,
            "@FZH@": 0, "@MFZH@": 1, "@CLMS@": 0},
    "claim": {"@WN@": None, "@W@": None, "@ASROW@": 0, "@BSROW@": 0,
              "@SEAT@": 0, "@SEATSHA@": 0, "@PSP@": 0, "@PSPPF@": 0, "@FWPROD@": 0,
              "@SEATPROJ@": 0, "@WPN@": 0, "@GDR@": 0, "@GATEL3@": 0, "@GATEPF@": 0,
              "@LEG3PF@": 0, "@FR0@": 0, "@FR1@": 0, "@FR2@": 0, "@PA@": 0,
              "@PB@": 0, "@JN@": 0, "@JP@": 0, "@JAND@": 0, "@JB@": 0, "@ASB@": 0,
              "@BSB@": 0, "@ARITHA@": 0, "@ARB@": 0, "@NA@": 0, "@OB@": 0,
              "@AB@": 0, "@NB@": 0, "@BB@": 0, "@ABASE@": 0, "@BBASE@": 0,
              "@PF@": 0, "@B@": 0, "@OD@": 0, "@SD@": 0, "@SD2@": 0, "@LEDG@": 1,
              "@KOLD@": 1, "@ORDW@": 1, "@R154@": 1, "@ROWS80@": 1, "@SVN@": 1,
              "@ST24@": 1, "@W17TO@": 1, "@W2TO@": 0, "@W1TO@": 0, "@DEPW@": 0,
              "@R16@": 0, "@WPREV@": 0, "@RROW@": 0, "@RENTRY@": 0, "@WN2@": 0,
              "@IDX@": 0, "@IDX2@": 0, "@MSGS@": 0, "@FW@": 0, "@FOPW@": 0, "@FOP@": 1,
              "@FOPM2@": 0, "@PRC@": 1, "@PROW1@": 0, "@PROW2@": 0, "@REGROW@": 0,
              "@FZH@": 0, "@MFZH@": 0, "@CLMS@": 1},
}


def vmap(s: str, kind: str) -> str:
    # NOTE: the mat block is vmap'd in TWO parts (pre / post, the chain
    # between them is verbatim-pinned r307), so per-part counts are only
    # UPPER BOUNDS of the whole-block catalog -- the assembled block is
    # then fully verified by text_asserts (stale-zero + fresh-present
    # scans on mat_new_faces); pf/entry/claim carry exact-count asserts.
    for a, tok in TOK:
        n = s.count(a)
        exp = FCOUNT[kind][tok]
        if exp is None:
            assert n > 0, f"{kind} TOK {tok}: count={n} expect>0: {a[:70]!r}"
        elif kind == "mat":
            assert n <= exp, f"{kind} TOK {tok}: count={n} expect<={exp}: {a[:70]!r}"
        else:
            assert n == exp, f"{kind} TOK {tok}: count={n} expect={exp}: {a[:70]!r}"
        if n:
            s = s.replace(a, tok)
    for tok, b in BACK:
        s = s.replace(tok, b)
    return s


# --- same-window honesty FIXUPS (3-item payload truth; applied AFTER vmap) ----
FIXUPS = {
    "pf": [
        ("# push; payload = seat MSG + pre-seat probe script + probe receipt + the" + CRLF +
         "    # W170 finalize product (4-item, W146 same-push precedent);",
         "# push; payload = seat MSG + pre-seat probe script + probe receipt" + CRLF +
         "    # (3-item; the W170 finalize product already on origin since r813," + CRLF +
         "    # not re-shipped, W146 same-push precedent);"),
    ],
    "entry": [
        ('"seat MSG + pre-seat probe script + probe receipt + the W170 finalize product (4-item, W146 precedent); "',
         '"seat MSG + pre-seat probe script + probe receipt (3-item; the W170 finalize product already on origin since r813, not re-shipped; W146 precedent); "'),
    ],
    "mat": [
        ("#     = seat MSG + pre-seat probe script + probe receipt + the W170" + CRLF +
         "    #     finalize product (4-item, W146 same-push precedent);",
         "#     = seat MSG + pre-seat probe script + probe receipt (3-item;" + CRLF +
         "    #     the W170 finalize product already on origin since r813, not" + CRLF +
         "    #     re-shipped, W146 same-push precedent);"),
    ],
}


def vmap_fix(s: str, kind: str) -> str:
    s = vmap(s, kind)
    for i, (old, new) in enumerate(FIXUPS.get(kind, [])):
        n = s.count(old)
        assert n == 1, f"{kind} fixup {i}: count={n} expect=1: {old[:70]!r}"
        s = s.replace(old, new)
    return s


def edit(path, pairs):
    src = io.open(path, encoding="utf-8", newline="").read()
    for i, (old, new) in enumerate(pairs):
        n = src.count(old)
        assert n == 1, f"{path}: needle {i} count={n} expect=1: {old[:80]!r}"
        src = src.replace(old, new)
    io.open(path, "w", encoding="utf-8", newline="").write(src)
    ast.parse(io.open(path, encoding="utf-8", newline="").read())
    print(f"{path}: {len(pairs)} edits landed, AST gate PASS")


pfsrc = io.open(PF, encoding="utf-8", newline="").read()
n1src = io.open(N1, encoding="utf-8", newline="").read()

# face-source zero-drift gate vs the r815 probe dumps
EO = '"engine_owner": "bm-a"},'
i1 = pfsrc.find("    # W170 (bm-a r813 freeze")
assert i1 > 0, "pf W170 comment block not found"
r1 = pfsrc.find('170: {"a": (388_804', i1)
assert r1 > i1, "pf W170 row not after comment block"
j1 = pfsrc.find(EO, r1) + len(EO)
block170_pf = pfsrc[i1:j1]
assert block170_pf == io.open(r"results\_r815bma_w171_probe_pf_block.txt",
                             encoding="utf-8", newline="").read(), "pf face drift vs probe"
assert block170_pf.count("engine_owner") == 1 and "9c2271baf" not in block170_pf

# pre-edit live registry parity (the W170 registered row must be intact
# before we append the W171 row -- r560 no-replace law)
sys.path.insert(0, ".")
sys.path.insert(0, "scripts")
import perpetual_faces as pfpre
assert pfpre.N1_BANDS[170] == {"a": (388_804, 390_803),
                               "b_exit": (390_804, 391_003),
                               "engine_owner": "bm-a"}, "pre-edit W170 row drift"
assert sorted(pfpre.N1_BANDS)[-1] == 170 and len(pfpre.N1_BANDS) == 168, "pre-edit row count"

# origin anti-collision pre-check (r530 never-dry + r687 dual-scan:
# fetch fresh, origin must carry no W171 registration before this freeze)
subprocess.run(["git", "fetch", "origin"], capture_output=True)
_r = subprocess.run(["git", "show", "origin/main:scripts/perpetual_faces.py"],
                    capture_output=True)
_op = _r.stdout.decode("utf-8", "replace")
assert _r.returncode == 0, "origin pf.py read failed"
assert '171: {"a"' not in _op, "origin already carries a W171 registration (r687 dual-scan)"
assert "# W171 (bm-a" not in _op, "origin already carries a W171 freeze block"
_r2 = subprocess.run(["git", "rev-list", "--count", "origin/main..HEAD"],
                    capture_output=True, text=True)
assert _r2.stdout.strip() == "0", f"local ahead of origin: {_r2.stdout.strip()} (behind-law)"
# seat-on-origin precondition (r565 law: seat published BEFORE this freeze)
_r3 = subprocess.run(["git", "show", "origin/main:fleet/inbox/MSG-2026-10-07-0843-bma-w171-seat.md"],
                    capture_output=True)
assert _r3.returncode == 0, "W171 seat MSG not on origin (r565 pre-freeze law)"

# --- a1: pf.py W170 comment block + row -> append W171 comment block + row ----
a1 = block170_pf + CRLF + "}"
r1n = block170_pf + CRLF + vmap_fix(block170_pf, "pf") + CRLF + "}"

# --- a2: n1.py WAVE_CONFIGS entry ----------------------------------------------
k = n1src.find('170: {"batch"')
assert k > 0, "n1 W170 entry not found"
m = n1src.find(EO, k) + len(EO)
entry170 = n1src[k:m]
assert entry170 == io.open(r"results\_r815bma_w171_probe_n1_entry.txt",
                           encoding="utf-8", newline="").read(), "entry face drift vs probe"
a2 = entry170 + CRLF + "                       }"
r2 = entry170 + CRLF + "                       " + vmap_fix(entry170, "entry") + CRLF + "                       }"

# --- a3: materializer block (chain split-verbatim + one-row extension) --------
w = n1src.find("# --- W170 materializer face")
t2 = n1src.find("# --- T-141 s2 lane face", w)
assert 0 < w < t2, "materializer anchors missing"
block = n1src[w:t2]
assert block == io.open(r"results\_r815bma_w171_probe_n1_mat.txt",
                        encoding="utf-8", newline="").read(), "mat face drift vs probe"
ci = block.find("assert pf.N1_BANDS[138]")
cj = block.find("# prior-wave disjointness")
assert 0 < ci < cj, "chain boundaries missing"
pre, chain, post = block[:ci], block[ci:cj], block[cj:]
chain_rows = re.findall(r"assert pf\.N1_BANDS\[(\d+)\]", chain)
assert chain_rows == [str(x) for x in range(138, 170)], chain_rows
w170row = ('assert pf.N1_BANDS[170] == {"a": (388_804, 390_803),' + CRLF +
           '                                    "b_exit": (390_804, 391_003),' + CRLF +
           '                                    "engine_owner": "bm-a"}, \\' + CRLF +
           '            "registered W170 row parity drift (r307; bm-a r813)"' + CRLF +
           "        ")
block171 = vmap_fix(pre, "mat") + chain + w170row + vmap(post, "mat")
a3 = block + "# --- T-141 s2 lane face"
r3 = block171 + "# --- T-141 s2 lane face"

# --- a4: PASS snippet claim insertion ------------------------------------------
cs = n1src.find('"+ W170 materializer face')
assert cs > 0, "W170 claim start not found"
ce = n1src.find('"r813 bm-a] "', cs) + len('"r813 bm-a] "')
assert 0 < cs < ce, "W170 claim end not found"
claim170 = n1src[cs:ce]
assert claim170 == io.open(r"results\_r815bma_w171_probe_n1_claim.txt",
                           encoding="utf-8", newline="").read(), "claim face drift vs probe"
a4 = '"r813 bm-a] "' + CRLF + '          "+ T-141 s2 "'
r4 = '"r813 bm-a] "' + CRLF + "          " + vmap_fix(claim170, "claim") + CRLF + '          "+ T-141 s2 "'


# --- text-level assertions (shared by dry-run and apply) ----------------------
def text_asserts(pf2: str, n2: str, blk2: str):
    # r773 pit law leg 3: full-file start>end malformed-window scans
    for path, txt in ((PF, pf2), (N1, n2)):
        bad = [mm.group() for mm in re.finditer(r"(\d{3})_(\d{3})\.\.(\d{3})_(\d{3})", txt)
               if int(mm.group(3)) < int(mm.group(1))]
        assert not bad, f"malformed windows remain in {path}: {bad[:4]}"
    # W172 projection prose present in the new W171 blocks (probe leg4 verbatim;
    # the projection HEAD is "W171+ projection" = this block's next-wave face)
    assert "# W171+ projection (gate-derived r814)" in pf2, "pf W171+ projection head missing"
    assert 'probe_receipt.json; W171+ projection "' in n2, "n1 W171+ projection head fragment missing"
    assert f"# {W172p_A} CLEAN hops=0 / B first-clean {W172p_B}" in pf2, "pf W172p prose missing"
    assert f"A first-clean {W172p_A} " in n2 and f"B first-clean {W172p_B} CLEAN" in n2, \
        "n1 W172p prose missing"
    assert "W172 A window; W172 freezer MUST re-derive on the post-W171" in pf2, \
        "pf W172 freezer prose missing"
    # r776 fragment-needle law: the freezer prose in the n1 entry is split
    # across python-string fragments -- assert the within-fragment shapes
    assert '"W172 A window; W172 freezer MUST re-derive on the "' in n2, "n1 W172 freezer fragment missing"
    assert '"W171 B band 393_004..393_203 will refuse the naive "' in n2, "n1 W171-band refuse fragment missing"
    # 3-item payload honesty faces landed
    assert "payload = seat MSG + pre-seat probe script + probe receipt" + CRLF + \
        "    # (3-item; the W170 finalize product already on origin since r813," in pf2, \
        "pf 3-item payload fixup missing"
    assert '"seat MSG + pre-seat probe script + probe receipt (3-item; the W170 finalize product already on origin since r813, not re-shipped; W146 precedent); "' in n2, \
        "entry 3-item payload fixup missing"
    assert "#     = seat MSG + pre-seat probe script + probe receipt (3-item;" in n2, \
        "mat 3-item payload fixup missing"
    # historical merge citation retained (structure persists; r812 historical)
    assert "single-window derive (r812 merged the gate legs INTO the" in pf2, "pf single-window face missing"
    assert '"--no-verify; single-window derive -- r812 merged the gate "' in n2, "entry single-window frag missing"
    assert "r814 pre-seat" in pf2 and "r814 pre-seat" in n2, "push session r814 face missing"
    assert "direct fast-forward behind-0" in pf2 and "direct fast-forward behind-0" in n2, \
        "direct-FF delivery face missing"
    assert SEAT_SHA in pf2 and SEAT_SHA in n2, "TRUE seat-push sha face missing"
    # r776 fragment law: the registered-row citation is split across python
    # string fragments -- assert the within-fragment shapes
    assert '"number law after the REGISTERED W170 row bm-a r813 freeze "' in n2, \
        "W170 row citation frag missing"
    assert '"cb7314d64, SINGLE STATE zero seat gap W2..W170 all "' in n2, \
        "W170 row citation frag2 missing"
    # r781 fragment law: the W170 finalize one-pass logical string physically
    # splits across python string fragments -- count the within-fragment
    # shapes (mat 1 + entry tail 1 == 2)
    assert n2.count("finalize one-pass bm-a r813") == 2, "W170 finalize one-pass count drift"
    assert "bm-a r813 freeze cb7314d64" in n2, "mat header registered-row citation missing"
    # the NEW W171 claim carries the rolled session attribution
    assert '"r815 bm-a] "' in n2, "W171 claim r815 attribution missing"
    # the healed W171 B-assert jump fragment rides the @JB@ token
    assert "own-wave A window reserved jumps to 393_004, first-clean " in blk2, \
        "W171 healed-fragment face missing"
    assert "own-wave A window reserved jumps to 390_804, first-clean" not in blk2, \
        "vmap-leak residue in new block"
    # no stale round/seat/number leftovers in the NEW W171 blocks only
    i2 = pf2.find("    # W171 (bm-a r815 freeze")
    j2 = pf2.find(EO, i2) + len(EO)
    newpfblk = pf2[i2:j2]
    k2 = n2.find('171: {"batch"')
    m2 = n2.find(EO, k2) + len(EO)
    newentry = n2[k2:m2]
    cs2 = n2.find('"+ W171 materializer face')
    ce2 = n2.find('"r815 bm-a] "', cs2) + len('"r815 bm-a] "')
    newclaim = n2[cs2:ce2]
    ci2 = blk2.find("assert pf.N1_BANDS[138]")
    cj2 = blk2.find("# prior-wave disjointness")
    mat_new_faces = blk2[:ci2] + blk2[cj2:]
    assert i2 > 0 and k2 > 0 and cs2 > 0, "new W171 block anchors missing"
    for tag, seg in (("pf", newpfblk), ("entry", newentry),
                     ("mat", mat_new_faces), ("claim", newclaim)):
        for stale in ("bm-a r811 freeze", "r811 bm-a freeze", "r811 bm-a] ",
                      "r810 gate", "r810 pre-seat", "r812 pre-seat",
                      "r812 bm-a", "r813 bm-a freeze", "r813 bm-a] ",
                      "W168 (bm-a r809", "W169 (bm-a r811", "W170 (bm-a r813",
                      "gate-derived r812", "gate-derived r810",
                      "MSG-2026-10-07-0738", "bma-w170-seat", "MSG-0738",
                      "0f00fa424", "9c2271baf", "2ea58d762",
                      "386_604", "386_404", "388_604", "388_603", "388_403",
                      "388_804..390_803", "388_804..389_003",
                      "777,212", "369,720", "775,012",
                      "twenty-ninth", "twenty-eighth",
                      "ONE HUNDRED-AND-SIXTIETH",
                      "engine_owner rows 159", "rows 85 + candidate",
                      "eighty-fifth",
                      "n1_w170", "n1w170", "n1_w169",
                      "PERPETUAL-N1-W170", "PERPETUAL_N1_W170",
                      "4-item, W146"):
            assert stale not in seg, f"stale {stale!r} residue in new W171 {tag} block"
    # 391_004..393_003 / 393_004..393_203 own-wave faces + prior-wave
    # citations (390_804..391_003 prior-B, 390_804..392_803 naive-A,
    # 391_004..391_203 naive-B) are NOT stale (r787 carve-out note):
    # they legitimately appear in the new W171 blocks as band faces
    for fresh, where in ((f"past the registered W170 B band", "pf"),
                         (f"390_804..392_803 REFUSED at its own start", "pf"),
                         ("REFUSED at its own start by the W170 B band", "pf"),
                         (f"hops=1 -> 391_004..393_003", "pf"),
                         (f"jumps to 393_004 -> 393_004..393_203,", "pf"),
                         ("thirtieth instance, E36 card", "pf"),
                         ("ONE HUNDRED-AND-SIXTY-FIRST", "entry"),
                         (f'"a_seed_base": 391_004,', "entry"),
                         (f'"b_exit_seed_base": 393_004,', "entry"),
                         ("A-hops-prior-B staircase thirtieth", "entry"),
                         ("thirtieth instance, E36 card, hops=1)", "claim"),
                         ("law sec.4 W171 row, ", "claim"),
                         ("bm-a r815 freeze", "pf"),
                         ("r815 bm-a freeze", "mat-new"),
                         ("engine_owner rows 160", "entry"),
                         ("rows 86 + candidate", "claim"),
                         ("eighty-sixth", "claim"),
                         ("wave 170 = first free number after", "mat-new")):
        seg = {"pf": newpfblk, "entry": newentry, "mat-new": mat_new_faces,
               "claim": newclaim}[where]
        assert fresh in seg, f"fresh {fresh!r} missing in new W171 {where} block"
    # corrupted historical faces must remain eradicated from both files
    for path, txt in ((PF, pf2), (N1, n2)):
        assert "362_204..362_003" not in txt and "362_404..360_403" not in txt, \
            f"r772 malformed-window residue in {path}"
    # materializer chain now 138..W170row (n=33)
    w2 = n2.find("# --- W171 materializer face")
    t3 = n2.find("# --- T-141 s2 lane face", w2)
    blk_check = n2[w2:t3]
    chain_rows2 = re.findall(r"assert pf\.N1_BANDS\[(\d+)\]",
                              blk_check[blk_check.find("assert pf.N1_BANDS[138]"):
                                        blk_check.find("# prior-wave disjointness")])
    assert chain_rows2 == [str(x) for x in range(138, 171)], chain_rows2
    # lineage constants disclosed: r795 band-facts stamp + r813 sec8
    # succession retained in the new mat faces
    assert "law sec.4 W171 row, r795" in mat_new_faces, "r795 lineage stamp missing"
    assert "r813 sec8 succession" in mat_new_faces, "r813 sec8 succession citation missing"


if DRY:
    sim_pf = pfsrc.replace(a1, r1n)
    assert sim_pf != pfsrc, "pf simulation no-op"
    sim_n1 = n1src.replace(a2, r2).replace(a3, r3).replace(a4, r4)
    assert sim_n1 != n1src, "n1 simulation no-op"
    ast.parse(sim_pf)
    ast.parse(sim_n1)
    w2 = sim_n1.find("# --- W171 materializer face")
    t3 = sim_n1.find("# --- T-141 s2 lane face", w2)
    blk2 = sim_n1[w2:t3]
    text_asserts(sim_pf, sim_n1, blk2)
    print("DRY-RUN PASS: zero-write simulation -- all stale+prose+AST+"
          "malformed-window+chain asserts green; no file modified")
else:
    # --- apply the four edits ---------------------------------------------------
    edit(PF, [(a1, r1n)])
    edit(N1, [(a2, r2), (a3, r3), (a4, r4)])

    # --- post-edit structural assertions ----------------------------------------
    import importlib
    import perpetual_faces as pf
    importlib.reload(pf)
    assert sorted(pf.N1_BANDS)[-1] == 171 and len(pf.N1_BANDS) == 169, \
        "pf N1_BANDS row-count drift after W171 insert"
    assert pf.N1_BANDS[171] == {"a": (391_004, 393_003),
                                "b_exit": (393_004, 393_203),
                                "engine_owner": "bm-a"}, "W171 row face drift"
    assert pf.N1_BANDS[170] == {"a": (388_804, 390_803),
                                "b_exit": (390_804, 391_003),
                                "engine_owner": "bm-a"}, "W170 row survived (r560 no-replace law)"
    import perpetual_faces_n1 as n1mod
    importlib.reload(n1mod)
    assert n1mod.WAVE_CONFIGS[171]["a_seed_base"] == 391_004 and \
        n1mod.WAVE_CONFIGS[171]["b_exit_seed_base"] == 393_004, "W171 seed bases drift"
    assert n1mod.WAVE_CONFIGS[171]["shard_subdir"] == "n1_w171" and \
        n1mod.WAVE_CONFIGS[171]["out_name"] == "n1_w171_results.json", "W171 path drift"
    assert n1mod.WAVE_CONFIGS[171]["prereg"].startswith("research/PERPETUAL_N1_W171_PREREG.md"), \
        "W171 per-wave prereg citation drift"
    assert os.path.exists(os.path.join("research", "PERPETUAL_N1_W171_PREREG.md")), \
        "W171 per-wave prereg missing on disk"

    pf2 = io.open(PF, encoding="utf-8", newline="").read()
    n2 = io.open(N1, encoding="utf-8", newline="").read()
    w2 = n2.find("# --- W171 materializer face")
    t3 = n2.find("# --- T-141 s2 lane face", w2)
    blk2 = n2[w2:t3]
    text_asserts(pf2, n2, blk2)

    print("post-edit structural assertions PASS: N1_BANDS 169 rows tail W171, "
          "W170 row intact, WAVE_CONFIGS[171] seeded, chain 138..170 n=33, "
          "W172p prose == r814 probe leg4 verbatim, honesty faces landed "
          "(3-item payload fixup; deferred self-ack direction rolled true), "
          "full-file malformed-window scans CLEAN on both files")
