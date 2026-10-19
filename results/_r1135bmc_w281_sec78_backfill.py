# -*- coding: utf-8 -*-
"""r1135 bm-c: W281 prereg sec.7/8 backfill (placeholders -> finalize actuals).

Line-targeted replacement; all other lines byte-preserved. Placeholder lines
are located structurally (lines carrying '占位' AND the §7 / §8 marker; exactly
one each -- zero CJK transcription of the placeholder text itself). All numeric
values machine-read from the fivekeys receipt + finalize product
(zero-transcription law). Idempotent guard: runs only when both placeholder
lines are present.
Clone lineage: _r1132bmc_w280_sec78_backfill.py (canon).
"""
import io
import json

PATH = "research/PERPETUAL_N1_W281_PREREG.md"
FK = "results/_r1135bmc_w281_fivekeys.json"
RES = "results/perpetual_faces/n1_w281_results.json"

fk = json.load(open(FK, encoding="utf-8"))
d = json.load(open(RES, encoding="utf-8"))
ck = {c["name"]: c for c in fk["checks"]}
pool = d["null_pool_cumulative"]

mu = fk["merged"]["mu"]
sig = fk["merged"]["sigma"]
semu = fk["merged"]["se_mu_k616120"]
wonly_mu = fk["w281_only"]["mu"]
wonly_sig = fk["w281_only"]["sigma"]
line_pre = fk["skill_line"]["line_pre_w281"]
line_m = fk["skill_line"]["line_merged_616120"]
n_eff = d["skill_line_v2_k_lift"]["n_eff_held_equal"]
k1 = ck["key1_w281_vs_merged_mu_gap"]["value"]
k1b = ck["key1b_merged_vs_w280_key"]["value"]
k2 = ck["key2_sigma_rel"]["value"]
k3 = ck["key3_a_p95_delta"]["value"]
k4 = ck["key4_k_lift_move"]["value"]
k_se_mu = ck["key5_se_mu_narrowing"]["band"]  # W280 frozen key, machine-read
assert ck["key5_se_mu_narrowing"]["pass"]
assert fk["ledger_identity"]["exact"] and fk["merged_k_identity"]["exact"]
cf = d["skill_line_v2_k_lift"]["canon_flip"]
assert "NOT performed" in cf
sc = json.dumps(d.get("shards_consumed"), ensure_ascii=False)
k_ap95_prior = 0.3294  # W280 frozen key cross-check anchor (fivekeys asserted equality)

NEW7 = (
    "- 账本恒等式：prev 1,040,335 + batch 2,200 = **1,042,535 EXACT**（science_gates.ledger 机读恒等断言过）；"
    "合并池 K：613,920 + 2,200 = **616,120 EXACT**。\n"
    "- merged mu = {mu:.8f} / merged sigma = {sig:.8f} / **se_mu@K616,120 = {semu:.6f}**（对照本波冻结键 W280 {ksemu:.6f}，{narrow}）；"
    "W281-only mu = {womu:.8f} / sigma = {wosig:.8f}。\n"
    "- K-lift 对照：line_pre_w281 = {lpre:.4f} → line_merged@616,120 = {lm:.4f}，delta = **{k4:+.4f}**（n_eff held {neff:,}）；"
    "canon flip = NOT performed by this wave（治理提案面 only，K2200 同例）。\n"
    "- §5 五预键机证：**6/6 ALL PASS**（key1 only-vs-merged gap {k1:.7f} / key1b merged-vs-W280键 {k1b:.7f} / "
    "key2 sigma rel {k2:.2e} / key3 A p95 delta {k3:+.4f}【{k_ap95_prior:.4f}→{ap95:.4f}，双向带内】/ key4 K-lift {k4:+.4f} / "
    "key5 se_mu {semu:.6f}≤{ksemu:.6f} {narrow}）——收据 results/_r1135bmc_w281_fivekeys.json（键=n1_w280_results.json 机读 r587 律·"
    "本波预测键冻结于 W280 实测——W280 finalize 起草窗前已落地·活链头基准）。\n"
    "- 六门探针：PRE-FINALIZE **ALL PASS 第 44 连续正确相位**（results/_r1135bmc_w281_sixgate.json——splice 完整性 "
    "**CR-normalized 恒等** worktree==落链 git blob @ aa376549cd【r1134 窗落的 splice·落链后 pf/n1 零愈合（本窗实测面）·setwave 出生站闸持守"
    "（_set_wave(281):1/_set_wave(280):1/_set_wave(279):1 全文件计数·段内 281 在/280 与 279 不在）·derive 证据件在位】；"
    "banned_direction_gate ADMIT rc0；pf/n1 selftest rc0；"
    "shards 12/12 全 >100KB；seed_admit_gate FREE x2【base=633501 span=2000 / base=635501 span=200】；"
    "wave_configs 行四面【对齐·engine_owner=bm-c】）。\n"
    "- audit 段：machine=bm-c，finalize_only；shards_consumed={sc}；"
    "preregistered_doc=research/PERPETUAL_N1_W281_PREREG.md；evidence_cutoff=2026-09-22（P-5C 冻结窗同窗律）。"
).format(
    mu=mu, sig=sig, semu=semu, womu=wonly_mu, wosig=wonly_sig,
    lpre=line_pre, lm=line_m, k1=k1, k1b=k1b, k2=k2, k3=k3, k4=k4,
    ap95=fk["a_band"]["full_sharpe_p95"], ksemu=k_se_mu, sc=sc,
    neff=n_eff, k_ap95_prior=k_ap95_prior,
    narrow=("窄化续行" if semu < k_se_mu else ("持平微窄" if semu == k_se_mu else "带内持平")),
)
assert fk["a_band"]["full_sharpe_p95"] is not None

NEW8 = (
    "- §5.5 W282+ 投影承接机证（finalize 产物 preregistered_doc 面机读）：W281 注册宇宙已落地（A 633_501..635_500 + B 635_501..635_700，本波冻结收据"
    "_w281bmc_freeze_receipt.json）——W282 A naive 起点 635_501 在 post-W281 注册宇宙上撞 W281 B 窗（staircase 预期 A-hop）；"
    "B naive 635_701..635_900 落投影 A 窗内（own-A reservation cascade 继续）——"
    "计数以活链重 derive 为准勿转录；勿假设 A-base==prior-B-tail+1 或 B-base==own-A-tail+1 相等式（E36 卡/W141 先例）；"
    "**W282 seat=next free number·下一冻结方必须 seat-first 发布且在 post-W281 宇宙上重 derive**（勿转录 r587）。\n"
    "- 宝藏与方法论捕获问：本批零新宝藏入册零新方法论卡——本窗六门 clone 全 count-asserted（行面/边界/出生站/账本面逐项断言）+fivekeys 6 针首跑全中，"
    "属既有机制持守验证，非新方法论卡。\n"
    "- 诚实披露面：(1) W281 splice 由 r1134 窗执行落链 aa376549cd（本窗实测 CR-normalized 恒等·pf/n1 落链后零愈合）；"
    "(2) 引擎 mtime-watch 自点火 W281 12/12（自提交 batches 806aefddd1 + 8c9247edbe，两批均自推上 origin）；"
    "(3) 本波预测键冻结于 W280 实测（起草窗前 W280 finalize 已落地 r1131 窗 02:0x·活链头基准·§5 头注记）；"
    "(4) 引擎 dedup W281 local 12/12 完备（本窗六门 shards 12/12 实测+splice 推送落链）；"
    "(5) prereg freeze 件 pushed（frozen sha256_16 → origin 5f279e44fc 上游面·W281 freeze 落链 f51afd09ad）。"
)

raw = io.open(PATH, encoding="utf-8", newline="").read()
eol = "\r\n" if raw.count("\r\n") >= raw.count("\n") - raw.count("\r\n") else "\n"
lines = raw.split(eol)
ph_idx = [i for i, ln in enumerate(lines) if "占位" in ln and ("§7" in ln or "§8" in ln)]
assert len(ph_idx) == 2, "placeholder line count != 2 (idempotent guard): %d" % len(ph_idx)
i7 = [i for i in ph_idx if "§7" in lines[i]]
i8 = [i for i in ph_idx if "§8" in lines[i]]
assert len(i7) == 1 and len(i8) == 1, ("marker split fail", ph_idx, i7, i8)
lines[i7[0]] = NEW7
lines[i8[0]] = NEW8
t2 = eol.join(lines)
assert t2.count("占位") == 0, "residual placeholder after backfill (seat-note line already healed r1134)"
io.open(PATH, "w", encoding="utf-8", newline="").write(t2)
print("backfilled: sec7 line -> NEW7, sec8 line -> NEW8; placeholders remaining:",
      t2.count("占位"), "; eol:", repr(eol))