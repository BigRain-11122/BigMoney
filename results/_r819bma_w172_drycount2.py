# -*- coding: utf-8 -*-
"""r819 W172 prereg build -- FULL dry analysis: apply ALL planned composites
on the W171 source, print remaining generic-token counts (EXPECT table
derive). Zero-write."""
import io
import re

SRC = r"results\_r819bma_w172_prereg_src.txt"
src = io.open(SRC, encoding="utf-8").read()

COMPOSITES = [
    ("TITLE", "# PERPETUAL-N1-W171 预注册 · N1 nulls-deepening 泵第 169 枚（never-dry 常供给例波·波序号连续·机面 derive：engine_owner 行 160+本候选=bm-a 第八十七枚自有波【r815】）"),
    ("WAVEFREE", "波号 171=注册表 W170 行后首个自由号"),
    ("VAC", "（r814 probe leg2/leg3 实跑）"),
    ("SEATPUB", "本机席位公示=MSG-2026-10-07-0843-bma-w171-seat 已推 origin 3290e586b 先于本冻结【r565 律·推送窗=r814 seat push 直接快进送达 3290e586b（4-item payload=seat MSG+pre-seat probe 脚本+probe 回执+W170 finalize 产物=W146 同推先例）；self-ack inbox→processed 移位待 W171 finalize 收口窗】"),
    ("MERGE", "（r814 承袭 r812 gate-合并单回执结构·单窗 derive·dual-window parity N/A 诚实注记）"),
    ("AFACE", "本波 **A-ext seed=391_004..393_003**（**A 面=FIRST-CLEAN past prior-wave B 阶梯第三十例**：A 面算术继续带 390_804..392_803 在其起点即被已注册 W170 B 带 390_804..391_003 **拒**（W170 席位 W171+ 投影+r812 probe leg4+W170 行投影散文（r813 冻结件）+W170 §8 承接面（r813 收口窗回填）四投影注记所预言）→ 诚实前向走 **1 hop** 落 **391_004..393_003**·**A base==前波 B 尾+1（391_003+1）机检关系**=**A-hops-prior-B 阶梯几何第三十例（E36 卡）**·非轮转 r587 前向单调断言在走册）"),
    ("BFACE", "**B-ext exit seed=393_004..393_203**（**B 面=FIRST-CLEAN past own-wave A**：B 面算术继续带 391_004..391_203 在注册宇宙上 CLEAN 但**落在本波 A 窗内**（**同窗互斥面 leg2 律·W141 先例**：A 与 B 同一冻结 commit 双注册·互斥断言强制 B 越过本波 A 窗）→ B 带本波 A 窗保留走 **1 hop** 落 **393_004..393_203**·**B base==本波 A 尾+1（393_003+1）机检关系**·hop 链逐跳在 probe 回执；**W170 席位 W171+ 投影+r812 probe leg4+W170 行投影散文 re-derive-MANDATORY 注记三面兑现**：投影预言 W171 须在 post-W170 注册宇宙重 derive 且 derive B 时预留本波 A 窗——本窗双面兑现·A 被拒+阶梯越带如投影所期·B 同窗互斥保留=投影所期·已如实披露非分叉）"),
    ("R250", "R250：W171 带从未指派·测量面零结果可锁"),
    ("SCANFACE", "扫描面=pre-W171 全一百六十八行注册 N1 带表（表尾 W170 行·leg0 机证 168 行）"),
    ("ANCHOR", "起稿窗实况：**W1..W170 N1 finalize 已全部落地**【W170 finalize one-pass bm-a r813 接管窗·§7/§8 已回填（W159/W168/W169 拖延窗先例同律·如实注记）】——净账本锚头 **779,412**（W170 finalize 落账【one-pass·K=371,920 合并池·voids LOWAMP-P1/P2】）"),
    ("POOL", "累计 null 池=371,920+2,200（本波）=**374,120 投影**"),
    ("SEATSENT", "本机 r814 席位 MSG-2026-10-07-0843-bma-w171-seat 已推 origin 3290e586b（r814 seat push·r565 律）·probe W172+ 投影 A 393_004..395_003 / B 393_204..393_403 **naive-B-inside-naive-A re-derive 强制注记+同窗互斥预披露**（投影 B 落投影 A 窗内·W171 B 带 393_004..393_203 注册后将拒 naive W172 A 窗=阶梯 A-hops-prior-B 继承第三十一例待 W172 注册宇宙复核）"),
    ("CLAIMLAW", "表尾后新首个自由号自领·r814 probe 单跑兑现注记（本窗冻结消费）"),
    ("ORDINALS", "T-2026-10-01-141 s1 引擎线第 161 波【bm-a 第八十七枚自有波【机面 derive：engine_owner==bm-a 行 86+本候选以 probe leg0 机证为准·同 W157/W158/W159/W160/W161/W162/W163/W165/W166/W167/W168/W169/W170 最近自有波】。（波号=注册表 W170 行后首个自由号·单态零席位空档；中位公示 MSG-2026-10-07-0843-bma-w171-seat 先推 origin 3290e586b r565 律；lane-free；dept:研究）"),
    ("V2W", "v2..W170 落地"),
    ("ASEED", "entry rng seed=**391_004+j**"),
    ("ASEEDPROSE", "法典 §4 W171 行 A=391_004..393_003·**FIRST-CLEAN past prior-wave B 阶梯第三十例**：算术续带 390_804..392_803 起点即被 W170 B 带拒→1 hop 落 391_004..393_003·A base==前波 B 尾+1 机检关系·E36 卡·hops=1·ADMIT 回执在场"),
    ("BENTRY", "entry rng=**391_004+j**（与 A[j] 同源配对语义逐字·runner 实证 entry=A_SEED_BASE+j）"),
    ("BSEEDPROSE", "exit rng=**393_004+j**（法典 §4 W171 行 B=393_004..393_203·**FIRST-CLEAN past own-wave A**：B 算术续带 391_004..391_203 在注册宇宙上 CLEAN 但落在本波 A 窗内→**同窗互斥面 leg2 律·W141 先例**强制 B 越本波 A 窗→保留走落 393_004..393_203·hops=1·**B base==本波 A 尾+1 机检关系**·非轮转 r587·hop 链逐跳在 probe 回执·与 W170 席位 W171+ 投影+r812 probe leg4+W170 行投影散文+W170 §8 承接面注记兑现收敛·ADMIT 回执在场）"),
    ("GATEW", "r814 bm-a 带闸窗（pre-seat probe r814 单窗·gate 腿合并结构承袭 r812 先例·parity N/A 诚实注记）"),
    ("FN", 'file_name="results/perpetual_faces/n1_w171_results.json"'),
    ("RFN", "results/perpetual_faces/n1_w171_results.json"),
    ("ODOLD", "results/perpetual_faces/n1_w170_results.json"),
    ("S5ANCH", "净账本锚头 779,412=W170 finalize 落账【one-pass·bm-a r813 接管窗·§7/§8 已回填】"),
    ("S51", "（W170 实测键 **−0.0928**·K=371,920 合并池·W170-only 实测 **−0.0927**）"),
    ("S51B", "（W2..W170 共一百六十九面实测 mu 稳定先例·单波跨键微）"),
    ("S52", "键 **0.245153**=W170 合并池实测 0.245153）"),
    ("S53", "A 档 full_sharpe_p95 与 W170 A 档 p95（**0.2931** 实测锚）差 **<0.05**（门标注法 W5..W170 先例"),
    ("KLKEY", "；键 W170 实测 K-lift **−0.0001**【line_merged@K371,920 **1.184**·line_pre 1.1841·n_eff 777,212"),
    ("WAVECLI", "--wave 171/finalize --wave 171"),
    ("EOB", "engine_owner==bm-a 86 行注册"),
    ("W136TO", "W136..W170"),
    ("OWNCHAIN", "W157/W158/W159/W160/W161/W162/W163/W165/W166/W167/W168/W169/W170 最近自有波"),
    ("W2TO", "W2..W170"),
    ("W1TO", "W1..W170"),
    ("PRC", "results/_r814bma_w171_probe_receipt.json"),
    ("PF", "PERPETUAL_N1_W171_PREREG.md"),
    ("B", "PERPETUAL-N1-W171"),
    ("WPN2", "W172+ 投影"),
]

out = src
fail = []
# historical protections FIRST (whole-block extraction, never rolled)
i0 = out.find("W118=bm-b r678 freeze")
i1 = out.find("（cb7314d64）")
assert 0 < i0 < i1, "single-state chain anchors missing"
CHAIN = out[i0:i1 + len("（cb7314d64）")]
assert CHAIN.endswith("W170=bm-a r813 freeze（cb7314d64）"), CHAIN[-60:]
out = out.replace(CHAIN, "@CHAIN@")
print(f"COMPOSITE CHAIN: len={len(CHAIN)}")
KLTAIL = ("W161 **+0.0002**/W165 **−0.0001**/W166 **+0.0000**/W167 **+0.0000**"
          "/W168 **−0.0002**/W169 **+0.0001**/W170 **−0.0001** 如实披露")
assert out.count(KLTAIL) == 1, out.count(KLTAIL)
out = out.replace(KLTAIL, "@KLT@")
SEMTAIL = ("→W165 **0.000408**→W166 **0.000407**→W167 **0.000406**→W168 **0.000404**→W169 **0.000403**→W170 **0.000402**】）")
assert out.count(SEMTAIL) == 1, out.count(SEMTAIL)
out = out.replace(SEMTAIL, "@SEMT@")
s55_i = out.find("5. **W172+ 投影（probe 机证·下波冻结方复核非转抄 r587 律）**")
s55_j = out.find("hop 链逐跳在 probe 回执。", s55_i)
assert 0 < s55_i < s55_j, "sec5.5 anchors missing"
S55 = out[s55_i:s55_j + len("hop 链逐跳在 probe 回执。")]
out = out.replace(S55, "@S55@")
print(f"COMPOSITE S55 wholesale: len={len(S55)}")
for name, needle in COMPOSITES:
    n = out.count(needle)
    print(f"COMPOSITE {name}: count={n}")
    if n < 1:
        fail.append((name, n))
    out = out.replace(needle, "@" + name + "@")
assert not fail, fail

print()
for t in ["W172", "W171", "W170", "W169", "n1_w171", "n1_w170", "371,920",
          "374,120", "779,412", "777,212", "171", "170", "169", "172", "168",
          "391_004", "393_004", "391_003", "393_003", "393_204", "395_204",
          "390_804", "r814", "r813", "r812", "3290e586b",
          "MSG-2026-10-07-0843", "bma-w171-seat", "W171+ 投影",
          "1.184", "1.1841", "0.245153", "0.2931", "−0.0927", "−0.0928",
          "0.000402", "0.000403", "第 169 枚", "第 161 波", "行 160",
          "第八十七枚", "一百六十八", "一百六十九", "阶梯第三十例", "第三十一例"]:
    c = out.count(t)
    print(f"REMAIN {t!r}: {c}")
    if c:
        i = out.find(t)
        print(f"   ctx: {out[max(0,i-45):i+55]!r}")
