# -*- coding: utf-8 -*-
"""r819 bm-a W172 freeze edits: four insertions (pf N1_BANDS[172] row +
n1 WAVE_CONFIGS[172] entry + n1 W172 materializer block refresh +
n1 PASS snippet claim insertion). DRY flag: --dry = zero-write simulation
(r781 verify-separation law + r811 dry-run precedent: full stale+prose+
AST asserts in memory BEFORE any write).

Bloodline: r815 _r815bma_w171_freeze_edits.py machinery (r773 pit law
freeze-editor compliance + r776 fragment-needle law + r781
verify-separation law), W172 facts live-registry-driven:
  - pre-seat probe results/_r818bma_w172_probe_receipt.json rc0 ADMIT
    (A 393_204..395_203 staircase THIRTY-FIRST instance E36 hops=1 past
    the registered W171 B band 393_004..393_203; naive 393_004..395_003
    refused at its own start by the W171 B band; B 395_204..395_403
    own-A mutual exclusion hops=1, naive 393_204..393_403);
  - face probe results/_r819bma_w172_face_probe_receipt.json rc0 (all
    four W171 faces dumped + needle counts; this TOK is built from the
    PHYSICAL probe-dumped shapes, r776 law);
  - seat MSG-2026-10-07-1012-bma-w172-seat published (r818 seat push
    01a7480e1 machine-derived via git log origin/main -- <path>; r565
    law: on origin BEFORE this freeze commit; seat MSG still in
    fleet/inbox/ at freeze time = honest DEFERRED state (self-ack move
    deferred to the W172 finalize window -- NO direction fixup needed
    this window, the W171-era DEFERRED prose rolls true);
  - 3-item payload truth: the W171-era faces already carry the 3-item
    prose (r815 fixup landed) -- the vmap rolls the composite faces
    (@FWPROD@ W170->W171 finalize product + @SINCER@ r813->r816); no
    FIXUPS dict needed this window;
  - per-wave prereg research/PERPETUAL_N1_W172_PREREG.md (r819 build
    via _r819bma_w172_prereg_build.py, banned gate ADMIT 0);
  - W171 finalize one-pass landed r816: ledger head 781,612, merged
    pool K=374,120 (n1_w171_results.json machine-read); W171 sec7/sec8
    settle backfill landed THIS r819 window (W169 r812+r813 precedent
    law) -- the W172 band-facts cite 'r819 sec8 succession' (the
    r813-citation rolls this window because the cited sec8 succession
    face = W171's, backfilled r819);
  - W171 freeze registered sha machine-derived = 456f3affc (git log
    origin/main --grep "W171 FREEZE");
  - lineage constants disclosed (r795 precedent, passed through):
    (a) the "wave N-1:" entry label + "wave N-1 = first free number"
    mat-header label ride the vmap verbatim (off-by-one lineage quirk
    since the W165 r795 band-facts template); (b) "law sec.4 W172 row,
    r795" band-facts template stamp keeps its r795; (c) "single-window
    derive (r812 merged the gate legs INTO the pre-seat probe..."
    stays (historical merge citation, the structure persists); (d) the
    bm-a-owned ordinal word rolls eighty-sixth -> eighty-seventh (the
    lineage pattern: ordinal word = prior-row count, rows 87 + candidate
    = 88th owned per probe leg0).

r773 pit law compliance:
  (1) full string-face inventory empirically probed BEFORE TOK
      (_r819bma_w172_face_probe.py -- four face dumps + needle-count
      receipt, rc0);
  (2) composite band strings tokenized WHOLE (every dotted band /
      seed-base row / jump phrase / projection pair is a single token;
      bare numerals run LAST);
  (3) post-edit full-file start>end malformed-window regex scan on BOTH
      touched files;
  (4) every projection value re-derived FROM the on-disk probe receipt
      (r587 never-transcribe law);
  (5) r776 fragment-needle law: all needles taken from the PHYSICAL
      probe-dumped shapes (the pf "r814 probe\\r\\n    # leg4" split
      form carried by @GATEPF@ + @LEG3PF@);
  (6) r560 insert-after-last-registered-row + pre-edit live registry
      parity + origin anti-collision pre-check (r530/r687: fetch +
      origin carries no W172 registration before this freeze);
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
probe = json.load(open(r"results/_r818bma_w172_probe_receipt.json", encoding="utf-8"))
assert probe["verdict"] == "ADMIT", probe["verdict"]
assert probe["bands"] == {"A": "393204_395203", "B": "395204_395403"}, probe["bands"]
leg0, leg1 = probe["legs"]["leg0"], probe["legs"]["leg1"]
leg2, leg3, leg4 = probe["legs"]["leg2"], probe["legs"]["leg3"], probe["legs"]["leg4"]
assert leg1["A"] == [393204, 395203] and leg1["B"] == [395204, 395403], leg1
assert leg1["hops_A"] == 1 and leg1["hops_B"] == 1, leg1
assert leg1["ARITH_A"] == [393004, 395003], leg1["ARITH_A"]
assert leg1["ARITH_B"] == [393204, 393403], leg1["ARITH_B"]
assert leg1["B_naive_first_clean"] == [393204, 393403], leg1
assert leg1["B_hop_chain"][0]["jump_to"] == 395204, leg1["B_hop_chain"]
assert leg2["conflicts"] == 0, leg2
assert leg3["origin_vacancy"] is True, leg3
assert leg0["rows"] == 169 and leg0["tail"] == "W171" and leg0["ordinal"] == 162 \
    and leg0["bma_ordinal"] == 88 and leg0["owner_rows"] == 161 \
    and leg0["bma_rows"] == 87 and leg0["w171_ledger_head"] == 781612, leg0
W173p_A = "395_204..397_203"
W173p_B = "395_404..395_603"
assert leg4["W173p_A"] == "395204..397203" and leg4["W173p_B"] == "395404..395603", leg4
assert leg4["hops_A"] == 0 and leg4["hops_B"] == 0, leg4
assert leg4["W173p_B_lands_inside_W173p_A"] is True, leg4
w171res = json.load(open(r"results/perpetual_faces/n1_w171_results.json", encoding="utf-8"))
assert w171res["null_pool_cumulative"]["merged"]["n_values"] == 374120, "W171 merged K drift"
assert w171res["null_pool_cumulative"]["merged"]["n_values"] + 2200 == 376320, \
    "W172 K projection arithmetic"
assert os.path.exists(os.path.join("research", "PERPETUAL_N1_W172_PREREG.md")), \
    "W172 per-wave prereg missing on disk"
_r = subprocess.run(["git", "log", "origin/main", "--format=%h", "--grep=W171 FREEZE", "-1"],
                    capture_output=True, text=True)
W171_SHA = _r.stdout.strip()
assert W171_SHA == "456f3affc", W171_SHA
_r2 = subprocess.run(["git", "log", "origin/main", "--format=%h", "-1", "--",
                      "fleet/inbox/MSG-2026-10-07-1012-bma-w172-seat.md"],
                     capture_output=True, text=True)
SEAT_SHA = _r2.stdout.strip()
assert SEAT_SHA == "01a7480e1", SEAT_SHA
# honesty precondition: the W172 seat MSG sits in fleet/inbox/ at freeze
# time (DEFERRED self-ack state; the mover would be THIS machine at the
# W172 finalize window) -- the rolled W171-era DEFERRED prose rides true.
assert os.path.exists(os.path.join("fleet", "inbox",
                                   "MSG-2026-10-07-1012-bma-w172-seat.md")), \
    "W172 seat MSG not in fleet/inbox/ (DEFERRED prose would be wrong)"
assert not os.path.exists(os.path.join("fleet", "inbox", "processed",
                                       "MSG-2026-10-07-1012-bma-w172-seat.md")), \
    "W172 seat MSG already processed (landed direction would be TRUE -- prose wrong)"


def u(s):
    return re.sub(r"(\d)(?=(\d{3})+$)", r"\1_", s)


# --- ordered value-map (tokens first, then back-substitution) ---------------
TOK = [
    # seat / push / payload carriers (composites FIRST)
    ('MSG-2026-10-07-0843-bma-w171-seat', "@SEAT@"),
    ('3290e586b', "@SEATSHA@"),
    ('r814 pre-seat push', "@PSP@"),
    ('r814 pre-seat', "@PSPPF@"),           # pf split fragment (after @PSP@)
    ('W170 finalize product', "@FWPROD@"),
    ('since r813', "@SINCER@"),              # 3-item face only (after composites)
    # seed-base rows (entry comment face; bands + ordinal carried WHOLE)
    ('"a_seed_base": 391_004,        # law sec.4 W171 A: 391_004..393_003 (FIRST-CLEAN past the registered W170 B band; arithmetic 390_804..392_803 REFUSED at own start by the W170 B band; hops=1; A-hops-prior-B staircase thirtieth instance, E36 card)', "@ASROW@"),
    ('"b_exit_seed_base": 393_004,   # law sec.4 W171 B: 393_004..393_203 (FIRST-CLEAN past the own-wave A window; arithmetic 391_004..391_203 lands inside own-A, same-freeze mutual exclusion W141 precedent; reserved walk hops=1; B base == own-A tail+1)', "@BSROW@"),
    # registered-prior-row citations (machine-verified sha pairing)
    ('W170 row bm-a r813 freeze', "@PROW1@"),
    ('cb7314d64, SINGLE STATE zero seat gap W2..W170 all', "@PROW2@"),
    ('bm-a r813 freeze cb7314d64', "@REGROW@"),
    # freeze-session composites (this window: bm-a r819 freeze)
    ('bm-a r815 freeze', "@FZH@"),
    ('r815 bm-a freeze', "@MFZH@"),
    ('r815 bm-a] ', "@CLMS@"),
    # prior-finalize citations (W171 finalize one-pass r816)
    ('W170 finalize landed same-window r813', "@FW@"),
    ('W170 finalize one-pass bm-a r813', "@FOPW@"),
    ('W170 bm-a r813 one-pass', "@FOP@"),
    ('finalize one-pass bm-a r813', "@FOPM2@"),
    # probe receipt carrier
    ('_r814bma_w171_probe_receipt.json', "@PRC@"),
    ('MSG-0843', "@MSGS@"),
    # gate / projection citations: W171-era W172+ projection faces
    ('r812 probe leg4', "@GATEL3@"),
    ('r812 probe', "@GATEPF@"),              # pf split fragment (after @GATEL3@)
    ('leg4', "@LEG3PF@"),                    # pf split fragment tail
    ('r813 sec8 succession', "@SEC8@"),
    ('W170 seat W171+ projection', "@SEATPROJ@"),
    ('W171+ projection', "@WPN@"),
    ('gate-derived r814', "@GDR@"),
    ('W171 B band 393_004..393_203 will refuse the naive', "@FR0@"),
    ('W172 A window; W172 freezer MUST re-derive on the ', "@FR1@"),
    ('post-W171 universe', "@FR2@"),
    # W173+ projection bands (probe leg4 verbatim, WHOLE; BEFORE all band
    # tokens and seed backstops -- r773 pit law)
    ('393_004..395_003', "@PA@"),
    ('393_204..393_403', "@PB@"),
    # jump phrases (longest first; BEFORE @BB@ which shares the B-band substring)
    ('jumps to 393_004, first-clean 393_004..393_203 hops=1', "@JN@"),
    ('jumps to 393_004 -> 393_004..393_203,', "@JP@"),
    ('393_004 and lands 393_004..393_203', "@JAND@"),
    ('own-wave A window reserved jumps to 393_004, first-clean ', "@JB@"),
    # assert composites
    ('== 391_004 == 391_003 + 1', "@ASB@"),
    ('== 393_004 == 393_003 + 1', "@BSB@"),
    ('set(range(391_004, 393_004))', "@ARITHA@"),
    ('set(range(393_004, 393_204))', "@ARB@"),
    # dotted band geometry
    ('390_804..392_803', "@NA@"),
    ('390_804..391_003', "@OB@"),
    ('391_004..393_003', "@AB@"),
    ('391_004..391_203', "@NB@"),
    ('393_004..393_203', "@BB@"),
    # base-relation composites
    ('391_003+1', "@ABASE@"),
    ('393_003+1', "@BBASE@"),
    # identity / stats / ordinals
    ('PERPETUAL_N1_W171_PREREG.md', "@PF@"),
    ('PERPETUAL-N1-W171', "@B@"),
    ('n1_w171_results.json', "@OD@"),
    ('n1_w171', "@SD@"),
    ('n1w171', "@SD2@"),
    ('779,412', "@LEDG@"),
    ('371,920', "@KOLD@"),
    ('ONE HUNDRED-AND-SIXTY-FIRST', "@ORDW@"),
    ('engine_owner rows 160', "@R154@"),
    ('rows 86 + candidate', "@ROWS80@"),
    ('eighty-sixth', "@SVN@"),
    ('thirtieth', "@ST24@"),
    ('W17..W170', "@W17TO@"),
    ('W2..W170', "@W2TO@"),
    ('W1..W170', "@W1TO@"),
    ('range(17, 171)', "@DEPW@"),
    ('range(16, 171)', "@R16@"),
    ('w < 171', "@WPREV@"),
    ('171: {"a": (391_004, 393_003), "b_exit": (393_004, 393_203),', "@RROW@"),
    ('171: {"batch"', "@RENTRY@"),
    # wave numbers (higher first: W172 projection -> W173; then W171->W172,
    # W170->W171)
    ('W172', "@WN2@"),
    ('W171', "@WN@"),
    ('W170', "@W@"),
    # bare numerals LAST
    ('171', "@IDX@"),
    ('170', "@IDX2@"),
]
BACK = [
    ("@SEAT@", "MSG-2026-10-07-1012-bma-w172-seat"),
    ("@SEATSHA@", SEAT_SHA),
    ("@PSP@", "r818 pre-seat push"),
    ("@PSPPF@", "r818 pre-seat"),
    ("@FWPROD@", "W171 finalize product"),
    ("@SINCER@", "since r816"),
    ("@ASROW@", '"a_seed_base": 393_204,        # law sec.4 W172 A: 393_204..395_203 (FIRST-CLEAN past the registered W171 B band; arithmetic 393_004..395_003 REFUSED at own start by the W171 B band; hops=1; A-hops-prior-B staircase thirty-first instance, E36 card)'),
    ("@BSROW@", '"b_exit_seed_base": 395_204,   # law sec.4 W172 B: 395_204..395_403 (FIRST-CLEAN past the own-wave A window; arithmetic 393_204..393_403 lands inside own-A, same-freeze mutual exclusion W141 precedent; reserved walk hops=1; B base == own-A tail+1)'),
    ("@PROW1@", "W171 row bm-a r815 freeze"),
    ("@PROW2@", "456f3affc, SINGLE STATE zero seat gap W2..W171 all"),
    ("@REGROW@", "bm-a r815 freeze 456f3affc"),
    ("@FZH@", "bm-a r819 freeze"),
    ("@MFZH@", "r819 bm-a freeze"),
    ("@CLMS@", "r819 bm-a] "),
    ("@FW@", "W171 finalize landed same-window r816"),
    ("@FOPW@", "W171 finalize one-pass bm-a r816"),
    ("@FOP@", "W171 bm-a r816 one-pass"),
    ("@FOPM2@", "finalize one-pass bm-a r816"),
    ("@PRC@", "_r818bma_w172_probe_receipt.json"),
    ("@MSGS@", "MSG-1012"),
    ("@GATEL3@", "r814 probe leg4"),
    ("@GATEPF@", "r814 probe"),
    ("@LEG3PF@", "leg4"),
    ("@SEC8@", "r819 sec8 succession"),
    ("@SEATPROJ@", "W171 seat W172+ projection"),
    ("@WPN@", "W172+ projection"),
    ("@GDR@", "gate-derived r818"),
    ("@FR0@", "W172 B band 395_204..395_403 will refuse the naive"),
    ("@FR1@", "W173 A window; W173 freezer MUST re-derive on the "),
    ("@FR2@", "post-W172 universe"),
    ("@PA@", W173p_A),
    ("@PB@", W173p_B),
    ("@JN@", "jumps to 395_204, first-clean 395_204..395_403 hops=1"),
    ("@JP@", "jumps to 395_204 -> 395_204..395_403,"),
    ("@JAND@", "395_204 and lands 395_204..395_403"),
    ("@JB@", "own-wave A window reserved jumps to 395_204, first-clean "),
    ("@ASB@", "== 393_204 == 393_203 + 1"),
    ("@BSB@", "== 395_204 == 395_203 + 1"),
    ("@ARITHA@", "set(range(393_204, 395_204))"),
    ("@ARB@", "set(range(395_204, 395_404))"),
    ("@NA@", "393_004..395_003"),
    ("@OB@", "393_004..393_203"),
    ("@AB@", "393_204..395_203"),
    ("@NB@", "393_204..393_403"),
    ("@BB@", "395_204..395_403"),
    ("@ABASE@", "393_203+1"),
    ("@BBASE@", "395_203+1"),
    ("@PF@", "PERPETUAL_N1_W172_PREREG.md"),
    ("@B@", "PERPETUAL-N1-W172"),
    ("@OD@", "n1_w172_results.json"),
    ("@SD@", "n1_w172"),
    ("@SD2@", "n1w172"),
    ("@LEDG@", "781,612"),
    ("@KOLD@", "374,120"),
    ("@ORDW@", "ONE HUNDRED-AND-SIXTY-SECOND"),
    ("@R154@", "engine_owner rows 161"),
    ("@ROWS80@", "rows 87 + candidate"),
    ("@SVN@", "eighty-seventh"),
    ("@ST24@", "thirty-first"),
    ("@W17TO@", "W17..W171"),
    ("@W2TO@", "W2..W171"),
    ("@W1TO@", "W1..W171"),
    ("@DEPW@", "range(17, 172)"),
    ("@R16@", "range(16, 172)"),
    ("@WPREV@", "w < 172"),
    ("@RROW@", '172: {"a": (393_204, 395_203), "b_exit": (395_204, 395_403),'),
    ("@RENTRY@", '172: {"batch"'),
    ("@WN2@", "W173"),
    ("@WN@", "W172"),
    ("@W@", "W171"),
    ("@IDX@", "172"),
    ("@IDX2@", "171"),
]
# r587 belt-and-braces: the projection BACK values equal probe leg4 verbatim
assert ("@PA@", W173p_A) in BACK and ("@PB@", W173p_B) in BACK

# per-face expected TOK counts (from the r819 face-probe receipt; r745 law)
FCOUNT = {
    "pf": {"@WN@": None, "@W@": None, "@ASROW@": 0, "@BSROW@": 0,
           "@SEAT@": 1, "@SEATSHA@": 1, "@PSP@": 0, "@PSPPF@": 2, "@FWPROD@": 1,
           "@SINCER@": 1, "@SEC8@": 1,
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
              "@SINCER@": 1, "@SEC8@": 2,
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
            "@SEAT@": 1, "@SEATSHA@": 1, "@PSP@": 1, "@PSPPF@": 0, "@FWPROD@": 1,
            "@SINCER@": 1, "@SEC8@": 2,
            "@SEATPROJ@": 3, "@WPN@": 0, "@GDR@": 0, "@GATEL3@": 3, "@GATEPF@": 0,
            "@LEG3PF@": 0, "@FR0@": 0, "@FR1@": 0, "@FR2@": 0, "@PA@": 0,
            "@PB@": 0, "@JN@": 0, "@JP@": 0, "@JAND@": 1, "@JB@": 1, "@ASB@": 1,
            "@BSB@": 1, "@ARITHA@": 1, "@ARB@": 1, "@NA@": 2, "@OB@": 2,
            "@AB@": 1, "@NB@": 2, "@BB@": 0, "@ABASE@": 2, "@BBASE@": 2,
            "@PF@": 1, "@B@": 2, "@OD@": 1, "@SD@": 1, "@SD2@": 2, "@LEDG@": 2,
            "@KOLD@": 1, "@ORDW@": 1, "@R154@": 1, "@ROWS80@": 1, "@SVN@": 1,
            "@ST24@": 2, "@W17TO@": 1, "@W2TO@": 4, "@W1TO@": 1, "@DEPW@": 1,
            "@R16@": 1, "@WPREV@": 3, "@RROW@": 0, "@RENTRY@": 0, "@WN2@": 0,
            "@IDX@": 10, "@IDX2@": 25, "@MSGS@": 1, "@FW@": 0, "@FOPW@": 1, "@FOP@": 1,
            "@FOPM2@": 0, "@PRC@": 1, "@PROW1@": 0, "@PROW2@": 0, "@REGROW@": 1,
            "@FZH@": 0, "@MFZH@": 1, "@CLMS@": 0},
    "claim": {"@WN@": None, "@W@": None, "@ASROW@": 0, "@BSROW@": 0,
              "@SEAT@": 0, "@SEATSHA@": 0, "@PSP@": 0, "@PSPPF@": 0, "@FWPROD@": 0,
              "@SINCER@": 0, "@SEC8@": 0,
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

# face-source zero-drift gate vs the r819 probe dumps
EO = '"engine_owner": "bm-a"},'
i1 = pfsrc.find("    # W171 (bm-a r815 freeze")
assert i1 > 0, "pf W171 comment block not found"
r1 = pfsrc.find('171: {"a": (391_004', i1)
assert r1 > i1, "pf W171 row not after comment block"
j1 = pfsrc.find(EO, r1) + len(EO)
block171_pf = pfsrc[i1:j1]
assert block171_pf == io.open(r"results\_r819bma_w172_probe_pf_block.txt",
                             encoding="utf-8", newline="").read(), "pf face drift vs probe"
assert block171_pf.count("engine_owner") == 1 and "456f3affc" not in block171_pf

# pre-edit live registry parity (the W171 registered row must be intact
# before we append the W172 row -- r560 no-replace law)
sys.path.insert(0, ".")
sys.path.insert(0, "scripts")
import perpetual_faces as pfpre
assert pfpre.N1_BANDS[171] == {"a": (391_004, 393_003),
                               "b_exit": (393_004, 393_203),
                               "engine_owner": "bm-a"}, "pre-edit W171 row drift"
assert sorted(pfpre.N1_BANDS)[-1] == 171 and len(pfpre.N1_BANDS) == 169, "pre-edit row count"

# origin anti-collision pre-check (r530 never-dry + r687 dual-scan:
# fetch fresh, origin must carry no W172 registration before this freeze)
subprocess.run(["git", "fetch", "origin"], capture_output=True)
_r = subprocess.run(["git", "show", "origin/main:scripts/perpetual_faces.py"],
                    capture_output=True)
_op = _r.stdout.decode("utf-8", "replace")
assert _r.returncode == 0, "origin pf.py read failed"
assert '172: {"a"' not in _op, "origin already carries a W172 registration (r687 dual-scan)"
assert "# W172 (bm-a" not in _op, "origin already carries a W172 freeze block"
_r2 = subprocess.run(["git", "rev-list", "--count", "origin/main..HEAD"],
                    capture_output=True, text=True)
assert _r2.stdout.strip() == "0", f"local ahead of origin: {_r2.stdout.strip()} (behind-law)"
# seat-on-origin precondition (r565 law: seat published BEFORE this freeze)
_r3 = subprocess.run(["git", "show", "origin/main:fleet/inbox/MSG-2026-10-07-1012-bma-w172-seat.md"],
                    capture_output=True)
assert _r3.returncode == 0, "W172 seat MSG not on origin (r565 pre-freeze law)"

# --- a1: pf.py W171 comment block + row -> append W172 comment block + row ----
a1 = block171_pf + CRLF + "}"
r1n = block171_pf + CRLF + vmap(block171_pf, "pf") + CRLF + "}"

# --- a2: n1.py WAVE_CONFIGS entry ----------------------------------------------
k = n1src.find('171: {"batch"')
assert k > 0, "n1 W171 entry not found"
m = n1src.find(EO, k) + len(EO)
entry171 = n1src[k:m]
assert entry171 == io.open(r"results\_r819bma_w172_probe_n1_entry.txt",
                           encoding="utf-8", newline="").read(), "entry face drift vs probe"
a2 = entry171 + CRLF + "                       }"
r2 = entry171 + CRLF + "                       " + vmap(entry171, "entry") + CRLF + "                       }"

# --- a3: materializer block (chain split-verbatim + one-row extension) --------
w = n1src.find("# --- W171 materializer face")
t2 = n1src.find("# --- T-141 s2 lane face", w)
assert 0 < w < t2, "materializer anchors missing"
block = n1src[w:t2]
assert block == io.open(r"results\_r819bma_w172_probe_n1_mat.txt",
                        encoding="utf-8", newline="").read(), "mat face drift vs probe"
ci = block.find("assert pf.N1_BANDS[138]")
cj = block.find("# prior-wave disjointness")
assert 0 < ci < cj, "chain boundaries missing"
pre, chain, post = block[:ci], block[ci:cj], block[cj:]
chain_rows = re.findall(r"assert pf\.N1_BANDS\[(\d+)\]", chain)
assert chain_rows == [str(x) for x in range(138, 171)], chain_rows
w171row = ('assert pf.N1_BANDS[171] == {"a": (391_004, 393_003),' + CRLF +
           '                                    "b_exit": (393_004, 393_203),' + CRLF +
           '                                    "engine_owner": "bm-a"}, \\' + CRLF +
           '            "registered W171 row parity drift (r307; bm-a r815)"' + CRLF +
           "        ")
block172 = vmap(pre, "mat") + chain + w171row + vmap(post, "mat")
a3 = block + "# --- T-141 s2 lane face"
r3 = block172 + "# --- T-141 s2 lane face"

# --- a4: PASS snippet claim insertion ------------------------------------------
cs = n1src.find('"+ W171 materializer face')
assert cs > 0, "W171 claim start not found"
ce = n1src.find('"r815 bm-a] "', cs) + len('"r815 bm-a] "')
assert 0 < cs < ce, "W171 claim end not found"
claim171 = n1src[cs:ce]
assert claim171 == io.open(r"results\_r819bma_w172_probe_n1_claim.txt",
                           encoding="utf-8", newline="").read(), "claim face drift vs probe"
a4 = '"r815 bm-a] "' + CRLF + '          "+ T-141 s2 "'
r4 = '"r815 bm-a] "' + CRLF + "          " + vmap(claim171, "claim") + CRLF + '          "+ T-141 s2 "'


# --- text-level assertions (shared by dry-run and apply) ----------------------
def text_asserts(pf2: str, n2: str, blk2: str):
    # r773 pit law leg 3: full-file start>end malformed-window scans
    for path, txt in ((PF, pf2), (N1, n2)):
        bad = [mm.group() for mm in re.finditer(r"(\d{3})_(\d{3})\.\.(\d{3})_(\d{3})", txt)
               if int(mm.group(3)) < int(mm.group(1))]
        assert not bad, f"malformed windows remain in {path}: {bad[:4]}"
    # W173 projection prose present in the new W172 blocks (probe leg4 verbatim;
    # the projection HEAD is "W172+ projection" = this block's next-wave face)
    assert "# W172+ projection (gate-derived r818)" in pf2, "pf W172+ projection head missing"
    assert 'probe_receipt.json; W172+ projection "' in n2, "n1 W172+ projection head fragment missing"
    assert f"# {W173p_A} CLEAN hops=0 / B first-clean {W173p_B}" in pf2, "pf W173p prose missing"
    assert f"A first-clean {W173p_A} " in n2 and f"B first-clean {W173p_B} CLEAN" in n2, \
        "n1 W173p prose missing"
    assert "W173 A window; W173 freezer MUST re-derive on the post-W172" in pf2, \
        "pf W173 freezer prose missing"
    # r776 fragment-needle law: the freezer prose in the n1 entry is split
    # across python-string fragments -- assert the within-fragment shapes
    assert '"W173 A window; W173 freezer MUST re-derive on the "' in n2, "n1 W173 freezer fragment missing"
    assert '"W172 B band 395_204..395_403 will refuse the naive "' in n2, "n1 W172-band refuse fragment missing"
    # 3-item payload faces landed (rolled via @FWPROD@/@SINCER@; no FIXUPS this window)
    assert "payload = seat MSG + pre-seat probe script + probe receipt" + CRLF + \
        "    # (3-item; the W171 finalize product already on origin since r816," in pf2, \
        "pf 3-item payload face missing"
    assert '"seat MSG + pre-seat probe script + probe receipt (3-item; the W171 finalize product already on origin since r816, not re-shipped; W146 precedent); "' in n2, \
        "entry 3-item payload face missing"
    assert "#     = seat MSG + pre-seat probe script + probe receipt (3-item;" in n2, \
        "mat 3-item payload face missing"
    # historical merge citation retained (structure persists; r812 historical)
    assert "single-window derive (r812 merged the gate legs INTO the" in pf2, "pf single-window face missing"
    assert '"--no-verify; single-window derive -- r812 merged the gate "' in n2, "entry single-window frag missing"
    assert "r818 pre-seat" in pf2 and "r818 pre-seat" in n2, "push session r818 face missing"
    assert "direct fast-forward behind-0" in pf2 and "direct fast-forward behind-0" in n2, \
        "direct-FF delivery face missing"
    assert SEAT_SHA in pf2 and SEAT_SHA in n2, "TRUE seat-push sha face missing"
    # r776 fragment law: the registered-row citation is split across python
    # string fragments -- assert the within-fragment shapes
    assert '"number law after the REGISTERED W171 row bm-a r815 freeze "' in n2, \
        "W171 row citation frag missing"
    assert '"456f3affc, SINGLE STATE zero seat gap W2..W171 all "' in n2, \
        "W171 row citation frag2 missing"
    # r781 fragment law: the W171 finalize one-pass logical string physically
    # splits across python string fragments -- count the within-fragment
    # shapes (mat 1 + entry tail 1 == 2)
    assert n2.count("finalize one-pass bm-a r816") == 2, "W171 finalize one-pass count drift"
    assert "bm-a r815 freeze 456f3affc" in n2, "mat header registered-row citation missing"
    # the NEW W172 claim carries the rolled session attribution
    assert '"r819 bm-a] "' in n2, "W172 claim r819 attribution missing"
    # the healed W172 B-assert jump fragment rides the @JB@ token
    assert "own-wave A window reserved jumps to 395_204, first-clean " in blk2, \
        "W172 healed-fragment face missing"
    assert "own-wave A window reserved jumps to 393_004, first-clean" not in blk2, \
        "vmap-leak residue in new block"
    # no stale round/seat/number leftovers in the NEW W172 blocks only
    i2 = pf2.find("    # W172 (bm-a r819 freeze")
    j2 = pf2.find(EO, i2) + len(EO)
    newpfblk = pf2[i2:j2]
    k2 = n2.find('172: {"batch"')
    m2 = n2.find(EO, k2) + len(EO)
    newentry = n2[k2:m2]
    cs2 = n2.find('"+ W172 materializer face')
    ce2 = n2.find('"r819 bm-a] "', cs2) + len('"r819 bm-a] "')
    newclaim = n2[cs2:ce2]
    ci2 = blk2.find("assert pf.N1_BANDS[138]")
    cj2 = blk2.find("# prior-wave disjointness")
    mat_new_faces = blk2[:ci2] + blk2[cj2:]
    assert i2 > 0 and k2 > 0 and cs2 > 0, "new W172 block anchors missing"
    for tag, seg in (("pf", newpfblk), ("entry", newentry),
                     ("mat", mat_new_faces), ("claim", newclaim)):
        for stale in ("r815 bm-a freeze", "r815 bm-a] ",
                      "r813 sec8 succession", "r814 pre-seat", "r814 pre-seat push",
                      "r812 probe", "r812 probe leg4",
                      "gate-derived r814",
                      "MSG-2026-10-07-0843", "bma-w171-seat", "MSG-0843",
                      "3290e586b", "cb7314d64", "456f3affc" if False else "cb7314d64",
                      "391_004", "391_003", "390_804",
                      "391_004..393_003", "391_004..391_203",
                      "390_804..392_803", "390_804..391_003",
                      "781,612" if False else "779,412", "371,920",
                      "thirtieth", "twenty-ninth",
                      "ONE HUNDRED-AND-SIXTY-FIRST",
                      "engine_owner rows 160", "rows 86 + candidate",
                      "eighty-sixth",
                      "n1_w171", "n1w171", "n1_w170",
                      "PERPETUAL-N1-W171", "PERPETUAL_N1_W171",
                      "since r813", "W170 finalize product",
                      "W170 seat W171+ projection", "W171+ projection",
                      "W17..W170", "W2..W170", "W1..W170",
                      "range(17, 171)", "range(16, 171)", "w < 171"):
            assert stale not in seg, f"stale {stale!r} residue in new W172 {tag} block"
    # 393_204..395_203 / 395_204..395_403 own-wave faces + prior-wave
    # citations (393_004..393_203 prior-B, 393_004..395_003 naive-A,
    # 393_204..393_403 naive-B) are NOT stale (r787 carve-out note):
    # they legitimately appear in the new W172 blocks as band faces
    for fresh, where in (("past the registered W171 B band", "pf"),
                         ("393_004..395_003 REFUSED at its own start", "pf"),
                         ("REFUSED at its own start by the W171 B band", "pf"),
                         ("hops=1 -> 393_204..395_203", "pf"),
                         ("jumps to 395_204 -> 395_204..395_403,", "pf"),
                         ("thirty-first instance, E36 card", "pf"),
                         ("ONE HUNDRED-AND-SIXTY-SECOND", "entry"),
                         ('"a_seed_base": 393_204,', "entry"),
                         ('"b_exit_seed_base": 395_204,', "entry"),
                         ("A-hops-prior-B staircase thirty-first", "entry"),
                         ("thirty-first instance, E36 card, hops=1)", "claim"),
                         ("law sec.4 W172 row, ", "claim"),
                         ("bm-a r819 freeze", "pf"),
                         ("r819 bm-a freeze", "mat-new"),
                         ("engine_owner rows 161", "entry"),
                         ("rows 87 + candidate", "claim"),
                         ("eighty-seventh", "claim"),
                         ("wave 171 = first free number after", "mat-new")):
        seg = {"pf": newpfblk, "entry": newentry, "mat-new": mat_new_faces,
               "claim": newclaim}[where]
        assert fresh in seg, f"fresh {fresh!r} missing in new W172 {where} block"
    # corrupted historical faces must remain eradicated from both files
    for path, txt in ((PF, pf2), (N1, n2)):
        assert "362_204..362_003" not in txt and "362_404..360_403" not in txt, \
            f"r772 malformed-window residue in {path}"
    # materializer chain now 138..W171row (n=34)
    w2 = n2.find("# --- W172 materializer face")
    t3 = n2.find("# --- T-141 s2 lane face", w2)
    blk_check = n2[w2:t3]
    chain_rows2 = re.findall(r"assert pf\.N1_BANDS\[(\d+)\]",
                              blk_check[blk_check.find("assert pf.N1_BANDS[138]"):
                                        blk_check.find("# prior-wave disjointness")])
    assert chain_rows2 == [str(x) for x in range(138, 172)], chain_rows2
    # lineage constants disclosed: r795 band-facts stamp + sec8
    # succession citation (r819 settle, this window) in the new mat faces
    assert "law sec.4 W172 row, r795" in mat_new_faces, "r795 lineage stamp missing"
    assert "r819 sec8 succession" in mat_new_faces, "r819 sec8 succession citation missing"
    # W172 claim K/ledger rolled faces (r781 fragment law: the ledger/K
    # logical string physically splits across python string fragments --
    # assert the within-fragment shapes)
    assert "net chain head 781,612 = " in newclaim and \
        "W171 bm-a r816 one-pass, K=374,120 merged pool" in newclaim, \
        "W172 claim ledger/K face missing"


if DRY:
    sim_pf = pfsrc.replace(a1, r1n)
    assert sim_pf != pfsrc, "pf simulation no-op"
    sim_n1 = n1src.replace(a2, r2).replace(a3, r3).replace(a4, r4)
    assert sim_n1 != n1src, "n1 simulation no-op"
    ast.parse(sim_pf)
    ast.parse(sim_n1)
    w2 = sim_n1.find("# --- W172 materializer face")
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
    assert sorted(pf.N1_BANDS)[-1] == 172 and len(pf.N1_BANDS) == 170, \
        "pf N1_BANDS row-count drift after W172 insert"
    assert pf.N1_BANDS[172] == {"a": (393_204, 395_203),
                                "b_exit": (395_204, 395_403),
                                "engine_owner": "bm-a"}, "W172 row face drift"
    assert pf.N1_BANDS[171] == {"a": (391_004, 393_003),
                                "b_exit": (393_004, 393_203),
                                "engine_owner": "bm-a"}, "W171 row survived (r560 no-replace law)"
    import perpetual_faces_n1 as n1mod
    importlib.reload(n1mod)
    assert n1mod.WAVE_CONFIGS[172]["a_seed_base"] == 393_204 and \
        n1mod.WAVE_CONFIGS[172]["b_exit_seed_base"] == 395_204, "W172 seed bases drift"
    assert n1mod.WAVE_CONFIGS[172]["shard_subdir"] == "n1_w172" and \
        n1mod.WAVE_CONFIGS[172]["out_name"] == "n1_w172_results.json", "W172 path drift"
    assert n1mod.WAVE_CONFIGS[172]["prereg"].startswith("research/PERPETUAL_N1_W172_PREREG.md"), \
        "W172 per-wave prereg citation drift"
    assert os.path.exists(os.path.join("research", "PERPETUAL_N1_W172_PREREG.md")), \
        "W172 per-wave prereg missing on disk"

    pf2 = io.open(PF, encoding="utf-8", newline="").read()
    n2 = io.open(N1, encoding="utf-8", newline="").read()
    w2 = n2.find("# --- W172 materializer face")
    t3 = n2.find("# --- T-141 s2 lane face", w2)
    blk2 = n2[w2:t3]
    text_asserts(pf2, n2, blk2)

    print("post-edit structural assertions PASS: N1_BANDS 170 rows tail W172, "
          "W171 row intact, WAVE_CONFIGS[172] seeded, chain 138..171 n=34, "
          "W173p prose == r818 probe leg4 verbatim, honesty faces landed "
          "(3-item payload rolled via vmap; deferred self-ack direction rolled true), "
          "full-file malformed-window scans CLEAN on both files")
