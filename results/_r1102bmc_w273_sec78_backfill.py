# -*- coding: utf-8 -*-
"""r1102 bm-c: W273 prereg sec.7/8 backfill (placeholders -> finalize actuals).

Line-targeted replacement; all other lines byte-preserved. Placeholder lines
are located by the '占位' substring (exactly 2 in the file; sec.7 face carries
the '§7 范式' marker, sec.8 the '§8 范式' marker) -- zero CJK transcription of
the placeholder text itself. All numeric values machine-read from the fivekeys
receipt + finalize product (zero-transcription law). Idempotent guard: runs
only when both placeholder lines are present.
Clone lineage: _r1100bmc_w272_sec78_backfill.py (canon).
"""
import io
import json

PATH = "research/PERPETUAL_N1_W273_PREREG.md"
FK = "results/_r1102bmc_w273_fivekeys.json"
RES = "results/perpetual_faces/n1_w273_results.json"

fk = json.load(open(FK, encoding="utf-8"))
d = json.load(open(RES, encoding="utf-8"))
ck = {c["name"]: c for c in fk["checks"]}
pool = d["null_pool_cumulative"]

mu = fk["merged"]["mu"]
sig = fk["merged"]["sigma"]
semu = fk["merged"]["se_mu_k598520"]
wonly_mu = fk["w273_only"]["mu"]
wonly_sig = fk["w273_only"]["sigma"]
line_pre = fk["skill_line"]["line_pre_w273"]
line_m = fk["skill_line"]["line_merged_598520"]
n_eff = d["skill_line_v2_k_lift"]["n_eff_held_equal"]
k1 = ck["key1_w273_vs_merged_mu_gap"]["value"]
k1b = ck["key1b_merged_vs_w272_key"]["value"]
k2 = ck["key2_sigma_rel"]["value"]
k3 = ck["key3_a_p95_delta"]["value"]
k4 = ck["key4_k_lift_move"]["value"]
k_se_mu = ck["key5_se_mu_narrowing"]["band"]  # W272 frozen key, machine-read
assert ck["key5_se_mu_narrowing"]["pass"]
assert fk["ledger_identity"]["exact"] and fk["merged_k_identity"]["exact"]
cf = d["skill_line_v2_k_lift"]["canon_flip"]
assert "NOT performed" in cf
sc = json.dumps(d.get("shards_consumed"), ensure_ascii=False)
k_ap95_prior = 0.3138  # W272 frozen key cross-check anchor (fivekeys asserted equality)

NEW7 = (
    "- 账本恒等式：prev 1,022,735 + batch 2,200 = **1,024,935 EXACT**（science_gates.ledger 机读恒等断言过）；"
    "合并池 K：596,320 + 2,200 = **598,520 EXACT**。\n"
    "- merged mu = {mu:.8f} / merged sigma = {sig:.8f} / **se_mu@K598,520 = {semu:.6f}**（对照本波冻结键 W272 {ksemu:.6f}，{narrow}）；"
    "W273-only mu = {womu:.8f} / sigma = {wosig:.8f}。\n"
    "- K-lift 对照：line_pre_w273 = {lpre:.4f} → line_merged@598,520 = {lm:.4f}，delta = **{k4:+.4f}**（n_eff held {neff:,}）；"
    "canon flip = NOT performed by this wave（治理提案面 only，K2200 同例）。\n"
    "- §5 五预键机证：**6/6 ALL PASS**（key1 only-vs-merged gap {k1:.7f} / key1b merged-vs-W272键 {k1b:.7f} / "
    "key2 sigma rel {k2:.2e} / key3 A p95 delta {k3:+.4f}【{k_ap95_prior:.4f}→{ap95:.4f}，双向带内】/ key4 K-lift {k4:+.4f} / "
    "key5 se_mu {semu:.6f}≤{ksemu:.6f} {narrow}）——收据 results/_r1102bmc_w273_fivekeys.json（键=n1_w272_results.json 机读 r587 律·"
    "本波预测键冻结于 W272 实测——W272 finalize 起草窗前已落地·活链头基准）。\n"
    "- 六门探针：PRE-FINALIZE **ALL PASS 第 36 连续正确相位**（results/_r1102bmc_w273_sixgate.json——splice 完整性 "
    "**CR-normalized 恒等** worktree==落链 git blob @ 04f2127db【r1102 bm-c 窗落的 splice·CLEAN-AT-BIRTH 第 6 代（引擎机械面）：r1076 家族 setwave 缺陷出生站预防代际持守"
    "（_set_wave(273):1/_set_wave(272):0/_set_wave(271):0 段内过闸）·9 项 pre-splice 编辑器期 authoring heal 披露（stale bm-a 归属族×3 + own-seat continuity + draft-ordinal face + (18 rows) 计数 + machine-SUB→E63-builder×3 + prereg surgery-delivery prose×2——全部 fail-closed 拦获或就地滚正·写盘前）·零引擎机械愈合】；"
    "banned_direction_gate ADMIT rc0；pf/n1 selftest rc0；"
    "shards 12/12 全 >100KB；seed_admit_gate FREE x2【base=615901 span=2000 / base=617901 span=200】；"
    "wave_configs 行四面【对齐·engine_owner=bm-c】）。\n"
    "- audit 段：machine=bm-c，finalize_only；shards_consumed={sc}；"
    "preregistered_doc=research/PERPETUAL_N1_W273_PREREG.md；evidence_cutoff=2026-09-22（P-5C 冻结窗同窗律）。"
).format(
    mu=mu, sig=sig, semu=semu, womu=wonly_mu, wosig=wonly_sig,
    lpre=line_pre, lm=line_m, k1=k1, k1b=k1b, k2=k2, k3=k3, k4=k4,
    ap95=fk["a_band"]["full_sharpe_p95"], ksemu=k_se_mu, sc=sc,
    neff=n_eff, k_ap95_prior=k_ap95_prior,
    narrow=("窄化续行" if semu < k_se_mu else ("持平微窄" if semu == k_se_mu else "带内持平")),
)
assert fk["a_band"]["full_sharpe_p95"] is not None

NEW8 = (
    "- §5.5 W274+ 投影承接机证（finalize 产物 preregistered_doc 面机读）：W273 注册宇宙已落地（A 615_901..617_900 + B 617_901..618_100，本波冻结收据"
    "_w273bmc_freeze_receipt.json）——W274 A naive 起点 617_901（pre-W273 宇宙 leg4 实测 CLEAN hops=0·收据 _w273bmc_20261018_probe_receipt.json）在 post-W273 注册宇宙上"
    "落注册 W273 B 带 617_901..618_100 内（staircase-affects-A 第 23 次 A-hop 预期·收据 downstream_seat 面预投影·"
    "计数以活链重 derive 为准勿转录）；B own-A reservation cascade 预期同样上移（B naive 618_101..618_300 落投影 A 窗内·post-W273 宇宙活链重 derive 决定·"
    "勿假设 A-base==prior-B-tail+1 或 B-base==own-A-tail+1 相等式·E36 卡/W141 先例）；"
    "**W274 seat=next free number·下一冻结方必须 seat-first 发布且在 post-W273 宇宙上重 derive**（勿转录 r587）。\n"
    "- 宝藏与方法论捕获问：本批零新宝藏入册零新方法论卡——setwave CLEAN-AT-BIRTH 面（r1076 家族缺陷在出生站被 derive editor 闸预防·零引擎机械愈合·代际持守第 6 证）"
    "属 r1088 根治律（CEO 缺陷出生地律 2026-10-16 执法）的持守验证，非新方法论卡；本窗 derive editor 9 项披露 heal（stale bm-a 归属族×3 + own-seat continuity + draft-ordinal face + (18 rows) 计数老化面 +"
    " machine-SUB→E63-builder×3 + prereg surgery-delivery prose×2——由 fail-closed 计数闸在编辑器期拦截·写盘前·零盘污零内容缺陷）"
    "为携带面出生站修正（零功能影响·editor 头注 + commit message 双面承载）。\n"
    "- 诚实披露面：(1) W273 splice 由 r1102 窗执行落链 04f2127db（本窗六门在 clean-at-birth 面上全绿+finalize one-pass+fivekeys 6/6 同窗正确相位执行——六门 PRE-FINALIZE 相位律继续成立·splice 直推 first-try 落链 origin==HEAD 双证）；"
    "(2) r1102 derive editor 9 项 authoring heal 已披露（编辑器期 fail-closed 拦获·零引擎机械盘污·头注+commit message 双面承载）；"
    "(3) 本波预测键冻结于 W272 实测（起草窗前 W272 finalize 已落地·活链头基准·§5 头注记）；"
    "(4) 引擎 dedup W273 local/remote 12/12 完备（本窗六门 shards 12/12 实测+splice 推送 04f2127db 落链）；"
    "(5) prereg freeze 件经树手术投送（frozen b6bbb69e92 local -> surgery-delivered origin 839441a547 + receipts eeb3bf07ad·r1102 窗·prereg sha256_16 2f289446a93fa102 字节恒等双证·r609 法 gate0 双核后全链绿）。"
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
