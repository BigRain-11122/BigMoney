# -*- coding: utf-8 -*-
"""r921 bm-a W200 per-wave prereg build (two-gen eval chain: old sides =
AST-extracted BACK values of results/_r919bma_w199_prereg_build.py, zero
transcription r587; live facts re-asserted at run time per r587).
Src = results/_r921bma_w200_prereg_src.txt (W199 prereg freeze-time blob
f312ec9d4, byte-verbatim binary extract, r877 law 4).  Output CRLF
(r370 law).  buildgen three laws honored: AST no-exec prior-gen
(ast.literal_eval only), DRY whole-file gate zero-write-first, U+2212
display forms (r833)."""
import ast
import io
import json
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"
GIT = r"C:\Program Files\Git\cmd\git.exe"
SRC_BLOB_COMMIT = "f312ec9d4"   # W199 prereg BUILD + freeze commit = src blob
SRC = "results/_r921bma_w200_prereg_src.txt"
OUT = "research/PERPETUAL_N1_W200_PREREG.md"
R919_BUILD = "results/_r919bma_w199_prereg_build.py"
R916_BUILD = "results/_r916bma_w198_prereg_build.py"
R914_BUILD = "results/_r914bma_w197_prereg_build.py"
M = "\u2212"
CNW = getattr(subprocess, "CREATE_NO_WINDOW", 0)


def git(*a):
    r = subprocess.run([GIT, "-C", ROOT] + list(a), capture_output=True,
                       creationflags=CNW)
    return r.stdout.decode("utf-8", errors="replace").strip()


# ---- extract the freeze-time src blob (r877 law 4, byte-verbatim) ----
blob = subprocess.run(
    [GIT, "-C", ROOT, "show", SRC_BLOB_COMMIT + ":research/PERPETUAL_N1_W199_PREREG.md"],
    capture_output=True, creationflags=CNW).stdout
with open(ROOT + "\\" + SRC.replace("/", "\\"), "wb") as fh:
    fh.write(blob)
assert b"\r\n" not in blob, "src blob expected LF (git-normalized)"
assert blob.decode("utf-8").count("SEED_REGISTRY \u5168\u952e 195 \u503c") == 1

# ---- live fact re-asserts (machine numbers, zero transcription) ----
subprocess.run([GIT, "-C", ROOT, "fetch", "origin"], capture_output=True,
               creationflags=CNW)
probe = json.load(open(r"results/_r920bma_w200_probe_receipt.json",
                      encoding="utf-8"))
assert probe["verdict"] == "ADMIT" and probe["bands"] == {
    "A": "454804_456803", "B": "456804_457003"}, probe
leg0 = probe["legs"]["leg0"]
assert leg0["rows"] == 197 and leg0["tail"] == "W199", leg0
assert leg0["ordinal"] == 190 and leg0["bma_ordinal"] == 115, leg0
assert leg0["owner_rows"] == 189 and leg0["bma_rows"] == 114, leg0
assert leg0["w199_ledger_head"] == 852145, leg0
leg1 = probe["legs"]["leg1"]
assert leg1["A"] == [454804, 456803] and leg1["B"] == [456804, 457003], leg1
assert leg1["hops_A"] == 1 and leg1["hops_B"] == 1
assert leg1["ARITH_A"] == [454604, 456603], leg1
assert leg1["ARITH_B"] == [454804, 455003], leg1
assert "SIXTIETH" in leg1["A_semantics"], leg1
assert probe["legs"]["leg2"]["conflicts"] == 0
assert probe["legs"]["leg3"]["origin_vacancy"] is True
leg4 = probe["legs"]["leg4"]
assert leg4["W201p_A"] == "456804..458803", leg4
assert leg4["W201p_B"] == "457004..457203", leg4
assert leg4["hops_A"] == 0 and leg4["hops_B"] == 0
assert leg4["W201p_B_lands_inside_W201p_A"] is True

res = json.load(open(r"results/perpetual_faces/n1_w199_results.json",
                     encoding="utf-8"))
npc = res["null_pool_cumulative"]
merged = npc["merged"]
assert merged["n_values"] == 435720, merged
assert merged["mu"] == -0.0927656024511154, merged
assert merged["sigma"] == 0.24511221451455875, merged
assert npc["w199_only"]["mu"] == -0.08596781818181819, npc
assert npc["se_mu_at_k435720"] == 0.000371, npc
assert npc["mu_delta_w199_vs_w198ext"] == 0.011157, npc
assert res["science_gates"]["ledger"]["total"] == 852145
kl = res["skill_line_v2_k_lift"]
assert kl["n_eff_held_equal"] == 849945, kl
assert kl["line_pre_w199"] == 1.188 and kl["line_merged_435720"] == 1.1881
assert kl["line_delta_k_lift"] == 0.0001, kl
assert res["families"]["A_random_engine_exit"]["full_sharpe_p95"] == 0.3304
# display-form derivation asserts (zero hand-rounding)
assert "%.4f" % merged["mu"] == "-0.0928"
assert "%.4f" % npc["w199_only"]["mu"] == "-0.0860"
assert "%.6f" % merged["sigma"] == "0.245112"

_vac = git("log", "origin/main", "--format=%h", "-n", "1", "-S",
           '200: {"a": (454_804', "--", "scripts/perpetual_faces.py")
assert _vac == "", "W200 five-face already on origin?!"
_fin199 = git("ls-tree", "origin/main",
              "results/perpetual_faces/n1_w199_results.json")
assert _fin199 != "", "W199 finalize NOT landed -- anchor must roll r590!"
_fin198 = git("ls-tree", "origin/main",
              "results/perpetual_faces/n1_w198_results.json")
assert _fin198 != "", "W198 finalize NOT landed -- chain integrity!"
_seat = git("log", "origin/main", "--format=%h", "-n", "1",
            "--diff-filter=A", "--",
            "fleet/inbox/MSG-2026-10-09-1645-bma-w200-seat.md")
assert _seat == "143fcfe1b", _seat
_anc = subprocess.run([GIT, "-C", ROOT, "merge-base", "--is-ancestor",
                       "143fcfe1b", "origin/main"], capture_output=True,
                      creationflags=CNW)
assert _anc.returncode == 0, "seat sha not ancestor of origin/main"
# seat MSG archive state = ALREADY processed at the seat-round closeout
import os
assert not os.path.exists(ROOT + r"\fleet\inbox\MSG-2026-10-09-1645-bma-w200-seat.md"), \
    "seat MSG back in inbox/?!"
assert os.path.exists(ROOT + r"\fleet\inbox\processed\MSG-2026-10-09-1645-bma-w200-seat.md"), \
    "seat MSG not in processed/ (ALREADY-archived state)"

sys.path.insert(0, "scripts")
sys.path.insert(0, ".")
import science_gates as _sg  # noqa: E402
REG_N = len(_sg.SEED_REGISTRY)
assert REG_N >= 195, "SEED_REGISTRY below freeze face: %d" % REG_N
_ws = [int(x) for x in _sg.SEED_REGISTRY.values() if isinstance(x, int)]
assert not [s for s in _ws if 454804 <= s <= 457003], "band overlap"

# ---- two-gen eval: old sides = r919 BACK (AST, no exec) ----
# r919 BACK carries '@CHAIN@': CHAIN_NEW (a Name) -- resolve via the
# r914 BACK chain literal + the r916 append + the r919 append
# (zero transcription).
_r919_src = io.open(R919_BUILD, encoding="utf-8").read()
_tree = ast.parse(_r919_src)
OLD_BACK = None
for _node in ast.walk(_tree):
    if (isinstance(_node, ast.Assign) and len(_node.targets) == 1
            and isinstance(_node.targets[0], ast.Name)
            and _node.targets[0].id == "BACK"
            and isinstance(_node.value, ast.Dict)):
        OLD_BACK = {}
        for k, v in zip(_node.value.keys, _node.value.values):
            key = ast.literal_eval(k)
            if isinstance(v, ast.Constant):
                OLD_BACK[key] = ast.literal_eval(v)
            else:
                assert isinstance(v, ast.Name) and v.id == "CHAIN_NEW", \
                    "unexpected non-literal BACK value for %s" % key
                OLD_BACK[key] = None  # resolved below
        break
assert OLD_BACK and len(OLD_BACK) == 40, "r919 BACK eval-parse failed: %s" % (
    len(OLD_BACK) if OLD_BACK else 0)
# resolve CHAIN_NEW (r919 build) = _chain_old + append_919;
# _chain_old = r916 chain = r914 chain + append_916
_append_919 = None
for _node in ast.walk(_tree):
    if (isinstance(_node, ast.Assign) and len(_node.targets) == 1
            and isinstance(_node.targets[0], ast.Name)
            and _node.targets[0].id == "CHAIN_NEW"
            and isinstance(_node.value, ast.BinOp)
            and isinstance(_node.value.op, ast.Add)):
        _append_919 = ast.literal_eval(_node.value.right)
assert _append_919 == "\uff1bW198=bm-a r916 freeze\uff0882b881a4f\uff09", _append_919
_r916_src = io.open(R916_BUILD, encoding="utf-8").read()
_r916_tree = ast.parse(_r916_src)
_append_916 = None
for _node in ast.walk(_r916_tree):
    if (isinstance(_node, ast.Assign) and len(_node.targets) == 1
            and isinstance(_node.targets[0], ast.Name)
            and _node.targets[0].id == "CHAIN_NEW"
            and isinstance(_node.value, ast.BinOp)
            and isinstance(_node.value.op, ast.Add)):
        _append_916 = ast.literal_eval(_node.value.right)
assert _append_916 == "\uff1bW197=bm-a r915 freeze\uff08522a0aef5\uff09", _append_916
_r914_src = io.open(R914_BUILD, encoding="utf-8").read()
_r914_tree = ast.parse(_r914_src)
_chain_914 = None
for _node in ast.walk(_r914_tree):
    if (isinstance(_node, ast.Assign) and len(_node.targets) == 1
            and isinstance(_node.targets[0], ast.Name)
            and _node.targets[0].id == "BACK"
            and isinstance(_node.value, ast.Dict)):
        for k, v in zip(_node.value.keys, _node.value.values):
            if ast.literal_eval(k) == "@CHAIN@":
                assert isinstance(v, ast.Constant), "r914 chain not literal"
                _chain_914 = ast.literal_eval(v)
assert _chain_914 and _chain_914.endswith(
    "\uff1bW196=bm-a r912 freeze\uff0802cf6b44d\uff09"), \
    "r914 chain tail unexpected: %r" % (_chain_914 or "")[-80:]
_chain_919 = _chain_914 + _append_916 + _append_919
assert _chain_919.endswith("\uff1bW198=bm-a r916 freeze\uff0882b881a4f\uff09"), \
    "r919 chain tail unexpected: %r" % _chain_919[-80:]
OLD_BACK["@CHAIN@"] = _chain_919
CHAIN_NEW = _chain_919 + "\uff1bW199=bm-a r919 freeze\uff08f312ec9d4\uff09"

BACK = {
    '@CHAIN@': CHAIN_NEW,
    '@TITLE@': '# PERPETUAL-N1-W200 \u9884\u6ce8\u518c \u00b7 N1 nulls-deepening \u6cf5\u7b2c 198 \u679a\uff08never-dry \u5e38\u4f9b\u7ed9\u4f8b\u6ce2\u00b7\u6ce2\u5e8f\u53f7\u8fde\u7eed\u00b7\u673a\u9762 derive\uff1aengine_owner \u884c 189 \u6ce8\u518c\u5728\u518c+W198/W199 finalize \u5df2\u843d\u8d26\u00b7anchor \u6eda\u52a8\u5df2\u5151\u73b0\uff08r590\uff09+\u672c\u5019\u9009=bm-a \u7b2c\u4e00\u767e\u4e00\u5341\u4e94\u679a\u81ea\u6709\u6ce2\u3010bm-a r921\u00b7buildgen \u8840\u7edf r830/r833/r877/r908/r911/r914/r916/r919 \u627f\u88ad\u00b7\u5e72\u51c0\u7a97 anchor=W199 \u5b9e\u6d4b r590 \u6eda\u52a8\u5151\u73b0\u3011\uff09',
    '@SEATBLOCK@': '\u3010\u672c\u51bb\u7ed3\u7a97 fetch \u5b9e\u6838\u8868\u5c3e\u65f6 W200 \u53f7\u4f4d\u7a7a\u6863\u00b7rg \u884c WAVE_CONFIGS+prereg \u8def\u5f84\u4e09\u67e5+origin ls-tree vacancy \u673a\u8bc1\uff08\u672c\u7a97 probe leg3 \u5b9e\u8dd1\uff09\uff1b\u5168 inbox/processed/ W200 \u5e2d\u4f4d\u96f6\u5916\u673a\u547d\u4e2d\uff1b**W198=bm-a r916 \u4e94\u9762\u51bb\u7ed3 82b881a4f \u5728\u518c\u00b7finalize \u5df2\u843d origin\uff08r917 one-pass d4ea4b348\u00b7\u8d26\u672c 849,945 EXACT \u96f6\u504f\u79bb\u4e94\u8fde\u7a97\u00b7K=433,520 EXACT\u00b7\u56db\u9884\u952e 4/4 PASS\uff09+W199=bm-a r919 \u4e94\u9762\u51bb\u7ed3 f312ec9d4 \u5728\u518c\uff08dead-session estate takeover absorb\uff09+\u5f15\u64ce\u81ea\u70e7 12/12 15:38..15:50\u00b7finalize \u5df2\u843d origin\uff08r920 one-push c19c67450\u00b7\u8d26\u672c 852,145 EXACT \u516d\u8fde\u7a97\u00b7K=435,720 EXACT\u00b7\u56db\u9884\u952e 4/4 PASS\u00b7skill_line_v2 1.1881\uff09\u2014\u2014\u8d77\u7a3f\u7a97\u6ce8\u518c\u5b87\u5b99=W198/W199 \u6ce8\u518c\u5e26\u5728\u518c+\u53cc finalize \u843d\u8d26\uff08N1_BANDS \u6ce8\u518c\u884c\u673a\u5668\u8bfb\u00b7probe leg0 \u673a\u8bc1 197 \u884c\u8868\u5c3e W199\uff09\u00b7r920 W200 probe \u5168\u817f\u673a\u8bc1**\uff1b\u672c\u673a\u5e2d\u4f4d\u516c\u793a=MSG-2026-10-09-1645-bma-w200-seat \u5df2\u63a8 origin 143fcfe1b \u5148\u4e8e\u672c\u51bb\u7ed3\u3010r565 \u5f8b\u00b7\u63a8\u9001\u7a97=r920 seat push \u76f4\u63a5\u5feb\u8fdb\u9001\u8fbe 143fcfe1b\uff08payload=seat MSG+W200 pre-seat probe \u811a\u672c+\u56de\u6267\u540c\u63a8\uff09\uff1bself-ack inbox\u2192processed \u79fb\u4f4d\u5df2\u5728\u5e2d\u4f4d\u8f6e\u6536\u53e3\u5b8c\u6210\uff08r920 closeout 980db1d3e consumed->processed\u00b7archive ALREADY\u00b7\u5982\u5b9e\u6ce8\u8bb0\uff09\u3011\u3011',
    '@AFACE@': '\u672c\u6ce2 **A-ext seed=454_804..456_803**\uff08**A \u9762=FIRST-CLEAN past prior-wave B \u9636\u68af\u7b2c\u516d\u5341\u4f8b**\uff1aA \u9762\u7b97\u672f\u7ee7\u7eed\u5e26 454_604..456_603 \u5728\u5176\u8d77\u70b9\u5373\u88ab W199 \u6ce8\u518c B \u5e26 454_604..454_803 **\u62d2**\uff08W199 \u00a75.5 \u6295\u5f71+r918 probe leg4 \u53cc\u6e90\u9884\u8a00+\u5f3a\u5236\u00b7r920 probe \u56de\u6267 A_semantics \u673a\u8bfb\u53cc\u5151\u73b0\uff09\u2192 \u8bda\u5b9e\u524d\u5411\u8d70 **1 hop** \u843d **454_804..456_803**\u00b7**A base==\u524d\u6ce2 B \u5c3e+1\uff08454_803+1\uff09\u673a\u68c0\u5173\u7cfb**=**A-hops-prior-B \u9636\u68af\u51e0\u4f55\u7b2c\u516d\u5341\u4f8b\uff08E36 \u5361\uff09**\u00b7\u975e\u8f6e\u8f6c r587 \u524d\u5411\u5355\u8c03\u65ad\u8a00\u5728\u8d70\u518c\uff1b\u5e8f\u6570\u9762\u5982\u5b9e\u62ab\u9732\uff1aW199 \u00a75.5 \u6295\u5f71\u9884\u544a\u7b2c\u516d\u5341\u4f8b\u00b7\u672c\u7a97 probe \u56de\u6267 A_semantics \u673a\u8bfb\u5e8f\u6570=SIXTIETH\uff08\u7b2c\u516d\u5341\u4f8b\uff09\u00b7\u672c\u4ef6\u6309\u56de\u6267\u5e8f\u6570\u9762\u8bb0\u8f7d\u975e\u8f6c\u6284\uff08r587\uff09\u00b7\u6295\u5f71\u4e0e\u56de\u6267\u4e24\u8bfb\u6cd5\u6052\u540c\uff09',
    '@BFACE@': '**B-ext exit seed=456_804..457_003**\uff08**B \u9762=FIRST-CLEAN past own-wave A**\uff1aB \u9762\u7b97\u672f\u7ee7\u7eed\u5e26 454_804..455_003 \u5728\u58f0\u660e\u5b87\u5b99\u4e0a CLEAN \u4f46**\u843d\u5728\u672c\u6ce2 A \u7a97 454_804..456_803 \u5185**\uff08**\u540c\u7a97\u4e92\u65a5\u9762 leg2 \u5f8b\u00b7W141 \u5148\u4f8b**\uff1aA \u4e0e B \u540c\u4e00\u51bb\u7ed3 commit \u53cc\u6ce8\u518c\u00b7\u4e92\u65a5\u65ad\u8a00\u5f3a\u5236 B \u8d8a\u8fc7\u672c\u6ce2 A \u7a97\uff09\u2192 B \u5e26\u672c\u6ce2 A \u7a97\u4fdd\u7559\u8d70 **1 hop** \u843d **456_804..457_003**\u00b7**B base==\u672c\u6ce2 A \u5c3e+1\uff08456_803+1\uff09\u673a\u68c0\u5173\u7cfb**\u00b7hop \u94fe\u9010\u8df3\u5728 probe \u56de\u6267\uff1b**W199 \u00a75.5 \u6295\u5f71+r918 probe leg4 \u627f\u63a5\u9762\u6ce8\u8bb0\u5151\u73b0**\uff1a\u6295\u5f71\u9884\u8a00 W200 \u987b\u5728 post-W199 \u6ce8\u518c\u5b87\u5b99\u91cd derive \u4e14 derive B \u65f6\u9884\u7559\u672c\u6ce2 A \u7a97\u2014\u2014\u672c\u7a97\u53cc\u9762\u5151\u73b0\u00b7A \u88ab\u62d2+\u9636\u68af\u8d8a\u5e26\u5982\u6295\u5f71\u6240\u671f\u00b7B \u540c\u7a97\u4e92\u65a5\u4fdd\u7559=\u6295\u5f71\u6240\u671f\u00b7\u5df2\u5982\u5b9e\u62ab\u9732\u975e\u5206\u53c9\uff09',
    '@ANCHOR0@': '\u8d77\u7a3f\u7a97\u5b9e\u51b5\uff1a**W1..W199 N1 finalize \u5df2\u5168\u90e8\u843d\u5730**\u3010\u51c0\u8d26\u672c\u951a\u5934 **852,145**\u00b7K=435,720 \u5408\u5e76\u6c60\u00b7n1_w199_results.json \u673a\u8bfb\uff08origin \u5728\u518c\uff09\u3011\uff1bW200=\u672c\u7a97\u5019\u9009\uff08\u5e2d\u4f4d\u5df2\u63a8 143fcfe1b\uff09\u2014\u2014**\u96f6\u5728\u98de\u4e0a\u6e38\u5e2d**\u00b7anchor=\u6700\u65b0\u5df2\u843d\u8d26\u952e\uff08W199 \u5b9e\u6d4b\u00b7r590 \u6eda\u52a8\u5df2\u5151\u73b0\uff1aW199 finalize \u5df2\u843d origin c19c67450\uff08r920 one-pass\u00b7\u8d26\u672c 852,145 EXACT \u96f6\u504f\u79bb\u00b7\u516d\u8fde\u7a97\uff09\u00b7\u8d77\u7a3f\u7a97\u5e72\u51c0\u7a97\u96f6\u5728\u98de\u4e0a\u6e38\u5e2d\u00b7r919 \u540c\u5f8b\u00b7\u65e0 v1 \u81ea\u7206\u9762\uff09',
    '@S5ANCH@': '\uff08\u8d77\u7a3f\u7a97\u5b9e\u51b5\u6ce8\u8bb0\uff1a**W1..W199 N1 finalize \u5df2\u5168\u90e8\u843d\u5730**\u2014\u2014\u51c0\u8d26\u672c\u951a\u5934 852,145\u00b7**K=435,720 \u5408\u5e76\u6c60**\u00b7**\u96f6\u5728\u98de\u4e0a\u6e38\u5e2d\uff08W198/W199 finalize \u5747\u5df2\u843d origin\u00b7ls-tree \u673a\u8bc1\uff09**\u2014\u2014\u672c\u6ce2 \u00a75 \u9884\u6d4b\u952e=**W199 \u5b9e\u6d4b\u503c**\u3010results/perpetual_faces/n1_w199_results.json\u00b7N1 \u9762\u6700\u65b0\u5df2\u843d\u8d26\u952e\u00b7origin \u5728\u518c\u673a\u8bc1\u3011',
    '@S55@': '5. **W201+ \u6295\u5f71\uff08probe \u673a\u8bc1\u00b7\u4e0b\u6ce2\u51bb\u7ed3\u65b9\u590d\u6838\u975e\u8f6c\u6284 r587 \u5f8b\uff09**\uff1aA first-clean 456_804..458_803 **CLEAN**\uff08hops=0\uff09\uff1bB first-clean **457_004..457_203 CLEAN**\uff08hops=0\uff09\u2014\u2014**naive B \u843d\u5728 naive A \u7a97\u5185**\uff08W141 \u540c\u7a97\u4e92\u65a5\u5148\u4f8b\u9002\u7528\u4e8e W201\uff1aW201 \u51bb\u7ed3\u65b9\u5fc5\u987b\u5728 post-W200 \u6ce8\u518c\u5b87\u5b99\u91cd derive \u4e14 derive B \u65f6\u9884\u7559\u672c\u6ce2 A \u7a97\u2014\u2014leg2 \u5f8b/E36 \u5361\uff09\uff1b**W200 B \u5e26 456_804..457_003 \u6ce8\u518c\u540e\u5c06\u62d2 naive W201 A \u7a97**\u2014\u2014W201 A \u91cd derive \u540c\u5f3a\u5236\uff08\u8d8a\u8fc7 W200 B \u5e26\u00b7\u9636\u68af A-hops-prior-B \u7ee7\u627f\u7b2c\u516d\u5341\u4e00\u4f8b\uff09\uff1bverify at W201 prereg\uff0chip \u94fe\u9010\u8df3\u5728 probe \u56de\u6267',
    '@S51@': '1. W200-only mu \u4e0e\u7d2f\u8ba1\u6c60 merged mu\uff08W199 \u5b9e\u6d4b\u952e **\u22120.0928**\u00b7K=435,720 \u5408\u5e76\u6c60\u00b7W199-only \u5b9e\u6d4b **\u22120.0860**\uff09\u5dee\u5f02 **|\u0394|<0.02**\uff08W2..W199 \u5171\u4e00\u767e\u4e5d\u5341\u4e5d\u9762\u5b9e\u6d4b mu \u7a33\u5b9a\u5148\u4f8b\u00b7\u5355\u6ce2\u8de8\u952e\u5fae\uff09',
    '@S52@': '2. sigma \u76f8\u5bf9\u53d8\u5316 **<\u00b110%**\uff08\u540c\u8bbe\u8ba1\u540c\u7a97\u00b7\u7eaf\u62bd\u6837\u6ce2\u52a8\uff1b\u952e **0.245112**=W199 \u5408\u5e76\u6c60\u5b9e\u6d4b 0.245112\uff09\u3002',
    '@S53@': '3. A \u6863 full_sharpe_p95 \u4e0e W199 A \u6863 p95\uff08**0.3304** \u5b9e\u6d4b\u951a\uff09\u5dee **<0.05**\uff08\u95e8\u6807\u6ce8\u6cd5 W5..W199 \u5148\u4f8b\uff1a\u7ed3\u679c\u77e5\u60c5\u9762\u4ec5\u4f5c\u673a\u5668\u65ad\u8a00\u4e4b\u7528\u00b7\u6d4b\u91cf\u9762\u975e\u6ce8\u518c\u5229\u76ca\uff09\u3002',
    '@S54@': '4. K-lift \u7ebf\u79fb\u52a8\u5e45\u5ea6 **\u2264\u00b10.02**\uff08\u7d2f\u8ba1\u6c60\u52a0\u6df1\u96f6 se_mu \u6536\u7a84\u7ebf\u81ea mu/sigma \u5fae\u8c03\u9762\u975e\u8d28\u53d8\u2014\u2014W136..W199 \u5148\u4f8b\u94fe\u62ab\u9732\u3010W189 +0.0003/W190 \u22120.0001/W191 +0.0001/W192 **\u22120.0002**/W193 **\u22120.0001**/W194 **+0.0000**/W195 **\u22120.0001**/W196 **+0.0001**/W197 **+0.0001**/W198 **+0.0000**/W199 **+0.0001**\u00b7\u952e W199 \u5b9e\u6d4b K-lift **+0.0001**\u00b7line_merged@K435,720 **1.1881**\u00b7line_pre 1.188\u00b7n_eff 849,945\uff1bse_mu \u6536\u7a84\u94fe W191 0.000379\u2192W192 0.000378\u2192W193 0.000377\u2192W194 0.000376\u2192W195 0.000375\u2192W196 0.000374\u2192W197 0.000373\u2192W198 0.000372\u2192W199 **0.000371**\u3011\uff09\u3002',
    '@GATEW2@': '\u672c\u6ce2\u673a\u9a8c ADMIT \u56de\u6267\u5728\u573a=_r920bma_w200 \u63a2\u9488\u7a97\uff08pre-seat probe \u5355\u7a97\u00b7gate \u817f\u5408\u5e76\u7ed3\u6784\u627f\u88ad r812/r820/r823 \u5148\u4f8b\u00b7parity N/A \u8bda\u5b9e\u6ce8\u8bb0\uff09\uff1bselftest W200 face\uff08A=first-clean past prior-wave B \u6052\u7b49\u00b7B=first-clean past own-wave A \u6052\u7b49+\u540c\u7a97\u4e92\u65a5\u65ad\u8a00\u00b7W199 \u884c parity \u817f\u3010r735 \u6d4b\u91cf-\u5b9e\u73b0\u5206\u53c9\u65cf\u9632\u62a4\u9762\uff1aA/B \u7a97 set-range \u9488\u5728\u573a\u3011\uff09\u968f\u4e94\u9762\u51bb\u7ed3\u843d\u5730',
    '@ASEED@': 'entry rng seed=**454_804+j**\uff08\u6cd5\u5178 \u00a74 W200 \u884c A=454_804..456_803\u00b7**FIRST-CLEAN past prior-wave B \u9636\u68af\u7b2c\u516d\u5341\u4f8b**\uff1a\u7b97\u672f\u7eed\u5e26 454_604..456_603 \u8d77\u70b9\u5373\u88ab W199 \u6ce8\u518c B \u5e26\u62d2\u21921 hop \u843d 454_804..456_803\u00b7A base==\u524d\u6ce2 B \u5c3e+1 \u673a\u68c0\u5173\u7cfb\u00b7E36 \u5361\u00b7hops=1\u00b7ADMIT \u56de\u6267\u5728\u573a\uff09',
    '@BSEED@': 'exit rng=**456_804+j**\uff08\u6cd5\u5178 \u00a74 W200 \u884c B=456_804..457_003\u00b7**FIRST-CLEAN past own-wave A**\uff1aB \u7b97\u672f\u7eed\u5e26 454_804..455_003 \u5728\u58f0\u660e\u5b87\u5b99\u4e0a CLEAN \u4f46\u843d\u5728\u672c\u6ce2 A \u7a97 454_804..456_803 \u5185\u2192**\u540c\u7a97\u4e92\u65a5\u9762 leg2 \u5f8b\u00b7W141 \u5148\u4f8b**\u5f3a\u5236 B \u8d8a\u672c\u6ce2 A \u7a97\u2192\u4fdd\u7559\u8d70\u843d 456_804..457_003\u00b7hops=1\u00b7**B base==\u672c\u6ce2 A \u5c3e+1 \u673a\u68c0\u5173\u7cfb**\u00b7\u975e\u8f6e\u8f6c r587\u00b7hop \u94fe\u9010\u8df3\u5728 probe \u56de\u6267\u00b7\u4e0e W199 \u00a75.5 \u6295\u5f71+r918 probe leg4 \u627f\u63a5\u9762\u6ce8\u8bb0\u5151\u73b0\u6536\u655b\u00b7ADMIT \u56de\u6267\u5728\u573a\uff09',
    '@ENGNOTE@': '**\u672c\u51bb\u7ed3=buildgen emission \u94fe\uff08r830/r833/r877/r908/r911/r914/r916/r919 \u8840\u7edf\u627f\u88ad\u00b7TOK \u4e24\u76f8 vmap+DRY \u5168\u6587\u4ef6\u95e8\u96f6\u5199\u5165\u5148\u884c+U+2212 \u663e\u793a\u5f62\u00b7\u4e94\u817f\u63a2\u9488\u56de\u6267\u5728\u573a\u4e3a\u51c6\u00b7anchor=W199 \u5b9e\u6d4b r590 \u6eda\u52a8\u5151\u73b0\u00b7selftest W200 face \u5c06\u968f\u4e94\u9762\u51bb\u7ed3\u843d\u5730\u9a8c\u8bc1\uff09\u3002**',
    '@CLAIM@': '- \u8ba4\u9886\uff1anever-dry \u5e38\u4f9b\u7ed9\u4f8b\u6ce2\uff08TRIAL_LABOR_LAW \u00a74\u00b7\u677f\u7a7a/\u6c60\u9971/\u65e0\u5728\u98de\u5224\u51b3\u6279=\u9ed8\u8ba4\u7eed\u8dd1\u4e0b\u4e00\u6ce2\u2014\u2014\u672c\u673a r920 \u5e2d\u4f4d MSG-2026-10-09-1645-bma-w200-seat \u5df2\u63a8 origin 143fcfe1b\uff08r920 seat push\u00b7r565 \u5f8b\uff09\u00b7probe W201+ \u6295\u5f71 A 456_804..458_803 / B 457_004..457_203 **naive-B-inside-naive-A re-derive \u5f3a\u5236\u6ce8\u8bb0+\u540c\u7a97\u4e92\u65a5\u9884\u62ab\u9732**\uff08\u6295\u5f71 B \u843d\u6295\u5f71 A \u7a97\u5185\u00b7W200 B \u5e26 456_804..457_003 \u6ce8\u518c\u540e\u5c06\u62d2 naive W201 A \u7a97=\u9636\u68af A-hops-prior-B \u7ee7\u627f\u7b2c\u516d\u5341\u4e00\u4f8b\u5f85 W201 \u6ce8\u518c\u5b87\u5b99\u590d\u6838\uff09\u3002\u8868\u5c3e\u540e\u65b0\u9996\u4e2a\u81ea\u7531\u53f7\u81ea\u9886\u00b7r920 probe \u5355\u8dd1\u5151\u73b0\u6ce8\u8bb0\uff08\u672c\u7a97\u51bb\u7ed3\u6d88\u8d39\uff09\uff1bO-20260924-1730 CEO \u5373\u65f6\u5f8b\uff08\u8ba4\u9886\u4e0e\u5f00\u52a8\u540c\u8f6e\u00b7\u7981\u6392\u672a\u6765\u8f6e\u6b21\uff09\uff1bT-2026-10-01-141 s1 \u5f15\u64ce\u7ebf\u7b2c 190 \u6ce2\u3010bm-a \u7b2c\u4e00\u767e\u4e00\u5341\u4e94\u679a\u81ea\u6709\u6ce2\u3010\u673a\u9762 derive\uff1aengine_owner==bm-a \u884c 114+\u672c\u5019\u9009\u4ee5 probe leg0 \u673a\u8bc1\u4e3a\u51c6\u3011\u3011\u3002\uff08\u6ce2\u53f7=\u6ce8\u518c\u8868 W199 \u5e2d\u540e\u9996\u4e2a\u81ea\u7531\u53f7\u00b7\u5355\u6001\u96f6\u5e2d\u4f4d\u7a7a\u6863\uff1b\u4e2d\u4f4d\u516c\u793a MSG-2026-10-09-1645-bma-w200-seat \u5148\u63a8 origin 143fcfe1b r565 \u5f8b\uff1blane-free\uff1bdept:\u7814\u7a76\uff09\u3002',
    '@SCANFACE@': '\u626b\u63cf\u9762=pre-W200 \u5168\u4e00\u767e\u4e5d\u5341\u4e03\u884c\u6ce8\u518c N1 \u5e26\u8868\uff08\u8868\u5c3e W199 \u884c\u00b7leg0 \u673a\u8bc1 197 \u884c\uff09',
    '@R250@': 'R250\uff1aW200 \u5e26\u4ece\u672a\u6307\u6d3e\u00b7\u6d4b\u91cf\u9762\u96f6\u7ed3\u679c\u53ef\u9501',
    '@PRCR@': 'results/_r920bma_w200_probe_receipt.json',
    '@RUNNERW@': 'W2..W199 \u843d\u5730 runner \u7684 wave \u53c2\u6570\u5316\u590d\u7528',
    '@BATCHNAME@': '\u6279\u540d=**PERPETUAL-N1-W200**',
    '@POOL@': '\u7d2f\u8ba1 null \u6c60=435,720\uff08W199 \u843d\u8d26\u5b9e\u6d4b\uff09+2,200\uff08\u672c\u6ce2\uff09=**437,920 \u6295\u5f71**',
    '@MATCOND@': '\u81ea\u89c1 W200 \u884c\u5e76\u70b9\u706b\u81ea\u70e7',
    '@GATECMD@': '--prereg research/PERPETUAL_N1_W200_PREREG.md',
    '@BENTRY@': 'entry rng=**454_804+j**\uff08\u4e0e A[j] \u540c\u6e90\u914d\u5bf9\u8bed\u4e49\u9010\u5b57\u00b7runner \u5b9e\u8bc1 entry=A_SEED_BASE+j\uff09',
    '@PROBEW@': '\u672c\u6ce2\u8bbe\u8ba1=W2..W199 \u9010\u5b57\u590d\u7528',
    '@DISJ@': 'W200 \u5e26\u4e0e v1 \u5728\u7528\u5e26\uff0810_000..10_099/20_000..20_019\uff09\u3001W1 ext \u5e26\uff0810_100..12_099/20_100..20_299\uff09\u3001W2..W199 \u5e26\uff08**\u5168\u6ce8\u518c\u5355\u6001**\uff09',
    '@POOL4@': '\u5df2\u843d\u8d26\u51c0\u503c\uff08\u8d77\u7a3f\u7a97\u5b9e\u6d41 W1..W199 \u5df2\u843d\u8d26 435,720 \u5b9e\u6d4b\u00b7derive \u7981\u624b\u6284\uff09+\u672c\u6ce2 2,200',
    '@LEDGER@': 'batch_name="PERPETUAL-N1-W200", batch_trials=2200, file_name="results/perpetual_faces/n1_w200_results.json"',
    '@CLI@': '--wave 200/finalize --wave 200',
    '@ENG6@': '\u3010n1_w200/ \u5206\u7247\u8ba1\u6570\u589e\u957f\u00b7\u552f\u4e00\u70b9\u706b\u8bc1\u636e\u00b7r325 \u5f8b\u3011',
    '@SHARD@': 'results/p2cal_ext/n1_w200/shard-<k>-of-12.json',
    '@RFN@': 'results/perpetual_faces/n1_w200_results.json',
    '@FINPRE@': 'finalize \u952e\u5e8f\u524d\u7f6e=**\u8d77\u7a3f\u7a97\u96f6\u5728\u98de\u4e0a\u6e38\u5e2d\uff08W198/W199 finalize \u5747\u5df2\u843d origin\u00b7ls-tree \u673a\u8bc1\uff09**\u2014\u2014\u8dd1\u65f6\u6309 registry \u952e derive \u590d\u6838\u00b7FAIL-CLOSED r307 \u4e24\u6001\u4f8b\u6052\u5728\u3002',
    '@EOBD@': '\uff08engine_owner==bm-a 114 \u884c\u6ce8\u518c + \u672c\u5019\u9009\u2014\u2014\u4ee5 probe leg0 \u673a\u8bc1\u4e3a\u51c6\uff09',
    '@BGATE@': '\uff08p2_calibration v1/v2 canon\uff1bv1 ext\uff1bv2..W199 \u843d\u5730\uff09',
    '@S7@': '\u5f85 W200 finalize \u7a97\u3011\n- \uff08\u5360\u4f4d\u00b7finalize one-pass \u540e\u673a\u68b0\u56de\u586b\uff1a\u8d26\u672c\u6052\u7b49\u5f0f+\u5408\u5e76\u6c60 K+merged mu/w-only mu/mu_delta+sigma+se_mu+skill_line_v2 K-lift+A \u6863 p95+\u00a75 \u56db\u9884\u952e\u673a\u8bc1+canon flip \u6001+audit.finalize_only+voids_applied\uff09\u3002',
    '@S8@': '\u3010finalize \u540c\u7a97\u56de\u586b\u00b7\u5f85 W200 finalize \u7a97\u3011\n- \uff08\u5360\u4f4d\u00b7\u00a75.5 W201+ \u6295\u5f71\u627f\u63a5+\u5b9d\u85cf/\u65b9\u6cd5\u8bba\u6355\u83b7\u95ee+\u8bda\u5b9e\u62ab\u9732\u9762\u00b7finalize \u6536\u53e3\u7a97\u673a\u68b0\u56de\u586b\uff09\u3002',
    '@WAVEFREE@': '\u6ce2\u53f7 200=\u6ce8\u518c\u8868 W199 \u5e2d\u540e\u9996\u4e2a\u81ea\u7531\u53f7'
}
assert len(BACK) == len(OLD_BACK) == 40, (len(BACK), len(OLD_BACK))
assert set(BACK) == set(OLD_BACK), "token set drift: %s" % (
    set(BACK) ^ set(OLD_BACK))

# ---- two-phase vmap (DRY whole-file gate, zero-write-first) ----
src = io.open(SRC, encoding="utf-8").read()
assert src.count("\r\n") == 0, "src blob expected LF"
src = src.replace("SEED_REGISTRY \u5168\u952e 195 \u503c",
                  "SEED_REGISTRY \u5168\u952e @@REGN@@ \u503c")
out_t = src
for tok, old in OLD_BACK.items():
    n = out_t.count(old)
    assert n == 1, "TOK %s count=%d (old head=%r)" % (tok, n, old[:80])
    out_t = out_t.replace(old, tok)
for tok, new in BACK.items():
    out_t = out_t.replace(tok, new)
out_t = out_t.replace("SEED_REGISTRY \u5168\u952e @@REGN@@ \u503c",
                      "SEED_REGISTRY \u5168\u952e %d \u503c" % REG_N)
resid = re.findall(r"@[A-Z0-9]+@", out_t)
assert not resid, "unsubstituted tokens remain: %s" % resid[:5]
bad = [mm.group() for mm in
       re.finditer(r"(\d{3})_(\d{3})\.(\d{3})_(\d{3})", out_t)
       if int(mm.group(3)) < int(mm.group(1))]
assert not bad, "malformed windows: %s" % bad[:4]
assert out_t.count("PERPETUAL-N1-W200") == 3, "batch id count drift"
assert out_t.count("\n") == src.count("\n"), "line structure drift"
for stale in ("FIFTY-NINTH", "452_404..454_403", "452_604..452_803",
              "452_604..454_603", "452_404..452_603", "452_604+j",
              "454_604+j", "PERPETUAL-N1-W199",
              "PERPETUAL_N1_W199_PREREG", "n1_w198_results.json",
              "n1_w199/", "435,540", "845,545",
              "1.1878", "1.1877", "1.1876", "0.3279", "0.245097",
              "W198-only \u5b9e\u6d4b", "0.0971", "line_pre 1.1878",
              "n_eff 847,745", "_r918bma", "3a875bf43",
              "MSG-2026-10-09-1507", "283379899",
              "engine_owner==bm-a 113",
              "\u7b2c 189 \u6ce2", "\u7b2c\u4e00\u767e\u4e00\u5341\u56db\u679a",
              "\u6cf5\u7b2c 197 \u679a", "W2..W198",
              "W1..W198", "\u5f85 W199 finalize \u7a97", "W200+ \u6295\u5f71",
              "engine_owner \u884c 188", "W197/W198 finalize",
              "pre-W199", "r914 v2", "r919\u00b7buildgen",
              "r918 probe \u5355\u8dd1"):
    assert stale not in out_t, "stale token survives: %r" % stale
assert M + "0.0928" in out_t and M + "0.0860" in out_t, "U+2212 forms"
assert out_t.count(M + "0.0001/W191") == 1
assert "W191=bm-a r894 freeze\uff08e5e4af81b\uff09" in out_t
assert "\uff1bW196=bm-a r912 freeze\uff0802cf6b44d\uff09\uff1bW197=bm-a " \
    "r915 freeze\uff08522a0aef5\uff09\uff1bW198=bm-a r916 freeze" \
    "\uff0882b881a4f\uff09\uff1bW199=bm-a r919 freeze" \
    "\uff08f312ec9d4\uff09\u3002" in out_t
assert out_t.count("n1_w199_results.json") == 2
assert out_t.count("W1..W199 N1 finalize \u5df2\u5168\u90e8\u843d\u5730") \
    == 2
assert out_t.count("n1_w200") == 4
assert "SIXTIETH" in out_t
assert "W199-only \u5b9e\u6d4b" in out_t, "anchor w-only face missing"
assert "852,145" in out_t and "435,720" in out_t and "437,920" in out_t
assert "454_804..456_803" in out_t and "456_804..457_003" in out_t
assert "849,945" in out_t, "n_eff face missing (legit survivor)"
assert out_t.count("433,520") == 1, "W198 K historical ref must be exactly 1"
assert out_t.count("849,945") == 2, "n_eff + W198 ledger refs must be exactly 2"
assert out_t.count("82b881a4f") == 2, "W198 freeze sha refs (chain+seatblock)"
assert "0.3304" in out_t and "0.245112" in out_t and "0.000371" in out_t
assert "1.1881" in out_t and "line_pre 1.188" in out_t
assert "f312ec9d4" in out_t, "W199 freeze sha missing (chain+seatblock)"
assert "143fcfe1b" in out_t, "W200 seat sha missing"
assert "980db1d3e" in out_t, "seat-round archive-closeout commit missing"

open(OUT, "wb").write(out_t.replace("\n", "\r\n").encode("utf-8"))
chk = io.open(OUT, encoding="utf-8", newline="").read()
assert chk == out_t.replace("\n", "\r\n"), "CRLF roundtrip drift"
print("W200 prereg built: %s bytes=%d crlf=%d" %
      (OUT, len(chk.encode("utf-8")), chk.count("\r\n")))
print("post-transform asserts PASS (counts, residue-zero, malformed-zero,"
      " stale-sweep CLEAN, U+2212 forms, anchor=W199 actuals r590)")
