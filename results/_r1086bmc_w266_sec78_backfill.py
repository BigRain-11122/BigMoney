# -*- coding: utf-8 -*-
"""r1086 bm-c: W266 prereg sec.7/8 backfill (placeholders -> finalize actuals).

Line-targeted replacement; all other lines byte-preserved. Placeholder lines
are located by the '占位' substring (exactly 2 in the file; sec.7 face carries
the '§7 范式' marker, sec.8 the '§8 范式' marker) -- zero CJK transcription of
the placeholder text itself. All numeric values machine-read from the fivekeys
receipt + finalize product (zero-transcription law). Idempotent guard: runs
only when both placeholder lines are present.
Clone lineage: _r1084bmc_w265_sec78_backfill.py (canon).
"""
import io
import json

PATH = "research/PERPETUAL_N1_W266_PREREG.md"
FK = "results/_r1086bmc_w266_fivekeys.json"
RES = "results/perpetual_faces/n1_w266_results.json"

fk = json.load(open(FK, encoding="utf-8"))
d = json.load(open(RES, encoding="utf-8"))
ck = {c["name"]: c for c in fk["checks"]}
pool = d["null_pool_cumulative"]

mu = fk["merged"]["mu"]
sig = fk["merged"]["sigma"]
semu = fk["merged"]["se_mu_k583120"]
wonly_mu = fk["w266_only"]["mu"]
wonly_sig = fk["w266_only"]["sigma"]
line_pre = fk["skill_line"]["line_pre_w266"]
line_m = fk["skill_line"]["line_merged_583120"]
k1 = ck["key1_w266_vs_merged_mu_gap"]["value"]
k1b = ck["key1b_merged_vs_w265_key"]["value"]
k2 = ck["key2_sigma_rel"]["value"]
k3 = ck["key3_a_p95_delta"]["value"]
k4 = ck["key4_k_lift_move"]["value"]
k_se_mu = 0.000321  # W265 frozen key (cross-check below)
assert fk["checks"][5]["name"] == "key5_se_mu_narrowing" and fk["checks"][5]["pass"]
sc = json.dumps(d.get("shards_consumed"), ensure_ascii=False)

NEW7 = (
    "- 账本恒等式：prev 1,007,335 + batch 2,200 = **1,009,535 EXACT**（science_gates.ledger 机读恒等断言过）；"
    "合并池 K：580,920 + 2,200 = **583,120 EXACT**。\n"
    "- merged mu = {mu:.8f} / merged sigma = {sig:.8f} / **se_mu@K583,120 = {semu:.6f}**（对照本波冻结键 W265 0.000321，{narrow}）；"
    "W266-only mu = {womu:.8f} / sigma = {wosig:.8f}。\n"
    "- K-lift 对照：line_pre_w266 = {lpre:.4f} → line_merged@583,120 = {lm:.4f}，delta = **{k4:+.4f}**（n_eff held 1,007,335）；"
    "canon flip = NOT performed by this wave（治理提案面 only，K2200 同例）。\n"
    "- §5 五预键机证：**6/6 ALL PASS**（key1 only-vs-merged gap {k1:.7f} / key1b merged-vs-W265键 {k1b:.7f} / "
    "key2 sigma rel {k2:.2e} / key3 A p95 delta {k3:+.4f}【0.3149→{ap95:.4f}，双向带内】/ key4 K-lift {k4:+.4f} / "
    "key5 se_mu {semu:.6f}≤{ksemu:.6f} {narrow}）——收据 results/_r1086bmc_w266_fivekeys.json（键=n1_w265_results.json 机读 r587 律·"
    "本波预测键冻结于 W265 实测——W265 finalize 起草窗前已落地·活链头基准）。\n"
    "- 六门探针：PRE-FINALIZE **ALL PASS 第 29 连续正确相位**（results/_r1086bmc_w266_sixgate.json——splice 完整性 "
    "**CR-normalized 恒等** worktree==落链 git blob @ dc71ecc3f9【58 代吸收窗落的死窗 splice 遗产·落前 pf/n1 sha256-16==冻结收据 post 零漂移】；"
    "banned_direction_gate ADMIT rc0；pf/n1 selftest rc0【**post-splice 单 token heal**：死窗编辑器遗留 W266 块 _set_wave(265) 未滚——H1 r1076 W264 家族第 3 代复发；"
    "runtime 证据=术前 selftest 死「W266 A hits W265」·收据 _r1086bmc_w266_selftest_heal.json·最小性证明=landed blob+同 token==愈合工作树 CR 归一恒等·术前 FAIL 面存证 _r1086bmc_w266_sixgate_prereheal_FAIL.json】；"
    "shards 12/12 全 >100KB；seed_admit_gate FREE x2【base=600501 span=2000 / base=602501 span=200】；"
    "wave_configs 行四面【对齐·engine_owner=bm-c】）。\n"
    "- audit 段：machine=bm-c，finalize_only；shards_consumed={sc}；"
    "preregistered_doc=research/PERPETUAL_N1_W266_PREREG.md；evidence_cutoff=2026-09-22（P-5C 冻结窗同窗律）。"
).format(
    mu=mu, sig=sig, semu=semu, womu=wonly_mu, wosig=wonly_sig,
    lpre=line_pre, lm=line_m, k1=k1, k1b=k1b, k2=k2, k3=k3, k4=k4,
    ap95=fk["a_band"]["full_sharpe_p95"], ksemu=k_se_mu, sc=sc,
    narrow=("窄化续行" if semu < k_se_mu else ("持平微窄" if semu == k_se_mu else "带内持平")),
)

NEW8 = (
    "- §5.5 W267+ 投影承接机证（finalize 产物 preregistered_doc 面机读）：W266 注册宇宙已落地（A 600_501..602_500 + B 602_501..602_700，本波冻结收据"
    "_w266bmc_freeze_receipt.json）——W267 A naive 起点 602_501 将被注册 W266 B 带拒（staircase-affects-A 第十六次连续 A-hop 预期承接兑现·收据 downstream_seat 面预投影）；"
    "B own-A reservation cascade 预期同样上移（post-W266 宇宙活链重 derive 决定·勿假设 A-base==prior-B-tail+1 或 B-base==own-A-tail+1 相等式·E36 卡/W141 先例）；"
    "**W267 seat=next free number·下一冻结方必须 seat-first 发布且在 post-W266 宇宙上重 derive**（勿转录 r587）。\n"
    "- 宝藏与方法论捕获问：本批零新宝藏入册零新方法论卡——post-splice 单 token heal 面（H1 r1076 W264 家族第 3 代复发·死窗编辑器失职面）"
    "属 E63 既有家族的披露改进（六门+heal 双收据承载·术前 FAIL 证据存档），非新方法论卡。\n"
    "- 诚实披露面：(1) W266 splice 由 09:25-09:50 死窗执行（O-20261018-0948 病根定谳=v1 发射器 25 分钟墙钟击杀·09:50 顶格命中最新实锚）、"
    "58 代吸收窗哈希验证后落链 dc71ecc3f9（引掣 12/12 自烧先于落链·burn-ahead disclosed honest——引掣读工作树字节==落链字节）；"
    "(2) post-splice 单 token heal（H1 家族第 3 代复发·最小性证明过闸·术前 FAIL 面存证）；"
    "(3) 本波预测键冻结于 W265 实测（起草窗前 W265 finalize 已落地·活链头基准·§5 头注记）；"
    "(4) 引擎 dedup W266 remote_done=0 面如实披露（两批 append 已随本窗 dc71ecc3f9 推送上 origin 实证·remote 面归引掣自愈域候下一拍重评·非本波债）。"
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
