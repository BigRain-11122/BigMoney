# -*- coding: utf-8 -*-
"""r963 bm-a W205 five-face freeze (CEO fill-order RE-ISSUE
O-20261010-2350-bm-c critical path). See module docstring in the
dry-run predecessor; measured-count edition (token inventory
machine-measured 2026-10-10 23:5x)."""
import ast
import json
import os
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
N1P = os.path.join(ROOT, "scripts", "perpetual_faces_n1.py")
PFP = os.path.join(ROOT, "scripts", "perpetual_faces.py")
PREREG_SRC = os.path.join(ROOT, "research", "PERPETUAL_N1_W204_PREREG.md")
PREREG_DST = os.path.join(ROOT, "research", "PERPETUAL_N1_W205_PREREG.md")
RCPT = os.path.join(ROOT, "results", "_r956bma_w205_probe_receipt.json")
OUT_RCPT = os.path.join(ROOT, "results", "_r963bma_w205_freeze_receipt.json")
SEAT_PROCESSED = "fleet/inbox/processed/MSG-2026-10-10-1627-bma-w205-seat.md"
SEAT_SHA = "63b5bd3dd56a011317771c98a9b661242c0d52de"
W204_SHA = "2c8ef33c8"
CNW = getattr(subprocess, "CREATE_NO_WINDOW", 0)
WRITE = "--write" in sys.argv
fails = []


def git_out(args):
    p = subprocess.run([r"C:\Program Files\Git\cmd\git.exe", "-C", ROOT]
                       + args, capture_output=True, creationflags=CNW)
    return (p.returncode, p.stdout.decode("utf-8", "replace"),
            p.stderr.decode("utf-8", "replace"))


def rep(text, old, new, expect, tag):
    n = text.count(old)
    if n != expect:
        fails.append("COUNT MISMATCH [%s]: got %d expect %d literal=%r"
                     % (tag, n, expect, old[:70]))
        return text
    return text.replace(old, new)


def chunk(text, start, end, stag):
    i = text.find(start)
    assert i >= 0, "start not found [%s]" % stag
    j = text.find(end, i)
    assert j > i, "end not found [%s]" % stag
    return text[i:j + len(end)]


def main():
    facts = {"round": 963, "machine": "bm-a", "wave": 205}

    # ---- G0 idempotence ----
    pf_probe = open(PFP, encoding="utf-8", errors="replace").read()
    if '205: {"a": (465_804' in pf_probe:
        print("ALREADY APPLIED: W205 pf row present -- abort")
        return 3
    if os.path.exists(PREREG_DST):
        print("ALREADY APPLIED: W205 prereg present -- abort")
        return 3

    # ---- G1 fetch + origin vacancy + seat/W204 ancestors ----
    rc, _, err = git_out(["fetch", "origin"])
    assert rc == 0, "fetch failed: %s" % err[:200]
    rc, origin_pf, err = git_out(["show", "origin/main:scripts/perpetual_faces.py"])
    assert rc == 0, "origin pf read failed"
    assert '205: {"a": (465_804' not in origin_pf, "ORIGIN TAIL MOVED: W205 on origin"
    assert '204: {"a": (463_604, 465_603), "b_exit": (465_604, 465_803),' in origin_pf, \
        "origin W204 row drift"
    rc, origin_n1, _ = git_out(["show", "origin/main:scripts/perpetual_faces_n1.py"])
    assert rc == 0
    assert "# --- W205 materializer face" not in origin_n1
    rc, _, _ = git_out(["show", "origin/main:research/PERPETUAL_N1_W205_PREREG.md"])
    assert rc != 0, "ORIGIN W205 prereg already present"
    rc, _, _ = git_out(["merge-base", "--is-ancestor", SEAT_SHA, "origin/main"])
    assert rc == 0, "seat push not an ancestor of origin/main"
    rc, _, _ = git_out(["merge-base", "--is-ancestor", W204_SHA, "origin/main"])
    assert rc == 0, "W204 freeze not an ancestor of origin/main"

    # ---- G2 probe receipt parity ----
    r = json.load(open(RCPT, encoding="utf-8"))
    assert r["verdict"] == "ADMIT"
    leg1 = r["legs"]["leg1"]
    assert leg1["A"] == [465804, 467803] and leg1["B"] == [467804, 468003]
    assert leg1["hops_A"] == 1 and leg1["hops_B"] == 1
    assert leg1["ARITH_A"] == [465604, 467603] and \
        leg1["ARITH_B"] == [465804, 466003]
    assert "SIXTY-FIFTH" in leg1["A_semantics"]
    leg0 = r["legs"]["leg0"]
    assert leg0["rows"] == 201 and leg0["tail"] == "W203"
    assert leg0["ordinal"] == 195 and leg0["bma_ordinal"] == 119
    assert leg0["owner_rows"] == 193 and leg0["bma_rows"] == 118
    assert r["legs"]["leg3"]["origin_vacancy"] is True
    leg4 = r["legs"]["leg4"]
    assert leg4["W206p_A"] == "467804_469803" and \
        leg4["W206p_B"] == "468004_468203"
    facts["receipt"] = "ADMIT parity OK"

    # ---- G2b W204-state guard FIRED: freeze-time re-verify ----
    sys.path.insert(0, os.path.join(ROOT, "scripts"))
    from perpetual_faces import N1_BANDS  # noqa: E402
    assert max(N1_BANDS) == 204 and len(N1_BANDS) == 202
    assert N1_BANDS[204] == {"a": (463604, 465603),
                            "b_exit": (465604, 465803),
                            "engine_owner": "bm-c"}
    assert N1_BANDS[203] == {"a": (461404, 463403),
                            "b_exit": (463404, 463603),
                            "engine_owner": "bm-a"}
    owners = {}
    for w, c in N1_BANDS.items():
        owners[c.get("engine_owner")] = owners.get(c.get("engine_owner"), 0) + 1
    assert owners.get("bm-a") == 118 and owners.get("bm-c") == 36 \
        and owners.get("bm-b") == 40 and owners.get(None) == 8 \
        and len(N1_BANDS) == 202
    fin = json.load(open(os.path.join(
        ROOT, "results", "perpetual_faces", "n1_w204_results.json"),
        encoding="utf-8"))
    assert fin["audit"] == {"machine": "bm-c", "finalize_only": True}
    assert fin["null_pool_cumulative"]["merged"]["n_values"] == 446720
    sk = fin["skill_line_v2_k_lift"]
    assert sk["line_pre_w204"] == 1.1888 and \
        sk["line_merged_446720"] == 1.1887 and \
        sk["line_delta_k_lift"] == -0.0001
    facts["w204_guard"] = {"rows": len(N1_BANDS), "tail": "W204",
                           "anchor_total": 864387, "anchor_K": 446720}
    assert os.path.exists(os.path.join(ROOT, SEAT_PROCESSED)), \
        "seat MSG not in processed/"
    w206_face = None
    for cand in ("fleet/inbox/MSG-20261010-2323-bmc-w206-seat.md",
                 "fleet/inbox/processed/MSG-20261010-2323-bmc-w206-seat.md"):
        if os.path.exists(os.path.join(ROOT, cand)):
            w206_face = cand
            break
    if w206_face:
        t206 = open(os.path.join(ROOT, w206_face), encoding="utf-8",
                    errors="replace").read()
        m = re.search(r"A (\d{3}_\d{3})\.\.(\d{3}_\d{3})", t206)
        if m:
            a0 = int(m.group(1).replace("_", ""))
            assert a0 >= 468004, "W206 declared A overlaps W205 B: %s" % m.group(0)
            facts["w206_declared_disjoint"] = True
    else:
        facts["w206_declared_disjoint"] = "seat-msg-not-local"

    # ---- G3 EOL detect ----
    n1_raw = open(N1P, encoding="utf-8", errors="replace", newline="").read()
    pf_raw = open(PFP, encoding="utf-8", errors="replace", newline="").read()
    n1_crlf = n1_raw.count("\r\n") > n1_raw.count("\n") / 2
    pf_crlf = pf_raw.count("\r\n") > pf_raw.count("\n") / 2
    n1n = n1_raw.replace("\r\n", "\n")
    pfn = pf_raw.replace("\r\n", "\n")
    facts["eol"] = {"n1_crlf": n1_crlf, "pf_crlf": pf_crlf}

    # ---- G4 extract live W204 fragments ----
    pf204 = chunk(pfn, "# W204 (bm-c r837 five-face freeze phase-2 splice rebuild",
                 '"engine_owner": "bm-c"},', "pf204")
    assert pfn.count(pf204) == 1
    cfg204 = chunk(n1n, '204: {"batch": "PERPETUAL-N1-W204",',
                  '"engine_owner": "bm-c"},', "cfg204")
    assert n1n.count(cfg204) == 1
    mat_start = n1n.find("    # --- W204 materializer face")
    t141 = n1n.find("    # --- T-141 s2 lane face", mat_start)
    assert mat_start >= 0 and t141 > mat_start
    mat204_full = n1n[mat_start:t141]
    assert mat204_full.rstrip("\n").endswith("_set_wave(2)")
    mat204 = mat204_full.rstrip("\n")
    assert n1n.count(mat204) == 1
    claim204 = chunk(n1n, '"+ W204 materializer face [same guard set',
                     '"r837 bm-c] "', "claim204")
    assert n1n.count(claim204) == 1
    facts["frag_sizes"] = {"pf": len(pf204), "cfg": len(cfg204),
                           "mat": len(mat204), "claim": len(claim204)}

    # ---- G5 mat205 ----
    ci = mat204.find("_set_wave(204)")
    ci = mat204.rfind("\n", 0, ci) + 1  # keep line-start indent
    body204 = mat204[ci:]
    comment205 = """    # --- W205 materializer face (r963 bm-a five-face freeze under CEO
    #     fill-order RE-ISSUE O-20261010-2350-bm-c critical path +
    #     O-20260924-1730 claim-and-start same-round law): bm-a's
    #     one-hundred-nineteenth owned per machine-derive (engine_owner==bm-a
    #     rows 118 + candidate); wave 205 = first free number after
    #     the REGISTERED W204 row (bm-c r837 freeze+finalize one-pass
    #     2c8ef33c8) -- SINGLE STATE zero seat gap (W2..W204 all
    #     registered). Seat published=reserved
    #     MSG-2026-10-10-1627-bma-w205-seat pushed to origin
    #     63b5bd3dd BEFORE this freeze, r565 law (payload = seat MSG +
    #     pre-seat probe script + probe receipt
    #     results/_r956bma_w205_probe_receipt.json; deletion-set
    #     EMPTY); W204-state guard FIRED at freeze time: the W204 row
    #     landed on origin (bm-c r837 2c8ef33c8) after the W205 seat
    #     -- this freeze re-pulled and re-verified the universe face
    #     per the seat's fail-safe leg0 law (registry rows 202, tail
    #     W204, W204 bands == the declared universe the W205 bands
    #     were derived on: a=(463_604,465_603), b_exit=(465_604,
    #     465_803), owner bm-c machine-read);
    #     zero --no-verify; the W205 seat MSG sits in
    #     fleet/inbox/processed/ at freeze time, honest archived
    #     per S7 law).
    #     TWO HUNDRED AND FIFTH engine wave BY
    #     MACHINE-DERIVE (engine_owner rows 194 + candidate; gate
    #     leg0 machine output governs per r359 law).
    #     W1..W204 finalize ALL LANDED (net chain head 864,387,
    #     K=446,720 merged pool; W204 finalize one-pass bm-c r837)
    #     -- ZERO in-flight upstream seats at freeze time, clean
    #     finalize chain precondition; the finalize merge loop
    #     still derives the wave set from registry keys at run
    #     time, FAIL-CLOSED r307 always on. ADMIT receipt
    #     results/_r956bma_w205_probe_receipt.json;
    #     not a re-pick (R250: W205 bands were never assigned)."""

    law_old = chunk(body204, 'assert WAVE_CONFIGS[203]["a_seed_base"]',
                   'law mirror parity)"', "law-block")
    body204 = rep(body204, law_old, "\x00LAW\x00", 1, "law-sentinel")
    pin_old = chunk(body204, 'assert pf.N1_BANDS[203] == {"a": (461_404, 463_403),',
                   'r307; bm-a r936)"', "pin-block")
    body204 = rep(body204, pin_old, "\x00PIN\x00", 1, "pin-sentinel")

    # band ranges (sentinel-protected targets where they collide
    # with single-source tokens below)
    body204 = rep(body204, "463_604..465_603", "465_804..467_803", 1, "band-A")
    body204 = rep(body204, "465_604..465_803", "467_804..468_003", 1, "band-B")
    body204 = rep(body204, "463_404..465_403", "\x00NA\x00", 2, "arith-A")
    body204 = rep(body204, "463_604..463_803", "465_804..466_003", 2, "arith-B")
    body204 = rep(body204, "463_404..463_603", "\x00PB\x00", 2, "prior-B")
    # singles (uniform staircase shift)
    body204 = rep(body204, "465_603", "467_803", 3, "own-A-tail")
    body204 = rep(body204, "463_604", "465_804", 2, "A-base")
    body204 = rep(body204, "463_603", "465_803", 3, "prior-B-tail")
    body204 = rep(body204, "465_604", "467_804", 5, "B-base")
    body204 = body204.replace("\x00NA\x00", "465_604..467_603")
    body204 = body204.replace("\x00PB\x00", "465_604..465_803")
    # upstream cites inside dep comment
    body204 = rep(body204, "860,945", "864,387", 1, "body-chain-head")
    body204 = rep(body204, "bm-a r938", "bm-c r837", 1, "body-upstream-cite")
    # staircase cfg refs
    body204 = rep(body204, "WAVE_CONFIGS[204]", "WAVE_CONFIGS[205]", 2, "stair-cfg")
    # vars
    body204 = rep(body204, "w203_a", "w204_a", 8, "var-a")
    body204 = rep(body204, "w203_b", "w204_b", 8, "var-b")
    # set/range faces
    body204 = rep(body204, "w < 204", "w < 205", 3, "wprev-set")
    body204 = rep(body204, "range(16, 204)", "range(16, 205)", 1, "range16")
    body204 = rep(body204, "range(17, 204)", "range(17, 205)", 1, "range17")
    body204 = rep(body204, "PERPETUAL_N1_W204_PREREG.md", "PERPETUAL_N1_W205_PREREG.md", 1, "prereg-name")
    body204 = rep(body204, "PERPETUAL-N1-W204-SHARD-", "PERPETUAL-N1-W205-SHARD-", 2, "shard-name")
    body204 = rep(body204, '"n1w204-0of12"', '"n1w205-0of12"', 1, "shard-id-0")
    body204 = rep(body204, '"n1w204-11of12"', '"n1w205-11of12"', 1, "shard-id-11")
    body204 = rep(body204, '"n1_w204_results.json"', '"n1_w205_results.json"', 1, "out-name")
    body204 = rep(body204, 'SHARD_DIR.endswith("n1_w204")', 'SHARD_DIR.endswith("n1_w205")', 1, "shard-dir")
    # ordinal + set_wave
    body204 = rep(body204, "SIXTY-FOURTH", "SIXTY-FIFTH", 2, "ordinal")
    body204 = rep(body204, "_set_wave(204)", "_set_wave(205)", 1, "set-wave")
    # W blankets (own-wave W204->W205 first, then prior-wave W203->W204)
    n_w204 = body204.count("W204")
    body204 = body204.replace("W204", "W205")
    n_w203 = body204.count("W203")
    body204 = body204.replace("W203", "W204")
    facts["body_W_rolls"] = {"W204_to_W205": n_w204, "W203_to_W204": n_w203}
    # restore law + pin blocks rolled
    law_new = rep(law_old, "WAVE_CONFIGS[203]", "WAVE_CONFIGS[204]", 3, "law-cfg")
    law_new = rep(law_new, "pf.N1_BANDS[203]", "pf.N1_BANDS[204]", 3, "law-pf")
    law_new = rep(law_new, '"bm-a"', '"bm-c"', 1, "law-owner")
    law_new = law_new.replace("W204 ", "W205 ")
    body204 = rep(body204, "\x00LAW\x00", law_new, 1, "law-restore")
    pin_new = rep(pin_old, 'pf.N1_BANDS[203] == {"a": (461_404, 463_403),',
                  'pf.N1_BANDS[204] == {"a": (463_604, 465_603),', 1, "pin-row-a")
    pin_new = rep(pin_new, '"b_exit": (463_404, 463_603),',
                  '"b_exit": (465_604, 465_803),', 1, "pin-row-b")
    pin_new = rep(pin_new, '"engine_owner": "bm-a"},',
                  '"engine_owner": "bm-c"},', 1, "pin-owner")
    pin_new = pin_new.replace("(r307; bm-a r936)", "(r307; bm-c r837)")
    pin_new = pin_new.replace("registered W203 row parity",
                              "registered W204 row parity")
    body204 = rep(body204, "\x00PIN\x00", pin_new, 1, "pin-restore")
    for tok in ("W203", "\x00", "bm-a r938", "860,945", "w203_", "n1_w204",
                "PERPETUAL-N1-W204", "PERPETUAL_N1_W204"):
        if tok in body204:
            fails.append("body residual %r remains" % tok)
    mat205 = comment205 + "\n" + body204

    # ---- G5b cfg205 ----
    D_OLD = ('"deletion-set EMPTY; delivery window = phase-2 splice rebuild "\n'
             '                   "after the W139/W140 SEED_REGISTRY adjudication carve-outs "\n'
             '                   "landed 7464be852 (O-20261010-1906-bm-c adjudicated, receipt "\n'
             '                   "MSG-2026-10-10-1940; the C1804 dead-session spliced dual "\n'
             '                   "files were NOT recoverable, r836 verified -- this entry is "\n'
             '                   "the honest rebuild from the committed ADMIT receipt on an "\n'
             '                   "origin-verbatim base per the r609 lesson); zero merge at "\n'
             '                   "freeze delivery, zero "')
    D_NEW = ('"deletion-set EMPTY; delivery window = direct freeze this "\n'
             '                   "window (W204-state guard FIRED: the W204 row landed on "\n'
             '                   "origin at bm-c r837 2c8ef33c8 AFTER the W205 seat -- this "\n'
             '                   "entry re-pulled and re-verified the universe face at freeze "\n'
             '                   "time per the seat fail-safe leg0 law: registry rows 202, "\n'
             '                   "tail W204, W204 bands == the declared universe the W205 "\n'
             '                   "bands were derived on, owner bm-c machine-read); zero merge "\n'
             '                   "at freeze delivery, zero "')
    P_OLD = ('"ADMIT convention upgrade); W205+ projection "\n'
             '                   "per this window gate: A first-clean 465_604..467_603 "\n'
             '                   "CLEAN / B first-clean 465_804..466_003 CLEAN -- naive "\n'
             '                   "B lands INSIDE the naive A window and the registered "\n'
             '                   "W204 B band 465_604..465_803 will refuse the naive "\n'
             '                   "W205 A window (W205 seat MSG-2026-10-10-1627-bma declared "\n'
             '                   "on the post-W204-declared universe; the W205 freezer MUST "\n'
             '                   "re-pull and re-verify if the W204 row lands before the "\n'
             '                   "W205 freeze); W206+ freezer MUST re-derive on the "\n'
             '                   "post-W205 universe AND reserve the own-wave A window "\n'
             '                   "when deriving B (W141 precedent, leg2 law, E36 "\n'
             '                   "staircase card); W1..W203 finalize ALL LANDED (W203 "\n'
             '                   "finalize one-pass bm-a r938, net chain head 860,945, "\n'
             '                   "merged pool K=444,520) -- ZERO in-flight upstream "\n')
    P_NEW = ('"ADMIT convention upgrade); W206+ projection "\n'
             '                   "per this window gate: A first-clean 467_804..469_803 "\n'
             '                   "CLEAN / B first-clean 468_004..468_203 CLEAN -- naive "\n'
             '                   "B lands INSIDE the naive A window and the registered "\n'
             '                   "W205 B band 467_804..468_003 will refuse the naive "\n'
             '                   "W206 A window (W206 seat MSG-20261010-2323-bmc declared "\n'
             '                   "on the post-W205-declared universe; the W206 freezer MUST "\n'
             '                   "re-pull and re-verify if the W205 row lands before the "\n'
             '                   "W206 freeze); W207+ freezer MUST re-derive on the "\n'
             '                   "post-W206 universe AND reserve the own-wave A window "\n'
             '                   "when deriving B (W141 precedent, leg2 law, E36 "\n'
             '                   "staircase card); W1..W204 finalize ALL LANDED (W204 "\n'
             '                   "finalize one-pass bm-c r837, net chain head 864,387, "\n'
             '                   "merged pool K=446,720) -- ZERO in-flight upstream "\n')
    cfg205 = rep(cfg204, D_OLD, D_NEW, 1, "cfg-delivery")
    cfg205 = rep(cfg205, P_OLD, P_NEW, 1, "cfg-projection")
    cfg205 = cfg205.replace(D_NEW, "\x00D\x00", 1)
    cfg205 = cfg205.replace(P_NEW, "\x00P\x00", 1)
    # band ranges (targets sentinel-protected where colliding)
    cfg205 = rep(cfg205, "463_604..465_603", "465_804..467_803", 2, "cfg-A")
    cfg205 = rep(cfg205, "465_604..465_803", "467_804..468_003", 2, "cfg-B")
    cfg205 = rep(cfg205, "463_404..465_403", "\x00NA\x00", 2, "cfg-arithA")
    cfg205 = rep(cfg205, "463_604..463_803", "465_804..466_003", 2, "cfg-arithB")
    cfg205 = rep(cfg205, "463_404..463_603", "\x00PB\x00", 2, "cfg-priorB")
    # singles
    cfg205 = rep(cfg205, "463_604", "465_804", 1, "cfg-A-base")
    cfg205 = rep(cfg205, "465_604", "467_804", 2, "cfg-B-base")
    cfg205 = cfg205.replace("\x00NA\x00", "465_604..467_603")
    cfg205 = cfg205.replace("\x00PB\x00", "465_604..465_803")
    # upstream cites
    cfg205 = rep(cfg205, "bm-a r936 freeze", "bm-c r837 freeze+finalize one-pass", 1, "cfg-up1")
    cfg205 = rep(cfg205, "b2bb60963", "2c8ef33c8", 1, "cfg-up2")
    cfg205 = rep(cfg205, "bm-a r938", "bm-c r837", 1, "cfg-up3")
    cfg205 = rep(cfg205, "860,945", "864,387", 1, "cfg-up4")
    cfg205 = rep(cfg205, "444,520", "446,720", 1, "cfg-up5")
    # seat / receipt / names / ordinals
    cfg205 = rep(cfg205, "MSG-20261010-0022-bmc-w204-seat PUSHED to origin 7cf82c262",
                 "MSG-2026-10-10-1627-bma-w205-seat PUSHED to origin 63b5bd3dd", 1, "cfg-seat")
    cfg205 = rep(cfg205, "results/_w204bmc_20261010_probe_receipt.json",
                 "results/_r956bma_w205_probe_receipt.json", 1, "cfg-receipt")
    cfg205 = rep(cfg205, '204: {"batch": "PERPETUAL-N1-W204",', '205: {"batch": "PERPETUAL-N1-W205",', 1, "cfg-rowno-batch")
    cfg205 = rep(cfg205, "PERPETUAL_N1_W204_PREREG.md", "PERPETUAL_N1_W205_PREREG.md", 1, "cfg-prereg")
    cfg205 = rep(cfg205, '"shard_subdir": "n1_w204", "out_name": "n1_w204_results.json"',
                 '"shard_subdir": "n1_w205", "out_name": "n1_w205_results.json"', 1, "cfg-shard")
    cfg205 = rep(cfg205, "TWO HUNDRED AND FOURTH", "TWO HUNDRED AND FIFTH", 1, "cfg-ordinal")
    cfg205 = rep(cfg205, "engine_owner rows 193", "engine_owner rows 194", 1, "cfg-ownerrows")
    cfg205 = rep(cfg205, "SIXTY-FOURTH", "SIXTY-FIFTH", 3, "cfg-stair")
    cfg205 = rep(cfg205, "SINGLE STATE zero seat gap W2..W203 all",
                 "SINGLE STATE zero seat gap W2..W204 all", 1, "cfg-singlestate")
    cfg205 = rep(cfg205, '"engine_owner": "bm-c"},', '"engine_owner": "bm-a"},', 1, "cfg-owner")
    # W blankets
    n_c204 = cfg205.count("W204")
    cfg205 = cfg205.replace("W204", "W205")
    n_c203 = cfg205.count("W203")
    cfg205 = cfg205.replace("W203", "W204")
    facts["cfg_W_rolls"] = {"W204_to_W205": n_c204, "W203_to_W204": n_c203}
    cfg205 = cfg205.replace("\x00D\x00", D_NEW, 1)
    cfg205 = cfg205.replace("\x00P\x00", P_NEW, 1)
    for tok in ("\x00", "splice rebuild", "C1804", "7cf82c262", "_w204bmc",
                "bm-a r936", "bm-a r938", "b2bb60963", "860,945", "444,520",
                "thirty-sixth", "n1_w204", "PERPETUAL-N1-W204"):
        if tok in cfg205:
            fails.append("cfg205 residual %r remains" % tok)

    # ---- G5c pf205 ----
    pf205 = """    # W205 (bm-a r963 freeze, seat MSG-2026-10-10-1627-bma-w205-seat pushed
    # to origin 63b5bd3dd pre-freeze r565 law; probe receipt
    # results/_r956bma_w205_probe_receipt.json ADMIT; W204-state guard
    # FIRED at freeze: the W204 row landed on origin (bm-c r837
    # freeze+finalize 2c8ef33c8) after the W205 seat -- re-pulled +
    # re-verified, bands match the declared universe the seat derived
    # on; A 465_804..467_803 hops=1 A-hops-prior-B staircase
    # SIXTY-FIFTH instance E36; B 467_804..468_003 hops=1 own-A
    # mutual exclusion W141; not a re-pick R250; zero --no-verify;
    # the W205 seat MSG sits in fleet/inbox/processed/ at freeze
    # time, honest archived per S7 law;
    # W206+ projection per probe leg4: A first-clean 467_804..469_803
    # CLEAN / B first-clean 468_004..468_203 CLEAN -- naive B lands
    # INSIDE the naive A window and the registered W205 B band
    # 467_804..468_003 will refuse the naive W206 A window (W206 seat
    # MSG-20261010-2323-bmc declared on the post-W205 universe; the
    # W206 freezer MUST re-pull and re-verify if the W205 row lands
    # before the W206 freeze); W206 freezer MUST re-derive on the
    # post-W205 universe AND reserve the own-wave A window when
    # deriving B (W141 precedent, same-freeze mutual exclusion, leg2
    # law, E36 staircase card; never transcribe r587)).
    205: {"a": (465_804, 467_803), "b_exit": (467_804, 468_003),
         "engine_owner": "bm-a"},"""

    # ---- G5d claim205 ----
    claim205 = """          "+ W205 materializer face [same guard set, dep=W17..W204 "
          "outputs ALL PRESENT (landed net chain head 864,387 = "
          "W204 bm-c r837 one-pass, K=446,720 merged pool) -- ZERO "
          "in-flight upstream seats at freeze, clean precondition, TWO HUNDRED AND FIFTH "
          "ENGINE-OWNED WAVE BY MACHINE-DERIVE (engine_owner rows 194 "
          "+ candidate) bm-a's one-hundred-nineteenth owned claim per "
          "machine-derive (engine_owner==bm-a rows 118 + candidate), "
          "A=FIRST-CLEAN past the registered W204 B band (staircase "
          "SIXTY-FIFTH instance, E36 card, hops=1) + B=FIRST-CLEAN past the "
          "own-wave A window (W141 precedent, leg2 law, same-freeze "
          "mutual exclusion, hops=1), W204-state guard re-verified at "
          "freeze (W204 landed bm-c 2c8ef33c8, bands match declared "
          "universe) + seed_admit_gate rc0 both bands FREE "
          "(O-20261010-1945-bm-a ADMIT convention upgrade), "
          "ADMIT receipt "
          "results/_r956bma_w205_probe_receipt.json, law sec.4 W205 row, "
          "r963 bm-a] "
"""
    claim205 = claim205.rstrip("\n")

    if fails:
        print("RESULT: FAIL at rolls (%d) -- zero writes" % len(fails))
        for f in fails:
            print("  -", f)
        return 1

    # ---- G6 prereg roll (W204 prereg -> W205 prereg) ----
    pre_src = open(PREREG_SRC, encoding="utf-8").read()
    P = [pre_src]

    def pr(old, new, expect, tag):
        old = old.replace("2026", "\x00Y26")
        P[0] = rep(P[0], old, new, expect, tag)

    P[0] = P[0].replace("2026", "\x00Y26")
    pr("# PERPETUAL-N1-W204 预注册 · N1 nulls-deepening 泵第 202 枚",
       "# PERPETUAL-N1-W205 预注册 · N1 nulls-deepening 泵第 203 枚", 1, "pre-header")
    pr("engine_owner 行 192 注册在册+W203 bm-a 席位在飞+本候选=bm-c 第三十六枚自有波【bm-c 交互窗 \x00Y26-10-10·CEO 填载令 standing+O-20261009-2334 本地满用令】",
       "engine_owner 行 194 注册在册+W203/W204 finalize 已落账·anchor 滚动已兑现（r590）+本候选=bm-a 第一百一十九枚自有波【bm-a r963 循环窗·CEO 填载令 standing+O-20261010-2350 RE-ISSUE（机队CPU回测排满·@bm-a W205 五面冻结=本班最高优先）】", 1, "pre-header2")
    pr("本机 bm-c 实例=**live daemon mtime-watch 热重载架构**——冻结编辑落工作栈后引擎下一 cycle n1_bands() mtime 复读自见新行自烧【r535 律·D-20261002-03 fix ①】",
       "本机 bm-a 实例=**tick 架构**——冻结编辑落工作栈后下一 tick 新进程读活栈自见新行自烧【r535 律】", 1, "pre-arch1")
    pr("+ **本窗领取令=CEO 直令 \x00Y26-10-08 ~23:5x「你的机器CPU算力闲置严重，自己去领回测任务！排满」standing + O-20261009-2334-bm-b §1-2 本地满用令（\x00Y26-10-09 23:34）**【bm-c 交互窗直执·O-20260924-1730 认领即开动同轮律·本机引擎队列空转实测（saturation_engine_state.bm-c.json queue_next 空·py_cpu 0.26% 实读）】",
       "+ **本窗领取令=CEO 直令 \x00Y26-10-08 ~23:5x「你的机器CPU算力闲置严重，自己去领回测任务！排满」standing + O-20261010-2350-bm-c RE-ISSUE（\x00Y26-10-10 ~23:1x「机队CPU算力全部用于回测，排满！」·@bm-a W205 五面冻结=本班最高优先）**【bm-a r963 循环窗直执·O-20260924-1730 认领即开动同轮律】", 1, "pre-claim-src")
    pr("**波号 204=注册表 W203 席后首个自由号**",
       "**波号 205=注册表 W204 席后首个自由号**", 1, "pre-waveno")
    pr("W203=bm-a r930 席位 MSG-\x00Y26-10-09-2329 在册（processed）·五面 band row+prereg 在飞未落 origin 如实注记——本波注册宇宙=W203 声明带注入（W203 席位 MSG origin 文本验证·probe leg0 机证）·r930 W203 probe leg4 强制令兑现（W192/r892 declared-injection 判例镜像）**；本机席位公示=MSG-20261010-0022-bmc-w204-seat 已推 origin 7cf82c262 先于本冻结【r565 律·§6.1.4 API 直构零本地 commit 通道如实注记】",
       "W203=bm-a r936 五面冻结 b2bb60963 在册+引擎自烧 12/12+finalize 已落 origin（r938 one-pass·账本 860,945 EXACT·K=444,520·四预键 4/4 PASS）+W204=bm-c r837 freeze+finalize 一窗全链 2c8ef33c8 在册（账本 862,187+2,200=864,387 EXACT·K=446,720·四预键 PASS·skill_line 1.1888→1.1887）——本波注册宇宙=W203/W204 注册带在册+双 finalize 落账（N1_BANDS 注册行机器读·冻结窗 leg0 重验 202 行表尾 W204）·**W204-state guard FIRED 兑现：席位 MSG fail-safe leg0 强制令（W204 row 落 origin 后冻结必须重拉重验）本窗实跑**（W192/r892 declared-injection 判例镜像收口）；本机席位公示=MSG-2026-10-10-1627-bma-w205-seat 已推 origin 63b5bd3dd 先于本冻结【r565 律·r956 seat push 直接快进送达（payload=seat MSG+W205 pre-seat probe 脚本+回执同推）】", 1, "pre-universe")
    pr("W202=bm-a r927/r928 freeze+finalize（c76a84dc2）；W203=bm-a r930 席位在册（五面在飞）——**W2..W203 全注册单态零空档**",
       "W202=bm-a r927/r928 freeze+finalize（c76a84dc2）；W203=bm-a r936 freeze（b2bb60963）；W204=bm-c r837 freeze+finalize（2c8ef33c8）——**W2..W204 全注册单态零空档**", 1, "pre-singlestate")
    pr("ADMIT 回执=results/_w204bmc_20261010_probe_receipt.json",
       "ADMIT 回执=results/_r956bma_w205_probe_receipt.json", 1, "pre-receipt")
    pr("本波 **A-ext seed=463_604..465_603**（**A 面=FIRST-CLEAN past prior-wave B 阶梯第六十四例**：A 面算术继续带 463_204..465_203 在其起点即被 W203 声明 B 带 463_404..463_603 **拒**（W203 席位 leg4 投影+r930 W203 probe leg4 所预言+强制）→ 诚实前向走 **1 hop** 落 **463_604..465_603**·**A base==前波 B 尾+1（463_603+1）机检关系**=**A-hops-prior-B 阶梯几何第六十四例（E36 卡）**",
       "本波 **A-ext seed=465_804..467_803**（**A 面=FIRST-CLEAN past prior-wave B 阶梯第六十五例**：A 面算术继续带 465_604..467_603 在其起点即被 W204 注册 B 带 465_604..465_803 **拒**（W204 pf/probe leg4 投影所预言+强制·本窗 probe 回执 A_semantics 机读兑现）→ 诚实前向走 **1 hop** 落 **465_804..467_803**·**A base==前波 B 尾+1（465_803+1）机检关系**=**A-hops-prior-B 阶梯几何第六十五例（E36 卡）**", 1, "pre-A-face")
    pr("SIXTY-FOURTH（第六十四例）", "SIXTY-FIFTH（第六十五例）", 1, "pre-ordinal")
    pr("**B-ext exit seed=465_604..465_803**（**B 面=FIRST-CLEAN past own-wave A**：B 面算术继续带 463_604..463_803 在声明宇宙上 CLEAN 但**落在本波 A 窗 463_604..465_603 内**",
       "**B-ext exit seed=467_804..468_003**（**B 面=FIRST-CLEAN past own-wave A**：B 面算术继续带 465_804..466_003 在声明宇宙上 CLEAN 但**落在本波 A 窗 465_804..467_803 内**", 1, "pre-B-face1")
    pr("→ B 带本波 A 窗保留走 **1 hop** 落 **465_604..465_803**·**B base==本波 A 尾+1（465_603+1）机检关系**",
       "→ B 带本波 A 窗保留走 **1 hop** 落 **467_804..468_003**·**B base==本波 A 尾+1（467_803+1）机检关系**", 1, "pre-B-face2")
    pr("**W203 席位 leg4 投影+r930 probe leg4 承接面注记兑现**：投影预言 W204 须在 post-W203 注册宇宙重 derive 且 derive B 时预留本波 A 窗",
       "**W204 pf/probe leg4 投影承接面注记兑现**：投影预言 W205 须在 post-W204 注册宇宙重 derive 且 derive B 时预留本波 A 窗", 1, "pre-B-face3")
    pr("扫描面=pre-W204 全二百行注册 N1 带表（表尾 W202 行·leg0 机证 200 行）+W203 声明带两条注入（origin 文本验证）；",
       "扫描面=pre-W205 全二百零二行注册 N1 带表（表尾 W204 行·冻结窗 leg0 机证 202 行）；", 1, "pre-scan-face")
    pr("【本机 bm-c 实例·live daemon mtime-watch 热重载架构】",
       "【本机 bm-a 实例·tick 架构】", 1, "pre-arch2")
    pr("**本冻结=交互窗直笔+探针机证（无 buildgen emission 链——extraction-from-emission 律 N/A 诚实注记·五腿探针回执在场为准·selftest W204 face 将随五面冻结落地验证）。**",
       "**本冻结=循环窗直笔+活片段单代滚动（r909 physical chunk-roll 术承袭：live W204 片段 runtime 提取零转抄 r587+W204-state guard 重验在先·五腿探针回执在场为准·selftest W205 face 将随五面冻结落地验证）。**", 1, "pre-method")
    pr("`scripts/perpetual_faces_n1.py`（W2..W202 落地 runner",
       "`scripts/perpetual_faces_n1.py`（W2..W204 落地 runner", 1, "pre-reuse")
    pr("批名=**PERPETUAL-N1-W204**", "批名=**PERPETUAL-N1-W205**", 1, "pre-batch")
    pr("起稿窗实况：**W1..W202 N1 finalize 已全部落地**【净账本锚头 **858,745**·K=442,320 合并池·n1_w202_results.json 机读】；**W203=bm-a r930 席位 MSG 在册·五面+prereg 在飞未落 origin（dead-tail adoption in flight）——本波上游在飞席注记=W203·「零在飞上游链前」断言不适用改如实注记**；",
       "起稿窗实况：**W1..W204 N1 finalize 已全部落地**【净账本锚头 **864,387**·K=446,720 合并池·n1_w204_results.json 机读（origin 在册）】——零在飞上游席·anchor=最新已落账键（W204 实测·r590 滚动已兑现）；", 1, "pre-s0")
    pr("累计 null 池=442,320+2,200（W203 投影）+2,200（本波）=**446,720 投影**",
       "累计 null 池=446,720（W204 落账实测）+2,200（本波）=**448,920 投影**", 1, "pre-pool")
    pr("本机引擎队列空转+py_cpu 0.26% 实读；**CEO 直令 \x00Y26-10-08 ~23:5x 领单 standing+O-20261009-2334-bm-b §1-2 本地满用令**",
       "本机引擎队列空转+py_cpu 0.2% 实读（satengine status queue_depth 0）；**CEO 直令 \x00Y26-10-08 ~23:5x 领单 standing+O-20261010-2350-bm-c RE-ISSUE「机队CPU算力全部用于回测，排满！」（@bm-a W205 五面冻结=本班最高优先）**", 1, "pre-claim2")
    pr("本机席位 MSG-20261010-0022-bmc-w204-seat 已推 origin 7cf82c262 r565 律·probe W205+ 投影 A 465_604..467_603 / B 465_804..466_003 **naive-B-inside-naive-A re-derive 强制注记+同窗互斥预披露**（投影 B 落投影 A 窗内·W204 B 带 465_604..465_803 注册后将拒 naive W205 A 窗=阶梯 A-hops-prior-B 继承第六十五例待 W205 注册宇宙复核）",
       "本机席位 MSG-2026-10-10-1627-bma-w205-seat 已推 origin 63b5bd3dd r565 律·probe W206+ 投影 A 467_804..469_803 / B 468_004..468_203 **naive-B-inside-naive-A re-derive 强制注记+同窗互斥预披露**（投影 B 落投影 A 窗内·W205 B 带 467_804..468_003 注册后将拒 naive W206 A 窗=阶梯 A-hops-prior-B 继承第六十六例待 W206 注册宇宙复核·W206 席位 MSG-20261010-2323-bmc 已声明 A 468_004..470_003=拒后 1 hop 实兑现）", 1, "pre-seat2")
    pr("T-2026-10-01-141 s1 引擎线第 194 波【bm-c 第三十六枚自有波【机面 derive：engine_owner==bm-c 行 35+本候选以 probe leg0 机证为准】】。（波号=注册表 W203 席后首个自由号·单态零席位空档；中位公示 MSG-20261010-0022-bmc-w204-seat 先推 origin 7cf82c262 r565 律；lane-free；dept:研究）",
       "T-2026-10-01-141 s1 引擎线第 195 波【bm-a 第一百一十九枚自有波【机面 derive：engine_owner==bm-a 行 118+本候选以 probe leg0 机证为准】】。（波号=注册表 W204 席后首个自由号·单态零席位空档；中位公示 MSG-2026-10-10-1627-bma-w205-seat 先推 origin 63b5bd3dd r565 律；lane-free；dept:研究）", 1, "pre-claim3")
    pr("engine_owner==bm-c 波的未烧分片=本地队列项", "engine_owner==bm-a 波的未烧分片=本地队列项", 1, "pre-materialize")
    pr("（本机 bm-c 实例=live daemon mtime-watch 热重载——五面冻结编辑落工作栈后引擎下一 cycle n1_bands() mtime 复读自见 W204 行并点火自烧【r535 律·D-20261002-03 fix ①·r325/r330 kill-restart 序免做】。**点火验证唯一证据=产物增长面**【r325 律·2 cycle 窗】·RAM face 随 cycle 上报",
       "（本机 bm-a 实例=tick 架构——五面冻结编辑落工作栈后引擎下一 tick 新进程读活栈自见 W205 行并点火自烧【r535 律·r325/r330 kill-restart 序免做】。**点火验证唯一证据=产物增长面**【r325 律·tick 窗】·RAM floor gate 机器例在场=自点火当 RAM 清", 1, "pre-ignite")
    pr("--prereg research/PERPETUAL_N1_W204_PREREG.md", "--prereg research/PERPETUAL_N1_W205_PREREG.md", 1, "pre-gate-path")
    pr("entry rng seed=**463_604+j**（法典 §4 W204 行 A=463_604..465_603·**FIRST-CLEAN past prior-wave B 阶梯第六十四例**：算术续带 463_204..465_203 起点即被 W203 声明 B 带拒→1 hop 落 463_604..465_603·",
       "entry rng seed=**465_804+j**（法典 §4 W205 行 A=465_804..467_803·**FIRST-CLEAN past prior-wave B 阶梯第六十五例**：算术续带 465_604..467_603 起点即被 W204 注册 B 带拒→1 hop 落 465_804..467_803·", 1, "pre-A-tier")
    pr("entry rng=**463_604+j**（与 A[j] 同源配对语义逐字·runner 实证 entry=A_SEED_BASE+j）；exit rng=**465_604+j**（法典 §4 W204 行 B=465_604..465_803·**FIRST-CLEAN past own-wave A**：B 算术续带 463_604..463_803 在声明宇宙上 CLEAN 但落在本波 A 窗 463_604..465_603 内→**同窗互斥面 leg2 律·W141 先例**强制 B 越本波 A 窗→保留走落 465_604..465_803·hops=1·**B base==本波 A 尾+1 机检关系**·非轮转 r587·hop 链逐跳在 probe 回执·与 W203 席位 leg4 投影+r930 probe leg4 承接面注记兑现收敛·ADMIT 回执在场）",
       "entry rng=**465_804+j**（与 A[j] 同源配对语义逐字·runner 实证 entry=A_SEED_BASE+j）；exit rng=**467_804+j**（法典 §4 W205 行 B=467_804..468_003·**FIRST-CLEAN past own-wave A**：B 算术续带 465_804..466_003 在声明宇宙上 CLEAN 但落在本波 A 窗 465_804..467_803 内→**同窗互斥面 leg2 律·W141 先例**强制 B 越本波 A 窗→保留走落 467_804..468_003·hops=1·**B base==本波 A 尾+1 机检关系**·非轮转 r587·hop 链逐跳在 probe 回执·与 W204 pf/probe leg4 投影承接面注记兑现收敛·ADMIT 回执在场）", 1, "pre-B-tier")
    pr("W204 带与 v1 在用带", "W205 带与 v1 在用带", 1, "pre-disjoint1")
    pr("W2..W202 带（**全注册单态**）、W203 声明带注入、", "W2..W204 带（**全注册单态**）、", 1, "pre-disjoint2")
    pr("本波机验 ADMIT 回执在场=_w204bmc_20261010 探针窗", "本波机验 ADMIT 回执在场=_r956bma_w205 探针窗", 1, "pre-disjoint3")
    pr("selftest W204 face（A=first-clean past prior-wave B 恒等·B=first-clean past own-wave A 恒等+同窗互斥断言·W203 行 parity 腿",
       "selftest W205 face（A=first-clean past prior-wave B 恒等·B=first-clean past own-wave A 恒等+同窗互斥断言·W204 行 parity 腿", 1, "pre-selftest")
    pr("（起草窗实流 W1..W202 已落账 442,320 实测·derive 禁手抄）+W203 2,200（在飞）+本波 2,200",
       "（起稿窗实流 W1..W204 已落账 446,720 实测·derive 禁手抄）+本波 2,200", 1, "pre-s4-pool")
    pr('batch_name="PERPETUAL-N1-W204", batch_trials=2200, file_name="results/perpetual_faces/n1_w204_results.json"',
       'batch_name="PERPETUAL-N1-W205", batch_trials=2200, file_name="results/perpetual_faces/n1_w205_results.json"', 1, "pre-s4-ledger")
    pr("（起草窗实况注记：**W1..W202 N1 finalize 已全部落地**——净账本锚头 858,745·**K=442,320 合并池**·**W203 在飞上游席注记（bm-a·r930 席位在册·五面在飞未落）——本波 §5 预测键=**W202 实测值**【results/perpetual_faces/n1_w202_results.json·N1 面最新已落账键·W203 落账后属上游先决非本键面】。",
       "（起稿窗实况注记：**W1..W204 N1 finalize 已全部落地**——净账本锚头 864,387·**K=446,720 合并池**·零在飞上游席（W203/W204 finalize 均已落 origin·ls-tree 机证）——本波 §5 预测键=**W204 实测值**【results/perpetual_faces/n1_w204_results.json·N1 面最新已落账键·origin 在册机证】。", 1, "pre-s5-pre")
    pr("1. W204-only mu 与累计池 merged mu（W202 实测键 **−0.0928**·K=442,320 合并池·W202-only 实测 **−0.0910**）差异 **|Δ|<0.02**（W2..W202 共二百面实测 mu 稳定先例·单波跨键微）。",
       "1. W205-only mu 与累计池 merged mu（W204 实测键 **−0.092697**·K=446,720 合并池·W204-only 实测 **−0.086008**）差异 **|Δ|<0.02**（W2..W204 共二百零三面实测 mu 稳定先例·单波跨键微）。", 1, "pre-s5-1")
    pr("2. sigma 相对变化 **<±10%**（同设计同窗·纯抽样波动；键 **0.245165**=W202 合并池实测 0.245165）。",
       "2. sigma 相对变化 **<±10%**（同设计同窗·纯抽样波动；键 **0.245097**=W204 合并池实测 0.245097）。", 1, "pre-s5-2")
    pr("3. A 档 full_sharpe_p95 与 W202 A 档 p95（**0.3214** 实测锚）差 **<0.05**（门标注法 W5..W202 先例",
       "3. A 档 full_sharpe_p95 与 W204 A 档 p95（**0.3053** 实测锚）差 **<0.05**（门标注法 W5..W204 先例", 1, "pre-s5-3")
    pr("键 W202 实测 K-lift **+0.0001**·line_merged@K442,320 **1.1887**·line_pre 1.1886·n_eff 856,545；se_mu 收窄链 …→W201→W202 **0.000369**】）。",
       "键 W204 实测 K-lift **−0.0001**·line_merged@K446,720 **1.1887**·line_pre 1.1888·n_eff 862,187；se_mu 收窄链 …→W203 0.000368→W204 **0.000367**】）。", 1, "pre-s5-4")
    pr("5. **W205+ 投影（probe 机证·下波冻结方复核非转抄 r587 律）**：A first-clean 465_604..467_603 **CLEAN**（hops=0）；B first-clean **465_804..466_003 CLEAN**（hops=0）——**naive B 落在 naive A 窗内**（W141 同窗互斥先例适用于 W205：W205 冻结方必须在 post-W204 注册宇宙重 derive 且 derive B 时预留本波 A 窗——leg2 律/E36 卡）；**W204 B 带 465_604..465_803 注册后将拒 naive W205 A 窗**——W205 A 重 derive 同强制（越过 W204 B 带·阶梯 A-hops-prior-B 继承第六十五例）；verify at W205 prereg，hop 链逐跳在 probe 回执。",
       "5. **W206+ 投影（probe 机证·下波冻结方复核非转抄 r587 律）**：A first-clean 467_804..469_803 **CLEAN**（hops=0）；B first-clean **468_004..468_203 CLEAN**（hops=0）——**naive B 落在 naive A 窗内**（W141 同窗互斥先例适用于 W206：W206 冻结方必须在 post-W205 注册宇宙重 derive 且 derive B 时预留本波 A 窗——leg2 律/E36 卡）；**W205 B 带 467_804..468_003 注册后将拒 naive W206 A 窗**——W206 A 重 derive 同强制（越过 W205 B 带·阶梯 A-hops-prior-B 继承第六十六例）；verify at W206 prereg，hop 链逐跳在 probe 回执。", 1, "pre-s5-5")
    pr("run --shard k --of 12 --wave 204/finalize --wave 204", "run --shard k --of 12 --wave 205/finalize --wave 205", 1, "pre-s6-runner")
    pr("（本机 bm-c 实例·**live daemon mtime-watch 热重载**·本地队列→PreIgnitionChecks→分离子进程点火→完成→台账处理【runner_args --lane engine 车道闸同 r523 律】）；**点火验证=2 cycle 内产物增长面**【n1_w204/ 分片计数增长·唯一点火证据·r325 律】",
       "（本机 bm-a 实例·**tick 架构**·本地队列→PreIgnitionChecks→分离子进程点火→完成→台账处理【runner_args --lane engine 车道闸同 r523 律】）；**点火验证=2 tick 内产物增长面**【n1_w205/ 分片计数增长·唯一点火证据·r325 律】", 1, "pre-s6-ignite")
    pr("results/p2cal_ext/n1_w204/shard-<k>-of-12.json", "results/p2cal_ext/n1_w205/shard-<k>-of-12.json", 1, "pre-s6-delivery1")
    pr("results/perpetual_faces/n1_w204_results.json`（finalize 合并件·顶层 evidence_cutoff·cutoff_meta·audit 段·K-lift 对照；finalize 键序前置=**起草窗在飞上游席 W203（bm-a·r930 席位在册）**",
       "results/perpetual_faces/n1_w205_results.json`（finalize 合并件·顶层 evidence_cutoff·cutoff_meta·audit 段·K-lift 对照；finalize 键序前置=**起稿窗零在飞上游席（W203/W204 finalize 均已落 origin·ls-tree 机证）**", 1, "pre-s6-delivery2")
    pr("bm-c live daemon 架构=engine ledger jsonl+state/face/history 以 git 交付（engine_owner==bm-c 35 行注册 + 本候选",
       "bm-a tick 架构=engine ledger jsonl+state/face/history 以 git 交付（engine_owner==bm-a 118 行注册 + 本候选", 1, "pre-s6-ledger")
    s7 = P[0].find("## §7")
    tail_anchor = P[0].find("- **跑前冻结=本件 commit**")
    assert s7 > 0 and tail_anchor > s7, "prereg §7 anchor drift"
    placeholder = ("## §7 跑后实证。【finalize 收口机械回填·待 W205 finalize 窗】\n"
                   "- （占位·finalize one-pass 后机械回填：账本恒等式+合并池 K+merged mu/"
                   "w-only mu/mu_delta+sigma+se_mu+skill_line_v2 K-lift+A 档 p95+§5 四预键机证"
                   "+canon flip 态+audit.finalize_only+voids_applied）。\n\n"
                   "## §8 批后复盘。【finalize 同窗回填·待 W205 finalize 窗】\n"
                   "- （占位·§5.5 W206+ 投影承接+宝藏/方法论捕获问+诚实披露面·finalize 收口窗机械回填）。\n\n")
    P[0] = P[0][:s7] + placeholder + P[0][tail_anchor:]
    P[0] = P[0].replace("\x00Y26", "2026")
    pre_rolled = P[0]
    for tok in ("_w204bmc", "7cf82c262", "C1804", "1422ad767", "splice rebuild",
                "第三十六枚", "bm-c 交互窗", "live daemon", "\x00"):
        if tok in pre_rolled:
            fails.append("prereg residual %r" % tok)
    facts["prereg_len"] = len(pre_rolled)

    if fails:
        print("RESULT: FAIL (%d) -- zero writes" % len(fails))
        for f in fails:
            print("  -", f)
        return 1

    # ---- G8 insertions ----
    IND = "                       "
    n1_b = n1n.replace(cfg204, cfg204 + "\n" + IND + cfg205, 1)
    if n1_b == n1n:
        fails.append("cfg insertion no-op")
    t141_pos = n1_b.find("    # --- T-141 s2 lane face")
    assert t141_pos > 0
    n1_c = n1_b[:t141_pos] + mat205 + "\n" + n1_b[t141_pos:]
    claim_anchor = claim204 + '\n          "+ T-141 s2 "'
    assert n1_c.count(claim_anchor) == 1, "claim anchor not unique"
    n1_final = n1_c.replace(claim_anchor,
                            claim204 + "\n" + claim205 +
                            '\n          "+ T-141 s2 "', 1)
    pf_final = pfn.replace(pf204, pf204 + "\n" + pf205, 1)
    if pf_final == pfn:
        fails.append("pf insertion no-op")

    # ---- G9 gates ----
    checks = [
        (n1_final, '205: {"batch": "PERPETUAL-N1-W205",', 1),
        (n1_final, '204: {"batch": "PERPETUAL-N1-W204",', 1),
        (n1_final, '203: {"batch": "PERPETUAL-N1-W203",', 1),
        (n1_final, "# --- W205 materializer face", 1),
        (n1_final, "# --- W204 materializer face", 1),
        (n1_final, '"a_seed_base": 465_804,', 1),
        (n1_final, '"b_exit_seed_base": 467_804,', 1),
        (n1_final, "_set_wave(205)", 1),
        (n1_final, "PERPETUAL_N1_W205_PREREG.md", 2),
        (n1_final, '"r963 bm-a] "', 1),
        (n1_final, '"r837 bm-c] "', 1),
        (n1_final, "bm-a's one-hundred-nineteenth owned claim", 1),
        (n1_final, 'assert WAVE_CONFIGS[204]["a_seed_base"] == pf.N1_BANDS[204]["a"][0]', 1),
        (n1_final, '"W205 engine_owner drift (law mirror parity)"', 1),
        (n1_final, 'assert pf.N1_BANDS[204] == {"a": (463_604, 465_603),', 1),
        (n1_final, 'W204 row parity drift (r307; bm-c r837)', 1),
        (pf_final, '205: {"a": (465_804, 467_803), "b_exit": (467_804, 468_003),', 1),
        (pf_final, '204: {"a": (463_604, 465_603), "b_exit": (465_604, 465_803),', 1),
        (pf_final, '203: {"a": (461_404, 463_403), "b_exit": (463_404, 463_603),', 1),
        (pf_final, "# W205 (bm-a r963 freeze", 1),
        (pf_final, "W205 seat MSG sits in", 1),
    ]
    for src, needle, cnt in checks:
        got = src.count(needle)
        if got != cnt:
            fails.append("post-edit needle %r count %d != %d"
                         % (needle[:50], got, cnt))
    pat = re.compile(r"(\d{3})_(\d{3})\.\.(\d{3})_(\d{3})")
    for name, txt in (("pf", pf_final), ("n1", n1_final)):
        bad = [mm.group() for mm in pat.finditer(txt)
               if int(mm.group(3)) < int(mm.group(1))]
        if bad:
            fails.append("%s malformed windows: %s" % (name, bad[:5]))
    w205_a = set(range(465804, 467804))
    w205_b = set(range(467804, 468004))
    assert not (w205_a & w205_b)
    for w, c in N1_BANDS.items():
        wa = set(range(c["a"][0], c["a"][1] + 1))
        wb = set(range(c["b_exit"][0], c["b_exit"][1] + 1))
        if (w205_a & wa) or (w205_a & wb) or (w205_b & wa) or (w205_b & wb):
            fails.append("W205 band collides wave %s" % w)
    ast.parse(n1_final)
    ast.parse(pf_final)
    print("AST gate: both files parse OK")

    if fails:
        print("RESULT: FAIL at gates (%d) -- zero writes" % len(fails))
        for f in fails:
            print("  -", f)
        return 1

    if not WRITE:
        print("DRY-RUN PASS: all gates green, zero writes (rerun --write)")
        with open(OUT_RCPT.replace(".json", "_dryrun.json"), "w",
                  encoding="utf-8") as fh:
            json.dump(facts, fh, indent=1, ensure_ascii=False)
        return 0

    # ---- G10 live writes ----
    n1_out = n1_final.replace("\n", "\r\n") if n1_crlf else n1_final
    pf_out = pf_final.replace("\n", "\r\n") if pf_crlf else pf_final
    with open(N1P, "w", encoding="utf-8", newline="") as fh:
        fh.write(n1_out)
    with open(PFP, "w", encoding="utf-8", newline="") as fh:
        fh.write(pf_out)
    with open(PREREG_DST, "w", encoding="utf-8", newline="") as fh:
        fh.write(pre_rolled)
    print("LIVE WRITES DONE: pf %d->%d B, n1 %d->%d B, prereg %d B"
          % (len(pfn), len(pf_final), len(n1n), len(n1_final), len(pre_rolled)))

    # ---- G11 py_compile + post-import ----
    for f in (N1P, PFP):
        prc = subprocess.run([sys.executable, "-m", "py_compile", f],
                             capture_output=True, creationflags=CNW)
        assert prc.returncode == 0, "py_compile failed: %s" % f
    chk = subprocess.run(
        [sys.executable, "-c",
         "import sys, json; sys.path.insert(0, 'scripts'); "
         "sys.path.insert(0, '.'); "
         "from perpetual_faces import N1_BANDS as B; "
         "import perpetual_faces_n1 as n1; "
         "cfg = n1.WAVE_CONFIGS[205]; "
         "print(json.dumps({'rows': len(B), 'w205': B.get(205), "
         "'w204': B.get(204), 'w203': B.get(203), "
         "'cfg205': [cfg['a_seed_base'], cfg['b_exit_seed_base'], "
         "cfg['shard_subdir'], cfg['out_name'], cfg['engine_owner']]}))"],
        cwd=ROOT, capture_output=True, creationflags=CNW)
    assert chk.returncode == 0, "post-import failed: %s" % chk.stderr[:300]
    post = json.loads(chk.stdout.decode("utf-8", "replace").strip().splitlines()[-1])
    assert post["rows"] == 203, "row count drift: %s" % post
    assert post["w205"] == {"a": [465804, 467803], "b_exit": [467804, 468003],
                            "engine_owner": "bm-a"}
    assert post["w204"] == {"a": [463604, 465603], "b_exit": [465604, 465803],
                            "engine_owner": "bm-c"}
    assert post["w203"] == {"a": [461404, 463403], "b_exit": [463404, 463603],
                            "engine_owner": "bm-a"}
    assert post["cfg205"] == [465804, 467804, "n1_w205",
                              "n1_w205_results.json", "bm-a"]
    facts["post_import"] = post

    # ---- G11b freeze-time gates ----
    g1 = subprocess.run([sys.executable, "Tools/banned_direction_gate.py",
                         "--prereg", "research/PERPETUAL_N1_W205_PREREG.md"],
                        cwd=ROOT, capture_output=True, creationflags=CNW)
    facts["banned_direction_gate_rc"] = g1.returncode
    assert g1.returncode == 0, "banned_direction_gate FAIL"
    g2 = subprocess.run([sys.executable, "Tools/seed_admit_gate.py",
                         "check", "--prereg",
                         "research/PERPETUAL_N1_W205_PREREG.md"],
                        cwd=ROOT, capture_output=True, creationflags=CNW)
    facts["seed_admit_gate_rc"] = g2.returncode
    g2out = (g2.stdout.decode("utf-8", "replace") +
             g2.stderr.decode("utf-8", "replace"))
    facts["seed_admit_gate_tail"] = g2out[-300:]
    print("seed_admit_gate rc=%d tail=%r" % (g2.returncode, g2out[-160:]))

    # ---- G12 receipt + PASS prints ----
    with open(OUT_RCPT, "w", encoding="utf-8") as fh:
        json.dump(facts, fh, indent=1, ensure_ascii=False)
    print("PASS 1/5 pf N1_BANDS[205]: a=(465_804,467_803) "
          "b_exit=(467_804,468_003) owner=bm-a (W204 row byte-intact)")
    print("PASS 2/5 n1 WAVE_CONFIGS[205]: batch=PERPETUAL-N1-W205 "
          "a_seed_base=465_804 b_exit_seed_base=467_804 shard=n1_w205 "
          "out=n1_w205_results.json owner=bm-a")
    print("PASS 3/5 n1 W205 materializer face: fresh comment + body rolled "
          "from live W204 (law-mirror W204/bm-c, pin W204 row, staircase "
          "SIXTY-FIFTH, deps range(17,205), prereg presence); claim appended")
    print("PASS 4/5 guards: origin vacancy + seat ancestor + W204-state "
          "guard FIRED re-verify (rows 202 tail W204 bands match declared) "
          "+ anchor 864,387/K446,720 machine-read + AST+py_compile + "
          "post-import parity + band disjointness vs all 202 rows + "
          "banned_direction_gate rc0 + seat MSG processed/ verified")
    print("PASS 5/5 summary: W205 = 195th engine wave, bm-a 119th owned; "
          "A=465_804..467_803 hops=1 SIXTY-FIFTH staircase; B=467_804..468_003 "
          "hops=1 own-A mutual exclusion (W141); prereg "
          "research/PERPETUAL_N1_W205_PREREG.md created (§5 keys=W204 "
          "measured, §7/§8 placeholders); "
          "receipt=results/_r963bma_w205_freeze_receipt.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
