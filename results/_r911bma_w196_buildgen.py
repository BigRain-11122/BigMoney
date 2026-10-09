# -*- coding: utf-8 -*-
"""r911 bm-a W196 per-wave prereg BUILDGEN (clean-window anchor roll).

Bloodline: r830 (E41 buildgen surgery) / r833 prereg-build three laws
(AST no-exec prior-gen / DRY full-file gate zero-write-first /
U+2212 display anchor forms) / r877 (binary src extraction) /
r893 W191 buildgen (two-phase vmap, composites first, numerals LAST) /
r904 W194 buildgen v2 (r590 anchor-roll realization) / r908 W195
buildgen (clean window) / r911 W196 buildgen (clean window:
W195 finalize landed BEFORE build r910 one-pass; zero in-flight
seats, no v1 self-detonation face).

OLD-SIDE ZERO-TRANSCRIBE LAW (r587 machine-derived, this wave's
realization): the 40 TOK old sides are NOT hand-copied.  They are
machine-extracted by ast.literal_eval of the W195 buildgen's BACK
dict (results/_r908bma_w195_buildgen.py module-level assignment) --
those 40 values are byte-identical to the physical W195 src text
(the W195 emitted build script wrote them verbatim), and each is
count==1-verified against the src in the DRY gate below.  Only the
NEW sides (BACK below) are constructed, from live-asserted facts.

Src: research/PERPETUAL_N1_W195_PREREG.md freeze-time blob (commit
b9b962672, W195 five-face freeze window).  Extracted byte-verbatim
(binary, LF, 20939B) to results/_r911bma_w196_prereg_src.txt (r877
law 4).

r587 machine-derived facts (live-asserted inside, zero transcribe):
  - r910 pre-seat probe results/_r910bma_w196_probe_receipt.json ADMIT
    (bands A 446_004..448_003 hops=1 staircase FIFTY-SIXTH;
     B 448_004..448_203 hops=1 W141 same-freeze mutual exclusion;
     naive A 445_804..447_803 refused at start by registered W195 B;
     naive B 446_004..446_203 lands inside own-wave A window);
  - W195 finalize results/perpetual_faces/n1_w195_results.json (ON
    ORIGIN, ls-tree machine-checked): ledger prev 841,145 / +2,200 =
    843,345; K=426,920; merged mu -0.09285038 (4dp -0.0929 display);
    w195-only -0.09697859 (4dp -0.0970); sigma 0.245069; se_mu 0.000375;
    A p95 0.3078; K-lift -0.0001 (line 1.1874->1.1873);
    n_eff_held_equal 841,145;
  - W196 seat MSG fleet/inbox/MSG-2026-10-09-1007-bma-w196-seat.md
    pushed origin 01992cd42 (r910 seat push, r565 law);
  - W194 five-face freeze 82670b0ba / W195 five-face freeze b9b962672
    on origin;
  - W196 five-face vacancy held on origin (machine-checked).
"""
import ast
import io
import json
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
SRC = "results/_r911bma_w196_prereg_src.txt"
OUT = "research/PERPETUAL_N1_W196_PREREG.md"
EMIT = "results/_r911bma_w196_prereg_build.py"
GEN195 = "results/_r908bma_w195_buildgen.py"
G = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"
GIT = r"C:\Program Files\Git\cmd\git.exe"
M = "\u2212"  # U+2212 display minus


def git(*a):
    r = subprocess.run([GIT, "-C", G] + list(a), capture_output=True)
    return r.stdout.decode("utf-8", errors="replace").strip()


# --- machine-derived facts (r587) --------------------------------------
subprocess.run([GIT, "-C", G, "fetch", "origin"], capture_output=True)
probe = json.load(open(r"results/_r910bma_w196_probe_receipt.json",
                       encoding="utf-8"))
assert probe["verdict"] == "ADMIT", probe["verdict"]
assert probe["bands"] == {"A": "446004_448003", "B": "448004_448203"}, \
    probe["bands"]
leg0, leg1 = probe["legs"]["leg0"], probe["legs"]["leg1"]
leg4 = probe["legs"]["leg4"]
assert leg1["A"] == [446004, 448003] and leg1["B"] == [448004, 448203], leg1
assert leg1["hops_A"] == 1 and leg1["hops_B"] == 1, leg1
assert leg1["ARITH_A"] == [445804, 447803], leg1["ARITH_A"]
assert leg1["B_naive_first_clean"] == [446004, 446203], leg1
assert leg1["B_hop_chain"][0] == {"hop": 1, "window": [446004, 446203],
                                  "jump_to": 448004}, leg1["B_hop_chain"]
assert leg0["rows"] == 193 and leg0["tail"] == "W195", leg0
assert leg0["ordinal"] == 186 and leg0["bma_ordinal"] == 111, leg0
assert leg0["owner_rows"] == 185 and leg0["bma_rows"] == 110, leg0
assert probe["legs"]["leg2"]["conflicts"] == 0, probe["legs"]["leg2"]
assert probe["legs"]["leg3"]["origin_vacancy"] is True, probe["legs"]["leg3"]
assert leg4["W197p_A"] == "448004..450003" and \
    leg4["W197p_B"] == "448204..448403", leg4
assert leg4["W197p_B_lands_inside_W197p_A"] is True, leg4
assert "FIFTY-SIXTH" in leg1["A_semantics"], leg1["A_semantics"]

res = json.load(open(r"results/perpetual_faces/n1_w195_results.json",
                     encoding="utf-8"))
npc = res["null_pool_cumulative"]
kl = res["skill_line_v2_k_lift"]
assert npc["merged"]["n_values"] == 426920, "K drift"
assert res["science_gates"]["ledger"]["total"] == 843345, "ledger head"
assert res["science_gates"]["ledger"]["prev_total"] == 841145, "ledger prev"
assert npc["se_mu_at_k426920"] == 0.000375, "se_mu drift"
assert kl["n_eff_held_equal"] == 841145, kl
assert abs(kl["line_delta_k_lift"] - (-0.0001)) < 1e-12, kl
assert abs(kl["line_pre_w195"] - 1.1874) < 1e-9 and \
    abs(kl["line_merged_426920"] - 1.1873) < 1e-9, kl
assert res["families"]["A_random_engine_exit"]["full_sharpe_p95"] == 0.3078
MU4 = ("%.4f" % npc["merged"]["mu"]).replace("-", M)
WONLY4 = ("%.4f" % npc["w195_only"]["mu"]).replace("-", M)
SIG6 = "%.6f" % npc["merged"]["sigma"]
assert MU4 == M + "0.0929" and WONLY4 == M + "0.0970" and SIG6 == "0.245069", \
    (MU4, WONLY4, SIG6)

W194_FF = git("log", "origin/main", "--format=%h", "-n", "1", "-S",
              '194: {"a": (441_604', "--", "scripts/perpetual_faces.py")
assert W194_FF == "82670b0ba", W194_FF
W195_FF = git("log", "origin/main", "--format=%h", "-n", "1", "-S",
              '195: {"a": (443_804', "--", "scripts/perpetual_faces.py")
assert W195_FF == "b9b962672", W195_FF
SEAT = git("log", "origin/main", "--format=%h", "-n", "1", "--diff-filter=A",
           "--", "fleet/inbox/MSG-2026-10-09-1007-bma-w196-seat.md")
assert SEAT == "01992cd42", SEAT
_vac = git("log", "origin/main", "--format=%h", "-n", "1", "-S",
           '196: {"a": (446_004', "--", "scripts/perpetual_faces.py")
assert _vac == "", "W196 five-face already on origin?!"
_fin194 = git("ls-tree", "origin/main",
              "results/perpetual_faces/n1_w194_results.json")
assert _fin194 != "", "W194 finalize NOT landed -- key-order face broken!"
_fin195 = git("ls-tree", "origin/main",
              "results/perpetual_faces/n1_w195_results.json")
assert _fin195 != "", "W195 finalize NOT landed -- anchor must roll r590!"
print("facts: ALL GREEN (anchor=W195 LANDED; W194/W195 finalize both on "
      "origin; W196 five-face vacancy held; seat 01992cd42)")

# live SEED_REGISTRY count (masked pre-TOK like r893 @@REGN@@ pattern)
sys.path.insert(0, "scripts")
sys.path.insert(0, ".")
import science_gates as _sg  # noqa: E402
REG_N = len(_sg.SEED_REGISTRY)
assert REG_N >= 194, "SEED_REGISTRY count below freeze face: %d" % REG_N
_waveseeds = []
for _k, _v in _sg.SEED_REGISTRY.items():
    if isinstance(_v, int):
        _waveseeds.append(_v)
    elif isinstance(_v, (list, tuple, range)):
        _waveseeds.extend(int(x) for x in _v)
_overlap = [s for s in _waveseeds if 446004 <= s <= 448203]
assert not _overlap, "seed registry overlaps W196 band: %s" % _overlap[:5]
print("REG_N=%d; W196 band zero-overlap machine-checked" % REG_N)

# --- src load -----------------------------------------------------------
src = io.open(SRC, encoding="utf-8").read()
assert src.count("\r\n") == 0, "src blob expected LF"
assert "PERPETUAL-N1-W195" in src and "443_804..445_803" in src, \
    "src face drift"
assert src.count("SEED_REGISTRY \u5168\u952e 194 \u503c") == 1, \
    "registry-count face not found in src (live count face)"
src_t = src.replace("SEED_REGISTRY \u5168\u952e 194 \u503c",
                    "SEED_REGISTRY \u5168\u952e @@REGN@@ \u503c")

# --- OLD-SIDE machine extraction: eval-parse W195 buildgen BACK dict ----
# The W195 BACK literal concatenates four live names (CHAIN_NEW / MU4 /
# WONLY4 / SIG6 / M).  Those names were bound to the W195 buildgen's OWN
# anchor values = the W194 finalize actuals (n1_w194_results.json), NOT
# the W195 values used in this wave's NEW sides.  Re-derive them
# machine-side from the W194 results file; the DRY gate count==1 check
# below is the hard verifier that they match the physical src.
gen195_src = io.open(GEN195, encoding="utf-8").read()
_tree = ast.parse(gen195_src)
BACK195 = None
for _node in ast.walk(_tree):
    if isinstance(_node, ast.Assign) and any(
            getattr(_t, "id", None) == "BACK" for _t in _node.targets):
        _res4 = json.load(open(
            r"results/perpetual_faces/n1_w194_results.json",
            encoding="utf-8"))
        _npc4 = _res4["null_pool_cumulative"]
        MU4_195 = ("%.4f" % _npc4["merged"]["mu"]).replace("-", M)
        WONLY4_195 = ("%.4f" % _npc4["w194_only"]["mu"]).replace("-", M)
        SIG6_195 = "%.6f" % _npc4["merged"]["sigma"]
        assert (MU4_195 == M + "0.0928" and WONLY4_195 == M + "0.0881"
                and SIG6_195 == "0.245098"), \
            (MU4_195, WONLY4_195, SIG6_195)
        _chain = re.search(
            r"W118=bm-b r678 freeze\uff08565e5b0b4\uff09.*?"
            r"W194=bm-a r905 freeze\uff0882670b0ba\uff09", src_t)
        assert _chain, "chain span not found in W195 src"
        _ns = {"CHAIN_NEW": _chain.group(), "MU4": MU4_195,
               "WONLY4": WONLY4_195, "SIG6": SIG6_195, "M": M}
        BACK195 = eval(compile(ast.Expression(_node.value),
                               GEN195, "eval"), _ns)
        break
assert BACK195 is not None, "BACK dict not found in W195 buildgen"
assert len(BACK195) == 40, "BACK195 entry count drift: %d" % len(BACK195)
ORDER = ["CHAIN", "TITLE", "SEATBLOCK", "AFACE", "BFACE", "ANCHOR0",
         "S5ANCH", "S55", "S51", "S52", "S53", "S54", "GATEW2", "ASEED",
         "BSEED", "ENGNOTE", "CLAIM", "S8", "S7", "SCANFACE", "R250",
         "PRCR", "RUNNERW", "BATCHNAME", "POOL", "MATCOND", "GATECMD",
         "BENTRY", "PROBEW", "DISJ", "POOL4", "LEDGER", "CLI", "ENG6",
         "SHARD", "RFN", "FINPRE", "EOBD", "BGATE", "WAVEFREE"]
assert sorted(ORDER) == sorted(k.strip("@") for k in BACK195), \
    "ORDER vs BACK195 keyset drift"
TOK = [(BACK195["@" + k + "@"], "@" + k + "@") for k in ORDER]
print("OLD SIDES: %d pairs machine-extracted from W195 buildgen BACK "
      "(eval-parsed literals + live-name injection, zero transcribe)"
      % len(TOK))

# --- W196 NEW sides (constructed from live facts) -----------------------
BACK = {
    "@CHAIN@": BACK195["@CHAIN@"] +
               "\uff1bW195=bm-a r909 freeze\uff08b9b962672\uff09",
    "@TITLE@": (
        "# PERPETUAL-N1-W196 \u9884\u6ce8\u518c \u00b7 N1 nulls-deepening "
        "\u6cf5\u7b2c 194 \u679a\uff08never-dry \u5e38\u4f9b\u7ed9\u4f8b"
        "\u6ce2\u00b7\u6ce2\u5e8f\u53f7\u8fde\u7eed\u00b7\u673a\u9762 "
        "derive\uff1aengine_owner \u884c 185 \u6ce8\u518c\u5728\u518c+"
        "W194/W195 finalize \u5df2\u843d\u8d26\u00b7anchor \u6eda\u52a8"
        "\u5df2\u5151\u73b0\uff08r590\uff09+\u672c\u5019\u9009=bm-a "
        "\u7b2c\u4e00\u767e\u4e00\u5341\u4e00\u679a\u81ea\u6709\u6ce2"
        "\u3010bm-a r911\u00b7buildgen \u8840\u7edf r830/r833/r877/r908 "
        "\u627f\u88ad\u00b7\u5e72\u51c0\u7a97 anchor=W195 \u5b9e\u6d4b "
        "r590 \u6eda\u52a8\u5151\u73b0\u3011\uff09"),
    "@SEATBLOCK@": (
        "\u3010\u672c\u51bb\u7ed3\u7a97 fetch \u5b9e\u6838\u8868\u5c3e"
        "\u65f6 W196 \u53f7\u4f4d\u7a7a\u6863\u00b7rg \u884c WAVE_CONFIGS+"
        "prereg \u8def\u5f84\u4e09\u67e5+origin ls-tree vacancy \u673a"
        "\u8bc1\uff08\u672c\u7a97 probe leg3 \u5b9e\u8dd1\uff09\uff1b"
        "\u5168 inbox/processed/ W196 \u5e2d\u4f4d\u96f6\u5916\u673a\u547d"
        "\u4e2d\uff1b**W194=bm-a r905 \u4e94\u9762\u51bb\u7ed3 82670b0ba "
        "\u5728\u518c\u00b7finalize \u5df2\u843d origin\uff08r906 one-pass "
        "bd1f515f2\u00b7\u8d26\u672c 841,145 EXACT \u96f6\u504f\u79bb"
        "\uff09+W195=bm-a r909 \u4e94\u9762\u51bb\u7ed3 b9b962672 \u5728"
        "\u518c\u00b7finalize \u5df2\u843d origin\uff08r910 one-pass "
        "a0b16d1d8\u00b7\u8d26\u672c 843,345 EXACT \u96f6\u504f\u79bb"
        "\uff09\u2014\u2014\u8d77\u7a3f\u7a97\u6ce8\u518c\u5b87\u5b99="
        "W194/W195 \u6ce8\u518c\u5e26\u5728\u518c+\u53cc finalize \u843d"
        "\u8d26\uff08N1_BANDS \u6ce8\u518c\u884c\u673a\u5668\u8bfb\u00b7"
        "probe leg0 \u673a\u8bc1 193 \u884c\u8868\u5c3e W195\uff09\u00b7"
        "r910 W196 probe \u5168\u817f\u673a\u8bc1**\uff1b"
        "\u672c\u673a\u5e2d\u4f4d\u516c\u793a=MSG-2026-10-09-1007-bma-"
        "w196-seat \u5df2\u63a8 origin 01992cd42 \u5148\u4e8e\u672c\u51bb"
        "\u7ed3\u3010r565 \u5f8b\u00b7\u63a8\u9001\u7a97=r910 seat push "
        "\u76f4\u63a5\u5feb\u8fdb\u9001\u8fbe 01992cd42\uff08payload=seat "
        "MSG+W196 pre-seat probe \u811a\u672c+\u56de\u6267\u540c\u63a8"
        "\uff09\uff1bself-ack inbox\u2192processed \u79fb\u4f4d\u968f\u4e94"
        "\u9762\u51bb\u7ed3\u7a97\u6536\u53e3\u5f52\u6863\uff08\u5982\u5b9e"
        "\u6ce8\u8bb0\uff09\u3011\u3011"),
    "@AFACE@": (
        "\u672c\u6ce2 **A-ext seed=446_004..448_003**\uff08**A \u9762="
        "FIRST-CLEAN past prior-wave B \u9636\u68af\u7b2c\u4e94\u5341"
        "\u516d\u4f8b**\uff1aA \u9762\u7b97\u672f\u7ee7\u7eed\u5e26 "
        "445_804..447_803 \u5728\u5176\u8d77\u70b9\u5373\u88ab W195 \u6ce8"
        "\u518c B \u5e26 445_804..446_003 **\u62d2**\uff08W195 \u00a75.5 "
        "\u6295\u5f71+r907 probe leg4 \u53cc\u6e90\u9884\u8a00+\u5f3a\u5236"
        "\u00b7r910 probe \u56de\u6267 A_semantics \u673a\u8bfb\u53cc"
        "\u5151\u73b0\uff09\u2192 \u8bda\u5b9e\u524d\u5411\u8d70 **1 "
        "hop** \u843d **446_004..448_003**\u00b7**A base==\u524d\u6ce2 B "
        "\u5c3e+1\uff08446_003+1\uff09\u673a\u68c0\u5173\u7cfb**=**A-"
        "hops-prior-B \u9636\u68af\u51e0\u4f55\u7b2c\u4e94\u5341\u516d"
        "\u4f8b\uff08E36 \u5361\uff09**\u00b7\u975e\u8f6e\u8f6c r587 "
        "\u524d\u5411\u5355\u8c03\u65ad\u8a00\u5728\u8d70\u518c\uff1b\u5e8f"
        "\u6570\u9762\u5982\u5b9e\u62ab\u9732\uff1aW195 \u00a75.5 \u6295"
        "\u5f71\u9884\u544a\u7b2c\u4e94\u5341\u516d\u4f8b\u00b7\u672c\u7a97 "
        "probe \u56de\u6267 A_semantics \u673a\u8bfb\u5e8f\u6570="
        "FIFTY-SIXTH\uff08\u7b2c\u4e94\u5341\u516d\u4f8b\uff09\u00b7\u672c"
        "\u4ef6\u6309\u56de\u6267\u5e8f\u6570\u9762\u8bb0\u8f7d\u975e"
        "\u8f6c\u6284\uff08r587\uff09\u00b7\u6295\u5f71\u4e0e\u56de\u6267"
        "\u4e24\u8bfb\u6cd5\u6052\u540c\uff09"),
    "@BFACE@": (
        "**B-ext exit seed=448_004..448_203**\uff08**B \u9762=FIRST-CLEAN "
        "past own-wave A**\uff1aB \u9762\u7b97\u672f\u7ee7\u7eed\u5e26 "
        "446_004..446_203 \u5728\u58f0\u660e\u5b87\u5b99\u4e0a CLEAN \u4f46"
        "**\u843d\u5728\u672c\u6ce2 A \u7a97 446_004..448_003 \u5185**"
        "\uff08**\u540c\u7a97\u4e92\u65a5\u9762 leg2 \u5f8b\u00b7W141 "
        "\u5148\u4f8b**\uff1aA \u4e0e B \u540c\u4e00\u51bb\u7ed3 commit "
        "\u53cc\u6ce8\u518c\u00b7\u4e92\u65a5\u65ad\u8a00\u5f3a\u5236 B "
        "\u8d8a\u8fc7\u672c\u6ce2 A \u7a97\uff09\u2192 B \u5e26\u672c"
        "\u6ce2 A \u7a97\u4fdd\u7559\u8d70 **1 hop** \u843d **448_004.."
        "448_203**\u00b7**B base==\u672c\u6ce2 A \u5c3e+1\uff08448_003+1"
        "\uff09\u673a\u68c0\u5173\u7cfb**\u00b7hop \u94fe\u9010\u8df3"
        "\u5728 probe \u56de\u6267\uff1b**W195 \u00a75.5 \u6295\u5f71+"
        "r908 prereg leg4 \u627f\u63a5\u9762\u6ce8\u8bb0\u5151\u73b0**"
        "\uff1a\u6295\u5f71\u9884\u8a00 W196 \u987b\u5728 post-W195 \u6ce8"
        "\u518c\u5b87\u5b99\u91cd derive \u4e14 derive B \u65f6\u9884"
        "\u7559\u672c\u6ce2 A \u7a97\u2014\u2014\u672c\u7a97\u53cc\u9762"
        "\u5151\u73b0\u00b7A \u88ab\u62d2+\u9636\u68af\u8d8a\u5e26\u5982"
        "\u6295\u5f71\u6240\u671f\u00b7B \u540c\u7a97\u4e92\u65a5\u4fdd"
        "\u7559=\u6295\u5f71\u6240\u671f\u00b7\u5df2\u5982\u5b9e\u62ab"
        "\u9732\u975e\u5206\u53c9\uff09"),
    "@ANCHOR0@": (
        "\u8d77\u7a3f\u7a97\u5b9e\u51b5\uff1a**W1..W195 N1 finalize \u5df2"
        "\u5168\u90e8\u843d\u5730**\u3010\u51c0\u8d26\u672c\u951a\u5934 "
        "**843,345**\u00b7K=426,920 \u5408\u5e76\u6c60\u00b7n1_w195_"
        "results.json \u673a\u8bfb\uff08origin \u5728\u518c\uff09\u3011"
        "\uff1bW196=\u672c\u7a97\u5019\u9009\uff08\u5e2d\u4f4d\u5df2\u63a8 "
        "01992cd42\uff09\u2014\u2014**\u96f6\u5728\u98de\u4e0a\u6e38\u5e2d"
        "**\u00b7anchor=\u6700\u65b0\u5df2\u843d\u8d26\u952e\uff08W195 "
        "\u5b9e\u6d4b\u00b7r590 \u6eda\u52a8\u5df2\u5151\u73b0\uff1aW195 "
        "finalize \u5df2\u843d origin a0b16d1d8\uff08r910 one-pass\u00b7"
        "\u8d26\u672c 843,345 EXACT \u96f6\u504f\u79bb\uff09\u00b7\u8d77"
        "\u7a3f\u7a97\u5e72\u51c0\u7a97\u96f6\u5728\u98de\u4e0a\u6e38"
        "\u5e2d\u00b7r908 v2 \u540c\u5f8b\u00b7\u65e0 v1 \u81ea\u7206"
        "\u9762\uff09"),
    "@S5ANCH@": (
        "\uff08\u8d77\u7a3f\u7a97\u5b9e\u51b5\u6ce8\u8bb0\uff1a**W1.."
        "W195 N1 finalize \u5df2\u5168\u90e8\u843d\u5730**\u2014\u2014"
        "\u51c0\u8d26\u672c\u951a\u5934 843,345\u00b7**K=426,920 \u5408"
        "\u5e76\u6c60**\u00b7**\u96f6\u5728\u98de\u4e0a\u6e38\u5e2d\uff08"
        "W194/W195 finalize \u5747\u5df2\u843d origin\u00b7ls-tree \u673a"
        "\u8bc1\uff09**\u2014\u2014\u672c\u6ce2 \u00a75 \u9884\u6d4b\u952e"
        "=**W195 \u5b9e\u6d4b\u503c**\u3010results/perpetual_faces/"
        "n1_w195_results.json\u00b7N1 \u9762\u6700\u65b0\u5df2\u843d\u8d26"
        "\u952e\u00b7origin \u5728\u518c\u673a\u8bc1\u3011"),
    "@S55@": (
        "5. **W197+ \u6295\u5f71\uff08probe \u673a\u8bc1\u00b7\u4e0b"
        "\u6ce2\u51bb\u7ed3\u65b9\u590d\u6838\u975e\u8f6c\u6284 r587 "
        "\u5f8b\uff09**\uff1aA first-clean 448_004..450_003 **CLEAN**"
        "\uff08hops=0\uff09\uff1bB first-clean **448_204..448_403 "
        "CLEAN**\uff08hops=0\uff09\u2014\u2014**naive B \u843d\u5728 "
        "naive A \u7a97\u5185**\uff08W141 \u540c\u7a97\u4e92\u65a5\u5148"
        "\u4f8b\u9002\u7528\u4e8e W197\uff1aW197 \u51bb\u7ed3\u65b9\u5fc5"
        "\u987b\u5728 post-W196 \u6ce8\u518c\u5b87\u5b99\u91cd derive "
        "\u4e14 derive B \u65f6\u9884\u7559\u672c\u6ce2 A \u7a97\u2014"
        "\u2014leg2 \u5f8b/E36 \u5361\uff09\uff1b**W196 B \u5e26 "
        "448_004..448_203 \u6ce8\u518c\u540e\u5c06\u62d2 naive W197 A "
        "\u7a97**\u2014\u2014W197 A \u91cd derive \u540c\u5f3a\u5236"
        "\uff08\u8d8a\u8fc7 W196 B \u5e26\u00b7\u9636\u68af A-hops-prior-B "
        "\u7ee7\u627f\u7b2c\u4e94\u5341\u4e03\u4f8b\uff09\uff1bverify at "
        "W197 prereg\uff0chop \u94fe\u9010\u8df3\u5728 probe \u56de\u6267"),
    "@S51@": (
        "1. W196-only mu \u4e0e\u7d2f\u8ba1\u6c60 merged mu\uff08W195 "
        "\u5b9e\u6d4b\u952e **" + MU4 + "**\u00b7K=426,920 \u5408\u5e76"
        "\u6c60\u00b7W195-only \u5b9e\u6d4b **" + WONLY4 + "**\uff09\u5dee"
        "\u5f02 **|\u0394|<0.02**\uff08W2..W195 \u5171\u4e00\u767e\u4e5d"
        "\u5341\u4e94\u9762\u5b9e\u6d4b mu \u7a33\u5b9a\u5148\u4f8b\u00b7"
        "\u5355\u6ce2\u8de8\u952e\u5fae\uff09"),
    "@S52@": (
        "2. sigma \u76f8\u5bf9\u53d8\u5316 **<\u00b110%**\uff08\u540c"
        "\u8bbe\u8ba1\u540c\u7a97\u00b7\u7eaf\u62bd\u6837\u6ce2\u52a8"
        "\uff1b\u952e **" + SIG6 + "**=W195 \u5408\u5e76\u6c60\u5b9e\u6d4b "
        + SIG6 + "\uff09\u3002"),
    "@S53@": (
        "3. A \u6863 full_sharpe_p95 \u4e0e W195 A \u6863 p95\uff08**"
        "0.3078** \u5b9e\u6d4b\u951a\uff09\u5dee **<0.05**\uff08\u95e8"
        "\u6807\u6ce8\u6cd5 W5..W195 \u5148\u4f8b\uff1a\u7ed3\u679c\u77e5"
        "\u60c5\u9762\u4ec5\u4f5c\u673a\u5668\u65ad\u8a00\u4e4b\u7528"
        "\u00b7\u6d4b\u91cf\u9762\u975e\u6ce8\u518c\u5229\u76ca\uff09\u3002"),
    "@S54@": (
        "4. K-lift \u7ebf\u79fb\u52a8\u5e45\u5ea6 **\u2264\u00b10.02**"
        "\uff08\u7d2f\u8ba1\u6c60\u52a0\u6df1\u96f6 se_mu \u6536\u7a84\u7ebf"
        "\u81ea mu/sigma \u5fae\u8c03\u9762\u975e\u8d28\u53d8\u2014\u2014"
        "W136..W195 \u5148\u4f8b\u94fe\u62ab\u9732\u3010W189 +0.0003/"
        "W190 " + M + "0.0001/W191 +0.0001/W192 **" + M + "0.0002**/W193 "
        "**" + M + "0.0001**/W194 **+0.0000**/W195 **" + M + "0.0001**"
        "\u00b7\u952e W195 \u5b9e\u6d4b K-lift **" + M + "0.0001**\u00b7"
        "line_merged@K426,920 **1.1873**\u00b7line_pre 1.1874\u00b7n_eff "
        "841,145\uff1bse_mu \u6536\u7a84\u94fe W191 0.000379\u2192W192 "
        "0.000378\u2192W193 0.000377\u2192W194 0.000376\u2192W195 **"
        "0.000375**\u3011\uff09\u3002"),
    "@GATEW2@": (
        "\u672c\u6ce2\u673a\u9a8c ADMIT \u56de\u6267\u5728\u573a=_r910bma_"
        "w196 \u63a2\u9488\u7a97\uff08pre-seat probe \u5355\u7a97\u00b7"
        "gate \u817f\u5408\u5e76\u7ed3\u6784\u627f\u88ad r812/r820/r823 "
        "\u5148\u4f8b\u00b7parity N/A \u8bda\u5b9e\u6ce8\u8bb0\uff09\uff1b"
        "selftest W196 face\uff08A=first-clean past prior-wave B \u6052"
        "\u7b49\u00b7B=first-clean past own-wave A \u6052\u7b49+\u540c"
        "\u7a97\u4e92\u65a5\u65ad\u8a00\u00b7W195 \u884c parity \u817f"
        "\u3010r735 \u6d4b\u91cf-\u5b9e\u73b0\u5206\u53c9\u65cf\u9632"
        "\u62a4\u9762\uff1aA/B \u7a97 set-range \u9488\u5728\u573a\u3011"
        "\uff09\u968f\u4e94\u9762\u51bb\u7ed3\u843d\u5730"),
    "@ASEED@": (
        "entry rng seed=**446_004+j**\uff08\u6cd5\u5178 \u00a74 W196 "
        "\u884c A=446_004..448_003\u00b7**FIRST-CLEAN past prior-wave B "
        "\u9636\u68af\u7b2c\u4e94\u5341\u516d\u4f8b**\uff1a\u7b97\u672f"
        "\u7eed\u5e26 445_804..447_803 \u8d77\u70b9\u5373\u88ab W195 "
        "\u6ce8\u518c B \u5e26\u62d2\u21921 hop \u843d 446_004..448_003"
        "\u00b7A base==\u524d\u6ce2 B \u5c3e+1 \u673a\u68c0\u5173\u7cfb"
        "\u00b7E36 \u5361\u00b7hops=1\u00b7ADMIT \u56de\u6267\u5728\u573a"
        "\uff09"),
    "@BSEED@": (
        "exit rng=**448_004+j**\uff08\u6cd5\u5178 \u00a74 W196 \u884c "
        "B=448_004..448_203\u00b7**FIRST-CLEAN past own-wave A**\uff1a"
        "B \u7b97\u672f\u7eed\u5e26 446_004..446_203 \u5728\u58f0\u660e"
        "\u5b87\u5b99\u4e0a CLEAN \u4f46\u843d\u5728\u672c\u6ce2 A \u7a97 "
        "446_004..448_003 \u5185\u2192**\u540c\u7a97\u4e92\u65a5\u9762 "
        "leg2 \u5f8b\u00b7W141 \u5148\u4f8b**\u5f3a\u5236 B \u8d8a\u672c"
        "\u6ce2 A \u7a97\u2192\u4fdd\u7559\u8d70\u843d 448_004..448_203"
        "\u00b7hops=1\u00b7**B base==\u672c\u6ce2 A \u5c3e+1 \u673a\u68c0"
        "\u5173\u7cfb**\u00b7\u975e\u8f6e\u8f6c r587\u00b7hop \u94fe\u9010"
        "\u8df3\u5728 probe \u56de\u6267\u00b7\u4e0e W195 \u00a75.5 \u6295"
        "\u5f71+r908 prereg leg4 \u627f\u63a5\u9762\u6ce8\u8bb0\u5151"
        "\u73b0\u6536\u655b\u00b7ADMIT \u56de\u6267\u5728\u573a\uff09"),
    "@ENGNOTE@": (
        "**\u672c\u51bb\u7ed3=buildgen emission \u94fe\uff08r830/r833/"
        "r877/r908 \u8840\u7edf\u627f\u88ad\u00b7TOK \u4e24\u76f8 vmap+DRY "
        "\u5168\u6587\u4ef6\u95e8\u96f6\u5199\u5165\u5148\u884c+U+2212 "
        "\u663e\u793a\u5f62\u00b7\u4e94\u817f\u63a2\u9488\u56de\u6267"
        "\u5728\u573a\u4e3a\u51c6\u00b7anchor=W195 \u5b9e\u6d4b r590 \u6eda"
        "\u52a8\u5151\u73b0\u00b7selftest W196 face \u5c06\u968f\u4e94"
        "\u9762\u51bb\u7ed3\u843d\u5730\u9a8c\u8bc1\uff09\u3002**"),
    "@CLAIM@": (
        "- \u8ba4\u9886\uff1anever-dry \u5e38\u4f9b\u7ed9\u4f8b\u6ce2"
        "\uff08TRIAL_LABOR_LAW \u00a74\u00b7\u677f\u7a7a/\u6c60\u9971/"
        "\u65e0\u5728\u98de\u5224\u51b3\u6279=\u9ed8\u8ba4\u7eed\u8dd1"
        "\u4e0b\u4e00\u6ce2\u2014\u2014\u672c\u673a r910 \u5e2d\u4f4d "
        "MSG-2026-10-09-1007-bma-w196-seat \u5df2\u63a8 origin "
        "01992cd42\uff08r910 seat push\u00b7r565 \u5f8b\uff09\u00b7probe "
        "W197+ \u6295\u5f71 A 448_004..450_003 / B 448_204..448_403 "
        "**naive-B-inside-naive-A re-derive \u5f3a\u5236\u6ce8\u8bb0+"
        "\u540c\u7a97\u4e92\u65a5\u9884\u62ab\u9732**\uff08\u6295\u5f71 "
        "B \u843d\u6295\u5f71 A \u7a97\u5185\u00b7W196 B \u5e26 "
        "448_004..448_203 \u6ce8\u518c\u540e\u5c06\u62d2 naive W197 A "
        "\u7a97=\u9636\u68af A-hops-prior-B \u7ee7\u627f\u7b2c\u4e94"
        "\u5341\u4e03\u4f8b\u5f85 W197 \u6ce8\u518c\u5b87\u5b99\u590d"
        "\u6838\uff09\u3002\u8868\u5c3e\u540e\u65b0\u9996\u4e2a\u81ea"
        "\u7531\u53f7\u81ea\u9886\u00b7r910 probe \u5355\u8dd1\u5151"
        "\u73b0\u6ce8\u8bb0\uff08\u672c\u7a97\u51bb\u7ed3\u6d88\u8d39"
        "\uff09\uff1bO-20260924-1730 CEO \u5373\u65f6\u5f8b\uff08\u8ba4"
        "\u9886\u4e0e\u5f00\u52a8\u540c\u8f6e\u00b7\u7981\u6392\u672a"
        "\u6765\u8f6e\u6b21\uff09\uff1bT-2026-10-01-141 s1 \u5f15\u64ce"
        "\u7ebf\u7b2c 186 \u6ce2\u3010bm-a \u7b2c\u4e00\u767e\u4e00\u5341"
        "\u4e00\u679a\u81ea\u6709\u6ce2\u3010\u673a\u9762 derive\uff1a"
        "engine_owner==bm-a \u884c 110+\u672c\u5019\u9009\u4ee5 probe "
        "leg0 \u673a\u8bc1\u4e3a\u51c6\u3011\u3011\u3002\uff08\u6ce2"
        "\u53f7=\u6ce8\u518c\u8868 W195 \u5e2d\u540e\u9996\u4e2a\u81ea"
        "\u7531\u53f7\u00b7\u5355\u6001\u96f6\u5e2d\u4f4d\u7a7a\u6863"
        "\uff1b\u4e2d\u4f4d\u516c\u793a MSG-2026-10-09-1007-bma-w196-"
        "seat \u5148\u63a8 origin 01992cd42 r565 \u5f8b\uff1blane-free"
        "\uff1bdept:\u7814\u7a76\uff09\u3002"),
    "@SCANFACE@": (
        "\u626b\u63cf\u9762=pre-W196 \u5168\u4e00\u767e\u4e5d\u5341"
        "\u4e09\u884c\u6ce8\u518c N1 \u5e26\u8868\uff08\u8868\u5c3e W195 "
        "\u884c\u00b7leg0 \u673a\u8bc1 193 \u884c\uff09"),
    "@R250@": ("R250\uff1aW196 \u5e26\u4ece\u672a\u6307\u6d3e\u00b7"
               "\u6d4b\u91cf\u9762\u96f6\u7ed3\u679c\u53ef\u9501"),
    "@PRCR@": "results/_r910bma_w196_probe_receipt.json",
    "@RUNNERW@": ("W2..W195 \u843d\u5730 runner \u7684 wave \u53c2\u6570"
                  "\u5316\u590d\u7528"),
    "@BATCHNAME@": "\u6279\u540d=**PERPETUAL-N1-W196**",
    "@POOL@": (
        "\u7d2f\u8ba1 null \u6c60=426,920\uff08W195 \u843d\u8d26\u5b9e"
        "\u6d4b\uff09+2,200\uff08\u672c\u6ce2\uff09=**429,120 \u6295\u5f71"
        "**"),
    "@MATCOND@": ("\u81ea\u89c1 W196 \u884c\u5e76\u70b9\u706b\u81ea"
                  "\u70e7"),
    "@GATECMD@": "--prereg research/PERPETUAL_N1_W196_PREREG.md",
    "@BENTRY@": (
        "entry rng=**446_004+j**\uff08\u4e0e A[j] \u540c\u6e90\u914d"
        "\u5bf9\u8bed\u4e49\u9010\u5b57\u00b7runner \u5b9e\u8bc1 "
        "entry=A_SEED_BASE+j\uff09"),
    "@PROBEW@": "\u672c\u6ce2\u8bbe\u8ba1=W2..W195 \u9010\u5b57\u590d"
                "\u7528",
    "@DISJ@": (
        "W196 \u5e26\u4e0e v1 \u5728\u7528\u5e26\uff0810_000..10_099/"
        "20_000..20_019\uff09\u3001W1 ext \u5e26\uff0810_100..12_099/"
        "20_100..20_299\uff09\u3001W2..W195 \u5e26\uff08**\u5168\u6ce8"
        "\u518c\u5355\u6001**\uff09"),
    "@POOL4@": (
        "\u5df2\u843d\u8d26\u51c0\u503c\uff08\u8d77\u7a3f\u7a97\u5b9e"
        "\u6d41 W1..W195 \u5df2\u843d\u8d26 426,920 \u5b9e\u6d4b\u00b7"
        "derive \u7981\u624b\u6284\uff09+\u672c\u6ce2 2,200"),
    "@LEDGER@": (
        'batch_name="PERPETUAL-N1-W196", batch_trials=2200, file_name='
        '"results/perpetual_faces/n1_w196_results.json"'),
    "@CLI@": "--wave 196/finalize --wave 196",
    "@ENG6@": ("\u3010n1_w196/ \u5206\u7247\u8ba1\u6570\u589e\u957f\u00b7"
               "\u552f\u4e00\u70b9\u706b\u8bc1\u636e\u00b7r325 \u5f8b"
               "\u3011"),
    "@SHARD@": "results/p2cal_ext/n1_w196/shard-<k>-of-12.json",
    "@RFN@": "results/perpetual_faces/n1_w196_results.json",
    "@FINPRE@": (
        "finalize \u952e\u5e8f\u524d\u7f6e=**\u8d77\u7a3f\u7a97\u96f6"
        "\u5728\u98de\u4e0a\u6e38\u5e2d\uff08W194/W195 finalize \u5747"
        "\u5df2\u843d origin\u00b7ls-tree \u673a\u8bc1\uff09**\u2014\u2014"
        "\u8dd1\u65f6\u6309 registry \u952e derive \u590d\u6838\u00b7"
        "FAIL-CLOSED r307 \u4e24\u6001\u4f8b\u6052\u5728\uff09\u3002"),
    "@EOBD@": ("\uff08engine_owner==bm-a 110 \u884c\u6ce8\u518c + "
               "\u672c\u5019\u9009\u2014\u2014\u4ee5 probe leg0 \u673a"
               "\u8bc1\u4e3a\u51c6\uff09"),
    "@BGATE@": ("\uff08p2_calibration v1/v2 canon\uff1bv1 ext\uff1b"
                "v2..W195 \u843d\u5730\uff09"),
    "@S7@": (
        "\u5f85 W196 finalize \u7a97\u3011\n- \uff08\u5360\u4f4d\u00b7"
        "finalize one-pass \u540e\u673a\u68b0\u56de\u586b\uff1a\u8d26"
        "\u672c\u6052\u7b49\u5f0f+\u5408\u5e76\u6c60 K+merged mu/w-only "
        "mu/mu_delta+sigma+se_mu+skill_line_v2 K-lift+A \u6863 p95+"
        "\u00a75 \u56db\u9884\u952e\u673a\u8bc1+canon flip \u6001+audit."
        "finalize_only+voids_applied\u3002\uff09"),
    "@S8@": (
        "\u3010finalize \u540c\u7a97\u56de\u586b\u00b7\u5f85 W196 "
        "finalize \u7a97\u3011\n- \uff08\u5360\u4f4d\u00b7\u00a75.5 "
        "W197+ \u6295\u5f71\u627f\u63a5+\u5b9d\u85cf/\u65b9\u6cd5\u8bba"
        "\u6355\u83b7\u95ee+\u8bda\u5b9e\u62ab\u9732\u9762\u00b7finalize "
        "\u6536\u53e3\u7a97\u673a\u68b0\u56de\u586b\u3002\uff09"),
    "@WAVEFREE@": ("\u6ce2\u53f7 196=\u6ce8\u518c\u8868 W195 \u5e2d"
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
# structural: line count preserved (spans are intra-line except S7/S8 pairs)
assert out_t.count("\n") == src_t.count("\n"), "line structure drift"
# U+2212 display forms present (W195 anchor rolled values)
assert M + "0.0929" in out_t and M + "0.0970" in out_t, "U+2212 forms"
assert "0.245069" in out_t and "0.3078" in out_t and "0.000375" in out_t
# batch-id sanity (title + batchname + ledger = 3 hyphenated forms)
nb = out_t.count("PERPETUAL-N1-W196")
assert nb == 3, "batch id count=%d (expect 3: title+batchname+ledger)" % nb
# stale sweep: W195-era wave-self faces that must have rolled
for stale in ("FIFTY-FIFTH", "\u7b2c\u4e94\u5341\u4e94\u4f8b",
              "443_804..445_803", "443_604..445_603", "443_804..444_003",
              "443_604..443_803", "443_804+j", "445_804+j",
              "**B-ext exit seed=445_804..446_003**",
              "PERPETUAL-N1-W195", "PERPETUAL_N1_W195_PREREG",
              "n1_w195/", "n1_w194_results.json",
              "MSG-2026-10-09-0844", "eb81c0878", "5cca13637",
              "engine_owner==bm-a 109", "engine_owner==bm-a \u884c 109",
              "\u7b2c 185 \u6ce2", "\u7b2c\u4e00\u767e\u4e00\u5341\u679a",
              "\u6cf5\u7b2c 193 \u679a", "\u6ce2\u53f7 195=",
              "\u6ce8\u518c\u8868 W194 \u5e2d\u540e",
              "\u5168\u4e00\u767e\u4e5d\u5341\u4e8c\u884c", "W2..W194",
              "\u5f85 W195 finalize \u7a97",
              "W196+ \u6295\u5f71", "r907 \u5e2d\u4f4d",
              "r907 probe \u5355\u8dd1", "r907 seat push",
              "r907 W195 probe", "r902 probe", "r904 prereg leg4",
              "\u884c 184 \u6ce8\u518c\u5728\u518c",
              "W193/W194 finalize", "r904\u00b7buildgen",
              "W194-only \u5b9e\u6d4b", "0.3135", "0.245098",
              "K=424,720", "836,745", "422,520", "424,720 \u6295\u5f71",
              "838,945", "1.1872", "line_pre 1.1873", "1316ab9e7",
              "r904 estate", "\u5728\u98de\u4e0a\u6e38\u5e2d W192"):
    assert stale not in out_t, "stale survives: %r" % stale
# legal persistences (prior-wave faces + chain mids + anchor refs)
assert "445_804..446_003" in out_t, "W195 B refusing band missing"
assert out_t.count(M + "0.0001/W191") == 1, "K-lift chain mid missing"
assert "W191=bm-a r894 freeze\uff08e5e4af81b\uff09" in out_t, \
    "chain W191 mid missing"
assert "\uff1bW194=bm-a r905 freeze\uff0882670b0ba\uff09\uff1bW195=bm-a " \
    "r909 freeze\uff08b9b962672\uff09\u3002" in out_t, "chain tail missing"
assert out_t.count("n1_w195_results.json") == 2, "anchor file refs"
assert out_t.count("n1_w194_results.json") == 0, "stale anchor file"
assert "v2..W195 \u843d\u5730" in out_t, "\u00a70.5 landed-set face"
assert out_t.count("W1..W195 N1 finalize \u5df2\u5168\u90e8\u843d\u5730") \
    == 2, "anchor landed-set faces"
assert "843,345" in out_t and "426,920" in out_t and "841,145" in out_t
assert "1.1873" in out_t and "\u952e W195 \u5b9e\u6d4b" in out_t
assert "bd1f515f2" in out_t and "a0b16d1d8" in out_t
# new-value presence
assert "FIFTY-SIXTH" in out_t and "\u7b2c\u4e94\u5341\u516d\u4f8b" in out_t
assert "\u7b2c\u4e94\u5341\u4e03\u4f8b" in out_t
assert out_t.count("n1_w196") == 4, "n1_w196 count drift"
assert out_t.count("MSG-2026-10-09-1007-bma-w196-seat") == 3
assert out_t.count("W197+ \u6295\u5f71") == 3
assert "446_004..448_003" in out_t and "448_004..448_203" in out_t
assert "445_804..447_803" in out_t and "446_004..446_203" in out_t
assert "448_004..450_003" in out_t and "448_204..448_403" in out_t
assert "446_004+j" in out_t and "448_004+j" in out_t
assert "429,120" in out_t and "\u7b2c 186 \u6ce2" in out_t
assert "\u7b2c\u4e00\u767e\u4e00\u5341\u4e00\u679a" in out_t
assert "\u6cf5\u7b2c 194 \u679a" in out_t
assert "\u6ce2\u53f7 196=\u6ce8\u518c\u8868 W195 \u5e2d\u540e\u9996\u4e2a" \
    "\u81ea\u7531\u53f7" in out_t
assert "W196-only" in out_t
assert "W195-only \u5b9e\u6d4b" in out_t, "anchor w-only face missing"
assert "446_003+1" in out_t and "448_003+1" in out_t, "base==tail+1 faces"
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
"""r911 bm-a W196 per-wave prereg build (EMITTED by
results/_r911bma_w196_buildgen.py; pairs baked; live facts re-asserted
at run time per r587).  Src = results/_r911bma_w196_prereg_src.txt
(W195 prereg freeze-time blob b9b962672, byte-verbatim binary extract,
r877 law 4).  Output CRLF (r370 law)."""
import io
import json
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
SRC = "results/_r911bma_w196_prereg_src.txt"
OUT = "research/PERPETUAL_N1_W196_PREREG.md"
G = r"%s"
GIT = r"C:\\Program Files\\Git\\cmd\\git.exe"

def git(*a):
    r = subprocess.run([GIT, "-C", G] + list(a), capture_output=True)
    return r.stdout.decode("utf-8", errors="replace").strip()

subprocess.run([GIT, "-C", G, "fetch", "origin"], capture_output=True)
probe = json.load(open(r"results/_r910bma_w196_probe_receipt.json",
                      encoding="utf-8"))
assert probe["verdict"] == "ADMIT" and probe["bands"] == {
    "A": "446004_448003", "B": "448004_448203"}, probe
leg0 = probe["legs"]["leg0"]
assert leg0["rows"] == 193 and leg0["tail"] == "W195", leg0
assert leg0["ordinal"] == 186 and leg0["bma_ordinal"] == 111, leg0
res = json.load(open(r"results/perpetual_faces/n1_w195_results.json",
                     encoding="utf-8"))
assert res["null_pool_cumulative"]["merged"]["n_values"] == 426920
assert res["science_gates"]["ledger"]["total"] == 843345
assert res["skill_line_v2_k_lift"]["n_eff_held_equal"] == 841145
_vac = git("log", "origin/main", "--format=%%h", "-n", "1", "-S",
           '196: {"a": (446_004', "--", "scripts/perpetual_faces.py")
assert _vac == "", "W196 five-face already on origin?!"
_fin194 = git("ls-tree", "origin/main",
              "results/perpetual_faces/n1_w194_results.json")
assert _fin194 != "", "W194 finalize NOT landed -- key-order face broken!"
_fin195 = git("ls-tree", "origin/main",
              "results/perpetual_faces/n1_w195_results.json")
assert _fin195 != "", "W195 finalize NOT landed -- anchor must roll r590!"
_seat = git("log", "origin/main", "--format=%%h", "-n", "1",
            "--diff-filter=A", "--",
            "fleet/inbox/MSG-2026-10-09-1007-bma-w196-seat.md")
assert _seat == "01992cd42", _seat

sys.path.insert(0, "scripts")
sys.path.insert(0, ".")
import science_gates as _sg  # noqa: E402
REG_N = len(_sg.SEED_REGISTRY)
assert REG_N >= 194, "SEED_REGISTRY below freeze face: %%d" %% REG_N
_ws = [int(x) for x in _sg.SEED_REGISTRY.values()
       if isinstance(x, int)]
assert not [s for s in _ws if 446004 <= s <= 448203], "band overlap"

TOK = %s
BACK = %s

src = io.open(SRC, encoding="utf-8").read()
assert src.count("\\r\\n") == 0, "src blob expected LF"
assert src.count("SEED_REGISTRY \\u5168\\u952e 194 \\u503c") == 1, \\
    "registry-count face not found in src"
src = src.replace("SEED_REGISTRY \\u5168\\u952e 194 \\u503c",
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
assert out_t.count("PERPETUAL-N1-W196") == 3, "batch id count drift"
assert out_t.count("\\n") == src.count("\\n"), "line structure drift"
M = "\\u2212"
for stale in ("FIFTY-FIFTH", "443_804..445_803", "443_604..443_803",
              "443_804+j", "445_804+j", "PERPETUAL-N1-W195",
              "PERPETUAL_N1_W195_PREREG", "n1_w195/",
              "n1_w194_results.json", "MSG-2026-10-09-0844", "eb81c0878",
              "5cca13637", "engine_owner==bm-a 109",
              "\\u7b2c 185 \\u6ce2", "\\u7b2c\\u4e00\\u767e\\u4e00\\u5341"
              "\\u679a", "\\u6cf5\\u7b2c 193 \\u679a", "W2..W194",
              "\\u5f85 W195 finalize \\u7a97", "W196+ \\u6295\\u5f71",
              "K=424,720", "836,745", "422,520", "1.1872", "0.3135",
              "0.245098", "W194-only \\u5b9e\\u6d4b", "838,945",
              "line_pre 1.1873", "1316ab9e7"):
    assert stale not in out_t, "stale token survives: %%r" %% stale
assert M + "0.0929" in out_t and M + "0.0970" in out_t, "U+2212 forms"
assert out_t.count(M + "0.0001/W191") == 1
assert "W191=bm-a r894 freeze\\uff08e5e4af81b\\uff09" in out_t
assert "\\uff1bW194=bm-a r905 freeze\\uff0882670b0ba\\uff09\\uff1bW195=bm-a " \\
    "r909 freeze\\uff08b9b962672\\uff09\\u3002" in out_t
assert out_t.count("n1_w195_results.json") == 2
assert out_t.count("W1..W195 N1 finalize \\u5df2\\u5168\\u90e8\\u843d\\u5730") \\
    == 2
assert out_t.count("n1_w196") == 4
assert "FIFTY-SIXTH" in out_t
assert "W195-only \\u5b9e\\u6d4b" in out_t, "anchor w-only face missing"
assert "843,345" in out_t and "426,920" in out_t and "429,120" in out_t
assert "446_004..448_003" in out_t and "448_004..448_203" in out_t

open(OUT, "wb").write(out_t.replace("\\n", "\\r\\n").encode("utf-8"))
chk = io.open(OUT, encoding="utf-8", newline="").read()
assert chk == out_t.replace("\\n", "\\r\\n"), "CRLF roundtrip drift"
print("W196 prereg built: %%s bytes=%%d crlf=%%d" %%
      (OUT, len(chk.encode("utf-8")), chk.count("\\r\\n")))
print("post-transform asserts PASS (counts, residue-zero, "
      "malformed-zero, stale-sweep CLEAN, U+2212 forms, anchor=W195)")
''' % (G, tok_lit, back_lit)
io.open(EMIT, "w", encoding="utf-8", newline="\n").write(emit_src)
print("EMITTED:", EMIT, len(emit_src), "bytes")
print("buildgen complete: DRY gate green -> emitted build script "
      "(run it next)")
