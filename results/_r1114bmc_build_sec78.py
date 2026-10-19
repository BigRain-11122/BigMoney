# -*- coding: utf-8 -*-
# r1114 bm-c: build the W277 sec.7/8 backfill clone from the r1111 W276 canon
# by COUNT-ASSERTED ORDERED TRANSFORM (zero transcription; engine batch shas
# machine-verified on the current chain: 0df07c846b six + 644b4f8459 six,
# both ls-tree-verified on origin this window; prereg delivery face honest:
# r1113 CAS-surgical e0bc4a0ddd, not a first-try plain push).
import io, py_compile

def rep(t, old, new, expect, tag, log):
    n = t.count(old)
    assert n == expect, f"[{tag}] count {n} != {expect}: {old[:90]!r}"
    return t.replace(old, new), log + [f"{tag}: {n}x"]

SRC = "results/_r1111bmc_w276_sec78_backfill.py"
DST = "results/_r1114bmc_w277_sec78_backfill.py"
t = io.open(SRC, encoding="utf-8", newline="").read()
log = []
R = [
 ('"""r1111 bm-c: W276 prereg sec.7/8 backfill', '"""r1114 bm-c: W277 prereg sec.7/8 backfill', 1, "s-doc"),
 ('Clone lineage: _r1108bmc_w275_sec78_backfill.py (canon).', 'Clone lineage: _r1111bmc_w276_sec78_backfill.py (canon).', 1, "s-lineage"),
 ('PATH = "research/PERPETUAL_N1_W276_PREREG.md"', 'PATH = "research/PERPETUAL_N1_W277_PREREG.md"', 1, "s-path"),
 ('FK = "results/_r1111bmc_w276_fivekeys.json"', 'FK = "results/_r1114bmc_w277_fivekeys.json"', 1, "s-fk"),
 ('RES = "results/perpetual_faces/n1_w276_results.json"', 'RES = "results/perpetual_faces/n1_w277_results.json"', 1, "s-res"),
 ('prev 1,029,335 + batch 2,200 = **1,031,535 EXACT**', 'prev 1,031,535 + batch 2,200 = **1,033,735 EXACT**', 1, "s-led"),
 ('合并池 K：602,920 + 2,200 = **605,120 EXACT**', '合并池 K：605,120 + 2,200 = **607,320 EXACT**', 1, "s-k"),
 ('line_pre = fk["skill_line"]["line_pre_w276"]', 'line_pre = fk["skill_line"]["line_pre_w277"]', 1, "s-lpre-acc"),
 ('semu = fk["merged"]["se_mu_k605120"]', 'semu = fk["merged"]["se_mu_k607320"]', 1, "s-semu-acc"),
 ('wonly_mu = fk["w276_only"]["mu"]', 'wonly_mu = fk["w277_only"]["mu"]', 1, "s-womu-acc"),
 ('wonly_sig = fk["w276_only"]["sigma"]', 'wonly_sig = fk["w277_only"]["sigma"]', 1, "s-wosig-acc"),
 ('line_m = fk["skill_line"]["line_merged_605120"]', 'line_m = fk["skill_line"]["line_merged_607320"]', 1, "s-lm-acc"),
 ('k1 = ck["key1_w276_vs_merged_mu_gap"]["value"]', 'k1 = ck["key1_w277_vs_merged_mu_gap"]["value"]', 1, "s-k1-acc"),
 ('k1b = ck["key1b_merged_vs_w275_key"]["value"]', 'k1b = ck["key1b_merged_vs_w276_key"]["value"]', 1, "s-k1b-acc"),
 ('  # W274 frozen key, machine-read', '  # W276 frozen key, machine-read', 1, "s-ksemu-comment"),
 ('**se_mu@K605,120 = {semu:.6f}**（对照本波冻结键 W275 {ksemu:.6f}', '**se_mu@K607,320 = {semu:.6f}**（对照本波冻结键 W276 {ksemu:.6f}', 1, "s-semu"),
 ('W276-only mu = {womu:.8f} / sigma = {wosig:.8f}', 'W277-only mu = {womu:.8f} / sigma = {wosig:.8f}', 1, "s-wonly"),
 ('line_pre_w276 = {lpre:.4f} → line_merged@605,120 = {lm:.4f}', 'line_pre_w277 = {lpre:.4f} → line_merged@607,320 = {lm:.4f}', 1, "s-line"),
 ('key1b merged-vs-W275键 {k1b:.7f}', 'key1b merged-vs-W276键 {k1b:.7f}', 1, "s-k1b"),
 ('收据 results/_r1111bmc_w276_fivekeys.json（键=n1_w275_results.json 机读 r587 律·', '收据 results/_r1114bmc_w277_fivekeys.json（键=n1_w276_results.json 机读 r587 律·', 1, "s-fkrecpt"),
 ('本波预测键冻结于 W275 实测——W275 finalize 起草窗前已落地·活链头基准）', '本波预测键冻结于 W276 实测——W276 finalize 起草窗前已落地·活链头基准）', 1, "s-fkrecpt2"),
 ('PRE-FINALIZE **ALL PASS 第 39 连续正确相位**（results/_r1111bmc_w276_sixgate.json', 'PRE-FINALIZE **ALL PASS 第 40 连续正确相位**（results/_r1114bmc_w277_sixgate.json', 1, "s-six"),
 ('worktree==落链 git blob @ 354a645155【r1111 bm-c 窗落的 splice·CLEAN-AT-BIRTH 第 9 代（引擎机械面）', 'worktree==落链 git blob @ 9e53371814【r1114 bm-c 窗落的 splice·CLEAN-AT-BIRTH 第 10 代（引擎机械面）', 1, "s-splice"),
 ('零编辑器 authoring heal（全 count-asserted reps first-try·date-roll rep 按代际同日 count-0 事实 DROP 披露）·零引擎机械愈合】；', '2 编辑器 gate-region 表愈合披露（期望表误读·canon 零命中·零 canon 异常·全 count-asserted canon reps first-try）·零引擎机械愈合】；', 1, "s-cab"),
 ('_set_wave(276):1/_set_wave(275):0/_set_wave(274):0 段内过闸', '_set_wave(277):1/_set_wave(276):0/_set_wave(275):0 段内过闸', 1, "s-sw"),
 ('seed_admit_gate FREE x2【base=622501 span=2000 / base=624501 span=200】', 'seed_admit_gate FREE x2【base=624701 span=2000 / base=626701 span=200】', 1, "s-seed"),
 ('preregistered_doc=research/PERPETUAL_N1_W276_PREREG.md', 'preregistered_doc=research/PERPETUAL_N1_W277_PREREG.md', 1, "s-audit-doc"),
 ('§5.5 W277+ 投影承接机证', '§5.5 W278+ 投影承接机证', 1, "s-8head"),
 ('W276 注册宇宙已落地（A 622_501..624_500 + B 624_501..624_700，本波冻结收据', 'W277 注册宇宙已落地（A 624_701..626_700 + B 626_701..626_900，本波冻结收据', 1, "s-8univ"),
 ('_w276bmc_freeze_receipt.json）——W277 A naive 起点 624_501', '_w277bmc_freeze_receipt.json）——W278 A naive 起点 626_701', 1, "s-8naiveA1"),
 ('（pre-W276 宇宙 leg4 实测 CLEAN hops=0·收据 _w276bmc_20261019_probe_receipt.json）在 post-W276 注册宇宙上', '（pre-W277 宇宙 leg4 实测 CLEAN hops=0·收据 _w277bmc_20261019_probe_receipt.json）在 post-W277 注册宇宙上', 1, "s-8naiveA2"),
 ('落注册 W276 B 带 624_501..624_700 内（staircase-affects-A 第 26 次 A-hop 预期', '落注册 W277 B 带 626_701..626_900 内（staircase-affects-A 第 27 次 A-hop 预期', 1, "s-8refuse"),
 ('B naive 624_501..624_900 落投影 A 窗内·post-W276 宇宙活链重 derive 决定', 'B naive 626_901..627_100 落投影 A 窗内·post-W277 宇宙活链重 derive 决定', 1, "s-8naiveB"),
 ('**W277 seat=next free number·下一冻结方必须 seat-first 发布且在 post-W276 宇宙上重 derive**', '**W278 seat=next free number·下一冻结方必须 seat-first 发布且在 post-W277 宇宙上重 derive**', 1, "s-8seat"),
 ('代际持守第 9 证·本代零 authoring heal 全 rep 一次过）', '代际持守第 10 证·本代零 canon heal）', 1, "s-8cab"),
 ('本窗 derive editor 零愈合（date-roll rep 按代际同日 count-0 事实 DROP·编辑器头注+commit message 双面承载）。', '本窗 derive editor 2 处 gate-region 表愈合披露（期望表误读·canon 零命中·零 canon 异常·编辑器头注+commit message 双面承载）。', 1, "s-8editor"),
 ('(1) W276 splice 由 r1111 窗执行落链 354a645155（中窗 bm-a r1073 链被 splice gate0 fail-closed 拦截·弃 1 可再生 watermark_red 面 bm-a 新者胜 r1028 律 + ff 7a70aee50 + 重跑零盘污·推送 df7dedfd07..354a645155 落链）', '(1) W277 splice 由 r1114 窗执行落链 9e53371814（first-try 落链 origin_base 5b2b2950f1 无中窗竞速·零盘污·推送 5b2b2950f1..9e53371814 落链）', 1, "s-8d1"),
 ('(2) 引擎 mtime-watch 自点火 W276 12/12（batched 自提交 df7dedfd07 六件 + 627c4e10f2 五件 + 尾件随批·splice 提交时引擎 batch1 骑链零冲突）', '(2) 引擎 mtime-watch 自点火 W277 12/12（batched 自提交 0df07c846b 六件 + 644b4f8459 六件 + 尾批自收·splice 落链后引擎批次自提交零冲突）', 1, "s-8d2"),
 ('(3) 本波预测键冻结于 W275 实测（起草窗前 W275 finalize 已落地 r1108·活链头基准·§5 头注记）', '(3) 本波预测键冻结于 W276 实测（起草窗前 W276 finalize 已落地 r1111·活链头基准·§5 头注记）', 1, "s-8d3"),
 ('(4) 引擎 dedup W276 local/remote 12/12 完备', '(4) 引擎 dedup W277 local/remote 12/12 完备（本窗 ls-tree origin 12/12 实证+六门 shards 12/12 实测·engine status 快照 remote_done=6=陈旧缓存面如实披露）', 1, "s-8d4"),
 ('(5) prereg freeze 件 pushed FIRST-TRY（frozen sha256_16 5352c7cf343fc5e5 → origin 770a47fa1f·r1110 窗·零 CAS graft 需求）', '(5) prereg freeze 件 pushed（frozen sha256_16 45ee1de94c7d36fd → origin e0bc4a0ddd·r1113 窗·CAS 外科零树触碰送达）', 1, "s-8d5"),
 ('k_ap95_prior = 0.3088  # W275 frozen key cross-check anchor (fivekeys asserted equality)', 'k_ap95_prior = 0.305  # W276 frozen key cross-check anchor (fivekeys asserted equality)', 1, "s-kp95"),
]
for old, new, expect, tag in R:
    t, log = rep(t, old, new, expect, tag, log)
io.open(DST, "w", encoding="utf-8", newline="").write(t)
py_compile.compile(DST, doraise=True)
print("\n".join(log))
print(f"SEC78 CLONE BUILT OK {DST} ({len(t.encode('utf-8'))}B)")
