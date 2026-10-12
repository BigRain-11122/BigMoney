# -*- coding: utf-8 -*-
# W219 per-wave prereg derivation (bm-c r920 freeze-prep, 2026-10-12 09:4x).
# Method: machine transform of the freeze-time W218 prereg blob
# (git show 9afb0b1d7:research/PERPETUAL_N1_W218_PREREG.md -- the exact
# pre-backfill commit face) with an explicit ordered replacement table.
# Pair old-sides are REPLAYED AT RUNTIME from the committed lineage chain
# (results/_w216bmc_prereg_derive.py PAIRS literal + results/_w217bmc_prereg_derive.py
# SUB literal + results/_w218bmc_prereg_derive.py SUB literal, materialized
# @L14@/@L15@/@T16@ -> 214/215/16 then @L14@/@L15@/@L16@/@T17@ -> 214/215/216/17)
# -- zero transcription; every replayed block is assert-verified count==1 in
# the freeze-time blob BEFORE any pair application (r787 preflight law).
# Bands/facts machine-derived from the committed ADMIT receipt
# results/_w219bmc_20261012_probe_receipt.json + n1_w218_results.json --
# never transcribed by eye (r587).
# Corruption-class guard (r914 heal law): heritage tokens inside pair
# new-sides are written as @L14@/@L15@/@L16@/@L17@/@T18@ placeholders and
# restored AFTER the generic shift, so the W217->W218 blanket shift cannot
# relabel chain-history legs, the se_mu chain tail, the RAM precedent list,
# or the estate parity list (the exact W215-face corruption class).
import ast, hashlib, json, subprocess, sys

sys.stdout.reconfigure(encoding="utf-8")
REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"

# ---------- freeze-time W218 blob ----------
BLOB = subprocess.run(["git", "-C", REPO, "show",
                       "9afb0b1d7:research/PERPETUAL_N1_W218_PREREG.md"],
                      capture_output=True).stdout
assert BLOB, "freeze-time W218 prereg blob fetch failed"
t = BLOB.decode("utf-8")
assert "## §7" in t and "占位" in t, "not the freeze-time (pre-backfill) face"

# ---------- replay-extract W219 PAIRS old-sides (lineage, zero transcription) ----------
def extract_lit(path, varname, expect):
    src = open(path, encoding="utf-8").read()
    val = None
    for node in ast.walk(ast.parse(src)):
        if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == varname:
            try:
                cand = ast.literal_eval(node.value)
            except Exception:
                cand = None
            if cand:
                val = cand
                break
    assert val and len(val) == expect, f"{varname} extract failed: {len(val) if val else 0}"
    return val

pairs216 = extract_lit(r"results\_w216bmc_prereg_derive.py", "PAIRS", 46)
SUB17 = extract_lit(r"results\_w217bmc_prereg_derive.py", "SUB", 46)
SUB18 = extract_lit(r"results\_w218bmc_prereg_derive.py", "SUB", 46)
OLD16 = [b.replace("@L14@", "214").replace("@T15@", "15") for _, b in pairs216]
OLD17 = []
for i, old in enumerate(OLD16):
    new = old
    for find, repl in SUB17[i]:
        c = new.count(find)
        assert c == 1, f"replay SUB17[{i}] count {c} != 1 for: {find[:60]}..."
        new = new.replace(find, repl, 1)
    OLD17.append(new.replace("@L14@", "214").replace("@L15@", "215").replace("@T16@", "16"))
OLD = []
for i, old in enumerate(OLD17):
    new = old
    for find, repl in SUB18[i]:
        c = new.count(find)
        assert c == 1, f"replay SUB18[{i}] count {c} != 1 for: {find[:60]}..."
        new = new.replace(find, repl, 1)
    OLD.append(new.replace("@L14@", "214").replace("@L15@", "215").replace("@L16@", "216").replace("@T17@", "17"))
# preflight: every replayed W218-face block sits exactly once in the blob
for i, old in enumerate(OLD):
    c = t.count(old)
    assert c == 1, f"preflight block[{i}] count {c} != 1 in freeze-time blob"

# ---------- machine-derived anchors (never hand-copied) ----------
rec = json.load(open(r"results\_w219bmc_20261012_probe_receipt.json", encoding="utf-8"))
assert rec["verdict"] == "ADMIT" and rec["bands"] == {"A": "496604_498603", "B": "498604_498803"}
w218 = json.load(open(r"results\perpetual_faces\n1_w218_results.json", encoding="utf-8"))
led = w218["science_gates"]["ledger"]
assert led["total"] == 903389 and led["prev_total"] == 901189 and led["batch_trials"] == 2200
merged = w218["null_pool_cumulative"]["merged"]
assert merged["n_values"] == 477520
w218only = w218["null_pool_cumulative"]["w218_only"]
A_p95 = w218["families"]["A_random_engine_exit"]["full_sharpe_p95"]
kl = w218["skill_line_v2_k_lift"]
assert kl["line_delta_k_lift"] == 0.0001 and kl["n_eff_held_equal"] == 901189
assert kl["line_pre_w218"] == 1.1907 and kl["line_merged_477520"] == 1.1908
se_mu = w218["null_pool_cumulative"]["se_mu_at_k477520"]
assert se_mu == 0.000355
leg1, leg4 = rec["legs"]["leg1"], rec["legs"]["leg4"]
assert leg1["A"] == [496604, 498603] and leg1["B"] == [498604, 498803]
assert leg1["ARITH_A"] == [496404, 498403] and leg1["B_naive_first_clean"] == [496604, 496803]
assert leg4["W220p_A"] == "498604..500603" and leg4["W220p_B"] == "498804..499003"
assert leg4["W220p_B_lands_inside_W220p_A"] is True
leg0 = rec["legs"]["leg0"]
assert leg0["rows"] == 216 and leg0["owner_rows"] == 208 and leg0["bmc_ordinal"] == 49 and leg0["ordinal"] == 209
# formatted-string guards: every literal below that carries a machine value
# is assert-verified against the live JSON here (zero eyeball)
def fmt8(x):
    return ("−" if x < 0 else "") + f"{abs(x):.8f}"
assert fmt8(merged["mu"]) == "−0.09278311", fmt8(merged["mu"])
assert fmt8(w218only["mu"]) == "−0.09960895", fmt8(w218only["mu"])
assert f"{merged['sigma']:.8f}" == "0.24510530", f"{merged['sigma']:.8f}"
assert f"{abs(w218only['mu'] - merged['mu']):.4f}" == "0.0068", f"{abs(w218only['mu'] - merged['mu']):.4f}"
assert f"{A_p95:.4f}" == "0.3037", f"{A_p95:.4f}"
# free RAM live read (honesty for the RAM note)
import psutil
_avail_gb = psutil.virtual_memory().available / 1e9
assert 0.2 <= _avail_gb <= 3.0, f"unexpected RAM face: {_avail_gb}"
RAM_GB = f"~{_avail_gb:.1f}"
print(f"live free RAM: {_avail_gb:.2f} GB -> note '{RAM_GB}GB'")
# engine live status (honesty for the block-1 carried face)
_st = subprocess.run([sys.executable, "Tools/saturation_engine.py", "status"],
                     cwd=REPO, capture_output=True, text=True, encoding="utf-8", errors="replace")
assert _st.returncode == 0, f"engine status FAIL: {(_st.stdout or '')[-300:]}"
assert '"burns_active": []' in (_st.stdout or "") or "'burns_active': []" in (_st.stdout or "") or '"burns_active":[]' in (_st.stdout or ""), "engine burns_active not empty at derive time"
assert '"queue_next": []' in (_st.stdout or "") or "'queue_next': []" in (_st.stdout or "") or '"queue_next":[]' in (_st.stdout or ""), "engine queue_next not empty at derive time"
print("engine live status: burns_active=[] queue_next=[] verified")

# ---------- per-pair submaps: index -> ordered (find, replace) ----------
SUB = {
 0: [("PERPETUAL-N1-W218 预注册 · N1 nulls-deepening 泵第 216 枚","PERPETUAL-N1-W219 预注册 · N1 nulls-deepening 泵第 217 枚"),
     ("engine_owner 行 207 注册在册（表尾 W217 行·probe leg0 机证 215 行","engine_owner 行 208 注册在册（表尾 W218 行·probe leg0 机证 216 行"),
     ("本候选=bm-c 第四十八枚自有波【live-derive face：席面 prose 47th=seat-time face（r917 窗 W217 注册后 live derive·r916 freeze receipt 47th owned 承袭）→freeze 时 live derive bm-c rows 47+候选=第 48 枚 EXACT","本候选=bm-c 第四十九枚自有波【live-derive face：席面 prose 48th=seat-time face（r919 窗 W218 注册后 live derive·r918 freeze receipt 48th owned 承袭）→freeze 时 live derive bm-c rows 48+候选=第 49 枚 EXACT"),
     ("【bm-c 循环班 r918 freeze 窗·2026-10-12 08:4x·","【bm-c 循环班 r920 freeze 窗·2026-10-12 09:4x·")],
 1: [("live-read r918：","live-read r920：")],
 2: [("波号 218=注册表 W217 席后首个自由号","波号 219=注册表 W218 席后首个自由号"),
     ("r917 窗实跑：origin inbox/processed/ 零 W218 席位外机命中","r919 窗实跑：origin inbox/processed/ 零 W219 席位外机命中"),
     ("perpetual_faces.py 零 218 行","perpetual_faces.py 零 219 行"),
     ("perpetual_faces_n1.py 零 PERPETUAL-N1-W218 WAVE_CONFIGS","perpetual_faces_n1.py 零 PERPETUAL-N1-W219 WAVE_CONFIGS"),
     ("origin 零 PERPETUAL_N1_W218_PREREG.md","origin 零 PERPETUAL_N1_W219_PREREG.md")],
 3: [("+W214=bm-c r910 五面冻结（4664900c8）+引擎自燃 12/12+r911 finalize one-pass 已落（K=468,720·账本头 894,589 机读·n1_w214_results.json·05:2x）+W215=bm-c r912 五面冻结（1e71c3b93）+引擎自燃 12/12+r913 finalize one-pass 已落（K=470,920·账本头 896,789 机读·n1_w215_results.json·06:1x）+W216=bm-c r914 五面冻结（0b3c489f0）+引擎自燃 12/12+r915 finalize one-pass 已落（K=473,120·账本头 898,989 机读·n1_w216_results.json·06:5x）+W217=bm-c r916 五面冻结（ad011fee2）+引擎自燃 12/12+r917 finalize one-pass 已落（K=475,320·账本头 901,189 机读·n1_w217_results.json·08:1x）——本波上游链=W1..W217 finalize 全落地","+W@L14@=bm-c r910 五面冻结（4664900c8）+引擎自燃 12/12+r911 finalize one-pass 已落（K=468,720·账本头 894,589 机读·n1_w@L14@_results.json·05:2x）+W@L15@=bm-c r912 五面冻结（1e71c3b93）+引擎自燃 12/12+r913 finalize one-pass 已落（K=470,920·账本头 896,789 机读·n1_w@L15@_results.json·06:1x）+W@L16@=bm-c r914 五面冻结（0b3c489f0）+引擎自燃 12/12+r915 finalize one-pass 已落（K=473,120·账本头 898,989 机读·n1_w@L16@_results.json·06:5x）+W@L17@=bm-c r916 五面冻结（ad011fee2）+引擎自燃 12/12+r917 finalize one-pass 已落（K=475,320·账本头 901,189 机读·n1_w@L17@_results.json·08:1x）+W218=bm-c r918 五面冻结（9afb0b1d7）+引擎自燃 12/12+r919 finalize one-pass 已落（K=477,520·账本头 903,389 机读·n1_w218_results.json·09:1x）——本波上游链=W1..W218 finalize 全落地")],
 4: [("本机席位公示=MSG-20261012-0830-bmc-w218-seat 已推 origin 8a4c1857a 先于本冻结【r565 律·席位先行·r917 窗】；下游 W219+ 投影见 §5.5（probe 机证 leg4·W219 freezer 承接面）】。","本机席位公示=MSG-20261012-0916-bmc-w219-seat 已推 origin 7615985e8 先于本冻结【r565 律·席位先行·r919 窗】；下游 W220+ 投影见 §5.5（probe 机证 leg4·W220 freezer 承接面）】。")],
 5: [("W2..W217 全注册在冻结时点成立","W2..W218 全注册在冻结时点成立")],
 6: [("results/_w218bmc_20261012_probe_receipt.json","results/_w219bmc_20261012_probe_receipt.json")],
 7: [("A-ext seed=494_404..496_403","A-ext seed=496_604..498_603"),
     ("A 面=FIRST-CLEAN past prior-wave B 阶梯第七十八例","A 面=FIRST-CLEAN past prior-wave B 阶梯第七十九例"),
     ("A 面算术继续带 494_204..496_203（自注册 W217 A 尾 494_203 续）在其起点即被 W217 注册 B 带 494_204..494_403 **拒**（W217 席位 leg4 投影+其 probe 所预言+强制）→ 诚实前向走 **1 hop** 落 **494_404..496_403**","A 面算术继续带 496_404..498_403（自注册 W218 A 尾 496_403 续）在其起点即被 W218 注册 B 带 496_404..496_603 **拒**（W218 席位 leg4 投影+其 probe 所预言+强制）→ 诚实前向走 **1 hop** 落 **496_604..498_603**"),
     ("A base==前波 B 尾+1（494_403+1）机检关系","A base==前波 B 尾+1（496_603+1）机检关系"),
     ("A-hops-prior-B 阶梯几何第七十八例（E36 卡）","A-hops-prior-B 阶梯几何第七十九例（E36 卡）"),
     ("A_semantics 机读序数=SEVENTY-EIGHTH（第七十八例）","A_semantics 机读序数=SEVENTY-NINTH（第七十九例）")],
 8: [("B-ext exit seed=496_404..496_603","B-ext exit seed=498_604..498_803"),
     ("B 面 naive first-clean 继续带 494_404..494_603 在注册宇宙上 CLEAN 但**落在本波 A 窗 494_404..496_403 内**","B 面 naive first-clean 继续带 496_604..496_803 在注册宇宙上 CLEAN 但**落在本波 A 窗 496_604..498_603 内**"),
     ("B 带本波 A 窗保留走 **1 hop** 落 **496_404..496_603**","B 带本波 A 窗保留走 **1 hop** 落 **498_604..498_803**"),
     ("B base==本波 A 尾+1（496_403+1）机检关系","B base==本波 A 尾+1（498_603+1）机检关系"),
     ("**W217 席位 leg4 投影承接面注记兑现**：投影预言 W218 须在 post-W217 注册宇宙重 derive 且 derive B 时预留本波 A 窗","**W218 席位 leg4 投影承接面注记兑现**：投影预言 W219 须在 post-W218 注册宇宙重 derive 且 derive B 时预留本波 A 窗")],
 9: [("R250：W218 带从未指派","R250：W219 带从未指派")],
 10: [("A base=494404 span=2000 checked=2000 verdict=FREE / B base=496404 span=200 checked=200 verdict=FREE","A base=496604 span=2000 checked=2000 verdict=FREE / B base=498604 span=200 checked=200 verdict=FREE")],
 11: [("扫描面=pre-W218 全二百一十五行注册 N1 带表（表尾 W217 行·probe leg0 机证 215 行 live 单态 owner rows 207）","扫描面=pre-W219 全二百一十六行注册 N1 带表（表尾 W218 行·probe leg0 机证 216 行 live 单态 owner rows 208）")],
 12: [("W2..W217 落地 runner","W2..W218 落地 runner")],
 13: [("selftest W218 face 将随五面冻结落地验证","selftest W219 face 将随五面冻结落地验证")],
 14: [("本件与 results/_w218bmc_freeze_edits.py","本件与 results/_w219bmc_freeze_edits.py"),
     ("按 _w217bmc_freeze_edits.py 模板派生","按 _w2@T18@bmc_freeze_edits.py 模板派生"),
     ("gate0.5 自查 W217 行+W217 finalize 件在场","gate0.5 自查 W218 行+W218 finalize 件在场"),
     ("estate 提取面=本机 W217 块物理字节","estate 提取面=本机 W218 块物理字节"),
     ("（r916/W217 先例 freeze-prep 同式","（r918/W218 先例 freeze-prep 同式")],
 15: [("- 批名=**PERPETUAL-N1-W218**。","- 批名=**PERPETUAL-N1-W219**。")],
 16: [("**W1..W217 N1 finalize 已全部落地**","**W1..W218 N1 finalize 已全部落地**"),
     ("净账本锚头 **901,189**·K=475,320 合并池·n1_w217_results.json 机读·W217 finalize one-pass bm-c r917 窗 08:1x（W217 面完整性=12/12 shards consumed+finalize audit finalize_only=true 收口·r916 freeze ad011fee2","净账本锚头 **903,389**·K=477,520 合并池·n1_w218_results.json 机读·W218 finalize one-pass bm-c r919 窗 09:1x（W218 面完整性=12/12 shards consumed+finalize audit finalize_only=true 收口·r918 freeze 9afb0b1d7")],
 17: [("累计 null 池=475,320+2,200（本波）=**477,520 投影**","累计 null 池=477,520+2,200（本波）=**479,720 投影**")],
 18: [("（本机席位公示 MSG-20261012-0830-bmc-w218-seat 已推 origin 8a4c1857a r565 律·probe W219+ 投影 A 496_404..498_403 / B 496_604..496_803","（本机席位公示 MSG-20261012-0916-bmc-w219-seat 已推 origin 7615985e8 r565 律·probe W220+ 投影 A 498_604..500_603 / B 498_804..499_003"),
     ("投影 B 落投影 A 窗内·W218 B 带 496_404..496_603 注册后将拒 naive W219 A 窗=阶梯 A-hops-prior-B 第七十九例——**W219 freezer 承接面强制注记：须在 post-W218 宇宙重 derive 且 derive B 时预留本波 A 窗","投影 B 落投影 A 窗内·W219 B 带 498_604..498_803 注册后将拒 naive W220 A 窗=阶梯 A-hops-prior-B 第八十例——**W220 freezer 承接面强制注记：须在 post-W219 宇宙重 derive 且 derive B 时预留本波 A 窗")],
 19: [("T-2026-10-01-141 s1 引擎线第 208 波【bm-c 第四十八枚自有波【机面 derive：probe leg0 bmc_ordinal=47 live face（r917 窗 live 单态计法）——freeze 时 live derive bm-c rows 47+候选=第 48 枚 EXACT","T-2026-10-01-141 s1 引擎线第 209 波【bm-c 第四十九枚自有波【机面 derive：probe leg0 bmc_ordinal=48 live face（r919 窗 live 单态计法）——freeze 时 live derive bm-c rows 48+候选=第 49 枚 EXACT"),
     ("波号=注册表 W217 席后首个自由号·单态零席位空档于冻结时点成立；中位公示 MSG-20261012-0830-bmc-w218-seat 先推 origin 8a4c1857a r565 律","波号=注册表 W218 席后首个自由号·单态零席位空档于冻结时点成立；中位公示 MSG-20261012-0916-bmc-w219-seat 先推 origin 7615985e8 r565 律")],
 20: [("本窗 free RAM ~0.8GB","本窗 free RAM " + RAM_GB + "GB"),
     ("W206/W211/W212/W213/W214/W215/W216/W217 低 RAM 实烧先例","W206/W211/W212/W213/W@L14@/W@L15@/W@L16@/W@L17@/W218 低 RAM 实烧先例")],
 21: [("复读自见 W218 行并点火自烧","复读自见 W219 行并点火自烧")],
 22: [("--prereg research/PERPETUAL_N1_W218_PREREG.md","--prereg research/PERPETUAL_N1_W219_PREREG.md")],
 23: [("v2..W217 落地）","v2..W218 落地）")],
 24: [("entry rng seed=**494_404+j**","entry rng seed=**496_604+j**"),
     ("法典 §4 W218 行 A=494_404..496_403","法典 §4 W219 行 A=496_604..498_603"),
     ("阶梯第七十八例**：算术续带 494_204..496_203 起点即被 W217 注册 B 带 494_204..494_403 拒→1 hop 落 494_404..496_403","阶梯第七十九例**：算术续带 496_404..498_403 起点即被 W218 注册 B 带 496_404..496_603 拒→1 hop 落 496_604..498_603")],
 25: [("entry rng=**494_404+j**","entry rng=**496_604+j**"),
     ("exit rng=**496_404+j**","exit rng=**498_604+j**"),
     ("法典 §4 W218 行 B=496_404..496_603","法典 §4 W219 行 B=498_604..498_803"),
     ("B 算术续带 494_404..494_603 在注册宇宙上 CLEAN 但落在本波 A 窗 494_404..496_403 内","B 算术续带 496_604..496_803 在注册宇宙上 CLEAN 但落在本波 A 窗 496_604..498_603 内"),
     ("保留走落 496_404..496_603","保留走落 498_604..498_803"),
     ("与 W217 席位 leg4 投影承接面注记兑现收敛","与 W218 席位 leg4 投影承接面注记兑现收敛")],
 26: [("（selftest 强制）：W218 带与 v1 在用带","（selftest 强制）：W219 带与 v1 在用带")],
 27: [("W2..W217 带（冻结时点全注册单态）","W2..W218 带（冻结时点全注册单态）")],
 28: [("本波机验 ADMIT 回执在场=_w218bmc_20261012 探针窗","本波机验 ADMIT 回执在场=_w219bmc_20261012 探针窗")],
 29: [("selftest W218 face（A=first-clean past prior-wave B 恒等·B=first-clean past own-wave A 恒等+同窗互斥断言·W217 行 parity 腿","selftest W219 face（A=first-clean past prior-wave B 恒等·B=first-clean past own-wave A 恒等+同窗互斥断言·W218 行 parity 腿")],
 30: [("从**本机 W217 块物理字节**提取","从**本机 W218 块物理字节**提取"),
     ("W217 块的 W216 leg（1 行）不入 estate 路径·提取后新增 W216+W217 leg 构成 W218 块 parity 76 行（W138..W206+W211+W212+W213+W214+W215+W216+W217）","W@L17@ 块的 W@L16@ leg（1 行）不入 estate 路径·提取后新增 W@L16@+W@L17@ leg 构成 W219 块 parity 77 行（W138..W206+W211+W212+W213+W@L14@+W@L15@+W@L16@+W@L17@+W218）")],
 31: [("起草窗实流 W1..W217 已落账 475,320 实测","起草窗实流 W1..W218 已落账 477,520 实测")],
 32: [("batch_name=\"PERPETUAL-N1-W218\", batch_trials=2200, file_name=\"results/perpetual_faces/n1_w218_results.json\"","batch_name=\"PERPETUAL-N1-W219\", batch_trials=2200, file_name=\"results/perpetual_faces/n1_w219_results.json\"")],
 33: [("（起草窗实况注记：**W1..W217 N1 finalize 已全部落地**——净账本锚头 901,189·**K=475,320 合并池**·**零在飞上游席——本波 §5 预测键=**W217 实测值**【results/perpetual_faces/n1_w217_results.json·N1 面最新已落账键·08:1x finalize one-pass】。","（起草窗实况注记：**W1..W218 N1 finalize 已全部落地**——净账本锚头 903,389·**K=477,520 合并池**·**零在飞上游席——本波 §5 预测键=**W218 实测值**【results/perpetual_faces/n1_w218_results.json·N1 面最新已落账键·09:1x finalize one-pass】。")],
 34: [("1. W218-only mu 与累计池 merged mu（W217 实测键 **−0.09275152**·K=475,320 合并池·W217-only 实测 **−0.10123773**）差异 **|Δ|<0.02**（W2..W217 共二百一十五面实测 mu 稳定先例·单波跨键微；W217-only vs merged 实差 0.0085 在带内）。","1. W219-only mu 与累计池 merged mu（W218 实测键 **−0.09278311**·K=477,520 合并池·W218-only 实测 **−0.09960895**）差异 **|Δ|<0.02**（W2..W218 共二百一十六面实测 mu 稳定先例·单波跨键微；W218-only vs merged 实差 0.0068 在带内）。")],
 35: [("键 **0.24508756**=W217 合并池实测）。","键 **0.24510530**=W218 合并池实测）。")],
 36: [("3. A 档 full_sharpe_p95 与 W217 A 档 p95（**0.3074** 实测锚）差 **<0.05**（门标注法 W5..W217 先例","3. A 档 full_sharpe_p95 与 W218 A 档 p95（**0.3037** 实测锚）差 **<0.05**（门标注法 W5..W218 先例")],
 37: [("W136..W217 先例链披露","W136..W218 先例链披露"),
     ("键 W217 实测 K-lift **−0.0001**·line_merged@K475,320 **1.1906**·line_pre_w217 1.1907·n_eff_held_equal 898,989","键 W218 实测 K-lift **+0.0001**·line_merged@K477,520 **1.1908**·line_pre_w218 1.1907·n_eff_held_equal 901,189"),
     ("se_mu 收窄链 …→W209 0.000362→W211 0.000361→W212 0.000360→W213 0.000359→W214 0.000358→W215 0.000357→W216 0.000356→W217 **0.000355**】","se_mu 收窄链 …→W209 0.000362→W211 0.000361→W212 0.000360→W213 0.000359→W@L14@ 0.000358→W@L15@ 0.000357→W@L16@ 0.000356→W@L17@ **0.000355**→W218 **0.000355**】")],
 38: [("5. **W219+ 投影（probe 机证 leg4·下波冻结方复核非转抄 r587 律）**：A naive first-clean 496_404..498_403 CLEAN（hops=0·pre-W218 宇宙）；B naive first-clean **496_604..496_803 CLEAN**（hops=0）——**naive B 落在 naive A 窗内**（W141 同窗互斥先例适用于 W219：W219 冻结方必须在 post-W218 注册宇宙重 derive 且 derive B 时预留本波 A 窗——leg2 律/E36 卡）；**W218 B 带 496_404..496_603 注册后将拒 naive W219 A 窗**——W219 A 重 derive 同强制（越过 W218 B 带·阶梯 A-hops-prior-B 第七十九例）；verify at W219 prereg","5. **W220+ 投影（probe 机证 leg4·下波冻结方复核非转抄 r587 律）**：A naive first-clean 498_604..500_603 CLEAN（hops=0·pre-W219 宇宙）；B naive first-clean **498_804..499_003 CLEAN**（hops=0）——**naive B 落在 naive A 窗内**（W141 同窗互斥先例适用于 W220：W220 冻结方必须在 post-W219 注册宇宙重 derive 且 derive B 时预留本波 A 窗——leg2 律/E36 卡）；**W219 B 带 498_604..498_803 注册后将拒 naive W220 A 窗**——W220 A 重 derive 同强制（越过 W219 B 带·阶梯 A-hops-prior-B 第八十例）；verify at W220 prereg")],
 39: [(" --wave 218/finalize --wave 218"," --wave 219/finalize --wave 219")],
 40: [("【n1_w218/ 分片计数增长·唯一点火证据·r325 律】","【n1_w219/ 分片计数增长·唯一点火证据·r325 律】")],
 41: [("`results/p2cal_ext/n1_w218/shard-<k>-of-12.json`","`results/p2cal_ext/n1_w219/shard-<k>-of-12.json`")],
 42: [("`results/perpetual_faces/n1_w218_results.json`（finalize 合并件·顶层 evidence_cutoff·cutoff_meta·audit 段·K-lift 对照；finalize 键序前置=**起草窗零在飞上游席（W1..W217 全落）**","`results/perpetual_faces/n1_w219_results.json`（finalize 合并件·顶层 evidence_cutoff·cutoff_meta·audit 段·K-lift 对照；finalize 键序前置=**起草窗零在飞上游席（W1..W218 全落）**")],
 43: [("engine_owner==bm-c 47 行注册〔冻结时点〕+ 本候选","engine_owner==bm-c 48 行注册〔冻结时点〕+ 本候选")],
 44: [("段——r917 W217 §7 范式）","段——r919 W218 §7 范式）")],
 45: [("（占位·finalize 同窗回填：§5.5 W219+ 投影承接机证/宝藏与方法论捕获问/诚实披露面——r917 W217 §8 范式）","（占位·finalize 同窗回填：§5.5 W220+ 投影承接机证/宝藏与方法论捕获问/诚实披露面——r919 W218 §8 范式）")],
}

# ---------- build + apply W219 pairs ----------
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
# Pairs covered every W218 self face (each count==1 asserted). Remaining
# "W218" tokens = pair-written legit refs (chain W218 leg, W1..W218 scope)
# which must STAY W218 -- mask, then age one-wave-older W217 refs to W218,
# then restore. @L14@/@L15@/@L16@/@L17@/@T18@ hold heritage tokens immune.
t = t.replace("n1_w218_results", "n1_@u_w@_results")   # protect pair-written upstream file refs
t = t.replace("PERPETUAL-N1-W218", "PERPETUAL-N1-W219")
t = t.replace("PERPETUAL_N1_W218", "PERPETUAL_N1_W219")
t = t.replace("n1_w218", "n1_w219")
t = t.replace("_w218bmc", "_w219bmc")
t = t.replace("W218", "@U_W@")
t = t.replace("W217", "W218")
t = t.replace("n1_w217", "n1_w218")
t = t.replace("PERPETUAL_N1_W217", "PERPETUAL_N1_W218")
t = t.replace("_w217bmc", "_w218bmc")
t = t.replace("@u_w@", "w218")
t = t.replace("@U_W@", "W218")
t = t.replace("@L14@", "214")
t = t.replace("@L15@", "215")
t = t.replace("@L16@", "216")
t = t.replace("@L17@", "217")
t = t.replace("@T18@", "18")

# ---- stale-token checklist (must all be ZERO) ----
STALE = ["494_404..496_403", "494_204..496_203", "494_204..494_403", "494_404..494_603",
         "494404", "第 216 枚", "SEVENTY-EIGHTH", "第七十八例", "第四十八枚",
         "207 注册在册", "bmc_ordinal=47", "r917 窗 W217 注册后", "0.3074", "−0.09275152",
         "−0.10123773", "0.24508756", "0830-bmc", "8a4c1857a",
         "08:1x（W217 面完整性", "08:1x finalize one-pass】", "二百一十五行", "r918 freeze 窗·2026-10-12 08:4x", "第 208 波",
         "n_eff_held_equal 898,989", "1.1906", "0.0085", "=**477,520 投影**", "engine_owner==bm-c 47 行",
         "prose 47th", "r916 freeze receipt 47th", "第 48 枚 EXACT", "pre-W218 宇宙",
         "W219 freezer 承接面", "r917 W217 §7 范式",
         "W218 B 带 496_404..496_603 注册后将拒 naive W219",
         "（494_403+1）", "（496_403+1）", "波号 218=", "A base=494404", "n1_w218/ 分片计数增长",
         'batch_name="PERPETUAL-N1-W218"']
# NOTE: "496_404..498_403" / "496_604..496_803" are NOT stale in the W219
# face -- they are the fresh A/B arithmetic-continuation bands (SUB[7]/SUB[8]
# /SUB[24]/SUB[25] write them); the §5.5 projection instances were consumed
# by pair 38. Same digits, different semantics (probed live 09:2x).
# "496_404..496_603" is NOT stale -- it is the fresh upstream refusing band
# (>=2 asserted below). "n1_w218_results.json" file refs stay (upstream
# legs) while "n1_w218/ 分片计数增长" IS stale (self shard face now n1_w219).
for s in STALE:
    c = t.count(s)
    if c:
        import re as _re
        for m in _re.finditer(_re.escape(s), t):
            print(f"--- STALE[{s}] ctx ---")
            print(t[max(0, m.start()-160):m.end()+80].replace("\n", " | "))
    assert c == 0, f"STALE token survives x{c}: {s}"

# ---- new-face presence checks ----
NEW = ["PERPETUAL-N1-W219", "第 217 枚", "496_604..498_603", "498_604..498_803",
       "SEVENTY-NINTH", "第七十九例", "第八十例", "第四十九枚",
       "903,389", "477,520", "479,720", "901,189",
       "MSG-20261012-0916-bmc-w219-seat", "7615985e8",
       "bmc_ordinal=48", "n1_w219_results.json", "0.3037", "−0.09278311",
       "−0.09960895", "0.24510530", "n_eff_held_equal 901,189", "0.000355",
       "1.1907", "1.1908", "第 209 波", "498_604..500_603", "498_804..499_003",
       "496_404..498_403", "496_604..496_803",
       "0.0068", "9afb0b1d7", "第 49 枚 EXACT", "W220 freezer 承接面",
       "r919 W218 §7 范式"]
for s in NEW:
    assert t.count(s) >= 1, f"NEW token missing: {s}"
# in-band sanity: own A band appears as the ADMIT face (>=4), own B band too
assert t.count("496_604..498_603") >= 4 and t.count("498_604..498_803") >= 4
# upstream W218 refusing band appears in A-face prose (band-facts + §3A)
assert t.count("496_404..496_603") >= 2
# chain-history legs present exactly once each (heritage restored verbatim)
assert t.count("+W213=bm-c r908 五面冻结（a24069f4c）") == 1
assert t.count("+W214=bm-c r910 五面冻结（4664900c8）") == 1
assert t.count("+W215=bm-c r912 五面冻结（1e71c3b93）") == 1
assert t.count("+W216=bm-c r914 五面冻结（0b3c489f0）") == 1
assert t.count("+W217=bm-c r916 五面冻结（ad011fee2）") == 1
assert t.count("+W218=bm-c r918 五面冻结（9afb0b1d7）") == 1
assert t.count("n1_w213_results.json·04:2x") == 1
assert t.count("n1_w214_results.json·05:2x") == 1
assert t.count("n1_w215_results.json·06:1x") == 1
assert t.count("n1_w216_results.json·06:5x") == 1
assert t.count("n1_w217_results.json·08:1x") == 1
assert t.count("n1_w218_results.json·09:1x") == 1
# healed RAM list + estate note + se_mu chain present
assert t.count("W206/W211/W212/W213/W214/W215/W216/W217/W218 低 RAM 实烧先例") == 1
assert t.count("（W138..W206+W211+W212+W213+W214+W215+W216+W217+W218）") == 1
assert t.count("按 _w218bmc_freeze_edits.py 模板派生") == 1
assert t.count("→W213 0.000359→W214 0.000358→W215 0.000357→W216 0.000356→W217 **0.000355**→W218 **0.000355**】") == 1

out = r"research\PERPETUAL_N1_W219_PREREG.md"
open(out, "wb").write(t.encode("utf-8"))
print("W219 prereg derived OK:", out)
print("bytes:", len(t.encode("utf-8")), "| sha16:", hashlib.sha256(t.encode("utf-8")).hexdigest()[:16])
print("W218(upper) refs (upstream, expected 40+):", t.count("W218"), "| W219 self:", t.count("W219"))
