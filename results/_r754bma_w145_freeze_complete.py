# -*- coding: utf-8 -*-
"""r754 bm-a W145 freeze-window COMPLETION (r753 dead-tail continuation per
r713/r752 law): dead session did band gate + registry insert, died before the
per-wave prereg materialization. This script completes the window:
  Phase A: uncommitted face self-tag fix r753->r754 (freeze commit lands r754;
           receipts keep _r753bma_* provenance names - produced in r753 window)
  Phase B: research/PERPETUAL_N1_W145_PREREG.md materialization from the
           freeze-time W144 source (ff6d2f918, placeholders intact) per r752
           bloodline law: 2-key blanket + 11 phases, every needle count-asserted
           (r735 lineage; needle set = dead-session measure2 + 3 added needles
           per r745 law: bare wave-number header, stale lowercase shard-dir
           counter, and the W145-push two-hop reality lines).
Receipt: results/_r754bma_w145_freeze_complete.json
"""
import io
import json
import subprocess

SRC_REF = "ff6d2f918:research/PERPETUAL_N1_W144_PREREG.md"
receipt = {"probe": "r754 bm-a W145 freeze-window completion (r753 dead-tail)",
           "phase_a": {}, "phase_b": {}, "post_checks": {}}

# ============ PHASE A: face self-tag fix (uncommitted work only) ============
targets = [
    (r"scripts\perpetual_faces.py",
     "# W145 (bm-a r753 freeze, seat MSG-2026-10-06-023x-bma-w145-seat",
     "# W145 (bm-a r754 freeze, seat MSG-2026-10-06-023x-bma-w145-seat"),
    (r"scripts\perpetual_faces_n1.py",
     "# --- W145 materializer face (r753 bm-a freeze, own-series law",
     "# --- W145 materializer face (r754 bm-a freeze, own-series law"),
    (r"scripts\perpetual_faces_n1.py",
     "# band facts (law sec.4 W145 row, r753): A = FIRST-CLEAN past",
     "# band facts (law sec.4 W145 row, r754): A = FIRST-CLEAN past"),
    (r"scripts\perpetual_faces_n1.py",
     "W145 row, r753 bm-a] ",
     "W145 row, r754 bm-a] "),
]
for path, old, new in targets:
    t = io.open(path, encoding="utf-8").read()
    if old in t:
        n = t.count(old)
        assert n == 1, "PHASE A needle %r count %d != 1" % (old[:60], n)
        t = t.replace(old, new)
        receipt["phase_a"][path + "|" + old[:40]] = 1
    else:
        assert t.count(new) == 1, "PHASE A needle absent and new tag missing"
        receipt["phase_a"][path + "|" + old[:40]] = "idempotent-skip"
    assert t.count(old) == 0 and t.count(new) >= 1
    io.open(path, "w", encoding="utf-8", newline="\n").write(t)

# ============ PHASE B: prereg materialization ============
src = subprocess.run(["git", "show", SRC_REF], capture_output=True,
                     check=True).stdout.decode("utf-8")
assert "## §7 跑后实证。【finalize 收口机械回填·占位——跑前为空】" in src, \
    "source must be the freeze-time version (placeholders intact)"
assert "## §8 批后复盘。【finalize 同窗回填·占位】" in src

# phase 1: 2-key blanket (r752 bloodline; W142/W141 = historical refs, NOT shifted)
s = src.replace("W144", "W145").replace("W143", "W144")
receipt["phase_b"]["blanket"] = {"W144_to_W145": src.count("W144"),
                                 "W143_to_W144": src.count("W143")}

def rep(old, new, expect):
    global s
    n = s.count(old)
    assert n == expect, "needle %r count %d != %d" % (old[:60], n, expect)
    s = s.replace(old, new)
    return n

# phase 2a: section-5.5 W146+ projection rewrite (before window replace-alls)
rep("W145+ 投影（gate 机证", "W146+ 投影（gate 机证", 1)
rep("A first-clean 333_604..335_603 **CLEAN**（hops=0）",
    "A first-clean 335_804..337_803 **CLEAN**（hops=0）", 1)
rep("B first-clean **333_804..334_003 CLEAN**（hops=0）",
    "B first-clean **336_004..336_203 CLEAN**（hops=0）", 1)
rep("W141 同窗互斥先例适用于 W145：W145 冻结方",
    "W141 同窗互斥先例适用于 W146：W146 冻结方", 1)
rep("拒 naive W145 A 窗", "拒 naive W146 A 窗", 1)
rep("verify at W145 prereg", "verify at W146 prereg", 1)
rep("W145 A 重 derive 同强制", "W146 A 重 derive 同强制", 1)
rep("W145+ 投影承接", "W146+ 投影承接", 1)  # section-8 placeholder

# phase 2b: claim seat (specific first, then remaining)
rep("r750 席位 MSG-2026-10-06-002x", "r753 席位 MSG-2026-10-06-023x", 1)
rep("投影 W145+ A 331_404..333_403 naive", "投影 W145+ A 333_604..335_603 naive", 1)
rep("r750 席位", "r753 席位", 1)

# phase 2c: own-B window replace-all FIRST, then prior-B (substring-order law)
rep("333_604..333_803", "335_804..336_003", 6)
rep("B 带 331_404..331_603 **拒**", "B 带 333_604..333_803 **拒**", 1)
rep("（r750 W144 gate 尾投影注记所预言）", "（r752 W145 gate 尾投影注记所预言）", 1)
rep("r750 W144 gate 尾投影 re-derive-MANDATORY",
    "r752 W145 gate 尾投影 re-derive-MANDATORY", 1)

# phase 2c-2: history tail
rep("W144=bm-a r750 freeze（86d3b070c·表尾）",
    "W144=bm-a r752 freeze（ff6d2f918·表尾）", 1)

# phase 2d: A windows / naive continuations / machine-checks / seeds
rep("331_604..333_603", "333_804..335_803", 5)
rep("331_404..333_403", "333_604..335_603", 2)
rep("331_604..331_803", "333_804..334_003", 2)
rep("（331_603+1）机检关系", "（333_803+1）机检关系", 1)
rep("（333_603+1）机检关系", "（335_803+1）机检关系", 1)
rep("seed=**331_604+j**", "seed=**333_804+j**", 1)
rep("entry rng=**331_604+j**", "entry rng=**333_804+j**", 1)
rep("exit rng=**333_604+j**", "exit rng=**335_804+j**", 1)
rep("阶梯第三例", "阶梯第四例", 3)

# phase 2e: seat/probe/receipt/push-window names
rep("_r752bma_w144_band_gate.py", "_r753bma_w145_band_gate.py", 2)
rep("_r751bma_w144_probe_receipt.json", "_r753bma_w145_probe_receipt.json", 1)
rep("_r751bma_w144_probe.py", "_r753bma_w145_probe.py", 2)
rep("MSG-2026-10-06-011x-bma-w144-seat", "MSG-2026-10-06-023x-bma-w145-seat", 2)
rep("已推 origin 2ba4a613f 先于本冻结【r565 律·推送窗=plain fast-forward delivery·behind 0 at fetch·零 UU·零 --no-verify】",
    "已推 origin 55c2a1715 先于本冻结【r565 律·推送窗=two-hop merge delivery 55c2a1715→d5fdbb317——首推撞 origin 前进=r524 behind-signal·merge-mode 收口·零 --no-verify】", 1)
rep("**席位推送窗实录（r751 窗口实况）**：席位+probe 回执单 commit=推送窗 fetch 实核 origin **落后 0** → plain fast-forward delivery 送达 **2ba4a613f**（零 UU·零竞态·零 --no-verify·干净快进）",
    "**席位推送窗实录（r753 窗口实况）**：席位+probe 回执单 commit 推送撞 origin 前进（r524 behind-signal·非快进拒）→ merge-mode 收口 two-hop delivery 送达 **55c2a1715 → d5fdbb317**（零 --no-verify）", 1)
rep("先推 origin 2ba4a613f r565 律", "先推 origin 55c2a1715 r565 律", 1)
rep("bm-a r751 6d93bd7ba", "bm-a r753 247e53cf8", 2)

# phase 2f: ledger / K (specific-before-general: 投影 first)
rep("314,720 投影", "316,920 投影", 1)
rep("312,520", "314,720", 6)
rep("710,611", "712,811", 2)
rep("n_eff 708,411", "n_eff 710,611", 1)

# phase 2g: section-5 prediction keys (W144 finalize actuals)
rep("−0.0928", "−0.0929", 1)
rep("−0.0958", "−0.1049", 1)
assert s.count("**0.2450**") == 1  # verify-only: W144 merged sigma == 0.2450 unchanged
rep("**0.3051**", "**0.3029**", 1)
rep("**1.1787**·line_pre 1.1786", "**1.1788**·line_pre 1.1788", 1)
rep("W141 +0.0001/W144 **+0.0001** 如实披露",
    "W141 +0.0001/W143 +0.0001/W144 **+0.0000** 如实披露", 1)
rep("键 W144 实测 K-lift **+0.0001**", "键 W144 实测 K-lift **+0.0000**", 1)
rep("se_mu 收窄键 W139 0.000444→W140 0.000443→W141 0.000441→W142 0.000440→W144 **0.000438**",
    "se_mu 收窄键 W140 0.000443→W141 0.000441→W142 0.000440→W143 0.000438→W144 **0.000437**", 1)
rep("共一百四十二面", "共一百四十三面", 1)
assert s.count("W136..W144 先例") == 1  # verify-only: shift produced the right range

# phase 2h: ordinals
rep("泵第 142 枚", "泵第 143 枚", 1)
rep("行 133+本候选", "行 134+本候选", 1)
rep("第六十枚", "第六十一枚", 3)
rep("【r752】", "【r754】", 1)
rep("第一百三十四引擎波", "第一百三十五引擎波", 1)
rep("引擎线第 134 波", "引擎线第 135 波", 1)
rep("行 59+本候选", "行 60+本候选", 2)
rep("59 行注册", "60 行注册", 1)
rep("全一百四十一行", "全一百四十二行", 1)
rep("leg0 机证 141 行", "leg0 机证 142 行", 1)
rep("同 W140/W141/W142/W144", "同 W141/W142/W143/W144", 2)
rep("r752 bm-a 冻结窗",
    "r753→r754 bm-a 冻结窗（r753 窗死尾·r754 续成收口——pre-seat probe 先跑·双窗 derive 恒等）", 1)
rep("波号 143=注册表 W144 行后首个自由号",
    "波号 145=注册表 W144 行后首个自由号", 1)  # r745-law added needle: bare wave number

# phase 2i: runner faces (own-first substring-order law)
rep("n1_w144_results.json", "n1_w145_results.json", 2)
rep("n1_w143_results.json", "n1_w144_results.json", 1)
rep("n1_w143/ 分片计数", "n1_w145/ 分片计数", 1)  # r745-law added: stale lowercase
rep("n1_w144/shard", "n1_w145/shard", 1)
rep("--wave 144", "--wave 145", 2)

# post checks
checks = {
    "title": ("# PERPETUAL-N1-W145 预注册 · N1 nulls-deepening 泵第 143 枚" in s),
    "batch_name": ("批名=**PERPETUAL-N1-W145**" in s),
    "finalize_batch": ('batch_name="PERPETUAL-N1-W145"' in s),
    "s7_placeholder": ("## §7 跑后实证。【finalize 收口机械回填·占位——跑前为空】" in s),
    "s8_placeholder": ("## §8 批后复盘。【finalize 同窗回填·占位】" in s),
    "A_band": ("A-ext seed=333_804..335_803" in s),
    "B_band": ("B-ext exit seed=335_804..336_003" in s),
    "no_stale_W144_band": ("331_604..333_603" not in s),
    "no_stale_prior_B": ("331_404..331_603" not in s),
    "evidence_cutoff": ('evidence_cutoff=**2026-09-22**' in s),
    "K_projection": ("314,720+2,200（本波）=**316,920 投影**" in s),
    "ledger_head": ("**712,811**" in s),
    "w146_projection": ("A first-clean 335_804..337_803 **CLEAN**（hops=0）" in s),
    "staircase_fourth": ("阶梯第四例" in s and "阶梯第三例" not in s),
    "freeze_tail": ("**跑前冻结=本件 commit**" in s),
}
receipt["post_checks"] = {k: bool(v) for k, v in checks.items()}
assert all(checks.values()), "post checks failed: %s" % \
    [k for k, v in checks.items() if not v]

# EOL convention: match the existing W144 prereg on-disk form
ref = open(r"research\PERPETUAL_N1_W144_PREREG.md", "rb").read()
crlf = b"\r\n" in ref
data = s.encode("utf-8")
if crlf:
    data = s.replace("\r\n", "\n").replace("\n", "\r\n").encode("utf-8")
io.open(r"research\PERPETUAL_N1_W145_PREREG.md", "wb").write(data)
receipt["phase_b"]["bytes"] = len(data)
receipt["phase_b"]["eol"] = "CRLF" if crlf else "LF"
receipt["status"] = "PASS"
io.open(r"results\_r754bma_w145_freeze_complete.json", "w",
        encoding="utf-8").write(json.dumps(receipt, ensure_ascii=False, indent=1))
print("FREEZE COMPLETE PASS: prereg %d bytes, eol=%s, all needles asserted"
      % (len(data), receipt["phase_b"]["eol"]))
