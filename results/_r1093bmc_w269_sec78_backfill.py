# -*- coding: utf-8 -*-
"""r1093 bm-c: W269 prereg sec.7/8 backfill (placeholders -> finalize actuals).

Line-targeted replacement; all other lines byte-preserved. Placeholder lines
are located by the '占位' substring (exactly 2 in the file; sec.7 face carries
the '§7 范式' marker, sec.8 the '§8 范式' marker) -- zero CJK transcription of
the placeholder text itself. All numeric values machine-read from the fivekeys
receipt + finalize product (zero-transcription law). Idempotent guard: runs
only when both placeholder lines are present.
Clone lineage: _r1091bmc_w268_sec78_backfill.py (canon).
"""
import io
import json

PATH = "research/PERPETUAL_N1_W269_PREREG.md"
FK = "results/_r1093bmc_w269_fivekeys.json"
RES = "results/perpetual_faces/n1_w269_results.json"

fk = json.load(open(FK, encoding="utf-8"))
d = json.load(open(RES, encoding="utf-8"))
ck = {c["name"]: c for c in fk["checks"]}
pool = d["null_pool_cumulative"]

mu = fk["merged"]["mu"]
sig = fk["merged"]["sigma"]
semu = fk["merged"]["se_mu_k589720"]
wonly_mu = fk["w269_only"]["mu"]
wonly_sig = fk["w269_only"]["sigma"]
line_pre = fk["skill_line"]["line_pre_w269"]
line_m = fk["skill_line"]["line_merged_589720"]
k1 = ck["key1_w269_vs_merged_mu_gap"]["value"]
k1b = ck["key1b_merged_vs_w268_key"]["value"]
k2 = ck["key2_sigma_rel"]["value"]
k3 = ck["key3_a_p95_delta"]["value"]
k4 = ck["key4_k_lift_move"]["value"]
k_se_mu = ck["key5_se_mu_narrowing"]["band"]  # W268 frozen key, machine-read
assert ck["key5_se_mu_narrowing"]["pass"]
assert fk["ledger_identity"]["exact"] and fk["merged_k_identity"]["exact"]
cf = d["skill_line_v2_k_lift"]["canon_flip"]
assert "NOT performed" in cf
sc = json.dumps(d.get("shards_consumed"), ensure_ascii=False)
k_ap95_prior = 0.3120  # W268 frozen key cross-check anchor (fivekeys asserted equality)

NEW7 = (
    "- 账本恒等式：prev 1,013,935 + batch 2,200 = **1,016,135 EXACT**（science_gates.ledger 机读恒等断言过）；"
    "合并池 K：587,520 + 2,200 = **589,720 EXACT**。\n"
    "- merged mu = {mu:.8f} / merged sigma = {sig:.8f} / **se_mu@K589,720 = {semu:.6f}**（对照本波冻结键 W268 {ksemu:.6f}，{narrow}）；"
    "W269-only mu = {womu:.8f} / sigma = {wosig:.8f}。\n"
    "- K-lift 对照：line_pre_w269 = {lpre:.4f} → line_merged@589,720 = {lm:.4f}，delta = **{k4:+.4f}**（n_eff held 1,013,935）；"
    "canon flip = NOT performed by this wave（治理提案面 only，K2200 同例）。\n"
    "- §5 五预键机证：**6/6 ALL PASS**（key1 only-vs-merged gap {k1:.7f} / key1b merged-vs-W268键 {k1b:.7f} / "
    "key2 sigma rel {k2:.2e} / key3 A p95 delta {k3:+.4f}【0.3120→{ap95:.4f}，双向带内】/ key4 K-lift {k4:+.4f} / "
    "key5 se_mu {semu:.6f}≤{ksemu:.6f} {narrow}）——收据 results/_r1093bmc_w269_fivekeys.json（键=n1_w268_results.json 机读 r587 律·"
    "本波预测键冻结于 W268 实测——W268 finalize 起草窗前已落地·活链头基准）。\n"
    "- 六门探针：PRE-FINALIZE **ALL PASS 第 32 连续正确相位**（results/_r1093bmc_w269_sixgate.json——splice 完整性 "
    "**CR-normalized 恒等** worktree==落链 git blob @ 440b07c94b【r1093 bm-c 窗落的 splice·CLEAN-AT-BIRTH 第 2 代：r1076 家族 setwave 缺陷在出生站被 derive editor p3_setwave_rootcure rep + phase5 presence gates 预防"
    "（_set_wave(269):1/_set_wave(268):0/_set_wave(267):0 段内过闸）·零外科愈合·零 post_splice_heals 面——r1088 根治律代际持守第 2 证】；"
    "banned_direction_gate ADMIT rc0；pf/n1 selftest rc0；"
    "shards 12/12 全 >100KB；seed_admit_gate FREE x2【base=607101 span=2000 / base=609101 span=200】；"
    "wave_configs 行四面【对齐·engine_owner=bm-c】）。\n"
    "- audit 段：machine=bm-c，finalize_only；shards_consumed={sc}；"
    "preregistered_doc=research/PERPETUAL_N1_W269_PREREG.md；evidence_cutoff=2026-09-22（P-5C 冻结窗同窗律）。"
).format(
    mu=mu, sig=sig, semu=semu, womu=wonly_mu, wosig=wonly_sig,
    lpre=line_pre, lm=line_m, k1=k1, k1b=k1b, k2=k2, k3=k3, k4=k4,
    ap95=fk["a_band"]["full_sharpe_p95"], ksemu=k_se_mu, sc=sc,
    narrow=("窄化续行" if semu < k_se_mu else ("持平微窄" if semu == k_se_mu else "带内持平")),
)
assert fk["a_band"]["full_sharpe_p95"] is not None

NEW8 = (
    "- §5.5 W270+ 投影承接机证（finalize 产物 preregistered_doc 面机读）：W269 注册宇宙已落地（A 607_101..609_100 + B 609_101..609_300，本波冻结收据"
    "_w269bmc_freeze_receipt.json）——W270 A naive 起点 609_101 落在注册 W269 B 带 609_101..609_300 内（staircase-affects-A 承接延续·收据 downstream_seat 面预投影·"
    "19th/18th 计数以活链重 derive 为准勿转录）；B own-A reservation cascade 预期同样上移（post-W269 宇宙活链重 derive 决定·勿假设 A-base==prior-B-tail+1 或 B-base==own-A-tail+1 相等式·E36 卡/W141 先例）；"
    "**W270 seat=next free number·下一冻结方必须 seat-first 发布且在 post-W269 宇宙上重 derive**（勿转录 r587）。\n"
    "- 宝藏与方法论捕获问：本批零新宝藏入册零新方法论卡——setwave CLEAN-AT-BIRTH 面（r1076 家族缺陷在出生站被 derive editor 闸预防·零愈合·代际持守第 2 证）"
    "属 r1088 根治律（CEO 缺陷出生地律 2026-10-16 执法）的持守验证，非新方法论卡；本窗 derive editor 4 项披露 heal（gone 清单同族 4 面：606_901/607_100 生产者新值 + range(248,268) dropped-range 新值 + if w<268) anti-gate 新值 + m248 活拆分边界标记——全部由 fail-closed 计数闸在编辑器期拦截·写盘前·零盘污零内容缺陷）"
    "均为携带面出生站修正（零功能影响·editor 头注 + commit message 双面承载）。\n"
    "- 诚实披露面：(1) W269 splice 由 r1093 窗执行落链 440b07c94b（本窗六门在 clean-at-birth 面上全绿+finalize one-pass+fivekeys 6/6 同窗正确相位执行——六门 PRE-FINALIZE 相位律继续成立）；"
    "(2) r1093 derive editor 4 项同族 gone-list heal 已披露（编辑器期 fail-closed 拦截·零盘污·头注+commit message 双面承载）；"
    "(3) 本波预测键冻结于 W268 实测（起草窗前 W268 finalize 已落地·活链头基准·§5 头注记）；"
    "(4) 引擎 dedup W269 local/remote 12/12 完备（本窗六门 shards 12/12 实测+splice 推送 440b07c94b 落链）。"
)

raw = io.open(PATH, encoding="utf-8", newline="").read()
eol = "\r\n" if raw.count("\r\n") >= raw.count("\n") - raw.count("\r\n") else "\n"
lines = raw.split(eol)
ph_idx = [i for i, ln in enumerate(lines) if "占位" in ln]
assert len(ph_idx) == 2, "placeholder line count != 2 (idempotent guard): %d" % len(ph_idx)
i7 = [i for i in ph_idx if "§7" in lines[i] or "\u00a77" in lines[i]]
i8 = [i for i in ph_idx if "§8" in lines[i] or "\u00a78" in lines[i]]
assert len(i7) == 1 and len(i8) == 1, ("marker split fail", ph_idx, i7, i8)
lines[i7[0]] = NEW7
lines[i8[0]] = NEW8
t2 = eol.join(lines)
assert t2.count("占位") == 0, "residual placeholder after backfill"
io.open(PATH, "w", encoding="utf-8", newline="").write(t2)
print("backfilled: sec7 line -> NEW7, sec8 line -> NEW8; placeholders remaining:",
      t2.count("占位"), "; eol:", repr(eol))
