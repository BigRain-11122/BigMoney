# -*- coding: utf-8 -*-
"""r863 bm-a W181 pre-TOK probe (r775 law: pre-TOK evidence list BEFORE any
buildgen).  Zero writes to canon faces; dumps AST-extracted TOK180/BACK180/
EXPECT from the r852 build script + DRY count verification against the W180
freeze-time blob + FRESH-token value surfaces for the S81 construction.
Bloodline: r852 preprobe machinery rolled one generation (W180 facts:
probe r862 ADMIT A 413_004..415_003 staircase FORTY-FIRST / B 415_004..415_203;
W180 finalize r854 one-pass head 801,905 K 393,920; W180 freeze 568848aa4;
W181 seat push 971316069)."""
import ast
import io
import json
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# --- 1. freeze-time blob (220a7b305 = W180 prereg freeze commit) -----------
blob = subprocess.run(
    ["git", "show", "220a7b305:research/PERPETUAL_N1_W180_PREREG.md"],
    capture_output=True).stdout
assert blob, "blob unreachable"
r = subprocess.run(
    ["git", "rev-parse", "220a7b305:research/PERPETUAL_N1_W180_PREREG.md"],
    capture_output=True, text=True)
blob_sha = r.stdout.strip()
assert blob_sha == "d863d90725f2094351742e099cd5d5197f151248", blob_sha
src = blob.decode("utf-8")
assert "\r\n" not in src, "blob expected LF"

# --- 2. AST-extract TOK180/BACK180/EXPECT from the r852 build script -------
src852 = io.open(r"results\_r852bma_w180_prereg_build.py", encoding="utf-8").read()
tree = ast.parse(src852)


def ev(n):
    if isinstance(n, ast.Constant):
        return n.value
    raise AssertionError("unsupported node %r" % (ast.dump(n)[:80],))


TOK180 = None
BACK180 = None
EXPECT = None
for node in tree.body:
    if isinstance(node, ast.Assign) and len(node.targets) == 1:
        tg = node.targets[0]
        if isinstance(tg, ast.Name) and isinstance(node.value, ast.List):
            if tg.id == "TOK180":
                TOK180 = [(ev(p.elts[0]), ev(p.elts[1])) for p in node.value.elts
                          if isinstance(p, ast.Tuple)]
            if tg.id == "BACK180":
                BACK180 = [(ev(p.elts[0]), ev(p.elts[1])) for p in node.value.elts
                           if isinstance(p, ast.Tuple)]
        if isinstance(tg, ast.Name) and tg.id == "EXPECT" and isinstance(node.value, ast.Dict):
            EXPECT = {ev(k): ev(v) for k, v in zip(node.value.keys, node.value.values)}
assert TOK180 and BACK180 and EXPECT, (bool(TOK180), bool(BACK180), bool(EXPECT))
assert len(BACK180) == len(TOK180) == 50, (len(TOK180), len(BACK180))
toks_b = [t for (t, _v) in BACK180]
toks_t = [t for (_o, t) in TOK180]
assert toks_b == toks_t, "TOK/BACK token order divergence"
print("extracted: TOK180=%d BACK180=%d EXPECT=%d" % (len(TOK180), len(BACK180), len(EXPECT)))

# --- 3. DRY count verification against the W180 freeze-time blob ------------
# TOK180 (from the r852 build) = W179-era old side -- diagnostic only.
# The S81 old side = BACK180 values (W180-era), consumed SEQUENTIALLY in
# BACK180 list order (r735 order law).
mism = []
mism_tok180 = []
counts = {}
for old, tok in TOK180:
    n = src.count(old)
    if n != EXPECT[tok]:
        mism_tok180.append(tok)
out_t = src
seq_pass = True
for tok, old in BACK180:
    n = out_t.count(old)
    counts[tok] = n
    if n != EXPECT[tok]:
        seq_pass = False
        mism.append({"tok": tok, "old": old[:80], "count": n, "expect": EXPECT[tok]})
    out_t = out_t.replace(old, tok)
print("TOK180 (W179-era old side, diagnostic): %d/%d match" %
      (len(TOK180) - len(mism_tok180), len(TOK180)))
print("BACK180 sequential DRY (REAL): %s (%d/%d match)" %
      ("PASS" if seq_pass else "FAIL", len(BACK180) - len(mism), len(BACK180)))
for m in mism[:12]:
    print("  MISMATCH", m["tok"], "count=%d expect=%d" % (m["count"], m["expect"]),
          repr(m["old"][:60]))

# --- 4. FRESH-token value surfaces ------------------------------------------
back180_map = dict(BACK180)
fresh_dump = {}
for tok in ("@S55@", "@SEATPUB@", "@ORDINALS@", "@OWNCHAIN@", "@CHAIN@", "@KLT@",
            "@SEMT@", "@N171@", "@N170@", "@N169@", "@TITLE@", "@ANCHOR@",
            "@KLKEY@", "@AFACE@", "@BFACE@", "@SEATSENT@", "@ASEEDPROSE@",
            "@S5ANCH@", "@POOL@", "@WAVEFREE@", "@WAVECLI@", "@FN@", "@ODOLD@",
            "@B@", "@EOB@"):
    fresh_dump[tok] = back180_map[tok]
sem = back180_map["@SEMT@"]
klt = back180_map["@KLT@"]
print("@SEMT@ close-bracket count:", sem.count("】）"))
print("@KLT@ tail count:", klt.count(" 如实披露"))
print("@CHAIN@ tail:", repr(back180_map["@CHAIN@"][-90:]))

# --- 5. environment checks ---------------------------------------------------
print("bandgate mentions in blob:", src.count("bandgate"), "| 带闸:", src.count("带闸"))
print("净账本锚头 799,705:", src.count("净账本锚头 799,705"))
print("799,705 total:", src.count("799,705"), "| 797,505:", src.count("797,505"),
      "| 391,720:", src.count("391,720"), "| **393,920 投影**:",
      src.count("**393,920 投影**"), "| bare 393,920:", src.count("393,920"))
print("PERPETUAL-N1-W180:", src.count("PERPETUAL-N1-W180"),
      "EXPECT[@B@]+1 =", EXPECT["@B@"] + 1)
for probe_s in ("r851 probe 回执", "（r851 probe leg2", "r848 probe", "r849 冻结件",
                "已回填（r850 窗", "d3b0737fe", "【r851】", "FORTIETH",
                "第四十例", "0.3265", "0.245086", "−0.0932", "1.1850",
                "391,720", "r851 probe leg4", "r851 bm-a 带闸窗"):
    print("blob has %-24r : %d" % (probe_s, src.count(probe_s)))

json.dump({
    "blob_sha": blob_sha, "blob_bytes": len(blob),
    "tok_count": len(TOK180), "dry_mismatches": mism,
    "expect": EXPECT, "counts": counts,
    "fresh_dump": fresh_dump,
    "semt_close_count": sem.count("】）"),
    "klt_tail_count": klt.count(" 如实披露"),
}, open(r"results\_r863bma_w181_preprobe.json", "w", encoding="utf-8"),
    ensure_ascii=False, indent=1)
print("preprobe written: results/_r863bma_w181_preprobe.json")
