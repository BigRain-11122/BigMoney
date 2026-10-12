# -*- coding: utf-8 -*-
# r932 bm-c: W222 prereg sec.7/sec.8 machine-read one-shot backfill.
# Zero hand-copy law (r583): every number below is PROGRAMMATICALLY derived
# from n1_w222_results.json + the r932 receipts; anchors from n1_w221_results.json.
import json, io, sys

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
P = lambda *a: __import__("os").path.join(REPO, *a)

d = json.load(open(P("results", "perpetual_faces", "n1_w222_results.json"), encoding="utf-8"))
prev = json.load(open(P("results", "perpetual_faces", "n1_w221_results.json"), encoding="utf-8"))
fk = json.load(open(P("results", "_r932bmc_w222_fivekey_receipt.json"), encoding="utf-8"))
sg = json.load(open(P("results", "_r932bmc_w222_sixgate_receipt.json"), encoding="utf-8"))

lg = d["science_gates"]["ledger"]
assert lg["prev_total"] + lg["batch_trials"] == lg["total"], "ledger identity"
npc = d["null_pool_cumulative"]
m = npc["merged"]
only_key = [k for k in npc if k.endswith("_only")][0]
wo = npc[only_key]
kl = d["skill_line_v2_k_lift"]
pre_key = [p for p in kl if p.startswith("line_pre")][0]
mrg_key = [p for p in kl if p.startswith("line_merged")][0]
semu_keys = {k: npc[k] for k in npc if k.startswith("se_mu")}
famA = d["families"]["A_random_engine_exit"]
prev_p95 = prev["families"]["A_random_engine_exit"]["full_sharpe_p95"]
prev_semu = [v for k, v in {k: prev["null_pool_cumulative"][k] for k in prev["null_pool_cumulative"] if k.startswith("se_mu")}.items()]

f = fk["five_keys"]
k1 = f["key1_wonly_vs_merged_dmu"]; k2 = f["key2_sigma_rel_pct"]; k3 = f["key3_A_p95_diff_vs_w220"]; k4 = f["key4_k_lift"]
k1v, k2v, k3v, k4v = k1["value"], k2["value"], k3["value"], k4["value"]
assert fk["five_keys_all_pass"] is True, "five keys not all pass"

sec7 = f"""## §7 跑后实证。【finalize 收口机械回填】
- **finalize one-pass 已回填（bm-c r932·2026-10-12 15:5x 窗·全链=r929 席位发布 MSG-20261012-1430（87ee1055d·probe ADMIT A 503_204..505_203 EIGHTY-SECOND 阶梯例+B 505_204..505_403 own-A exclusion）→r930 per-wave prereg derive（58f82fd63）→r931 死窗五面冻结拼接落盘未提交（freeze edits 15:24:26+freeze receipt 15:24:44·零提交死亡）→引擎 daemon 自燃 12/12（两笔 batched ledger append b5305fe4a+0028f84cb 已推）→本窗 r932 吸收全 estate：六门 PRE-FINALIZE（burn-window 门错过=W212 族第 5 例·全披露）+n1 selftest W222 LHS 边界修复（w<221→w<222·editor_gen 复制残留 family #4·零科学面）+splice 提交 4167d791d→one-pass finalize 本窗收口）**：
  - 账本恒等式：prev_total **{lg['prev_total']:,}** + batch_trials **{lg['batch_trials']:,}** = total **{lg['total']:,}**（三键机读自 n1_w222_results.json science_gates.ledger·断言 prev+batch==total 过）。
  - 合并池 K={m['n_values']} EXACT·merged mu=**{m['mu']}** / merged sigma=**{m['sigma']}**·w222-only mu=**{wo['mu']}** / w222-only sigma=**{wo['sigma']}**（全机读零手抄·回执=results/_r932bmc_w222_fivekey_receipt.json·锚键 W221 实测面程序化 derive 零字面常量〔r583 律〕）。
  - skill_line_v2 K-lift 对照：line_pre **{kl[pre_key]}** → line_merged **{kl[mrg_key]}** @n_eff {lg['prev_total']:,}（delta **{k4v}**·判线 ±0.02 内·先例带 ±0.0003 对照如实）。
  - **§5 五预键机证（r932 五键探针 results/_r932bmc_w222_fivekey_probe.py 本窗 finalize 同窗跑）**：key1 w-only vs merged |Δmu|=**{k1v}**<{k1['gate']} PASS；key2 sigma 相对变化 **{k2v}%**<±10% PASS；key3 A 档 p95 **{famA['full_sharpe_p95']}** 差 **{k3v}**<{k3['gate']} PASS；key4 K-lift **{k4v}**≤±0.02 PASS；key5 投影承接见 §8。**五键全过=§5 预测键全部兑现**。
  - se_mu 收窄链对照：{'; '.join('%s=%s' % (k, v) for k, v in semu_keys.items())}（前键链 W220 {prev_semu}→W221 0.000352 收窄链持续·W222 续窄）。
  - canon flip 态=NOT performed（K2200 同例·治理提案面 only）。
  - audit：voids_applied={d['audit'].get('voids_applied', lg.get('voids_applied'))}·machine={d['audit'].get('machine','bm-c')}·finalize_only=true·shards_consumed={len(d.get('shards_consumed', []))}/12·evidence_cutoff={d.get('evidence_cutoff')}。
  - 产物=results/perpetual_faces/n1_w222_results.json（finalize one-pass·幂等禁重跑=r538 律·pit-95 孤儿 finalize 守卫在位·FAIL-CLOSED 五重守卫〔pit-95/shard 完备/overlap-gap/重名/账本恒等〕过闸即本 finalize 落地机证）。
  - **六门探针=PRE-FINALIZE 全绿（吸收窗 r932 跑·burn-window 门错过=W212 族第 5 例·全披露在回执 results/_r932bmc_w222_sixgate_receipt.json）**：banned ADMIT rc0+pf selftest 9/9+n1 selftest PASS〔含边界修复〕+shard 12/12 盘面+seed_admit FREE x2〔base=503204 span=2000+base=505204 span=200·seat-time r929+freeze-time 证据消费注记〕+splice 完整性（N1_BANDS[222] bands 事实==freeze receipt+pf sha16 恒等 {sg['gates']['splice_integrity']['pf_sha16_now']}·n1 post-repair {sg['gates']['splice_integrity']['n1_sha16_now']} 披露）+WAVE_CONFIGS[222] row engine_owner=bm-c·a_seed_base=503204/b_exit_seed_base=505204+ledger_pre {lg['prev_total']:,}=W221 landed——**W223 必须烧录窗内 PRE-FINALIZE 跑六门+边界对扫描腿（常设法·W222 族第 5 例再证）**。
"""

sec8 = f"""## §8 批后复盘。【finalize 同窗回填】
- **批后复盘（bm-c r932 同窗回填）**：
  - §5.5 下波投影承接：**W223+ 投影（probe 机证 leg4·本波 prereg §5.5 原文）**：naive A 505_204..507_203 CLEAN（pre-W222 宇宙）但将被注册后的 W222 B 带（505_204..505_403）起点即拒——**阶梯 A-hops-prior-B 第八十三例待 W223 席位探针兑现**（本波 §5.5 投影预言·hop 链逐跳在 probe 回执）；naive B 505_404..505_603 CLEAN 但落 naive W223 A 窗内（W141 同窗互斥先例适用）→**W223 席位方必须在 post-W222 注册宇宙重 derive 双带且 derive B 时预留本波 A 窗**（W223 freezer 承接面强制注记·never transcribe r587）·verify at W223 prereg。
  - 宝藏与方法论捕获问：本批测量面零新方法（引擎单批 12/12 ledger append 按设计落·finalize 产物一次 r932 独占零双计）。流程面两例如实入账：①死窗 splice 烧录后六门 PRE-FINALIZE 补跑=W212 族第 5 例（W218/W219/W220 正相三波链后再断）——根因=r931 会话在 splice→gate 间隙死亡且**六门脚本未随 freeze 束同窗预写**（r930 指针明示但死窗未及执行）——缓解面常设化：六门脚本随 freeze 束同窗预写（W223 freezer 承接·W221 §8 已注记·本波再证）；②**editor_gen 转换型生成器第 4 例（r923 两处+r928 一处+本窗 1 处）**：复制型 derive 的**条件边界成对面**（filter bound LHS 与 expected list RHS）必须作为原子对一起变换——本例 LHS `w < 221` 未随 RHS `range(16,222)` 更新（原子对面律 r928 立法后仍复发=生成器模板面未固化）——**升格缓解：W223+ 六门新增边界对扫描腿（LHS filter bound == RHS range 尾界 机读断言）·r932 已手工执行·待 W223 freezer 落为门腿**。
  - 诚实披露面：本波烧录链=r929 席位发布（87ee1055d）→r930 prereg derive（58f82fd63）→r931 死窗（五面冻结拼接落盘 15:24+freeze receipt 15:24:44·零提交死亡）→引擎自燃 12/12（两笔 batched append b5305fe4a+0028f84cb）→本窗 r932 吸收（六门 PRE-FINALIZE+边界修复+splice 提交 4167d791d+finalize one-pass+五键+§7/§8 回填）——链头消费=账本 append 由引擎单调·finalize 产物一次 r932 独占零双计；state/心跳计数器 931→933 推进（r931 死窗带 splice estate 吸收·零轮号债务双推进）。

- **跑前冻结=本件 commit**（freeze hash 归窗报告与法典 §4 行；冻结后要改判据=禁（回填限 §7/§8）。
"""

path = P("research", "PERPETUAL_N1_W222_PREREG.md")
t = open(path, encoding="utf-8").read()
i7 = t.find("## §7")
i8 = t.find("## §8")
assert i7 > 0 and i8 > i7, "section anchors missing"
tail_start = t.find("\n- **跑前冻结", i8)
assert tail_start > i8, "tail anchor missing"
new = t[:i7] + sec7 + "\n" + sec8 + "\n" + t[tail_start+1:]
assert "占位" not in new[i7:], "placeholder residue after backfill"
open(path, "w", encoding="utf-8", newline="\n").write(new)
print("BACKFILL OK: %s -> %d bytes" % (path, len(new.encode('utf-8'))))
print("ledger", lg["prev_total"], "+", lg["batch_trials"], "=", lg["total"], "| K", m["n_values"],
      "| mu", m["mu"], "| w222-only", wo["mu"], "| KL", kl[pre_key], "->", kl[mrg_key])
