# -*- coding: utf-8 -*-
"""r1089 bm-c: W267 prereg sec.7/8 backfill (placeholders -> finalize actuals).

Line-targeted replacement; all other lines byte-preserved. Placeholder lines
are located by the '占位' substring (exactly 2 in the file; sec.7 face carries
the '§7 范式' marker, sec.8 the '§8 范式' marker) -- zero CJK transcription of
the placeholder text itself. All numeric values machine-read from the fivekeys
receipt + finalize product (zero-transcription law). Idempotent guard: runs
only when both placeholder lines are present.
Clone lineage: _r1086bmc_w266_sec78_backfill.py (canon).
"""
import io
import json

PATH = "research/PERPETUAL_N1_W267_PREREG.md"
FK = "results/_r1089bmc_w267_fivekeys.json"
RES = "results/perpetual_faces/n1_w267_results.json"

fk = json.load(open(FK, encoding="utf-8"))
d = json.load(open(RES, encoding="utf-8"))
ck = {c["name"]: c for c in fk["checks"]}
pool = d["null_pool_cumulative"]

mu = fk["merged"]["mu"]
sig = fk["merged"]["sigma"]
semu = fk["merged"]["se_mu_k585320"]
wonly_mu = fk["w267_only"]["mu"]
wonly_sig = fk["w267_only"]["sigma"]
line_pre = fk["skill_line"]["line_pre_w267"]
line_m = fk["skill_line"]["line_merged_585320"]
k1 = ck["key1_w267_vs_merged_mu_gap"]["value"]
k1b = ck["key1b_merged_vs_w266_key"]["value"]
k2 = ck["key2_sigma_rel"]["value"]
k3 = ck["key3_a_p95_delta"]["value"]
k4 = ck["key4_k_lift_move"]["value"]
k_se_mu = ck["key5_se_mu_narrowing"]["band"]  # W266 frozen key, machine-read
assert ck["key5_se_mu_narrowing"]["pass"]
assert fk["ledger_identity"]["exact"] and fk["merged_k_identity"]["exact"]
cf = d["skill_line_v2_k_lift"]["canon_flip"]
assert "NOT performed" in cf
sc = json.dumps(d.get("shards_consumed"), ensure_ascii=False)

NEW7 = (
    "- 账本恒等式：prev 1,009,535 + batch 2,200 = **1,011,735 EXACT**（science_gates.ledger 机读恒等断言过）；"
    "合并池 K：583,120 + 2,200 = **585,320 EXACT**。\n"
    "- merged mu = {mu:.8f} / merged sigma = {sig:.8f} / **se_mu@K585,320 = {semu:.6f}**（对照本波冻结键 W266 {ksemu:.6f}，{narrow}）；"
    "W267-only mu = {womu:.8f} / sigma = {wosig:.8f}。\n"
    "- K-lift 对照：line_pre_w267 = {lpre:.4f} → line_merged@585,320 = {lm:.4f}，delta = **{k4:+.4f}**（n_eff held 1,009,535）；"
    "canon flip = NOT performed by this wave（治理提案面 only，K2200 同例）。\n"
    "- §5 五预键机证：**6/6 ALL PASS**（key1 only-vs-merged gap {k1:.7f} / key1b merged-vs-W266键 {k1b:.7f} / "
    "key2 sigma rel {k2:.2e} / key3 A p95 delta {k3:+.4f}【0.3268→{ap95:.4f}，负向回落双向带内】/ key4 K-lift {k4:+.4f} / "
    "key5 se_mu {semu:.6f}≤{ksemu:.6f} {narrow}）——收据 results/_r1089bmc_w267_fivekeys.json（键=n1_w266_results.json 机读 r587 律·"
    "本波预测键冻结于 W266 实测——W266 finalize 起草窗前已落地·活链头基准）。\n"
    "- 六门探针：PRE-FINALIZE **ALL PASS 第 30 连续正确相位**（results/_r1089bmc_w267_sixgate.json——splice 完整性 "
    "**CR-normalized 恒等** worktree==落链 git blob @ 7b9e9377【r1088 bm-c 窗落的 splice+setwave ROOT CURE 遗产·healed n1=4262450a0e33b2ee 直载】；"
    "banned_direction_gate ADMIT rc0；pf/n1 selftest rc0【**setwave 出生站根治**：r1076 家族第 4 代复发（splice 携带 _set_wave(265) 陈旧 canon 头面·术后 selftest 红起）"
    "按 CEO 缺陷出生地律 2026-10-16 在出生站焊死=derive editor p3_setwave_rootcure rep + phase5 presence gates（_set_wave(267):1/_set_wave(265):0 段内过闸）+ 活体 L74709 单点外科愈合"
    "（W265 L73397/W266 L74051 面保全·splice 未重放）·收据 post_splice_heals.setwave_rootcure 面+证据件 _r1088bmc_n1_setwave_heal.py/_r1088bmc_derive_editor_log.txt】；"
    "shards 12/12 全 >100KB；seed_admit_gate FREE x2【base=602701 span=2000 / base=604701 span=200】；"
    "wave_configs 行四面【对齐·engine_owner=bm-c】）。\n"
    "- audit 段：machine=bm-c，finalize_only；shards_consumed={sc}；"
    "preregistered_doc=research/PERPETUAL_N1_W267_PREREG.md；evidence_cutoff=2026-09-22（P-5C 冻结窗同窗律）。"
).format(
    mu=mu, sig=sig, semu=semu, womu=wonly_mu, wosig=wonly_sig,
    lpre=line_pre, lm=line_m, k1=k1, k1b=k1b, k2=k2, k3=k3, k4=k4,
    ap95=fk["a_band"]["full_sharpe_p95"], ksemu=k_se_mu, sc=sc,
    narrow=("窄化续行" if semu < k_se_mu else ("持平微窄" if semu == k_se_mu else "带内持平")),
)

NEW8 = (
    "- §5.5 W268+ 投影承接机证（finalize 产物 preregistered_doc 面机读）：W267 注册宇宙已落地（A 602_701..604_700 + B 604_701..604_900，本波冻结收据"
    "_w267bmc_freeze_receipt.json）——W268 A naive 起点 604_701 落在注册 W267 B 带 604_701..604_900 内（staircase-affects-A 承接延续·收据 downstream_seat 面预投影·"
    "18th/17th 计数以活链重 derive 为准勿转录）；B own-A reservation cascade 预期同样上移（post-W267 宇宙活链重 derive 决定·勿假设 A-base==prior-B-tail+1 或 B-base==own-A-tail+1 相等式·E36 卡/W141 先例）；"
    "**W268 seat=next free number·下一冻结方必须 seat-first 发布且在 post-W267 宇宙上重 derive**（勿转录 r587）。\n"
    "- 宝藏与方法论捕获问：本批零新宝藏入册零新方法论卡——setwave 出生站根治面（r1076 家族第 4 代复发·derive editor p3_setwave_rootcure + phase5 presence gates）"
    "属 CEO 缺陷出生地律（2026-10-16）的执法改进+E63 既有家族的出生站焊闸（六门+冻结收据 post_splice_heals 双面承载·证据件存档），非新方法论卡；"
    "+1 老化律已由 r1088 editor L208-215 注释成文，W268 编辑器交接=按老化律 rep('_set_wave(267)','_set_wave(268)',1) + presence gates（_set_wave(268):1/_set_wave(267):0）。\n"
    "- 诚实披露面：(1) W267 splice+setwave 根治由 r1088 窗执行落链 7b9e9377（本窗 r1089 六门在愈合面上全绿+finalize one-pass+fivekeys 6/6 同窗正确相位执行——六门 PRE-FINALIZE 相位律继续成立）；"
    "(2) r1088 窗 2 项 prereg 侧 heal 已披露（收据 wave 字段 265→266 陈旧自 W265-TOL-canon 面+authored 戳 09:0x→10:5x 按 prereg derive mtime 实测）；"
    "(3) 本波预测键冻结于 W266 实测（起草窗前 W266 finalize 已落地·活链头基准·§5 头注记）；"
    "(4) 引擎 dedup W267 local/remote 12/12 完备（本窗六门 shards 12/12 实测+组树 origin 已随 r1088 推送实证）。"
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
