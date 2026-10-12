# -*- coding: utf-8 -*-
# W218 per-wave prereg derivation (bm-c r918 freeze-prep, 2026-10-12 08:4x).
# Method: machine transform of the freeze-time W217 prereg blob
# (git show ad011fee2:research/PERPETUAL_N1_W217_PREREG.md -- the exact
# pre-backfill commit face) with an explicit ordered replacement table.
# Pair old-sides are REPLAYED AT RUNTIME from the committed W217 derive
# (results/_w217bmc_prereg_derive.py SUB literal + results/_w216bmc_prereg_derive.py
# literal PAIRS, materialized @L14@/@L15@/@T16@ -> 214/215/16) -- zero
# transcription; every replayed block is assert-verified count==1 in the
# freeze-time blob BEFORE any pair application (r787 preflight law).
# Bands/facts machine-derived from the committed ADMIT receipt
# results/_w218bmc_20261012_probe_receipt.json + n1_w217_results.json --
# never transcribed by eye (r587).
# Corruption-class guard (r914 heal law): heritage tokens inside pair
# new-sides are written as @L14@/@L15@/@L16@/@T17@ placeholders and restored
# AFTER the generic shift, so the W216->W217 blanket shift cannot relabel
# chain-history legs, the se_mu chain tail, the RAM precedent list, or the
# estate parity list (the exact W215-face corruption class).
import ast, hashlib, json, subprocess, sys

sys.stdout.reconfigure(encoding="utf-8")
REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"

# ---------- freeze-time W217 blob ----------
BLOB = subprocess.run(["git", "-C", REPO, "show",
                       "ad011fee2:research/PERPETUAL_N1_W217_PREREG.md"],
                      capture_output=True).stdout
assert BLOB, "freeze-time W217 prereg blob fetch failed"
t = BLOB.decode("utf-8")
assert "## §7" in t and "占位" in t, "not the freeze-time (pre-backfill) face"

# ---------- replay-extract W217 PAIRS old-sides (lineage, zero transcription) ----------
src16 = open(r"results\_w216bmc_prereg_derive.py", encoding="utf-8").read()
pairs216 = None
for node in ast.walk(ast.parse(src16)):
    if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == "PAIRS":
        pairs216 = ast.literal_eval(node.value)
assert pairs216 and len(pairs216) == 46, f"W216 PAIRS extract failed: {len(pairs216) if pairs216 else 0}"
src17 = open(r"results\_w217bmc_prereg_derive.py", encoding="utf-8").read()
SUB17 = None
for node in ast.walk(ast.parse(src17)):
    if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == "SUB":
        SUB17 = ast.literal_eval(node.value)
assert SUB17 and len(SUB17) == 46, f"W217 SUB extract failed: {len(SUB17) if SUB17 else 0}"
OLD16 = [b.replace("@L14@", "214").replace("@T15@", "15") for _, b in pairs216]
OLD = []
for i, old in enumerate(OLD16):
    new = old
    for find, repl in SUB17[i]:
        c = new.count(find)
        assert c == 1, f"replay SUB17[{i}] count {c} != 1 for: {find[:60]}..."
        new = new.replace(find, repl, 1)
    OLD.append(new.replace("@L14@", "214").replace("@L15@", "215").replace("@T16@", "16"))
# preflight: every replayed W217-face block sits exactly once in the blob
for i, old in enumerate(OLD):
    c = t.count(old)
    assert c == 1, f"preflight block[{i}] count {c} != 1 in freeze-time blob"

# ---------- machine-derived anchors (never hand-copied) ----------
rec = json.load(open(r"results\_w218bmc_20261012_probe_receipt.json", encoding="utf-8"))
assert rec["verdict"] == "ADMIT" and rec["bands"] == {"A": "494404_496403", "B": "496404_496603"}
w217 = json.load(open(r"results\perpetual_faces\n1_w217_results.json", encoding="utf-8"))
led = w217["science_gates"]["ledger"]
assert led["total"] == 901189 and led["prev_total"] == 898989 and led["batch_trials"] == 2200
merged = w217["null_pool_cumulative"]["merged"]
assert merged["n_values"] == 475320
w217only = w217["null_pool_cumulative"]["w217_only"]
A_p95 = w217["families"]["A_random_engine_exit"]["full_sharpe_p95"]
kl = w217["skill_line_v2_k_lift"]
assert kl["line_delta_k_lift"] == -0.0001 and kl["n_eff_held_equal"] == 898989
assert kl["line_pre_w217"] == 1.1907 and kl["line_merged_475320"] == 1.1906
se_mu = w217["null_pool_cumulative"]["se_mu_at_k475320"]
assert se_mu == 0.000355
leg1, leg4 = rec["legs"]["leg1"], rec["legs"]["leg4"]
assert leg1["A"] == [494404, 496403] and leg1["B"] == [496404, 496603]
assert leg1["ARITH_A"] == [494204, 496203] and leg1["B_naive_first_clean"] == [494404, 494603]
assert leg4["W219p_A"] == "496404..498403" and leg4["W219p_B"] == "496604..496803"
assert leg4["W219p_B_lands_inside_W219p_A"] is True
leg0 = rec["legs"]["leg0"]
assert leg0["rows"] == 215 and leg0["owner_rows"] == 207 and leg0["bmc_ordinal"] == 48 and leg0["ordinal"] == 208
# formatted-string guards: every literal below that carries a machine value
# is assert-verified against the live JSON here (zero eyeball)
def fmt8(x):
    return ("−" if x < 0 else "") + f"{abs(x):.8f}"
assert fmt8(merged["mu"]) == "−0.09275152", fmt8(merged["mu"])
assert fmt8(w217only["mu"]) == "−0.10123773", fmt8(w217only["mu"])
assert f"{merged['sigma']:.8f}" == "0.24508756", f"{merged['sigma']:.8f}"
assert f"{abs(w217only['mu'] - merged['mu']):.4f}" == "0.0085", f"{abs(w217only['mu'] - merged['mu']):.4f}"
assert f"{A_p95:.4f}" == "0.3074", f"{A_p95:.4f}"
# free RAM live read (honesty for the RAM note)
import psutil
_avail_gb = psutil.virtual_memory().available / 1e9
assert 0.4 <= _avail_gb <= 2.5, f"unexpected RAM face: {_avail_gb}"
print(f"live free RAM: {_avail_gb:.2f} GB -> note '~0.8GB'")

# ---------- per-pair submaps: index -> ordered (find, replace) ----------
SUB = {
 0: [("PERPETUAL-N1-W217 预注册 · N1 nulls-deepening 泵第 215 枚","PERPETUAL-N1-W218 预注册 · N1 nulls-deepening 泵第 216 枚"),
     ("engine_owner 行 206 注册在册（表尾 W216 行·probe leg0 机证 214 行","engine_owner 行 207 注册在册（表尾 W217 行·probe leg0 机证 215 行"),
     ("本候选=bm-c 第四十七枚自有波【live-derive face：席面 prose 46th=seat-time face（r915 窗 W216 注册后 live derive·r914 freeze receipt 46th owned 承袭）→freeze 时 live derive bm-c rows 46+候选=第 47 枚 EXACT","本候选=bm-c 第四十八枚自有波【live-derive face：席面 prose 47th=seat-time face（r917 窗 W217 注册后 live derive·r916 freeze receipt 47th owned 承袭）→freeze 时 live derive bm-c rows 47+候选=第 48 枚 EXACT"),
     ("【bm-c 循环班 r916 freeze 窗·2026-10-12 07:3x·","【bm-c 循环班 r918 freeze 窗·2026-10-12 08:4x·")],
 1: [("live-read r916：","live-read r918：")],
 2: [("波号 217=注册表 W216 席后首个自由号","波号 218=注册表 W217 席后首个自由号"),
     ("r915 窗实跑：origin inbox/processed/ 零 W217 席位外机命中","r917 窗实跑：origin inbox/processed/ 零 W218 席位外机命中"),
     ("perpetual_faces.py 零 217 行","perpetual_faces.py 零 218 行"),
     ("perpetual_faces_n1.py 零 PERPETUAL-N1-W217 WAVE_CONFIGS","perpetual_faces_n1.py 零 PERPETUAL-N1-W218 WAVE_CONFIGS"),
     ("origin 零 PERPETUAL_N1_W217_PREREG.md","origin 零 PERPETUAL_N1_W218_PREREG.md")],
 3: [("+W214=bm-c r910 五面冻结（4664900c8）+引擎自燃 12/12+r911 finalize one-pass 已落（K=468,720·账本头 894,589 机读·n1_w214_results.json·05:2x）","+W@L14@=bm-c r910 五面冻结（4664900c8）+引擎自燃 12/12+r911 finalize one-pass 已落（K=468,720·账本头 894,589 机读·n1_w@L14@_results.json·05:2x）"),
     ("+W215=bm-c r912 五面冻结（1e71c3b93）+引擎自燃 12/12+r913 finalize one-pass 已落（K=470,920·账本头 896,789 机读·n1_w215_results.json·06:1x）+W216=bm-c r914 五面冻结（0b3c489f0）+引擎自燃 12/12+r915 finalize one-pass 已落（K=473,120·账本头 898,989 机读·n1_w216_results.json·06:5x）——本波上游链=W1..W216 finalize 全落地","+W@L15@=bm-c r912 五面冻结（1e71c3b93）+引擎自燃 12/12+r913 finalize one-pass 已落（K=470,920·账本头 896,789 机读·n1_w@L15@_results.json·06:1x）+W@L16@=bm-c r914 五面冻结（0b3c489f0）+引擎自燃 12/12+r915 finalize one-pass 已落（K=473,120·账本头 898,989 机读·n1_w@L16@_results.json·06:5x）+W217=bm-c r916 五面冻结（ad011fee2）+引擎自燃 12/12+r917 finalize one-pass 已落（K=475,320·账本头 901,189 机读·n1_w217_results.json·08:1x）——本波上游链=W1..W217 finalize 全落地")],
 4: [("本机席位公示=MSG-20261012-0700-bmc-w217-seat 已推 origin 1e1454cfb 先于本冻结【r565 律·席位先行·r915 窗】；下游 W218+ 投影见 §5.5（probe 机证 leg4·W218 freezer 承接面）】。","本机席位公示=MSG-20261012-0830-bmc-w218-seat 已推 origin 8a4c1857a 先于本冻结【r565 律·席位先行·r917 窗】；下游 W219+ 投影见 §5.5（probe 机证 leg4·W219 freezer 承接面）】。")],
 5: [("W2..W216 全注册在冻结时点成立","W2..W217 全注册在冻结时点成立")],
 6: [("results/_w217bmc_20261012_probe_receipt.json","results/_w218bmc_20261012_probe_receipt.json")],
 7: [("A-ext seed=492_204..494_203","A-ext seed=494_404..496_403"),
     ("A 面=FIRST-CLEAN past prior-wave B 阶梯第七十七例","A 面=FIRST-CLEAN past prior-wave B 阶梯第七十八例"),
     ("A 面算术继续带 492_004..494_003（自注册 W216 A 尾 492_003 续）在其起点即被 W216 注册 B 带 492_004..492_203 **拒**（W216 席位 leg4 投影+其 probe 所预言+强制）→ 诚实前向走 **1 hop** 落 **492_204..494_203**","A 面算术继续带 494_204..496_203（自注册 W217 A 尾 494_203 续）在其起点即被 W217 注册 B 带 494_204..494_403 **拒**（W217 席位 leg4 投影+其 probe 所预言+强制）→ 诚实前向走 **1 hop** 落 **494_404..496_403**"),
     ("A base==前波 B 尾+1（492_203+1）机检关系","A base==前波 B 尾+1（494_403+1）机检关系"),
     ("A-hops-prior-B 阶梯几何第七十七例（E36 卡）","A-hops-prior-B 阶梯几何第七十八例（E36 卡）"),
     ("A_semantics 机读序数=SEVENTY-SEVENTH（第七十七例）","A_semantics 机读序数=SEVENTY-EIGHTH（第七十八例）")],
 8: [("B-ext exit seed=494_204..494_403","B-ext exit seed=496_404..496_603"),
     ("B 面 naive first-clean 继续带 492_204..492_403 在注册宇宙上 CLEAN 但**落在本波 A 窗 492_204..494_203 内**","B 面 naive first-clean 继续带 494_404..494_603 在注册宇宙上 CLEAN 但**落在本波 A 窗 494_404..496_403 内**"),
     ("B 带本波 A 窗保留走 **1 hop** 落 **494_204..494_403**","B 带本波 A 窗保留走 **1 hop** 落 **496_404..496_603**"),
     ("B base==本波 A 尾+1（494_203+1）机检关系","B base==本波 A 尾+1（496_403+1）机检关系"),
     ("W216 席位 leg4 投影承接面注记兑现**：投影预言 W217 须在 post-W216 注册宇宙重 derive 且 derive B 时预留本波 A 窗","W217 席位 leg4 投影承接面注记兑现**：投影预言 W218 须在 post-W217 注册宇宙重 derive 且 derive B 时预留本波 A 窗")],
 9: [("R250：W217 带从未指派","R250：W218 带从未指派")],
 10: [("A base=492204 span=2000 checked=2000 verdict=FREE / B base=494204 span=200 checked=200 verdict=FREE","A base=494404 span=2000 checked=2000 verdict=FREE / B base=496404 span=200 checked=200 verdict=FREE")],
 11: [("扫描面=pre-W217 全二百一十四行注册 N1 带表（表尾 W216 行·probe leg0 机证 214 行 live 单态 owner rows 206）","扫描面=pre-W218 全二百一十五行注册 N1 带表（表尾 W217 行·probe leg0 机证 215 行 live 单态 owner rows 207）")],
 12: [("W2..W216 落地 runner","W2..W217 落地 runner")],
 13: [("selftest W217 face 将随五面冻结落地验证","selftest W218 face 将随五面冻结落地验证")],
 14: [("本件与 results/_w217bmc_freeze_edits.py","本件与 results/_w218bmc_freeze_edits.py"),
     ("按 _w216bmc_freeze_edits.py 模板派生","按 _w2@T17@bmc_freeze_edits.py 模板派生"),
     ("gate0.5 自查 W216 行+W216 finalize 件在场","gate0.5 自查 W217 行+W217 finalize 件在场"),
     ("estate 提取面=本机 W216 块物理字节","estate 提取面=本机 W217 块物理字节"),
     ("（r914/W216 先例 freeze-prep 同式","（r916/W217 先例 freeze-prep 同式")],
 15: [("- 批名=**PERPETUAL-N1-W217**。","- 批名=**PERPETUAL-N1-W218**。")],
 16: [("**W1..W216 N1 finalize 已全部落地**","**W1..W217 N1 finalize 已全部落地**"),
     ("净账本锚头 **898,989**·K=473,120 合并池·n1_w216_results.json 机读·W216 finalize one-pass bm-c r915 窗 06:5x（W216 面完整性=12/12 shards consumed+finalize audit finalize_only=true 收口·r914 freeze 0b3c489f0","净账本锚头 **901,189**·K=475,320 合并池·n1_w217_results.json 机读·W217 finalize one-pass bm-c r917 窗 08:1x（W217 面完整性=12/12 shards consumed+finalize audit finalize_only=true 收口·r916 freeze ad011fee2")],
 17: [("累计 null 池=473,120+2,200（本波）=**475,320 投影**","累计 null 池=475,320+2,200（本波）=**477,520 投影**")],
 18: [("（本机席位公示 MSG-20261012-0700-bmc-w217-seat 已推 origin 1e1454cfb r565 律·probe W218+ 投影 A 494_204..496_203 / B 494_404..494_603","（本机席位公示 MSG-20261012-0830-bmc-w218-seat 已推 origin 8a4c1857a r565 律·probe W219+ 投影 A 496_404..498_403 / B 496_604..496_803"),
     ("投影 B 落投影 A 窗内·W217 B 带 494_204..494_403 注册后将拒 naive W218 A 窗=阶梯 A-hops-prior-B 第七十八例——**W218 freezer 承接面强制注记：须在 post-W217 宇宙重 derive 且 derive B 时预留本波 A 窗","投影 B 落投影 A 窗内·W218 B 带 496_404..496_603 注册后将拒 naive W219 A 窗=阶梯 A-hops-prior-B 第七十九例——**W219 freezer 承接面强制注记：须在 post-W218 宇宙重 derive 且 derive B 时预留本波 A 窗")],
 19: [("T-2026-10-01-141 s1 引擎线第 207 波【bm-c 第四十七枚自有波【机面 derive：probe leg0 bmc_ordinal=46 live face（r915 窗 live 单态计法）——freeze 时 live derive bm-c rows 46+候选=第 47 枚 EXACT","T-2026-10-01-141 s1 引擎线第 208 波【bm-c 第四十八枚自有波【机面 derive：probe leg0 bmc_ordinal=47 live face（r917 窗 live 单态计法）——freeze 时 live derive bm-c rows 47+候选=第 48 枚 EXACT"),
     ("波号=注册表 W216 席后首个自由号·单态零席位空档于冻结时点成立；中位公示 MSG-20261012-0700-bmc-w217-seat 先推 origin 1e1454cfb r565 律","波号=注册表 W217 席后首个自由号·单态零席位空档于冻结时点成立；中位公示 MSG-20261012-0830-bmc-w218-seat 先推 origin 8a4c1857a r565 律")],
 20: [("本窗 free RAM ~0.5GB","本窗 free RAM ~0.8GB"),
     ("（MV XQ i2v 影片链=CEO 优先令在飞占用·O-20261011-0012 sec.2.3 影片链优先不变）","（MV XQ i2v 影片链=bm-c lane 已收官〔O-20261012-0739 §1〕·常驻底盘占用仍在高位）"),
     ("W206/W211/W212/W213/W214/W215/W216 低 RAM 实烧先例","W206/W211/W212/W213/W@L14@/W@L15@/W@L16@/W217 低 RAM 实烧先例")],
 21: [("复读自见 W217 行并点火自烧","复读自见 W218 行并点火自烧")],
 22: [("--prereg research/PERPETUAL_N1_W217_PREREG.md","--prereg research/PERPETUAL_N1_W218_PREREG.md")],
 23: [("v2..W216 落地）","v2..W217 落地）")],
 24: [("entry rng seed=**492_204+j**","entry rng seed=**494_404+j**"),
     ("法典 §4 W217 行 A=492_204..494_203","法典 §4 W218 行 A=494_404..496_403"),
     ("阶梯第七十七例**：算术续带 492_004..494_003 起点即被 W216 注册 B 带 492_004..492_203 拒→1 hop 落 492_204..494_203","阶梯第七十八例**：算术续带 494_204..496_203 起点即被 W217 注册 B 带 494_204..494_403 拒→1 hop 落 494_404..496_403")],
 25: [("entry rng=**492_204+j**","entry rng=**494_404+j**"),
     ("exit rng=**494_204+j**","exit rng=**496_404+j**"),
     ("法典 §4 W217 行 B=494_204..494_403","法典 §4 W218 行 B=496_404..496_603"),
     ("B 算术续带 492_204..492_403 在注册宇宙上 CLEAN 但落在本波 A 窗 492_204..494_203 内","B 算术续带 494_404..494_603 在注册宇宙上 CLEAN 但落在本波 A 窗 494_404..496_403 内"),
     ("保留走落 494_204..494_403","保留走落 496_404..496_603"),
     ("与 W216 席位 leg4 投影承接面注记兑现收敛","与 W217 席位 leg4 投影承接面注记兑现收敛")],
 26: [("（selftest 强制）：W217 带与 v1 在用带","（selftest 强制）：W218 带与 v1 在用带")],
 27: [("W2..W216 带（冻结时点全注册单态）","W2..W217 带（冻结时点全注册单态）")],
 28: [("本波机验 ADMIT 回执在场=_w217bmc_20261012 探针窗","本波机验 ADMIT 回执在场=_w218bmc_20261012 探针窗")],
 29: [("selftest W217 face（A=first-clean past prior-wave B 恒等·B=first-clean past own-wave A 恒等+同窗互斥断言·W216 行 parity 腿","selftest W218 face（A=first-clean past prior-wave B 恒等·B=first-clean past own-wave A 恒等+同窗互斥断言·W217 行 parity 腿")],
 30: [("从**本机 W216 块物理字节**提取","从**本机 W217 块物理字节**提取"),
     ("W216 块的 W215 leg（1 行）不入 estate 路径·提取后新增 W215+W216 leg 构成 W217 块 parity 75 行（W138..W206+W211+W212+W213+W214+W215+W216）","W217 块的 W@L16@ leg（1 行）不入 estate 路径·提取后新增 W@L16@+W217 leg 构成 W218 块 parity 76 行（W138..W206+W211+W212+W213+W@L14@+W@L15@+W@L16@+W217）")],
 31: [("起草窗实流 W1..W216 已落账 473,120 实测","起草窗实流 W1..W217 已落账 475,320 实测")],
 32: [("batch_name=\"PERPETUAL-N1-W217\", batch_trials=2200, file_name=\"results/perpetual_faces/n1_w217_results.json\"","batch_name=\"PERPETUAL-N1-W218\", batch_trials=2200, file_name=\"results/perpetual_faces/n1_w218_results.json\"")],
 33: [("（起草窗实况注记：**W1..W216 N1 finalize 已全部落地**——净账本锚头 898,989·**K=473,120 合并池**·**零在飞上游席——本波 §5 预测键=**W216 实测值**【results/perpetual_faces/n1_w216_results.json·N1 面最新已落账键·06:5x finalize one-pass】。","（起草窗实况注记：**W1..W217 N1 finalize 已全部落地**——净账本锚头 901,189·**K=475,320 合并池**·**零在飞上游席——本波 §5 预测键=**W217 实测值**【results/perpetual_faces/n1_w217_results.json·N1 面最新已落账键·08:1x finalize one-pass】。")],
 34: [("1. W217-only mu 与累计池 merged mu（W216 实测键 **−0.09271206**·K=473,120 合并池·W216-only 实测 **−0.10025573**）差异 **|Δ|<0.02**（W2..W216 共二百一十四面实测 mu 稳定先例·单波跨键微；W216-only vs merged 实差 0.0075 在带内）。","1. W218-only mu 与累计池 merged mu（W217 实测键 **−0.09275152**·K=475,320 合并池·W217-only 实测 **−0.10123773**）差异 **|Δ|<0.02**（W2..W217 共二百一十五面实测 mu 稳定先例·单波跨键微；W217-only vs merged 实差 0.0085 在带内）。")],
 35: [("键 **0.24510342**=W216 合并池实测","键 **0.24508756**=W217 合并池实测")],
 36: [("3. A 档 full_sharpe_p95 与 W216 A 档 p95（**0.2952** 实测锚）差 **<0.05**（门标注法 W5..W216 先例","3. A 档 full_sharpe_p95 与 W217 A 档 p95（**0.3074** 实测锚）差 **<0.05**（门标注法 W5..W217 先例")],
 37: [("W136..W216 先例链披露","W136..W217 先例链披露"),
     ("键 W216 实测 K-lift **−0.0002**·line_merged@K473,120 **1.1906**·line_pre_w216 1.1908·n_eff_held_equal 896,789","键 W217 实测 K-lift **−0.0001**·line_merged@K475,320 **1.1906**·line_pre_w217 1.1907·n_eff_held_equal 898,989"),
     ("se_mu 收窄链 …→W209 0.000362→W211 0.000361→W212 0.000360→W213 0.000359→W214 0.000358→W215 0.000357→W216 **0.000356**】","se_mu 收窄链 …→W209 0.000362→W211 0.000361→W212 0.000360→W213 0.000359→W@L14@ 0.000358→W@L15@ 0.000357→W@L16@ 0.000356→W217 **0.000355**】")],
 38: [("5. **W218+ 投影（probe 机证 leg4·下波冻结方复核非转抄 r587 律）**：A naive first-clean 494_204..496_203 CLEAN（hops=0·pre-W217 宇宙）；B naive first-clean **494_404..494_603 CLEAN**（hops=0）——**naive B 落在 naive A 窗内**（W141 同窗互斥先例适用于 W218：W218 冻结方必须在 post-W217 注册宇宙重 derive 且 derive B 时预留本波 A 窗——leg2 律/E36 卡）；**W217 B 带 494_204..494_403 注册后将拒 naive W218 A 窗**——W218 A 重 derive 同强制（越过 W217 B 带·阶梯 A-hops-prior-B 第七十八例）；verify at W218 prereg","5. **W219+ 投影（probe 机证 leg4·下波冻结方复核非转抄 r587 律）**：A naive first-clean 496_404..498_403 CLEAN（hops=0·pre-W218 宇宙）；B naive first-clean **496_604..496_803 CLEAN**（hops=0）——**naive B 落在 naive A 窗内**（W141 同窗互斥先例适用于 W219：W219 冻结方必须在 post-W218 注册宇宙重 derive 且 derive B 时预留本波 A 窗——leg2 律/E36 卡）；**W218 B 带 496_404..496_603 注册后将拒 naive W219 A 窗**——W219 A 重 derive 同强制（越过 W218 B 带·阶梯 A-hops-prior-B 第七十九例）；verify at W219 prereg")],
 39: [(" --wave 217/finalize --wave 217"," --wave 218/finalize --wave 218")],
 40: [("【n1_w217/ 分片计数增长·唯一点火证据·r325 律】","【n1_w218/ 分片计数增长·唯一点火证据·r325 律】")],
 41: [("`results/p2cal_ext/n1_w217/shard-<k>-of-12.json`","`results/p2cal_ext/n1_w218/shard-<k>-of-12.json`")],
 42: [("`results/perpetual_faces/n1_w217_results.json`（finalize 合并件·顶层 evidence_cutoff·cutoff_meta·audit 段·K-lift 对照；finalize 键序前置=**起草窗零在飞上游席（W1..W216 全落）","`results/perpetual_faces/n1_w218_results.json`（finalize 合并件·顶层 evidence_cutoff·cutoff_meta·audit 段·K-lift 对照；finalize 键序前置=**起草窗零在飞上游席（W1..W217 全落）")],
 43: [("engine_owner==bm-c 46 行注册〔冻结时点〕+ 本候选","engine_owner==bm-c 47 行注册〔冻结时点〕+ 本候选")],
 44: [("段——r915 W216 §7 范式）","段——r917 W217 §7 范式）")],
 45: [("（占位·finalize 同窗回填：§5.5 W218+ 投影承接机证/宝藏与方法论捕获问/诚实披露面——r915 W216 §8 范式）","（占位·finalize 同窗回填：§5.5 W219+ 投影承接机证/宝藏与方法论捕获问/诚实披露面——r917 W217 §8 范式）")],
}

# ---------- build + apply W218 pairs ----------
PAIRS = []
for i, old in enumerate(OLD):
    new = old
    for find, repl in SUB[i]:
        c = new.count(find)
        assert c == 1, f"submap[{i}] count {c} != 1 for: {find[:60]}..."
        new = new.replace(find, repl, 1)
    PAIRS.append((old, new))

for old, new in PAIRS:
    c = t.count(old)
    assert c == 1, f"pair count {c} != 1: {old[:70]}..."
    t = t.replace(old, new, 1)

# ---- generic wave-token shifts (after targeted pairs) ----
# Pairs covered every W217 self face (each count==1 asserted). Remaining
# "W217" tokens = pair-written legit refs (chain W217 leg, W1..W217 scope)
# which must STAY W217 -- mask, then age one-wave-older W216 refs to W217,
# then restore. @L14@/@L15@/@L16@/@T17@ hold heritage tokens immune.
t = t.replace("n1_w217_results", "n1_@u_w@_results")   # protect pair-written upstream file refs
t = t.replace("PERPETUAL-N1-W217", "PERPETUAL-N1-W218")
t = t.replace("PERPETUAL_N1_W217", "PERPETUAL_N1_W218")
t = t.replace("n1_w217", "n1_w218")
t = t.replace("_w217bmc", "_w218bmc")
t = t.replace("W217", "@U_W@")
t = t.replace("W216", "W217")
t = t.replace("n1_w216", "n1_w217")
t = t.replace("PERPETUAL_N1_W216", "PERPETUAL_N1_W217")
t = t.replace("_w216bmc", "_w217bmc")
t = t.replace("@u_w@", "w217")
t = t.replace("@U_W@", "W217")
t = t.replace("@L14@", "214")
t = t.replace("@L15@", "215")
t = t.replace("@L16@", "216")
t = t.replace("@T17@", "17")

# ---- stale-token checklist (must all be ZERO) ----
STALE = ["492_204..494_203", "492_004..494_003", "492_004..492_203", "492_204..492_403",
         "492204", "第 215 枚", "SEVENTY-SEVENTH", "第七十七例", "第四十七枚",
         "206 注册在册", "bmc_ordinal=46", "r915 窗 W217 注册后", "0.2952", "−0.09271206",
         "−0.10025573", "0.24510342", "0700-bmc", "1e1454cfb",
         "06:5x（W216 面完整性", "06:5x finalize one-pass】", "二百一十四行", "r916 freeze 窗·2026-10-12 07:3x", "第 207 波",
         "n_eff_held_equal 896,789", "1.1908", "0.0075", "=**475,320 投影**", "engine_owner==bm-c 46 行",
         "prose 46th", "r914 freeze receipt 46th", "第 47 枚 EXACT", "pre-W217 宇宙",
         "W218 freezer 承接面", "r915 W216 §7 范式",
         "W217 B 带 494_204..494_403 注册后将拒 naive W218",
         "（492_203+1）", "（494_203+1）", "波号 217=", "A base=492204", "n1_w217/ 分片计数增长",
         "batch_name=\"PERPETUAL-N1-W217\""]
# NOTE: "494_204..496_203" / "494_404..494_603" are NOT stale in the W218
# face -- they are the fresh A/B arithmetic-continuation bands (SUB[7]/SUB[8]
# /SUB[24]/SUB[25] write them); the §5.5 projection instances were consumed
# by pair 38. Same digits, different semantics (probed live 08:19).
# "494_204..494_403" is NOT stale -- it is the fresh upstream refusing band
# (>=2 asserted below). "n1_w217/ 分片计数增长" IS stale (self shard face
# now n1_w218) while "n1_w217_results.json" file refs stay (upstream legs).
for s in STALE:
    c = t.count(s)
    if c:
        import re as _re
        for m in _re.finditer(_re.escape(s), t):
            print(f"--- STALE[{s}] ctx ---")
            print(t[max(0, m.start()-160):m.end()+80].replace("\n", " | "))
    assert c == 0, f"STALE token survives x{c}: {s}"

# ---- new-face presence checks ----
NEW = ["PERPETUAL-N1-W218", "第 216 枚", "494_404..496_403", "496_404..496_603",
       "SEVENTY-EIGHTH", "第七十八例", "第七十九例", "第四十八枚",
       "901,189", "475,320", "477,520", "898,989",
       "MSG-20261012-0830-bmc-w218-seat", "8a4c1857a",
       "bmc_ordinal=47", "n1_w218_results.json", "0.3074", "−0.09275152",
       "−0.10123773", "0.24508756", "n_eff_held_equal 898,989", "0.000355",
       "1.1906", "1.1907", "第 208 波", "496_404..498_403", "496_604..496_803",
       "494_204..496_203", "494_404..494_603",
       "0.0085", "ad011fee2", "第 48 枚 EXACT", "W219 freezer 承接面",
       "r917 W217 §7 范式"]
for s in NEW:
    assert t.count(s) >= 1, f"NEW token missing: {s}"
# in-band sanity: own A band appears as the ADMIT face (>=4), own B band too
assert t.count("494_404..496_403") >= 4 and t.count("496_404..496_603") >= 4
# upstream W217 refusing band appears in A-face prose (band-facts + §3A)
assert t.count("494_204..494_403") >= 2
# chain-history legs present exactly once each (heritage restored verbatim)
assert t.count("+W213=bm-c r908 五面冻结（a24069f4c）") == 1
assert t.count("+W214=bm-c r910 五面冻结（4664900c8）") == 1
assert t.count("+W215=bm-c r912 五面冻结（1e71c3b93）") == 1
assert t.count("+W216=bm-c r914 五面冻结（0b3c489f0）") == 1
assert t.count("+W217=bm-c r916 五面冻结（ad011fee2）") == 1
assert t.count("n1_w213_results.json·04:2x") == 1
assert t.count("n1_w214_results.json·05:2x") == 1
assert t.count("n1_w215_results.json·06:1x") == 1
assert t.count("n1_w216_results.json·06:5x") == 1
assert t.count("n1_w217_results.json·08:1x") == 1
# healed RAM list + estate note + se_mu chain present
assert t.count("W206/W211/W212/W213/W214/W215/W216/W217 低 RAM 实烧先例") == 1
assert t.count("（W138..W206+W211+W212+W213+W214+W215+W216+W217）") == 1
assert t.count("按 _w217bmc_freeze_edits.py 模板派生") == 1
assert t.count("→W213 0.000359→W214 0.000358→W215 0.000357→W216 0.000356→W217 **0.000355**") == 1

out = r"research\PERPETUAL_N1_W218_PREREG.md"
open(out, "wb").write(t.encode("utf-8"))
print("W218 prereg derived OK:", out)
print("bytes:", len(t.encode("utf-8")), "| sha16:", hashlib.sha256(t.encode("utf-8")).hexdigest()[:16])
print("W217(upper) refs (upstream, expected 40+):", t.count("W217"), "| W218 self:", t.count("W218"))
