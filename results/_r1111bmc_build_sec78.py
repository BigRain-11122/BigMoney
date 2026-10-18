# -*- coding: utf-8 -*-
# r1111 bm-c: build the W276 sec.7/8 backfill clone from the r1108 W275 canon
# by COUNT-ASSERTED ORDERED TRANSFORM (zero transcription; engine batch shas
# machine-verified on the current chain: df7dedfd07 six + 627c4e10f2 five).
import io, py_compile

def rep(t, old, new, expect, tag, log):
    n = t.count(old)
    assert n == expect, f"[{tag}] count {n} != {expect}: {old[:90]!r}"
    return t.replace(old, new), log + [f"{tag}: {n}x"]

SRC = "results/_r1108bmc_w275_sec78_backfill.py"
DST = "results/_r1111bmc_w276_sec78_backfill.py"
t = io.open(SRC, encoding="utf-8", newline="").read()
log = []
R = [
 ('"""r1108 bm-c: W275 prereg sec.7/8 backfill', '"""r1111 bm-c: W276 prereg sec.7/8 backfill', 1, "s-doc"),
 ('Clone lineage: _r1105bmc_w274_sec78_backfill.py (canon).', 'Clone lineage: _r1108bmc_w275_sec78_backfill.py (canon).', 1, "s-lineage"),
 ('PATH = "research/PERPETUAL_N1_W275_PREREG.md"', 'PATH = "research/PERPETUAL_N1_W276_PREREG.md"', 1, "s-path"),
 ('FK = "results/_r1108bmc_w275_fivekeys.json"', 'FK = "results/_r1111bmc_w276_fivekeys.json"', 1, "s-fk"),
 ('RES = "results/perpetual_faces/n1_w275_results.json"', 'RES = "results/perpetual_faces/n1_w276_results.json"', 1, "s-res"),
 ('prev 1,027,135 + batch 2,200 = **1,029,335 EXACT**', 'prev 1,029,335 + batch 2,200 = **1,031,535 EXACT**', 1, "s-led"),
 ('合并池 K：600,720 + 2,200 = **602,920 EXACT**', '合并池 K：602,920 + 2,200 = **605,120 EXACT**', 1, "s-k"),
 ('line_pre = fk["skill_line"]["line_pre_w275"]', 'line_pre = fk["skill_line"]["line_pre_w276"]', 1, "s-lpre-acc"),
 ('semu = fk["merged"]["se_mu_k602920"]', 'semu = fk["merged"]["se_mu_k605120"]', 1, "s-semu-acc"),
 ('wonly_mu = fk["w275_only"]["mu"]', 'wonly_mu = fk["w276_only"]["mu"]', 1, "s-womu-acc"),
 ('wonly_sig = fk["w275_only"]["sigma"]', 'wonly_sig = fk["w276_only"]["sigma"]', 1, "s-wosig-acc"),
 ('line_m = fk["skill_line"]["line_merged_602920"]', 'line_m = fk["skill_line"]["line_merged_605120"]', 1, "s-lm-acc"),
 ('k1 = ck["key1_w275_vs_merged_mu_gap"]["value"]', 'k1 = ck["key1_w276_vs_merged_mu_gap"]["value"]', 1, "s-k1-acc"),
 ('k1b = ck["key1b_merged_vs_w274_key"]["value"]', 'k1b = ck["key1b_merged_vs_w275_key"]["value"]', 1, "s-k1b-acc"),
 ('**se_mu@K602,920 = {semu:.6f}**（对照本波冻结键 W274 {ksemu:.6f}', '**se_mu@K605,120 = {semu:.6f}**（对照本波冻结键 W275 {ksemu:.6f}', 1, "s-semu"),
 ('W275-only mu = {womu:.8f} / sigma = {wosig:.8f}', 'W276-only mu = {womu:.8f} / sigma = {wosig:.8f}', 1, "s-wonly"),
 ('line_pre_w275 = {lpre:.4f} → line_merged@602,920 = {lm:.4f}', 'line_pre_w276 = {lpre:.4f} → line_merged@605,120 = {lm:.4f}', 1, "s-line"),
 ('key1b merged-vs-W274键 {k1b:.7f}', 'key1b merged-vs-W275键 {k1b:.7f}', 1, "s-k1b"),
 ('收据 results/_r1108bmc_w275_fivekeys.json（键=n1_w274_results.json 机读 r587 律·', '收据 results/_r1111bmc_w276_fivekeys.json（键=n1_w275_results.json 机读 r587 律·', 1, "s-fkrecpt"),
 ('本波预测键冻结于 W274 实测——W274 finalize 起草窗前已落地·活链头基准）。', '本波预测键冻结于 W275 实测——W275 finalize 起草窗前已落地·活链头基准）。', 1, "s-fkrecpt2"),
 ('PRE-FINALIZE **ALL PASS 第 38 连续正确相位**（results/_r1108bmc_w275_sixgate.json', 'PRE-FINALIZE **ALL PASS 第 39 连续正确相位**（results/_r1111bmc_w276_sixgate.json', 1, "s-six"),
 ('worktree==落链 git blob @ 018782314d【r1108 bm-c 窗落的 splice·CLEAN-AT-BIRTH 第 8 代（引擎机械面）', 'worktree==落链 git blob @ 354a645155【r1111 bm-c 窗落的 splice·CLEAN-AT-BIRTH 第 9 代（引擎机械面）', 1, "s-splice"),
 ('_set_wave(275):1/_set_wave(274):0/_set_wave(273):0 段内过闸', '_set_wave(276):1/_set_wave(275):0/_set_wave(274):0 段内过闸', 1, "s-sw"),
 ('seed_admit_gate FREE x2【base=620301 span=2000 / base=622301 span=200】', 'seed_admit_gate FREE x2【base=622501 span=2000 / base=624501 span=200】', 1, "s-seed"),
 ('preregistered_doc=research/PERPETUAL_N1_W275_PREREG.md', 'preregistered_doc=research/PERPETUAL_N1_W276_PREREG.md', 1, "s-audit-doc"),
 ('§5.5 W276+ 投影承接机证', '§5.5 W277+ 投影承接机证', 1, "s-8head"),
 ('W275 注册宇宙已落地（A 620_301..622_300 + B 622_301..622_500，本波冻结收据', 'W276 注册宇宙已落地（A 622_501..624_500 + B 624_501..624_700，本波冻结收据', 1, "s-8univ"),
 ('_w275bmc_freeze_receipt.json）——W276 A naive 起点 622_301', '_w276bmc_freeze_receipt.json）——W277 A naive 起点 624_501', 1, "s-8naiveA1"),
 ('（pre-W275 宇宙 leg4 实测 CLEAN hops=0·收据 _w275bmc_20261019_probe_receipt.json）在 post-W275 注册宇宙上', '（pre-W276 宇宙 leg4 实测 CLEAN hops=0·收据 _w276bmc_20261019_probe_receipt.json）在 post-W276 注册宇宙上', 1, "s-8naiveA2"),
 ('落注册 W275 B 带 622_301..622_500 内（staircase-affects-A 第 25 次 A-hop 预期', '落注册 W276 B 带 624_501..624_700 内（staircase-affects-A 第 26 次 A-hop 预期', 1, "s-8refuse"),
 ('B naive 622_501..622_700 落投影 A 窗内·post-W275 宇宙活链重 derive 决定', 'B naive 624_501..624_900 落投影 A 窗内·post-W276 宇宙活链重 derive 决定', 1, "s-8naiveB"),
 ('**W276 seat=next free number·下一冻结方必须 seat-first 发布且在 post-W275 宇宙上重 derive**', '**W277 seat=next free number·下一冻结方必须 seat-first 发布且在 post-W276 宇宙上重 derive**', 1, "s-8seat"),
 ('代际持守第 8 证', '代际持守第 9 证', 1, "s-8cab"),
 ('(1) W275 splice 由 r1108 窗执行落链 018782314d（origin 中窗竞速 bm-b r1072 双提交 d1330ca4e6+9c4ef60548 → stash-bridge 三可再生探针面 rebase 干净 → 推送 9c4ef60548..5089f02250 落链 origin==HEAD 双证·watermark_red UU 以 stash 侧本机面解决·S6 再生兜底）',
  '(1) W276 splice 由 r1111 窗执行落链 354a645155（中窗 bm-a r1073 链被 splice gate0 fail-closed 拦截·弃 1 可再生 watermark_red 面 bm-a 新者胜 r1028 律 + ff 7a70aee50 + 重跑零盘污·推送 df7dedfd07..354a645155 落链）', 1, "s-8d1"),
 ('(2) 引擎 mtime-watch 自点火 W275 12/12（batched 自提交 5089f02250 六件 + e639699d59 四件 + 尾批自收·splice-rebase 时引擎 batch1 骑链重放零冲突）',
  '(2) 引擎 mtime-watch 自点火 W276 12/12（batched 自提交 df7dedfd07 六件 + 627c4e10f2 五件 + 尾件随批·splice 提交时引擎 batch1 骑链零冲突）', 1, "s-8d2"),
 ('(3) 本波预测键冻结于 W274 实测（起草窗前 W274 finalize 已落地 r1105·活链头基准·§5 头注记）', '(3) 本波预测键冻结于 W275 实测（起草窗前 W275 finalize 已落地 r1108·活链头基准·§5 头注记）', 1, "s-8d3"),
 ('(4) 引擎 dedup W275 local/remote 12/12 完备', '(4) 引擎 dedup W276 local/remote 12/12 完备', 1, "s-8d4"),
 ('(5) prereg freeze 件 pushed FIRST-TRY（frozen sha256_16 e4e1ce44f5afd03b → origin 1fcc0bc30f·r1107 窗·零 CAS graft 需求）', '(5) prereg freeze 件 pushed FIRST-TRY（frozen sha256_16 5352c7cf343fc5e5 → origin 770a47fa1f·r1110 窗·零 CAS graft 需求）', 1, "s-8d5"),
 ('k_ap95_prior = 0.3009  # W274 frozen key cross-check anchor (fivekeys asserted equality)', 'k_ap95_prior = 0.3088  # W275 frozen key cross-check anchor (fivekeys asserted equality)', 1, "s-kp95"),
]
for old, new, expect, tag in R:
    t, log = rep(t, old, new, expect, tag, log)
io.open(DST, "w", encoding="utf-8", newline="").write(t)
py_compile.compile(DST, doraise=True)
print("\n".join(log))
print(f"SEC78 CLONE BUILT OK {DST} ({len(t.encode('utf-8'))}B)")
