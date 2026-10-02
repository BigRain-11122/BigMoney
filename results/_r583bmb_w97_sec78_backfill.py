# r583 bm-b: W97 prereg sec7/8 mechanical backfill v2
# (runtime slice anchors -- zero hand-typed anchor bytes, r570 law)
P = 'research/PERPETUAL_N1_W97_PREREG.md'
b = open(P, 'rb').read()
assert b.count(b'\r\n') == 0, 'expected pure LF file'
s = b.decode('utf-8')

S7 = '\u00a77'
S8 = '\u00a78'
END = '\u8dd1\u524d\u51bb\u7ed3'  # 跑前冻结
i7 = s.find('## ' + S7)
i8 = s.find('## ' + S8)
ie = s.find('- **' + END)
assert 0 < i7 < i8 < ie, (i7, i8, ie)

new7 = (
'## \u00a77 跑后实证。【r581 冻结占位·r583 finalize 收口机械回填】\n\n'
'- 12/12 分片 bm-b 引擎烧毕（r581 冻结 commit 后 tick 架构自燃免重启·r535 律·r582 窗 12/12 烧毕·产品 12/12 r582 已交付 origin=r310 完备性门实核）；finalize one-pass（r538 律·首跑禁重跑·r583 首 commit 携带产物）。\n'
'- ledger：prev_total 575,748（W96 bm-a r583 落账解锁·链序 W94 571,348 bm-a→W95 573,548 bm-b→W96 575,748 bm-a）+ batch_trials 2,200 = **577,948**；voids_applied=LOWAMP-P1/P2。\n'
'- w97-only：n=2,200·mu=\u22120.0938044·sigma=0.2506648；merged：n=211,320·mu=\u22120.0928240·sigma=0.2448950（§0 投影「W1..W97 落账后 K=211,320」逐位吻合）；mu_delta_w97_vs_w96ext=\u22120.000754。\n'
'- skill_line_v2 @n_eff_held 575,748：1.1682→**1.1685**（K-lift delta +0.0003≤0.02 门内·正负交替如实报〔W93 \u22120.0002→W94 +0.0000→W95 +0.0000→W96 +0.0001→W97 +0.0003〕）；se_mu @K211,320=0.000533（收窄链：W91 0.000550→W93 0.000544→W95 0.000538→W97 0.000533）；canon_flip 未执行（治理提案面·K2200 同法）。\n'
'- §5 预测四门全过：|Δmu|=0.00109<0.02（冻结锚=W91 merged \u22120.0927138）；σ 变化 +0.06%<±10%（键 0.2447465·本波 merged 0.2448950）；A 档 p95 差 0.0010<0.05（锚 0.3275·本波 0.3285）；K-lift +0.0003≥\u22120.02。产物 results/perpetual_faces/n1_w97_results.json（顶层 evidence_cutoff=2026-09-22·cutoff_meta·audit.machine=bm-b·shards_consumed 12）。\n\n'
)

new8 = (
'## \u00a78 批后复盘。【r583 补全】\n\n'
'- 链序实况：冻结窗（r581）五在飞上游席——finalize 收口窗（r583）实况=W95 bm-b r582 落账→W96 bm-a r583 落账→本波 W97 one-pass 落账=三连收口，r307 两态律跑时复核通过（pre-W97 K=209,120 与 W96 merged 逐位吻合=链连续性实证）、零改判据。\n'
'- 供给面：本波 finalize 解锁 W98 bm-a finalize 链序（12/12 产品已在 origin·r583 bm-a 披露「W98 finalize blocked by W97」FAIL-CLOSED 席位依赖=本轮解除）；同窗 W99 bm-c 12/12 烧毕 finalize-pending（候 W98）+W100 bm-b r583 冻结+同窗 W101 bm-a r583 冻结（r531 异号共存面）——供给线连续。\n'
'- §5 W98+ 投影复核：A 239_004..241_003 CLEAN/B 58_201..58_400 CLEAN——下波冻结方 bm-a r582 机验逐位吻合（ADMIT 回执 results/_r582bma_w98_band_gate.py hops 0/0·r302 投影三查先例）。\n\n'
)

s2 = s[:i7] + new7 + s[i8:]
j8 = s2.find('## ' + S8)
s2 = s2[:j8] + new8 + s2[ie:]
assert '\u5360\u4f4d\u00b7finalize \u540e\u673a\u68b0\u56de\u586b' not in s2, 'placeholder line residue remains'
open(P, 'wb').write(s2.encode('utf-8'))
print('backfill v2 written, bytes', len(b), '->', len(s2.encode('utf-8')))
