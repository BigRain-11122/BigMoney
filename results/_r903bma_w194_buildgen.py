# -*- coding: utf-8 -*-
"""r903 bm-a W194 per-wave prereg BUILDGEN (generator): constructs the
W193->W194 TOK/BACK pair map, runs the full preflight DRY gate (r787
preflight dry-run law, ZERO writes until all green), then EMITS
results/_r903bma_w194_prereg_build.py (the executable build script with
pairs baked).

Bloodline: r830 (E41 buildgen surgery) / r833 prereg-build three laws
(AST no-exec prior-gen / DRY full-file gate zero-write-first /
U+2212 display anchor forms) / r877 S83 roll (old side = physical src
POST-ROLL text; binary src extraction) / r893 W191 buildgen (two-phase
vmap, whole-string composites, numerals LAST, r735 substring-order law)
/ r901 W193 buildgen (anchor=W191 per r590 with W192 finalize in
flight upstream -- this window extends the same anchor law to a TWO
in-flight upstream seat face: W192 finalize pending + W193 burn
COMPLETE finalize key-order-locked r307).

Src: research/PERPETUAL_N1_W193_PREREG.md freeze-time blob 5512a886a
(commit 9c0c089b8 == origin/main HEAD face, verified EQUAL this window;
W193 sec7/sec8 still placeholders = safe build src, no actuals leak).
Extracted byte-verbatim (binary) to results/_r903bma_w194_prereg_src.txt.

r587 machine-derived facts (live-asserted inside, zero transcribe):
  - r902 pre-seat probe results/_r902bma_w194_probe_receipt.json ADMIT:
    A 441_604..443_603 (staircase FIFTY-FOURTH, E36; naive A
    441_404..443_403 REFUSED at own start by registered W193 B band
    441_404..441_603, hops=1) / B 443_604..443_803 (own-wave A
    reservation, W141 leg2, hops=1; naive B 441_604..441_803 lands
    inside own-A);
    leg0 rows=191 tail W193 owner_rows=183 bma_rows=108 ordinal=184
    bma_ordinal=109 w191_ledger_head=833,536;
    leg4 W195+ projection A 443_604..445_603 hops=0 / B 443_804..444_003
    hops=0, B-inside-A True.
  - W191 finalize results/perpetual_faces/n1_w191_results.json:
    ledger 831,336+2,200=833,536 EXACT; K merged=418,120 EXACT;
    merged mu -0.0929 4dp display HOLDS (fifth-wave display hold);
    w-only -0.0898; sigma 0.245166; A p95 0.3049; K-lift +0.0001;
    line 1.1871 -> 1.1872; n_eff 831,336; se_mu chain tail 0.000379.
    ANCHOR STAYS W191 (r590 push-time re-derive): W192 finalize product
    ABSENT on origin (bm-c lane) AND W193 finalize product ABSENT
    (burn COMPLETE 12/12 but finalize key-order-locked r307 behind
    W192) -- honest two-in-flight-upstream-seat disclosure.
  - shas: W191 five-face e5e4af81b, W192 five-face f8703842c, W193
    five-face 5cf0d6175, W194 seat MSG add 5cca13637; W194 five-face
    vacancy on origin (empty -S pick).

Structural disclosures vs the W193 physical src (bm-a buildgen face):
  * claim context rolls to the r902 seat push (5cca13637) with W195+
    projection (probe leg4 machine values);
  * both in-flight upstream seats (W192 bm-c finalize-pending + W193
    bm-a burn-COMPLETE finalize-locked) disclosed on every anchor face;
  * chain W193 entry appended (5cf0d6175);
  * SEED_REGISTRY live count 191 unchanged this window (no new named
    seed registrations since r901); masked pre-TOK like the r893
    @@REGN@@ vestigial pattern;
  * pool projection 418,120+2,200(W192)+2,200(W193)+2,200(this)=424,720.

Output written CRLF (on-disk convention, r370 law) by the EMITTED
script; this generator writes nothing but the emitted script itself
(after its own DRY gate is fully green).
"""
import ast
import io
import json
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
SRC = "results/_r903bma_w194_prereg_src.txt"
OUT = "research/PERPETUAL_N1_W194_PREREG.md"
EMIT = "results/_r903bma_w194_prereg_build.py"
G = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"
M = "\u2212"  # U+2212 display minus


def git(*a):
    r = subprocess.run(["git", "-C", G] + list(a), capture_output=True)
    return r.stdout.decode("utf-8", errors="replace").strip()


# --- machine-derived facts (r587) --------------------------------------
subprocess.run(["git", "-C", G, "fetch", "origin"], capture_output=True)
probe = json.load(open(r"results/_r902bma_w194_probe_receipt.json",
                      encoding="utf-8"))
assert probe["verdict"] == "ADMIT", probe["verdict"]
assert probe["bands"] == {"A": "441604_443603", "B": "443604_443803"}, \
    probe["bands"]
leg0, leg1 = probe["legs"]["leg0"], probe["legs"]["leg1"]
leg4 = probe["legs"]["leg4"]
assert leg1["A"] == [441604, 443603] and leg1["B"] == [443604, 443803], leg1
assert leg1["hops_A"] == 1 and leg1["hops_B"] == 1, leg1
assert leg1["ARITH_A"] == [441404, 443403], leg1["ARITH_A"]
assert leg1["ARITH_B"] == [441604, 441803], leg1["ARITH_B"]
assert leg1["B_naive_first_clean"] == [441604, 441803], leg1
assert leg1["B_naive_hops"] == 0, leg1
assert leg1["B_hop_chain"][0] == {"hop": 1, "window": [441604, 441803],
                                 "jump_to": 443604}, leg1["B_hop_chain"]
assert leg0["rows"] == 191 and leg0["tail"] == "W193", leg0
assert leg0["ordinal"] == 184 and leg0["bma_ordinal"] == 109, leg0
assert leg0["owner_rows"] == 183 and leg0["bma_rows"] == 108, leg0
assert leg0["w191_ledger_head"] == 833536, leg0
assert probe["legs"]["leg2"]["conflicts"] == 0, probe["legs"]["leg2"]
assert probe["legs"]["leg3"]["origin_vacancy"] is True, probe["legs"]["leg3"]
assert leg4["W195p_A"] == "443604..445603" and \
    leg4["W195p_B"] == "443804..444003", leg4
assert leg4["hops_A"] == 0 and leg4["hops_B"] == 0, leg4
assert leg4["W195p_B_lands_inside_W195p_A"] is True, leg4
assert "FIFTY-FOURTH" in leg1["A_semantics"], leg1["A_semantics"]

res = json.load(open(r"results/perpetual_faces/n1_w191_results.json",
                     encoding="utf-8"))
npc = res["null_pool_cumulative"]
kl = res["skill_line_v2_k_lift"]
assert npc["merged"]["n_values"] == 418120, "K drift"
assert npc["pre_w191_cumulative"]["n_values"] == 415920, "pre-K drift"
assert res["science_gates"]["ledger"]["total"] == 833536, "ledger head"
assert res["science_gates"]["ledger"]["prev_total"] == 831336, "ledger prev"
assert npc["se_mu_at_k418120"] == 0.000379, "se_mu drift"
assert kl["n_eff_held_equal"] == 831336, kl
assert abs(kl["line_delta_k_lift"] - 0.0001) < 1e-12, kl
assert abs(kl["line_pre_w191"] - 1.1871) < 1e-9 and \
    abs(kl["line_merged_418120"] - 1.1872) < 1e-9, kl
assert res["families"]["A_random_engine_exit"]["full_sharpe_p95"] == 0.3049
MU4 = ("%.4f" % npc["merged"]["mu"]).replace("-", M)
WONLY4 = ("%.4f" % npc["w191_only"]["mu"]).replace("-", M)
SIG6 = "%.6f" % npc["merged"]["sigma"]
assert MU4 == M + "0.0929" and WONLY4 == M + "0.0898" and SIG6 == "0.245166", \
    (MU4, WONLY4, SIG6)

W191_FF = git("log", "origin/main", "--format=%h", "-n", "1", "-S",
              '191: {"a": (435_004', "--", "scripts/perpetual_faces.py")
assert W191_FF == "e5e4af81b", W191_FF
W192_FF = git("log", "origin/main", "--format=%h", "-n", "1", "-S",
              '192: {"a": (437_204', "--", "scripts/perpetual_faces.py")
assert W192_FF == "f8703842c", W192_FF
W193_FF = git("log", "origin/main", "--format=%h", "-n", "1", "-S",
              '193: {"a": (439_404', "--", "scripts/perpetual_faces.py")
assert W193_FF == "5cf0d6175", W193_FF
SEAT = git("log", "origin/main", "--format=%h", "-n", "1", "--diff-filter=A",
           "--", "fleet/inbox/MSG-2026-10-09-0627-bma-w194-seat.md")
assert SEAT == "5cca13637", SEAT
_vac = git("log", "origin/main", "--format=%h", "-n", "1", "-S",
           '194: {"a": (441_604', "--", "scripts/perpetual_faces.py")
assert _vac == "", "W194 five-face already on origin?!"
_fin192 = git("ls-tree", "origin/main",
              "results/perpetual_faces/n1_w192_results.json")
assert _fin192 == "", "W192 finalize landed -- anchor must roll (r590)!"
_fin193 = git("ls-tree", "origin/main",
              "results/perpetual_faces/n1_w193_results.json")
assert _fin193 == "", "W193 finalize landed -- anchor must roll (r590)!"
print("facts: ALL GREEN (anchor=W191; W192/W193 finalize both in-flight; "
      "W194 five-face vacancy)")

# live SEED_REGISTRY count (unchanged 191 this window, no new named seeds
# since r901); masked pre-TOK like r893 @@REGN@@ pattern
sys.path.insert(0, "scripts")
sys.path.insert(0, ".")
import science_gates as _sg  # noqa: E402
REG_N = len(_sg.SEED_REGISTRY)
assert REG_N == 191, "SEED_REGISTRY count drift: %d" % REG_N

# --- src load -----------------------------------------------------------
src = io.open(SRC, encoding="utf-8").read()
assert src.count("\r\n") == 0, "src blob expected LF"
assert "PERPETUAL-N1-W193" in src and "439_404..441_403" in src, \
    "src face drift"
assert src.count("SEED_REGISTRY \u5168\u952e 191 \u503c") == 1, \
    "registry-count face not found in src (old live count)"
# pre-TOK registry mask (value unchanged this generation: 191)
src_t = src.replace("SEED_REGISTRY \u5168\u952e 191 \u503c",
                    "SEED_REGISTRY \u5168\u952e @@REGN@@ \u503c")


def span(text, start, end, tag):
    i = text.find(start)
    assert i >= 0, "span start not found [%s]: %r" % (tag, start[:60])
    j = text.find(end, i)
    assert j > i, "span end not found [%s]: %r" % (tag, end[:60])
    out = text[i:j + len(end)]
    assert text.count(out) == 1, "span not unique [%s]" % tag
    return out


# --- pair construction (old side = physical src text, r877 law 1) -------
# chain: extract verbatim from src (r587 zero-transcribe)
_m = re.search(r"W118=bm-b r678 freeze\uff08565e5b0b4\uff09.*?"
               r"W192=bm-c r787 freeze\uff08f8703842c\uff09", src_t)
assert _m, "chain anchor not found"
CHAIN_OLD = _m.group()
CHAIN_NEW = (CHAIN_OLD + "\uff1bW193=bm-a r901 freeze\uff085cf0d6175\uff09")
assert "e5e4af81b" in CHAIN_NEW and "f8703842c\uff09" in CHAIN_NEW
assert CHAIN_NEW.endswith("5cf0d6175\uff09")
assert "ea42ee94a" not in CHAIN_NEW
assert src_t.count(CHAIN_OLD) == 1

TITLE_OLD = src_t.split("\n")[0]
assert TITLE_OLD.startswith("# PERPETUAL-N1-W193 "), TITLE_OLD[:50]
assert TITLE_OLD.endswith("\uff09"), TITLE_OLD[-20:]

SEATBLOCK_OLD = span(src_t,
                     "\u3010\u672c\u51bb\u7ed3\u7a97 fetch \u5b9e\u6838\u8868"
                     "\u5c3e\u65f6 W193 \u53f7\u4f4d\u7a7a\u6863",
                     "\uff08\u5982\u5b9e\u6ce8\u8bb0\uff09\u3011\u3011",
                     "seatblock")
CLAIM_OLD = span(src_t,
                 "- \u8ba4\u9886\uff1anever-dry \u5e38\u4f9b\u7ed9\u4f8b"
                 "\u6ce2\uff08TRIAL_LABOR_LAW \u00a74\u00b7\u677f\u7a7a",
                 "dept:\u7814\u7a76\uff09\u3002", "claim")
AFACE_OLD = span(src_t,
                 "\u672c\u6ce2 **A-ext seed=439_404..441_403**\uff08",
                 "\u6295\u5f71\u4e0e\u56de\u6267\u4e24\u8bfb\u6cd5\u6052"
                 "\u540c\uff09", "aface")
BFACE_OLD = span(src_t,
                 "**B-ext exit seed=441_404..441_603**\uff08",
                 "\u5df2\u5982\u5b9e\u62ab\u9732\u975e\u5206\u53c9\uff09",
                 "bface")
ANCHOR0_OLD = span(src_t,
                   "\u8d77\u7a3f\u7a97\u5b9e\u51b5\uff1a**W1..W191 N1 "
                   "finalize \u5df2\u5168\u90e8\u843d\u5730**\u3010\u51c0"
                   "\u8d26\u672c\u951a\u5934",
                   "\u65ad\u8a00\u4e0d\u9002\u7528\u6539\u5982\u5b9e\u6ce8"
                   "\u8bb0**", "anchor0")
S5ANCH_OLD = span(src_t,
                  "\uff08\u8d77\u8349\u7a97\u5b9e\u51b5\u6ce8\u8bb0\uff1a"
                  "**W1..W191 N1 finalize \u5df2\u5168\u90e8\u843d\u5730**"
                  "\u2014\u2014\u51c0\u8d26\u672c\u951a\u5934",
                  "\u975e\u672c\u952e\u9762\u3011", "s5anch")
S55_OLD = span(src_t,
               "5. **W194+ \u6295\u5f71\uff08probe \u673a\u8bc1",
               "hop \u94fe\u9010\u8df3\u5728 probe \u56de\u6267", "s55")
S51_OLD = span(src_t,
               "1. W193-only mu \u4e0e\u7d2f\u8ba1\u6c60 merged mu\uff08"
               "W191 \u5b9e\u6d4b\u952e **",
               "\u5355\u6ce2\u8de8\u952e\u5fae\uff09", "s51")
GATEW2_OLD = span(src_t,
                  "\u672c\u6ce2\u673a\u9a8c ADMIT \u56de\u6267\u5728\u573a="
                  "_r900bma_w193 \u63a2\u9488\u7a97\uff08",
                  "\u968f\u4e94\u9762\u51bb\u7ed3\u843d\u5730", "gatew2")
ASEED_OLD = span(src_t,
                 "entry rng seed=**439_404+j**\uff08\u6cd5\u5178 \u00a74 "
                 "W193 \u884c A",
                 "ADMIT \u56de\u6267\u5728\u573a\uff09", "aseed")
BSEED_OLD = span(src_t,
                 "exit rng=**441_404+j**\uff08\u6cd5\u5178 \u00a74 W193 "
                 "\u884c B",
                 "ADMIT \u56de\u6267\u5728\u573a\uff09", "bseed")
ENGNOTE_OLD = span(src_t,
                   "**\u672c\u51bb\u7ed3=buildgen emission \u94fe\uff08",
                   "selftest W193 face \u5c06\u968f\u4e94\u9762\u51bb\u7ed3"
                   "\u843d\u5730\u9a8c\u8bc1\uff09\u3002**", "engnote")

TOK = [
    # (old, token)  -- composites first, bare numerals LAST (r773/r775)
    (CHAIN_OLD, "@CHAIN@"),
    (TITLE_OLD, "@TITLE@"),
    (SEATBLOCK_OLD, "@SEATBLOCK@"),
    (AFACE_OLD, "@AFACE@"),
    (BFACE_OLD, "@BFACE@"),
    (ANCHOR0_OLD, "@ANCHOR0@"),
    (S5ANCH_OLD, "@S5ANCH@"),
    (S55_OLD, "@S55@"),
    (S51_OLD, "@S51@"),
    (GATEW2_OLD, "@GATEW2@"),
    (ASEED_OLD, "@ASEED@"),
    (BSEED_OLD, "@BSEED@"),
    (ENGNOTE_OLD, "@ENGNOTE@"),
    (CLAIM_OLD, "@CLAIM@"),
    # ---- short literals ----
    ("\u626b\u63cf\u9762=pre-W193 \u5168\u4e00\u767e\u4e5d\u5341\u884c"
     "\u6ce8\u518c N1 \u5e26\u8868\uff08\u8868\u5c3e W192 \u884c\u00b7"
     "leg0 \u673a\u8bc1 190 \u884c\uff09", "@SCANFACE@"),
    ("R250\uff1aW193 \u5e26\u4ece\u672a\u6307\u6d3e\u00b7\u6d4b\u91cf"
     "\u9762\u96f6\u7ed3\u679c\u53ef\u9501", "@R250@"),
    ("results/_r900bma_w193_probe_receipt.json", "@PRCR@"),
    ("W2..W192 \u843d\u5730 runner \u7684 wave \u53c2\u6570\u5316\u590d"
     "\u7528", "@RUNNERW@"),
    ("\u6279\u540d=**PERPETUAL-N1-W193**", "@BATCHNAME@"),
    ("\u7d2f\u8ba1 null \u6c60=418,120+2,200\uff08W192 \u6295\u5f71\uff09"
     "+2,200\uff08\u672c\u6ce2\uff09=**422,520 \u6295\u5f71**", "@POOL@"),
    ("\u81ea\u89c1 W193 \u884c\u5e76\u70b9\u706b\u81ea\u70e7", "@MATCOND@"),
    ("--prereg research/PERPETUAL_N1_W193_PREREG.md", "@GATECMD@"),
    ("entry rng=**439_404+j**\uff08\u4e0e A[j] \u540c\u6e90\u914d\u5bf9"
     "\u8bed\u4e49\u9010\u5b57\u00b7runner \u5b9e\u8bc1 entry=A_SEED_BASE"
     "+j\uff09", "@BENTRY@"),
    ("\u672c\u6ce2\u8bbe\u8ba1=W2..W192 \u9010\u5b57\u590d\u7528",
     "@PROBEW@"),
    ("W193 \u5e26\u4e0e v1 \u5728\u7528\u5e26\uff0810_000..10_099/"
     "20_000..20_019\uff09\u3001W1 ext \u5e26\uff0810_100..12_099/"
     "20_100..20_299\uff09\u3001W2..W192 \u5e26\uff08**\u5168\u6ce8\u518c"
     "\u5355\u6001**\uff09", "@DISJ@"),
    ("\u5df2\u843d\u8d26\u51c0\u503c\uff08\u8d77\u7a3f\u7a97\u5b9e\u6d41 "
     "W1..W191 \u5df2\u843d\u8d26 418,120 \u5b9e\u6d4b\u00b7derive "
     "\u7981\u624b\u6284\uff09+W192 2,200\uff08\u5728\u98de\uff09+\u672c"
     "\u6ce2 2,200", "@POOL4@"),
    ('batch_name="PERPETUAL-N1-W193", batch_trials=2200, file_name='
     '"results/perpetual_faces/n1_w193_results.json"', "@LEDGER@"),
    ("--wave 193/finalize --wave 193", "@CLI@"),
    ("\u3010n1_w193/ \u5206\u7247\u8ba1\u6570\u589e\u957f\u00b7\u552f"
     "\u4e00\u70b9\u706b\u8bc1\u636e\u00b7r325 \u5f8b\u3011", "@ENG6@"),
    ("results/p2cal_ext/n1_w193/shard-<k>-of-12.json", "@SHARD@"),
    ("results/perpetual_faces/n1_w193_results.json", "@RFN@"),
    ("finalize \u952e\u5e8f\u524d\u7f6e=**\u8d77\u7a3f\u7a97\u5728\u98de"
     "\u4e0a\u6e38\u5e2d W192\uff08bm-c\u00b7\u4e94\u9762\u51bb\u7ed3"
     "\u5728\u518c\uff09**\u2014\u2014\u8dd1\u65f6\u6309 registry \u952e "
     "derive \u590d\u6838\u00b7FAIL-CLOSED r307 \u4e24\u6001\u4f8b\u6052"
     "\u5728", "@FINPRE@"),
    ("\uff08engine_owner==bm-a 107 \u884c\u6ce8\u518c + \u672c\u5019"
     "\u9009\u2014\u2014\u4ee5 probe leg0 \u673a\u8bc1\u4e3a\u51c6\uff09",
     "@EOBD@"),
    ("\u5f85 W193 finalize \u7a97\u3011\n- \uff08\u5360\u4f4d\u00b7"
     "finalize one-pass \u540e\u673a\u68b0\u56de\u586b\uff1a\u8d26\u672c"
     "\u6052\u7b49\u5f0f+\u5408\u5e76\u6c60 K+merged mu/w-only mu/"
     "mu_delta+sigma+se_mu+skill_line_v2 K-lift+A \u6863 p95+\u00a75 "
     "\u56db\u9884\u952e\u673a\u8bc1+canon flip \u6001+audit.finalize_only"
     "+voids_applied\u3002\uff09", "@S7@"),
    ("\u3010finalize \u540c\u7a97\u56de\u586b\u00b7\u5f85 W193 finalize "
     "\u7a97\u3011\n- \uff08\u5360\u4f4d\u00b7\u00a75.5 W194+ \u6295"
     "\u5f71\u627f\u63a5+\u5b9d\u85cf/\u65b9\u6cd5\u8bba\u6355\u83b7"
     "\u95ee+\u8bda\u5b9e\u62ab\u9732\u9762\u00b7finalize \u6536\u53e3"
     "\u7a97\u673a\u68b0\u56de\u586b\u3002\uff09", "@S8@"),
    # ---- numerals LAST ----
    ("\u6ce2\u53f7 193=\u6ce8\u518c\u8868 W192 \u5e2d\u540e\u9996\u4e2a"
     "\u81ea\u7531\u53f7", "@WAVEFREE@"),
]

BACK = {
    "@CHAIN@": CHAIN_NEW,
    "@TITLE@": (
        "# PERPETUAL-N1-W194 \u9884\u6ce8\u518c \u00b7 N1 nulls-deepening "
        "\u6cf5\u7b2c 192 \u679a\uff08never-dry \u5e38\u4f9b\u7ed9\u4f8b"
        "\u6ce2\u00b7\u6ce2\u5e8f\u53f7\u8fde\u7eed\u00b7\u673a\u9762 "
        "derive\uff1aengine_owner \u884c 183 \u6ce8\u518c\u5728\u518c+"
        "W193 \u70e7\u5f55 COMPLETE\u00b7finalize \u952e\u5e8f\u95ed\u9501"
        "\u5728\u98de+\u672c\u5019\u9009=bm-a \u7b2c\u4e00\u767e\u96f6"
        "\u4e5d\u679a\u81ea\u6709\u6ce2\u3010bm-a r903\u00b7buildgen "
        "\u8840\u7edf r830/r833/r877 \u627f\u88ad\u3011\uff09"),
    "@SEATBLOCK@": (
        "\u3010\u672c\u51bb\u7ed3\u7a97 fetch \u5b9e\u6838\u8868\u5c3e"
        "\u65f6 W194 \u53f7\u4f4d\u7a7a\u6863\u00b7rg \u884c WAVE_CONFIGS+"
        "prereg \u8def\u5f84\u4e09\u67e5+origin ls-tree vacancy \u673a"
        "\u8bc1\uff08\u672c\u7a97 probe leg3 \u5b9e\u8dd1\uff09\uff1b"
        "\u5168 inbox/processed/ W194 \u5e2d\u4f4d\u96f6\u5916\u673a\u547d"
        "\u4e2d\uff1b**W192=bm-c r787 \u4e94\u9762\u51bb\u7ed3 f8703842c "
        "\u5728\u518c\u00b7finalize \u5728\u98de\u672a\u843d origin+W193="
        "bm-a r901 \u4e94\u9762\u51bb\u7ed3 5cf0d6175 \u5728\u518c\u00b7"
        "\u70e7\u5f55 COMPLETE 12/12\u00b7finalize \u952e\u5e8f\u95ed\u9501"
        "\uff08W192 \u672a\u843d\u00b7r307\uff09\u5982\u5b9e\u6ce8\u8bb0"
        "\u2014\u2014\u672c\u6ce2\u6ce8\u518c\u5b87\u5b99=W192/W193 \u6ce8"
        "\u518c\u5e26\u5728\u518c\uff08N1_BANDS \u6ce8\u518c\u884c\u673a"
        "\u5668\u8bfb\u00b7probe leg0 \u673a\u8bc1 191 \u884c\u8868\u5c3e "
        "W193\uff09\u00b7r902 W194 probe \u5168\u817f\u673a\u8bc1**\uff1b"
        "\u672c\u673a\u5e2d\u4f4d\u516c\u793a=MSG-2026-10-09-0627-bma-"
        "w194-seat \u5df2\u63a8 origin 5cca13637 \u5148\u4e8e\u672c\u51bb"
        "\u7ed3\u3010r565 \u5f8b\u00b7\u63a8\u9001\u7a97=r902 seat push "
        "\u76f4\u63a5\u5feb\u8fdb\u9001\u8fbe 5cca13637\uff08payload=seat "
        "MSG+W194 pre-seat probe \u811a\u672c+\u56de\u6267\u540c\u63a8"
        "\uff09\uff1bself-ack inbox\u2192processed \u79fb\u4f4d\u968f\u4e94"
        "\u9762\u51bb\u7ed3\u7a97\u6536\u53e3\u5f52\u6863\uff08\u5982\u5b9e"
        "\u6ce8\u8bb0\uff09\u3011\u3011"),
    "@AFACE@": (
        "\u672c\u6ce2 **A-ext seed=441_604..443_603**\uff08**A \u9762="
        "FIRST-CLEAN past prior-wave B \u9636\u68af\u7b2c\u4e94\u5341"
        "\u56db\u4f8b**\uff1aA \u9762\u7b97\u672f\u7ee7\u7eed\u5e26 "
        "441_404..443_403 \u5728\u5176\u8d77\u70b9\u5373\u88ab W193 \u6ce8"
        "\u518c B \u5e26 441_404..441_603 **\u62d2**\uff08W193 \u00a75.5 "
        "\u6295\u5f71+r901 prereg leg4+r900 probe leg4 \u53cc\u6e90\u9884"
        "\u8a00+\u5f3a\u5236\u00b7r902 probe \u56de\u6267 A_semantics "
        "\u673a\u8bfb\u53cc\u5151\u73b0\uff09\u2192 \u8bda\u5b9e\u524d"
        "\u5411\u8d70 **1 hop** \u843d **441_604..443_603**\u00b7**A base"
        "==\u524d\u6ce2 B \u5c3e+1\uff08441_603+1\uff09\u673a\u68c0\u5173"
        "\u7cfb**=**A-hops-prior-B \u9636\u68af\u51e0\u4f55\u7b2c\u4e94"
        "\u5341\u56db\u4f8b\uff08E36 \u5361\uff09**\u00b7\u975e\u8f6e"
        "\u8f6c r587 \u524d\u5411\u5355\u8c03\u65ad\u8a00\u5728\u8d70"
        "\u518c\uff1b\u5e8f\u6570\u9762\u5982\u5b9e\u62ab\u9732\uff1a"
        "W193 \u00a75.5 \u6295\u5f71\u9884\u544a\u7b2c\u4e94\u5341\u56db"
        "\u4f8b\u00b7\u672c\u7a97 probe \u56de\u6267 A_semantics \u673a"
        "\u8bfb\u5e8f\u6570=FIFTY-FOURTH\uff08\u7b2c\u4e94\u5341\u56db"
        "\u4f8b\uff09\u00b7\u672c\u4ef6\u6309\u56de\u6267\u5e8f\u6570"
        "\u9762\u8bb0\u8f7d\u975e\u8f6c\u6284\uff08r587\uff09\u00b7\u6295"
        "\u5f71\u4e0e\u56de\u6267\u4e24\u8bfb\u6cd5\u6052\u540c\uff09"),
    "@BFACE@": (
        "**B-ext exit seed=443_604..443_803**\uff08**B \u9762=FIRST-CLEAN "
        "past own-wave A**\uff1aB \u9762\u7b97\u672f\u7ee7\u7eed\u5e26 "
        "441_604..441_803 \u5728\u58f0\u660e\u5b87\u5b99\u4e0a CLEAN \u4f46"
        "**\u843d\u5728\u672c\u6ce2 A \u7a97 441_604..443_603 \u5185**"
        "\uff08**\u540c\u7a97\u4e92\u65a5\u9762 leg2 \u5f8b\u00b7W141 "
        "\u5148\u4f8b**\uff1aA \u4e0e B \u540c\u4e00\u51bb\u7ed3 commit "
        "\u53cc\u6ce8\u518c\u00b7\u4e92\u65a5\u65ad\u8a00\u5f3a\u5236 B "
        "\u8d8a\u8fc7\u672c\u6ce2 A \u7a97\uff09\u2192 B \u5e26\u672c"
        "\u6ce2 A \u7a97\u4fdd\u7559\u8d70 **1 hop** \u843d **443_604.."
        "443_803**\u00b7**B base==\u672c\u6ce2 A \u5c3e+1\uff08443_603+1"
        "\uff09\u673a\u68c0\u5173\u7cfb**\u00b7hop \u94fe\u9010\u8df3"
        "\u5728 probe \u56de\u6267\uff1b**W193 \u00a75.5 \u6295\u5f71+"
        "r901 prereg leg4 \u627f\u63a5\u9762\u6ce8\u8bb0\u5151\u73b0**"
        "\uff1a\u6295\u5f71\u9884\u8a00 W194 \u987b\u5728 post-W193 \u6ce8"
        "\u518c\u5b87\u5b99\u91cd derive \u4e14 derive B \u65f6\u9884"
        "\u7559\u672c\u6ce2 A \u7a97\u2014\u2014\u672c\u7a97\u53cc\u9762"
        "\u5151\u73b0\u00b7A \u88ab\u62d2+\u9636\u68af\u8d8a\u5e26\u5982"
        "\u6295\u5f71\u6240\u671f\u00b7B \u540c\u7a97\u4e92\u65a5\u4fdd"
        "\u7559=\u6295\u5f71\u6240\u671f\u00b7\u5df2\u5982\u5b9e\u62ab"
        "\u9732\u975e\u5206\u53c9\uff09"),
    "@ANCHOR0@": (
        "\u8d77\u7a3f\u7a97\u5b9e\u51b5\uff1a**W1..W191 N1 finalize \u5df2"
        "\u5168\u90e8\u843d\u5730**\u3010\u51c0\u8d26\u672c\u951a\u5934 "
        "**833,536**\u00b7K=418,120 \u5408\u5e76\u6c60\u00b7n1_w191_"
        "results.json \u673a\u8bfb\u3011\uff1b**W192=bm-c \u4e94\u9762"
        "\u51bb\u7ed3\u5728\u518c\uff08f8703842c\uff09\u00b7finalize "
        "\u5728\u98de\u672a\u843d origin+W193=bm-a \u4e94\u9762\u51bb\u7ed3"
        "\u5728\u518c\uff085cf0d6175\uff09\u00b7\u70e7\u5f55 COMPLETE "
        "12/12\u00b7finalize \u952e\u5e8f\u95ed\u9501\uff08r307\uff09"
        "\u2014\u2014\u672c\u6ce2\u4e0a\u6e38\u5728\u98de\u5e2d\u6ce8\u8bb0"
        "=W192/W193 \u53cc\u5e2d\u00b7\u300c\u96f6\u5728\u98de\u4e0a\u6e38"
        "\u94fe\u524d\u300d\u65ad\u8a00\u4e0d\u9002\u7528\u6539\u5982"
        "\u5b9e\u6ce8\u8bb0**"),
    "@S5ANCH@": (
        "\uff08\u8d77\u8349\u7a97\u5b9e\u51b5\u6ce8\u8bb0\uff1a**W1.."
        "W191 N1 finalize \u5df2\u5168\u90e8\u843d\u5730**\u2014\u2014"
        "\u51c0\u8d26\u672c\u951a\u5934 833,536\u00b7**K=418,120 \u5408"
        "\u5e76\u6c60**\u00b7**W192/W193 \u5728\u98de\u4e0a\u6e38\u5e2d"
        "\u6ce8\u8bb0\uff08bm-c/bm-a\u00b7\u4e94\u9762\u51bb\u7ed3\u5728"
        "\u518c\u00b7finalize \u5728\u98de\u672a\u843d\u00b7W193 \u70e7"
        "\u5f55 COMPLETE\uff09\u2014\u2014\u672c\u6ce2 \u00a75 \u9884\u6d4b"
        "\u952e=**W191 \u5b9e\u6d4b\u503c**\u3010results/perpetual_faces/"
        "n1_w191_results.json\u00b7N1 \u9762\u6700\u65b0\u5df2\u843d\u8d26"
        "\u952e\u00b7W192/W193 \u843d\u8d26\u540e\u5c5e\u4e0a\u6e38\u5148"
        "\u51b3\u975e\u672c\u952e\u9762\u3011"),
    "@S55@": (
        "5. **W195+ \u6295\u5f71\uff08probe \u673a\u8bc1\u00b7\u4e0b"
        "\u6ce2\u51bb\u7ed3\u65b9\u590d\u6838\u975e\u8f6c\u6284 r587 "
        "\u5f8b\uff09**\uff1aA first-clean 443_604..445_603 **CLEAN**"
        "\uff08hops=0\uff09\uff1bB first-clean **443_804..444_003 "
        "CLEAN**\uff08hops=0\uff09\u2014\u2014**naive B \u843d\u5728 "
        "naive A \u7a97\u5185**\uff08W141 \u540c\u7a97\u4e92\u65a5\u5148"
        "\u4f8b\u9002\u7528\u4e8e W195\uff1aW195 \u51bb\u7ed3\u65b9\u5fc5"
        "\u987b\u5728 post-W194 \u6ce8\u518c\u5b87\u5b99\u91cd derive "
        "\u4e14 derive B \u65f6\u9884\u7559\u672c\u6ce2 A \u7a97\u2014"
        "\u2014leg2 \u5f8b/E36 \u5361\uff09\uff1b**W194 B \u5e26 "
        "443_604..443_803 \u6ce8\u518c\u540e\u5c06\u62d2 naive W195 A "
        "\u7a97**\u2014\u2014W195 A \u91cd derive \u540c\u5f3a\u5236"
        "\uff08\u8d8a\u8fc7 W194 B \u5e26\u00b7\u9636\u68af A-hops-prior-B "
        "\u7ee7\u627f\u7b2c\u4e94\u5341\u4e94\u4f8b\uff09\uff1bverify at "
        "W195 prereg\uff0chop \u94fe\u9010\u8df3\u5728 probe \u56de\u6267"),
    "@S51@": (
        "1. W194-only mu \u4e0e\u7d2f\u8ba1\u6c60 merged mu\uff08W191 "
        "\u5b9e\u6d4b\u952e **" + MU4 + "**\u00b7K=418,120 \u5408\u5e76"
        "\u6c60\u00b7W191-only \u5b9e\u6d4b **" + WONLY4 + "**\uff09\u5dee"
        "\u5f02 **|\u0394|<0.02**\uff08W2..W191 \u5171\u4e00\u767e\u4e5d"
        "\u5341\u9762\u5b9e\u6d4b mu \u7a33\u5b9a\u5148\u4f8b\u00b7\u5355"
        "\u6ce2\u8de8\u952e\u5fae\uff09"),
    "@GATEW2@": (
        "\u672c\u6ce2\u673a\u9a8c ADMIT \u56de\u6267\u5728\u573a=_r902bma_"
        "w194 \u63a2\u9488\u7a97\uff08pre-seat probe \u5355\u7a97\u00b7"
        "gate \u817f\u5408\u5e76\u7ed3\u6784\u627f\u88ad r812/r820/r823 "
        "\u5148\u4f8b\u00b7parity N/A \u8bda\u5b9e\u6ce8\u8bb0\uff09\uff1b"
        "selftest W194 face\uff08A=first-clean past prior-wave B \u6052"
        "\u7b49\u00b7B=first-clean past own-wave A \u6052\u7b49+\u540c"
        "\u7a97\u4e92\u65a5\u65ad\u8a00\u00b7W193 \u884c parity \u817f"
        "\u3010r735 \u6d4b\u91cf-\u5b9e\u73b0\u5206\u53c9\u65cf\u9632"
        "\u62a4\u9762\uff1aA/B \u7a97 set-range \u9488\u5728\u573a\u3011"
        "\uff09\u968f\u4e94\u9762\u51bb\u7ed3\u843d\u5730"),
    "@ASEED@": (
        "entry rng seed=**441_604+j**\uff08\u6cd5\u5178 \u00a74 W194 "
        "\u884c A=441_604..443_603\u00b7**FIRST-CLEAN past prior-wave B "
        "\u9636\u68af\u7b2c\u4e94\u5341\u56db\u4f8b**\uff1a\u7b97\u672f"
        "\u7eed\u5e26 441_404..443_403 \u8d77\u70b9\u5373\u88ab W193 "
        "\u6ce8\u518c B \u5e26\u62d2\u21921 hop \u843d 441_604..443_603"
        "\u00b7A base==\u524d\u6ce2 B \u5c3e+1 \u673a\u68c0\u5173\u7cfb"
        "\u00b7E36 \u5361\u00b7hops=1\u00b7ADMIT \u56de\u6267\u5728\u573a"
        "\uff09"),
    "@BSEED@": (
        "exit rng=**443_604+j**\uff08\u6cd5\u5178 \u00a74 W194 \u884c "
        "B=443_604..443_803\u00b7**FIRST-CLEAN past own-wave A**\uff1a"
        "B \u7b97\u672f\u7eed\u5e26 441_604..441_803 \u5728\u58f0\u660e"
        "\u5b87\u5b99\u4e0a CLEAN \u4f46\u843d\u5728\u672c\u6ce2 A \u7a97 "
        "441_604..443_603 \u5185\u2192**\u540c\u7a97\u4e92\u65a5\u9762 "
        "leg2 \u5f8b\u00b7W141 \u5148\u4f8b**\u5f3a\u5236 B \u8d8a\u672c"
        "\u6ce2 A \u7a97\u2192\u4fdd\u7559\u8d70\u843d 443_604..443_803"
        "\u00b7hops=1\u00b7**B base==\u672c\u6ce2 A \u5c3e+1 \u673a\u68c0"
        "\u5173\u7cfb**\u00b7\u975e\u8f6e\u8f6c r587\u00b7hop \u94fe\u9010"
        "\u8df3\u5728 probe \u56de\u6267\u00b7\u4e0e W193 \u00a75.5 \u6295"
        "\u5f71+r901 prereg leg4 \u627f\u63a5\u9762\u6ce8\u8bb0\u5151"
        "\u73b0\u6536\u655b\u00b7ADMIT \u56de\u6267\u5728\u573a\uff09"),
    "@ENGNOTE@": (
        "**\u672c\u51bb\u7ed3=buildgen emission \u94fe\uff08r830/r833/"
        "r877 \u8840\u7edf\u627f\u88ad\u00b7TOK \u4e24\u76f8 vmap+DRY "
        "\u5168\u6587\u4ef6\u95e8\u96f6\u5199\u5165\u5148\u884c+U+2212 "
        "\u663e\u793a\u5f62\u00b7\u4e94\u817f\u63a2\u9488\u56de\u6267"
        "\u5728\u573a\u4e3a\u51c6\u00b7selftest W194 face \u5c06\u968f"
        "\u4e94\u9762\u51bb\u7ed3\u843d\u5730\u9a8c\u8bc1\uff09\u3002**"),
    "@CLAIM@": (
        "- \u8ba4\u9886\uff1anever-dry \u5e38\u4f9b\u7ed9\u4f8b\u6ce2"
        "\uff08TRIAL_LABOR_LAW \u00a74\u00b7\u677f\u7a7a/\u6c60\u9971/"
        "\u65e0\u5728\u98de\u5224\u51b3\u6279=\u9ed8\u8ba4\u7eed\u8dd1"
        "\u4e0b\u4e00\u6ce2\u2014\u2014\u672c\u673a r902 \u5e2d\u4f4d "
        "MSG-2026-10-09-0627-bma-w194-seat \u5df2\u63a8 origin "
        "5cca13637\uff08r902 seat push\u00b7r565 \u5f8b\uff09\u00b7probe "
        "W195+ \u6295\u5f71 A 443_604..445_603 / B 443_804..444_003 "
        "**naive-B-inside-naive-A re-derive \u5f3a\u5236\u6ce8\u8bb0+"
        "\u540c\u7a97\u4e92\u65a5\u9884\u62ab\u9732**\uff08\u6295\u5f71 "
        "B \u843d\u6295\u5f71 A \u7a97\u5185\u00b7W194 B \u5e26 "
        "443_604..443_803 \u6ce8\u518c\u540e\u5c06\u62d2 naive W195 A "
        "\u7a97=\u9636\u68af A-hops-prior-B \u7ee7\u627f\u7b2c\u4e94"
        "\u5341\u4e94\u4f8b\u5f85 W195 \u6ce8\u518c\u5b87\u5b99\u590d"
        "\u6838\uff09\u3002\u8868\u5c3e\u540e\u65b0\u9996\u4e2a\u81ea"
        "\u7531\u53f7\u81ea\u9886\u00b7r902 probe \u5355\u8dd1\u5151"
        "\u73b0\u6ce8\u8bb0\uff08\u672c\u7a97\u51bb\u7ed3\u6d88\u8d39"
        "\uff09\uff1bO-20260924-1730 CEO \u5373\u65f6\u5f8b\uff08\u8ba4"
        "\u9886\u4e0e\u5f00\u52a8\u540c\u8f6e\u00b7\u7981\u6392\u672a"
        "\u6765\u8f6e\u6b21\uff09\uff1bT-2026-10-01-141 s1 \u5f15\u64ce"
        "\u7ebf\u7b2c 184 \u6ce2\u3010bm-a \u7b2c\u4e00\u767e\u96f6"
        "\u4e5d\u679a\u81ea\u6709\u6ce2\u3010\u673a\u9762 derive\uff1a"
        "engine_owner==bm-a \u884c 108+\u672c\u5019\u9009\u4ee5 probe "
        "leg0 \u673a\u8bc1\u4e3a\u51c6\u3011\u3011\u3002\uff08\u6ce2"
        "\u53f7=\u6ce8\u518c\u8868 W193 \u5e2d\u540e\u9996\u4e2a\u81ea"
        "\u7531\u53f7\u00b7\u5355\u6001\u96f6\u5e2d\u4f4d\u7a7a\u6863"
        "\uff1b\u4e2d\u4f4d\u516c\u793a MSG-2026-10-09-0627-bma-w194-"
        "seat \u5148\u63a8 origin 5cca13637 r565 \u5f8b\uff1blane-free"
        "\uff1bdept:\u7814\u7a76\uff09\u3002"),
    "@SCANFACE@": (
        "\u626b\u63cf\u9762=pre-W194 \u5168\u4e00\u767e\u4e5d\u5341"
        "\u4e00\u884c\u6ce8\u518c N1 \u5e26\u8868\uff08\u8868\u5c3e W193 "
        "\u884c\u00b7leg0 \u673a\u8bc1 191 \u884c\uff09"),
    "@R250@": ("R250\uff1aW194 \u5e26\u4ece\u672a\u6307\u6d3e\u00b7"
               "\u6d4b\u91cf\u9762\u96f6\u7ed3\u679c\u53ef\u9501"),
    "@PRCR@": "results/_r902bma_w194_probe_receipt.json",
    "@RUNNERW@": ("W2..W193 \u843d\u5730 runner \u7684 wave \u53c2\u6570"
                  "\u5316\u590d\u7528"),
    "@BATCHNAME@": "\u6279\u540d=**PERPETUAL-N1-W194**",
    "@POOL@": (
        "\u7d2f\u8ba1 null \u6c60=418,120+2,200\uff08W192 \u6295\u5f71"
        "\uff09+2,200\uff08W193 \u6295\u5f71\uff09+2,200\uff08\u672c"
        "\u6ce2\uff09=**424,720 \u6295\u5f71**"),
    "@MATCOND@": ("\u81ea\u89c1 W194 \u884c\u5e76\u70b9\u706b\u81ea"
                  "\u70e7"),
    "@GATECMD@": "--prereg research/PERPETUAL_N1_W194_PREREG.md",
    "@BENTRY@": (
        "entry rng=**441_604+j**\uff08\u4e0e A[j] \u540c\u6e90\u914d"
        "\u5bf9\u8bed\u4e49\u9010\u5b57\u00b7runner \u5b9e\u8bc1 "
        "entry=A_SEED_BASE+j\uff09"),
    "@PROBEW@": "\u672c\u6ce2\u8bbe\u8ba1=W2..W193 \u9010\u5b57\u590d"
                "\u7528",
    "@DISJ@": (
        "W194 \u5e26\u4e0e v1 \u5728\u7528\u5e26\uff0810_000..10_099/"
        "20_000..20_019\uff09\u3001W1 ext \u5e26\uff0810_100..12_099/"
        "20_100..20_299\uff09\u3001W2..W193 \u5e26\uff08**\u5168\u6ce8"
        "\u518c\u5355\u6001**\uff09"),
    "@POOL4@": (
        "\u5df2\u843d\u8d26\u51c0\u503c\uff08\u8d77\u7a3f\u7a97\u5b9e"
        "\u6d41 W1..W191 \u5df2\u843d\u8d26 418,120 \u5b9e\u6d4b\u00b7"
        "derive \u7981\u624b\u6284\uff09+W192 2,200\uff08\u5728\u98de"
        "\uff09+W193 2,200\uff08\u70e7\u5f55 COMPLETE\u00b7finalize "
        "\u952e\u5e8f\u95ed\u9501\uff09+\u672c\u6ce2 2,200"),
    "@LEDGER@": (
        'batch_name="PERPETUAL-N1-W194", batch_trials=2200, file_name='
        '"results/perpetual_faces/n1_w194_results.json"'),
    "@CLI@": "--wave 194/finalize --wave 194",
    "@ENG6@": ("\u3010n1_w194/ \u5206\u7247\u8ba1\u6570\u589e\u957f"
               "\u00b7\u552f\u4e00\u70b9\u706b\u8bc1\u636e\u00b7r325 "
               "\u5f8b\u3011"),
    "@SHARD@": "results/p2cal_ext/n1_w194/shard-<k>-of-12.json",
    "@RFN@": "results/perpetual_faces/n1_w194_results.json",
    "@FINPRE@": (
        "finalize \u952e\u5e8f\u524d\u7f6e=**\u8d77\u7a3f\u7a97\u5728"
        "\u98de\u4e0a\u6e38\u5e2d W192/W193\uff08bm-c/bm-a\u00b7\u4e94"
        "\u9762\u51bb\u7ed3\u5728\u518c\u00b7W193 \u70e7\u5f55 COMPLETE"
        "\uff09**\u2014\u2014\u8dd1\u65f6\u6309 registry \u952e derive "
        "\u590d\u6838\u00b7FAIL-CLOSED r307 \u4e24\u6001\u4f8b\u6052"
        "\u5728"),
    "@EOBD@": ("\uff08engine_owner==bm-a 108 \u884c\u6ce8\u518c + "
               "\u672c\u5019\u9009\u2014\u2014\u4ee5 probe leg0 \u673a"
               "\u8bc1\u4e3a\u51c6\uff09"),
    "@S7@": (
        "\u5f85 W194 finalize \u7a97\u3011\n- \uff08\u5360\u4f4d\u00b7"
        "finalize one-pass \u540e\u673a\u68b0\u56de\u586b\uff1a\u8d26"
        "\u672c\u6052\u7b49\u5f0f+\u5408\u5e76\u6c60 K+merged mu/w-only "
        "mu/mu_delta+sigma+se_mu+skill_line_v2 K-lift+A \u6863 p95+"
        "\u00a75 \u56db\u9884\u952e\u673a\u8bc1+canon flip \u6001+audit."
        "finalize_only+voids_applied\u3002\uff09"),
    "@S8@": (
        "\u3010finalize \u540c\u7a97\u56de\u586b\u00b7\u5f85 W194 "
        "finalize \u7a97\u3011\n- \uff08\u5360\u4f4d\u00b7\u00a75.5 "
        "W195+ \u6295\u5f71\u627f\u63a5+\u5b9d\u85cf/\u65b9\u6cd5\u8bba"
        "\u6355\u83b7\u95ee+\u8bda\u5b9e\u62ab\u9732\u9762\u00b7finalize "
        "\u6536\u53e3\u7a97\u673a\u68b0\u56de\u586b\u3002\uff09"),
    "@WAVEFREE@": ("\u6ce2\u53f7 194=\u6ce8\u518c\u8868 W193 \u5e2d"
                   "\u540e\u9996\u4e2a\u81ea\u7531\u53f7"),
}

# --- preflight DRY gate (r787 countcheck + r833 zero-write) -------------
print("DRY GATE: counting old sides in src (progressive, vmap-order) ...")
problems = []
out_t = src_t
for old, tok in TOK:
    n = out_t.count(old)
    if n != 1:
        problems.append((tok, n, old[:60]))
        continue
    out_t = out_t.replace(old, tok)
if problems:
    for tok, n, head in problems:
        print("  COUNT-FAIL %-14s count=%d head=%r" % (tok, n, head))
    raise SystemExit("DRY GATE red: %d pair(s) failed" % len(problems))
print("  all %d old sides count==1 (progressive vmap order)" % len(TOK))

# BACK phase on the tokenized text
for tok, new in BACK.items():
    out_t = out_t.replace(tok, new)
out_t = out_t.replace("SEED_REGISTRY \u5168\u952e @@REGN@@ \u503c",
                      "SEED_REGISTRY \u5168\u952e %d \u503c" % REG_N)
resid = re.findall(r"@[A-Z0-9]+@", out_t)
assert not resid, "residual tokens: %s" % resid[:6]
bad = [mm.group() for mm in
       re.finditer(r"(\d{3})_(\d{3})\.\.(\d{3})_(\d{3})", out_t)
       if int(mm.group(3)) < int(mm.group(1))]
assert not bad, "malformed windows: %s" % bad[:4]
# U+2212 display forms present (anchor display hold, fifth wave)
assert M + "0.0929" in out_t and M + "0.0898" in out_t, "U+2212 forms"
assert "0.245166" in out_t and "0.3049" in out_t and "0.000379" in out_t
# batch-id sanity (title + batchname + ledger = 3 hyphenated forms)
nb = out_t.count("PERPETUAL-N1-W194")
assert nb == 3, "batch id count=%d (expect 3: title+batchname+ledger)" % nb
# stale sweep: W193-era values that must have rolled
for stale in ("FIFTY-THIRD", "\u7b2c\u4e94\u5341\u4e09\u4f8b",
              "439_204..441_203", "439_404..441_403", "439_204..439_403",
              "439_404..439_603", "439_404+j", "441_404+j",
              "**B-ext exit seed=441_404..441_603**",
              "PERPETUAL-N1-W193", "PERPETUAL_N1_W193_PREREG",
              "n1_w193", "MSG-2026-10-09-0458", "9df3078c5",
              "engine_owner==bm-a 107", "engine_owner==bm-a \u884c 107",
              "\u7b2c 183 \u6ce2", "\u7b2c\u4e00\u767e\u96f6\u516b"
              "\u679a", "\u6cf5\u7b2c 191 \u679a",
              "\u6ce2\u53f7 193=", "\u6ce8\u518c\u8868 W192 \u5e2d\u540e",
              "\u5168\u4e00\u767e\u4e5d\u5341\u884c", "422,520",
              "W2..W192", "W193-only", "\u5f85 W193 finalize \u7a97",
              "W194+ \u6295\u5f71", "r900 \u5e2d\u4f4d",
              "r900 probe \u5355\u8dd1", "r900 seat push",
              "r900 W193 probe", "\u884c 182 \u6ce8\u518c\u5728\u518c",
              "W192 finalize \u5728\u98de", "r901\u00b7buildgen"):
    assert stale not in out_t, "stale survives: %r" % stale
# legal persistences (display-HOLD + chain mids + anchor faces)
assert M + "0.0929" in out_t, "merged-mu 4dp display hold missing"
assert out_t.count("W190 0.000380") == 1, "se_mu chain mid W190 missing"
assert out_t.count(M + "0.0001/W191") == 1, "K-lift chain mid missing"
assert "W191=bm-a r894 freeze\uff08e5e4af81b\uff09" in out_t, \
    "chain W191 mid missing"
assert "\uff1bW192=bm-c r787 freeze\uff08f8703842c\uff09\uff1bW193=bm-a " \
    "r901 freeze\uff085cf0d6175\uff09\u3002" in out_t, "chain tail missing"
assert out_t.count("n1_w191_results.json") == 2, "anchor file refs"
assert "v2..W191 \u843d\u5730" in out_t, "\u00a70.5 landed-set face"
assert out_t.count("W1..W191 N1 finalize \u5df2\u5168\u90e8\u843d\u5730") \
    == 2, "anchor landed-set faces"
# new-value presence
assert "FIFTY-FOURTH" in out_t and "\u7b2c\u4e94\u5341\u56db\u4f8b" in out_t
assert out_t.count("n1_w194") == 4, "n1_w194 count drift"
assert out_t.count("MSG-2026-10-09-0627-bma-w194-seat") == 3
assert out_t.count("W195+ \u6295\u5f71") == 3
assert "441_604..443_603" in out_t and "443_604..443_803" in out_t
assert "443_604..445_603" in out_t and "443_804..444_003" in out_t
assert "424,720" in out_t and "\u7b2c 184 \u6ce2" in out_t
assert "\u7b2c\u4e00\u767e\u96f6\u4e5d\u679a" in out_t
assert "\u6cf5\u7b2c 192 \u679a" in out_t
assert "\u6ce2\u53f7 194=\u6ce8\u518c\u8868 W193 \u5e2d\u540e\u9996\u4e2a" \
    "\u81ea\u7531\u53f7" in out_t
assert "W194-only" in out_t
print("  vmap simulation: residual-zero, malformed-zero, stale-sweep CLEAN")
print("DRY GATE: ALL GREEN (zero writes performed)")


# --- emit the build script ----------------------------------------------
def q(s):
    return repr(s)


tok_lit = "[\n" + ",\n".join("    (%s, %s)" % (q(o), q(t))
                             for o, t in TOK) + ",\n]"
back_lit = "{\n" + ",\n".join("    %s: %s" % (q(k), q(v))
                              for k, v in BACK.items()) + "\n}"
emit_src = '''# -*- coding: utf-8 -*-
"""r903 bm-a W194 per-wave prereg build (EMITTED by
results/_r903bma_w194_buildgen.py; pairs baked; live facts re-asserted
at run time per r587).  Src = results/_r903bma_w194_prereg_src.txt
(W193 prereg freeze-time blob 5512a886a, byte-verbatim binary extract,
r877 law 4).  Output CRLF (r370 law)."""
import io
import json
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
SRC = "results/_r903bma_w194_prereg_src.txt"
OUT = "research/PERPETUAL_N1_W194_PREREG.md"
G = r"%s"

def git(*a):
    r = subprocess.run(["git", "-C", G] + list(a), capture_output=True)
    return r.stdout.decode("utf-8", errors="replace").strip()

subprocess.run(["git", "-C", G, "fetch", "origin"], capture_output=True)
probe = json.load(open(r"results/_r902bma_w194_probe_receipt.json",
                      encoding="utf-8"))
assert probe["verdict"] == "ADMIT" and probe["bands"] == {
    "A": "441604_443603", "B": "443604_443803"}, probe
leg0 = probe["legs"]["leg0"]
assert leg0["rows"] == 191 and leg0["tail"] == "W193" and \\
    leg0["w191_ledger_head"] == 833536, leg0
assert leg0["ordinal"] == 184 and leg0["bma_ordinal"] == 109, leg0
res = json.load(open(r"results/perpetual_faces/n1_w191_results.json",
                     encoding="utf-8"))
assert res["null_pool_cumulative"]["merged"]["n_values"] == 418120
assert res["science_gates"]["ledger"]["total"] == 833536
_vac = git("log", "origin/main", "--format=%%h", "-n", "1", "-S",
           '194: {"a": (441_604', "--", "scripts/perpetual_faces.py")
assert _vac == "", "W194 five-face already on origin?!"
_fin192 = git("ls-tree", "origin/main",
              "results/perpetual_faces/n1_w192_results.json")
assert _fin192 == "", "W192 finalize landed -- anchor must roll (r590)!"
_fin193 = git("ls-tree", "origin/main",
              "results/perpetual_faces/n1_w193_results.json")
assert _fin193 == "", "W193 finalize landed -- anchor must roll (r590)!"

sys.path.insert(0, "scripts")
sys.path.insert(0, ".")
import science_gates as _sg  # noqa: E402
REG_N = len(_sg.SEED_REGISTRY)
assert REG_N == 191, "SEED_REGISTRY count drift: %%d" %% REG_N

TOK = %s
BACK = %s

src = io.open(SRC, encoding="utf-8").read()
assert src.count("\\r\\n") == 0, "src blob expected LF"
assert src.count("SEED_REGISTRY \\u5168\\u952e 191 \\u503c") == 1, \\
    "registry-count face not found in src"
src = src.replace("SEED_REGISTRY \\u5168\\u952e 191 \\u503c",
                  "SEED_REGISTRY \\u5168\\u952e @@REGN@@ \\u503c")
out_t = src
for old, tok in TOK:
    n = out_t.count(old)
    assert n == 1, "TOK %%s count=%%d" %% (tok, n)
    out_t = out_t.replace(old, tok)
for tok, new in BACK.items():
    out_t = out_t.replace(tok, new)
out_t = out_t.replace("SEED_REGISTRY \\u5168\\u952e @@REGN@@ \\u503c",
                      "SEED_REGISTRY \\u5168\\u952e %%d \\u503c" %% REG_N)
resid = re.findall(r"@[A-Z0-9]+@", out_t)
assert not resid, "unsubstituted tokens remain: %%s" %% resid[:5]
bad = [mm.group() for mm in
       re.finditer(r"(\\d{3})_(\\d{3})\\.(\\d{3})_(\\d{3})", out_t)
       if int(mm.group(3)) < int(mm.group(1))]
assert not bad, "malformed windows: %%s" %% bad[:4]
assert out_t.count("PERPETUAL-N1-W194") == 3, "batch id count drift"
M = "\\u2212"
for stale in ("FIFTY-THIRD", "\\u7b2c\\u4e94\\u5341\\u4e09\\u4f8b",
              "439_204..441_203", "439_404..441_403", "439_204..439_403",
              "439_404..439_603", "439_404+j", "441_404+j",
              "**B-ext exit seed=441_404..441_603**",
              "PERPETUAL-N1-W193", "PERPETUAL_N1_W193_PREREG",
              "n1_w193", "MSG-2026-10-09-0458", "9df3078c5",
              "engine_owner==bm-a 107", "engine_owner==bm-a \\u884c 107",
              "\\u7b2c 183 \\u6ce2", "\\u7b2c\\u4e00\\u767e\\u96f6\\u516b"
              "\\u679a", "\\u6cf5\\u7b2c 191 \\u679a",
              "\\u6ce2\\u53f7 193=", "\\u6ce8\\u518c\\u8868 W192 \\u5e2d\\u540e",
              "\\u5168\\u4e00\\u767e\\u4e5d\\u5341\\u884c", "422,520",
              "W2..W192", "W193-only", "\\u5f85 W193 finalize \\u7a97",
              "W194+ \\u6295\\u5f71", "r900 \\u5e2d\\u4f4d",
              "r900 probe \\u5355\\u8dd1", "r900 seat push",
              "r900 W193 probe", "\\u884c 182 \\u6ce8\\u518c\\u5728\\u518c",
              "W192 finalize \\u5728\\u98de", "r901\\u00b7buildgen"):
    assert stale not in out_t, "stale token survives: %%r" %% stale
assert M+"0.0929" in out_t and M+"0.0898" in out_t, "U+2212 forms"
assert out_t.count("W190 0.000380") == 1
assert "W191=bm-a r894 freeze\\uff08e5e4af81b\\uff09" in out_t
assert "\\uff1bW192=bm-c r787 freeze\\uff08f8703842c\\uff09\\uff1bW193=bm-a " \\
    "r901 freeze\\uff085cf0d6175\\uff09\\u3002" in out_t
assert out_t.count("n1_w194") == 4
assert "FIFTY-FOURTH" in out_t

open(OUT, "wb").write(out_t.replace("\\n", "\\r\\n").encode("utf-8"))
chk = io.open(OUT, encoding="utf-8", newline="").read()
assert chk == out_t.replace("\\n", "\\r\\n"), "CRLF roundtrip drift"
print("W194 prereg built: %%s bytes=%%d crlf=%%d" %%
      (OUT, len(chk.encode("utf-8")), chk.count("\\r\\n")))
print("post-transform asserts PASS (counts, residue-zero, "
      "malformed-zero, stale-sweep CLEAN, U+2212 forms)")
''' % (G, tok_lit, back_lit)
io.open(EMIT, "w", encoding="utf-8", newline="\n").write(emit_src)
print("EMITTED:", EMIT, len(emit_src), "bytes")
print("buildgen complete: DRY gate green -> emitted build script (run it next)")
