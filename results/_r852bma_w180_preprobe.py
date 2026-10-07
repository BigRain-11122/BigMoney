# -*- coding: utf-8 -*-
"""r852 bm-a W180 pre-TOK probe (r775 law: pre-TOK evidence list BEFORE any
buildgen).  Zero writes to canon faces; dumps AST-extracted TOK179/BACK179/
EXPECT from the r849 build script + DRY count verification against the W179
freeze-time blob + FRESH-token value surfaces for the S80 construction."""
import ast
import io
import json
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# --- 1. freeze-time blob (6f14c35d5 = W179 prereg freeze commit) -----------
blob = subprocess.run(
    ["git", "show", "6f14c35d5:research/PERPETUAL_N1_W179_PREREG.md"],
    capture_output=True).stdout
assert blob, "blob unreachable"
r = subprocess.run(
    ["git", "rev-parse", "6f14c35d5:research/PERPETUAL_N1_W179_PREREG.md"],
    capture_output=True, text=True)
blob_sha = r.stdout.strip()
src = blob.decode("utf-8")
assert "\r\n" not in src, "blob expected LF"

# --- 2. AST-extract TOK179/BACK179/EXPECT from the r849 build script -------
src849 = io.open(r"results\_r849bma_w179_prereg_build.py", encoding="utf-8").read()
tree = ast.parse(src849)


def ev(n):
    if isinstance(n, ast.Constant):
        return n.value
    raise AssertionError("unsupported node %r" % (ast.dump(n)[:80],))


TOK179 = None
BACK179 = None
EXPECT = None
for node in tree.body:
    if isinstance(node, ast.Assign) and len(node.targets) == 1:
        tg = node.targets[0]
        if isinstance(tg, ast.Name) and isinstance(node.value, ast.List):
            if tg.id == "TOK179":
                TOK179 = [(ev(p.elts[0]), ev(p.elts[1])) for p in node.value.elts
                          if isinstance(p, ast.Tuple)]
            if tg.id == "BACK179":
                BACK179 = [(ev(p.elts[0]), ev(p.elts[1])) for p in node.value.elts
                           if isinstance(p, ast.Tuple)]
        if isinstance(tg, ast.Name) and tg.id == "EXPECT" and isinstance(node.value, ast.Dict):
            EXPECT = {ev(k): ev(v) for k, v in zip(node.value.keys, node.value.values)}
assert TOK179 and BACK179 and EXPECT, (bool(TOK179), bool(BACK179), bool(EXPECT))
assert len(BACK179) == len(TOK179) == 50, (len(TOK179), len(BACK179))
toks_b = [t for (t, _v) in BACK179]
toks_t = [t for (_o, t) in TOK179]
assert toks_b == toks_t, "TOK/BACK token order divergence"
print("extracted: TOK179=%d BACK179=%d EXPECT=%d" % (len(TOK179), len(BACK179), len(EXPECT)))

# --- 3. DRY count verification against the W179 freeze-time blob ------------
# TOK179 (from the r849 build) = W178-era old side -- diagnostic only.
# The S80 old side = BACK179 values (W179-era), consumed SEQUENTIALLY in
# BACK179 list order (r735 order law: long composites first; each earlier
# replacement removes occurrences so later short tokens see the remainder).
mism = []
mism_tok179 = []
counts = {}
for old, tok in TOK179:
    n = src.count(old)
    if n != EXPECT[tok]:
        mism_tok179.append(tok)
out_t = src
seq_pass = True
for tok, old in BACK179:
    n = out_t.count(old)
    counts[tok] = n
    if n != EXPECT[tok]:
        seq_pass = False
        mism.append({"tok": tok, "old": old[:80], "count": n, "expect": EXPECT[tok]})
    out_t = out_t.replace(old, tok)
print("TOK179 (W178-era old side, diagnostic): %d/%d match" %
      (len(TOK179) - len(mism_tok179), len(TOK179)))
print("BACK179 sequential DRY (REAL): %s (%d/%d match)" %
      ("PASS" if seq_pass else "FAIL", len(BACK179) - len(mism), len(BACK179)))
for m in mism[:12]:
    print("  MISMATCH", m["tok"], "count=%d expect=%d" % (m["count"], m["expect"]),
          repr(m["old"][:60]))

# --- 4. FRESH-token value surfaces ------------------------------------------
back179_map = dict(BACK179)
fresh_dump = {}
for tok in ("@S55@", "@SEATPUB@", "@ORDINALS@", "@OWNCHAIN@", "@CHAIN@", "@KLT@",
            "@SEMT@", "@N171@", "@N170@", "@N169@", "@TITLE@", "@ANCHOR@",
            "@KLKEY@", "@AFACE@", "@BFACE@", "@SEATSENT@", "@ASEEDPROSE@",
            "@S5ANCH@", "@POOL@", "@WAVEFREE@", "@WAVECLI@", "@FN@", "@ODOLD@",
            "@B@", "@EOB@"):
    fresh_dump[tok] = back179_map[tok]
sem = back179_map["@SEMT@"]
klt = back179_map["@KLT@"]
print("@SEMT@ '】）' count:", sem.count("】）"))
print("@KLT@ ' 如实披露' count:", klt.count(" 如实披露"))
print("@CHAIN@ tail:", repr(back179_map["@CHAIN@"][-80:]))

# --- 5. environment checks ---------------------------------------------------
print("bandgate mentions in blob:", src.count("bandgate"), "| 带闸:", src.count("带闸"))
print("净账本锚头 797,505:", src.count("净账本锚头 797,505"))
print("797,505 total:", src.count("797,505"), "| 795,305:", src.count("795,305"),
      "| 389,520:", src.count("389,520"), "| **391,720 投影**:",
      src.count("**391,720 投影**"), "| bare 391,720:", src.count("391,720"))
print("PERPETUAL-N1-W179:", src.count("PERPETUAL-N1-W179"),
      "EXPECT[@B@]+1 =", EXPECT["@B@"] + 1)
for probe in ("r848 probe 回执", "（r848 probe leg2", "r844 probe", "r845 冻结件",
              "已回填（r846 窗", "4c645c95f", "【r849】", "THIRTY-NINTH",
              "第三十九例", "0.3275", "0.245104", "−0.0923", "1.1849",
              "389,520", "r848 probe leg4", "r848 bm-a 带闸窗"):
    print("blob has %-24r : %d" % (probe, src.count(probe)))

json.dump({
    "blob_sha": blob_sha, "blob_bytes": len(blob),
    "tok_count": len(TOK179), "dry_mismatches": mism,
    "expect": EXPECT, "counts": counts,
    "fresh_dump": fresh_dump,
    "semt_close_count": sem.count("】）"),
    "klt_tail_count": klt.count(" 如实披露"),
}, open(r"results\_r852bma_w180_preprobe.json", "w", encoding="utf-8"),
    ensure_ascii=False, indent=1)
print("preprobe written: results/_r852bma_w180_preprobe.json")
