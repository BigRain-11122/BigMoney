# -*- coding: utf-8 -*-
"""r919 bm-a W199 per-wave prereg build (two-gen eval chain: old sides =
AST-extracted BACK values of results/_r916bma_w198_prereg_build.py, zero
transcription r587; live facts re-asserted at run time per r587).
Src = results/_r919bma_w199_prereg_src.txt (W198 prereg freeze-time blob
82b881a4f, byte-verbatim binary extract, r877 law 4).  Output CRLF
(r370 law).  buildgen three laws honored: AST no-exec prior-gen
(ast.literal_eval only), DRY whole-file gate zero-write-first, U+2212
display forms (r833)."""
import ast
import io
import json
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"
GIT = r"C:\Program Files\Git\cmd\git.exe"
SRC_BLOB_COMMIT = "82b881a4f"   # W198 prereg BUILD commit = freeze-time blob
SRC = "results/_r919bma_w199_prereg_src.txt"
OUT = "research/PERPETUAL_N1_W199_PREREG.md"
R916_BUILD = "results/_r916bma_w198_prereg_build.py"
M = "\u2212"
CNW = getattr(subprocess, "CREATE_NO_WINDOW", 0)


def git(*a):
    r = subprocess.run([GIT, "-C", ROOT] + list(a), capture_output=True,
                       creationflags=CNW)
    return r.stdout.decode("utf-8", errors="replace").strip()


# ---- extract the freeze-time src blob (r877 law 4, byte-verbatim) ----
blob = subprocess.run(
    [GIT, "-C", ROOT, "show", SRC_BLOB_COMMIT + ":research/PERPETUAL_N1_W198_PREREG.md"],
    capture_output=True, creationflags=CNW).stdout
with open(ROOT + "\\" + SRC.replace("/", "\\"), "wb") as fh:
    fh.write(blob)
assert b"\r\n" not in blob, "src blob expected LF (git-normalized)"
assert blob.decode("utf-8").count("SEED_REGISTRY \u5168\u952e 195 \u503c") == 1

# ---- live fact re-asserts (machine numbers, zero transcription) ----
subprocess.run([GIT, "-C", ROOT, "fetch", "origin"], capture_output=True,
               creationflags=CNW)
probe = json.load(open(r"results/_r918bma_w199_probe_receipt.json",
                      encoding="utf-8"))
assert probe["verdict"] == "ADMIT" and probe["bands"] == {
    "A": "452604_454603", "B": "454604_454803"}, probe
leg0 = probe["legs"]["leg0"]
assert leg0["rows"] == 196 and leg0["tail"] == "W198", leg0
assert leg0["ordinal"] == 189 and leg0["bma_ordinal"] == 114, leg0
assert leg0["owner_rows"] == 188 and leg0["bma_rows"] == 113, leg0
assert leg0["w198_ledger_head"] == 849945, leg0
leg1 = probe["legs"]["leg1"]
assert leg1["A"] == [452604, 454603] and leg1["B"] == [454604, 454803], leg1
assert leg1["hops_A"] == 1 and leg1["hops_B"] == 1
assert leg1["ARITH_A"] == [452404, 454403], leg1
assert leg1["ARITH_B"] == [452604, 452803], leg1
assert "FIFTY-NINTH" in leg1["A_semantics"], leg1
assert probe["legs"]["leg2"]["conflicts"] == 0
assert probe["legs"]["leg3"]["origin_vacancy"] is True
leg4 = probe["legs"]["leg4"]
assert leg4["W200p_A"] == "454604..456603", leg4
assert leg4["W200p_B"] == "454804..455003", leg4
assert leg4["hops_A"] == 0 and leg4["hops_B"] == 0
assert leg4["W200p_B_lands_inside_W200p_A"] is True

res = json.load(open(r"results/perpetual_faces/n1_w198_results.json",
                     encoding="utf-8"))
npc = res["null_pool_cumulative"]
merged = npc["merged"]
assert merged["n_values"] == 433520, merged
assert merged["mu"] == -0.09280009941871194, merged
assert merged["sigma"] == 0.24509712676076273, merged
assert npc["w198_only"]["mu"] == -0.09712509090909091, npc
assert npc["se_mu_at_k433520"] == 0.000372, npc
assert npc["mu_delta_w198_vs_w197ext"] == -0.01596, npc
assert res["science_gates"]["ledger"]["total"] == 849945
kl = res["skill_line_v2_k_lift"]
assert kl["n_eff_held_equal"] == 847745, kl
assert kl["line_pre_w198"] == 1.1878 and kl["line_merged_433520"] == 1.1878
assert kl["line_delta_k_lift"] == 0.0, kl
assert res["families"]["A_random_engine_exit"]["full_sharpe_p95"] == 0.3279
# display-form derivation asserts (zero hand-rounding)
assert "%.4f" % merged["mu"] == "-0.0928"
assert "%.4f" % npc["w198_only"]["mu"] == "-0.0971"
assert "%.6f" % merged["sigma"] == "0.245097"

_vac = git("log", "origin/main", "--format=%h", "-n", "1", "-S",
           '199: {"a": (452_604', "--", "scripts/perpetual_faces.py")
assert _vac == "", "W199 five-face already on origin?!"
_fin198 = git("ls-tree", "origin/main",
              "results/perpetual_faces/n1_w198_results.json")
assert _fin198 != "", "W198 finalize NOT landed -- anchor must roll r590!"
_fin197 = git("ls-tree", "origin/main",
              "results/perpetual_faces/n1_w197_results.json")
assert _fin197 != "", "W197 finalize NOT landed -- chain integrity!"
_seat = git("log", "origin/main", "--format=%h", "-n", "1",
            "--diff-filter=A", "--",
            "fleet/inbox/MSG-2026-10-09-1507-bma-w199-seat.md")
assert _seat == "3a875bf43", _seat
_anc = subprocess.run([GIT, "-C", ROOT, "merge-base", "--is-ancestor",
                      "3a875bf43", "origin/main"], capture_output=True,
                      creationflags=CNW)
assert _anc.returncode == 0, "seat sha not ancestor of origin/main"

sys.path.insert(0, "scripts")
sys.path.insert(0, ".")
import science_gates as _sg  # noqa: E402
REG_N = len(_sg.SEED_REGISTRY)
assert REG_N >= 195, "SEED_REGISTRY below freeze face: %d" % REG_N
_ws = [int(x) for x in _sg.SEED_REGISTRY.values() if isinstance(x, int)]
assert not [s for s in _ws if 452604 <= s <= 454803], "band overlap"

# ---- two-gen eval: old sides = r916 BACK (AST, no exec) ----
# r916 BACK carries '@CHAIN@': CHAIN_NEW (a Name) -- resolve via the
# r914 BACK chain literal + the r916 append constant (zero transcription).
_r916_src = io.open(R916_BUILD, encoding="utf-8").read()
_tree = ast.parse(_r916_src)
OLD_BACK = None
for _node in ast.walk(_tree):
    if (isinstance(_node, ast.Assign) and len(_node.targets) == 1
            and isinstance(_node.targets[0], ast.Name)
            and _node.targets[0].id == "BACK"
            and isinstance(_node.value, ast.Dict)):
        OLD_BACK = {}
        for k, v in zip(_node.value.keys, _node.value.values):
            key = ast.literal_eval(k)
            if isinstance(v, ast.Constant):
                OLD_BACK[key] = ast.literal_eval(v)
            else:
                assert isinstance(v, ast.Name) and v.id == "CHAIN_NEW", \
                    "unexpected non-literal BACK value for %s" % key
                OLD_BACK[key] = None  # resolved below
        break
assert OLD_BACK and len(OLD_BACK) == 40, "r916 BACK eval-parse failed: %s" % (
    len(OLD_BACK) if OLD_BACK else 0)
# resolve CHAIN_NEW = _chain_old + "<append>" where _chain_old = r914 chain
_append = None
for _node in ast.walk(_tree):
    if (isinstance(_node, ast.Assign) and len(_node.targets) == 1
            and isinstance(_node.targets[0], ast.Name)
            and _node.targets[0].id == "CHAIN_NEW"
            and isinstance(_node.value, ast.BinOp)
            and isinstance(_node.value.op, ast.Add)):
        _append = ast.literal_eval(_node.value.right)
assert _append == "\uff1bW197=bm-a r915 freeze\uff08522a0aef5\uff09", _append
R914_BUILD = "results/_r914bma_w197_prereg_build.py"
_r914_src = io.open(R914_BUILD, encoding="utf-8").read()
_r914_tree = ast.parse(_r914_src)
_chain_914 = None
for _node in ast.walk(_r914_tree):
    if (isinstance(_node, ast.Assign) and len(_node.targets) == 1
            and isinstance(_node.targets[0], ast.Name)
            and _node.targets[0].id == "BACK"
            and isinstance(_node.value, ast.Dict)):
        for k, v in zip(_node.value.keys, _node.value.values):
            if ast.literal_eval(k) == "@CHAIN@":
                assert isinstance(v, ast.Constant), "r914 chain not literal"
                _chain_914 = ast.literal_eval(v)
assert _chain_914 and _chain_914.endswith(
    "\uff1bW196=bm-a r912 freeze\uff0802cf6b44d\uff09"), \
    "r914 chain tail unexpected: %r" % (_chain_914 or "")[-80:]
OLD_BACK["@CHAIN@"] = _chain_914 + _append

_chain_old = OLD_BACK["@CHAIN@"]
assert _chain_old.endswith("\uff1bW197=bm-a r915 freeze\uff08522a0aef5\uff09"), \
    "r916 chain tail unexpected: %r" % _chain_old[-80:]
CHAIN_NEW = _chain_old + "\uff1bW198=bm-a r916 freeze\uff0882b881a4f\uff09"

BACK = {
    '@CHAIN@': CHAIN_NEW,
    '@TITLE@': '# PERPETUAL-N1-W199 预注册 · N1 nulls-deepening 泵第 197 枚（never-dry 常供给例波·波序号连续·机面 derive：engine_owner 行 188 注册在册+W197/W198 finalize 已落账·anchor 滚动已兑现（r590）+本候选=bm-a 第一百一十四枚自有波【bm-a r919·buildgen 血统 r830/r833/r877/r908/r911/r914/r916 承袭·干净窗 anchor=W198 实测 r590 滚动兑现】）',
    '@SEATBLOCK@': '【本冻结窗 fetch 实核表尾时 W199 号位空档·rg 行 WAVE_CONFIGS+prereg 路径三查+origin ls-tree vacancy 机证（本窗 probe leg3 实跑）；全 inbox/processed/ W199 席位零外机命中；**W197=bm-a r915 五面冻结+finalize one-pass 同落 522a0aef5 在册（dead-session 冻结 13:0x+引擎自烧 12/12 13:01..13:12 先落·estate absorbed per r899·账本 847,745 EXACT 零偏离四连窗·K=431,320 EXACT·四预键 PASS）+W198=bm-a r916 五面冻结 82b881a4f 在册·finalize 已落 origin（r917 one-pass d4ea4b348·账本 849,945 EXACT 零偏离五连窗·K=433,520 EXACT·四预键 4/4 PASS）——起稿窗注册宇宙=W197/W198 注册带在册+双 finalize 落账（N1_BANDS 注册行机器读·probe leg0 机证 196 行表尾 W198）·r918 W199 probe 全腿机证**；本机席位公示=MSG-2026-10-09-1507-bma-w199-seat 已推 origin 3a875bf43 先于本冻结【r565 律·推送窗=r918 seat push 直接快进送达 3a875bf43（payload=seat MSG+W199 pre-seat probe 脚本+回执同推）；self-ack inbox→processed 移位随五面冻结窗收口归档（如实注记）】】',
    '@AFACE@': '本波 **A-ext seed=452_604..454_603**（**A 面=FIRST-CLEAN past prior-wave B 阶梯第五十九例**：A 面算术继续带 452_404..454_403 在其起点即被 W198 注册 B 带 452_404..452_603 **拒**（W198 §5.5 投影+r915 probe leg4 双源预言+强制·r918 probe 回执 A_semantics 机读双兑现）→ 诚实前向走 **1 hop** 落 **452_604..454_603**·**A base==前波 B 尾+1（452_603+1）机检关系**=**A-hops-prior-B 阶梯几何第五十九例（E36 卡）**·非轮转 r587 前向单调断言在走册；序数面如实披露：W198 §5.5 投影预告第五十九例·本窗 probe 回执 A_semantics 机读序数=FIFTY-NINTH（第五十九例）·本件按回执序数面记载非转抄（r587）·投影与回执两读法恒同）',
    '@BFACE@': '**B-ext exit seed=454_604..454_803**（**B 面=FIRST-CLEAN past own-wave A**：B 面算术继续带 452_604..452_803 在声明宇宙上 CLEAN 但**落在本波 A 窗 452_604..454_603 内**（**同窗互斥面 leg2 律·W141 先例**：A 与 B 同一冻结 commit 双注册·互斥断言强制 B 越过本波 A 窗）→ B 带本波 A 窗保留走 **1 hop** 落 **454_604..454_803**·**B base==本波 A 尾+1（454_603+1）机检关系**·hop 链逐跳在 probe 回执；**W198 §5.5 投影+r915 probe leg4 承接面注记兑现**：投影预言 W199 须在 post-W198 注册宇宙重 derive 且 derive B 时预留本波 A 窗——本窗双面兑现·A 被拒+阶梯越带如投影所期·B 同窗互斥保留=投影所期·已如实披露非分叉）',
    '@ANCHOR0@': '起稿窗实况：**W1..W198 N1 finalize 已全部落地**【净账本锚头 **849,945**·K=433,520 合并池·n1_w198_results.json 机读（origin 在册）】；W199=本窗候选（席位已推 3a875bf43）——**零在飞上游席**·anchor=最新已落账键（W198 实测·r590 滚动已兑现：W198 finalize 已落 origin d4ea4b348（r917 one-pass·账本 849,945 EXACT 零偏离·五连窗）·起稿窗干净窗零在飞上游席·r916 同律·无 v1 自爆面）',
    '@S5ANCH@': '（起稿窗实况注记：**W1..W198 N1 finalize 已全部落地**——净账本锚头 849,945·**K=433,520 合并池**·**零在飞上游席（W197/W198 finalize 均已落 origin·ls-tree 机证）**——本波 §5 预测键=**W198 实测值**【results/perpetual_faces/n1_w198_results.json·N1 面最新已落账键·origin 在册机证】',
    '@S55@': '5. **W200+ 投影（probe 机证·下波冻结方复核非转抄 r587 律）**：A first-clean 454_604..456_603 **CLEAN**（hops=0）；B first-clean **454_804..455_003 CLEAN**（hops=0）——**naive B 落在 naive A 窗内**（W141 同窗互斥先例适用于 W200：W200 冻结方必须在 post-W199 注册宇宙重 derive 且 derive B 时预留本波 A 窗——leg2 律/E36 卡）；**W199 B 带 454_604..454_803 注册后将拒 naive W200 A 窗**——W200 A 重 derive 同强制（越过 W199 B 带·阶梯 A-hops-prior-B 继承第六十例）；verify at W200 prereg，hop 链逐跳在 probe 回执',
    '@S51@': '1. W199-only mu 与累计池 merged mu（W198 实测键 **\u22120.0928**·K=433,520 合并池·W198-only 实测 **\u22120.0971**）差异 **|\u0394|<0.02**（W2..W198 共一百九十八面实测 mu 稳定先例·单波跨键微）',
    '@S52@': '2. sigma 相对变化 **<\u00b110%**（同设计同窗·纯抽样波动；键 **0.245097**=W198 合并池实测 0.245097）。',
    '@S53@': '3. A 档 full_sharpe_p95 与 W198 A 档 p95（**0.3279** 实测锚）差 **<0.05**（门标注法 W5..W198 先例：结果知情面仅作机器断言之用·测量面非注册利益）。',
    '@S54@': '4. K-lift 线移动幅度 **\u2264\u00b10.02**（累计池加深零 se_mu 收窄线自 mu/sigma 微调面非质变——W136..W198 先例链披露【W189 +0.0003/W190 \u22120.0001/W191 +0.0001/W192 **\u22120.0002**/W193 **\u22120.0001**/W194 **+0.0000**/W195 **\u22120.0001**/W196 **+0.0001**/W197 **+0.0001**/W198 **+0.0000**·键 W198 实测 K-lift **+0.0000**·line_merged@K433,520 **1.1878**·line_pre 1.1878·n_eff 847,745；se_mu 收窄链 W191 0.000379\u2192W192 0.000378\u2192W193 0.000377\u2192W194 0.000376\u2192W195 0.000375\u2192W196 0.000374\u2192W197 0.000373\u2192W198 **0.000372**】）。',
    '@GATEW2@': '本波机验 ADMIT 回执在场=_r918bma_w199 探针窗（pre-seat probe 单窗·gate 腿合并结构承袭 r812/r820/r823 先例·parity N/A 诚实注记）；selftest W199 face（A=first-clean past prior-wave B 恒等·B=first-clean past own-wave A 恒等+同窗互斥断言·W198 行 parity 腿【r735 测量-实现分叉族防护面：A/B 窗 set-range 针在场】）随五面冻结落地',
    '@ASEED@': 'entry rng seed=**452_604+j**（法典 §4 W199 行 A=452_604..454_603·**FIRST-CLEAN past prior-wave B 阶梯第五十九例**：算术续带 452_404..454_403 起点即被 W198 注册 B 带拒\u21921 hop 落 452_604..454_603·A base==前波 B 尾+1 机检关系·E36 卡·hops=1·ADMIT 回执在场）',
    '@BSEED@': 'exit rng=**454_604+j**（法典 §4 W199 行 B=454_604..454_803·**FIRST-CLEAN past own-wave A**：B 算术续带 452_604..452_803 在声明宇宙上 CLEAN 但落在本波 A 窗 452_604..454_603 内\u2192**同窗互斥面 leg2 律·W141 先例**强制 B 越本波 A 窗\u2192保留走落 454_604..454_803·hops=1·**B base==本波 A 尾+1 机检关系**·非轮转 r587·hop 链逐跳在 probe 回执·与 W198 §5.5 投影+r915 probe leg4 承接面注记兑现收敛·ADMIT 回执在场）',
    '@ENGNOTE@': '**本冻结=buildgen emission 链（r830/r833/r877/r908/r911/r914/r916 血统承袭·TOK 两相 vmap+DRY 全文件门零写入先行+U+2212 显示形·五腿探针回执在场为准·anchor=W198 实测 r590 滚动兑现·selftest W199 face 将随五面冻结落地验证）。**',
    '@CLAIM@': '- 认领：never-dry 常供给例波（TRIAL_LABOR_LAW §4·板空/池饱/无在飞判决批=默认续跑下一波——本机 r918 席位 MSG-2026-10-09-1507-bma-w199-seat 已推 origin 3a875bf43（r918 seat push·r565 律）·probe W200+ 投影 A 454_604..456_603 / B 454_804..455_003 **naive-B-inside-naive-A re-derive 强制注记+同窗互斥预披露**（投影 B 落投影 A 窗内·W199 B 带 454_604..454_803 注册后将拒 naive W200 A 窗=阶梯 A-hops-prior-B 继承第六十例待 W200 注册宇宙复核）。表尾后新首个自由号自领·r918 probe 单跑兑现注记（本窗冻结消费）；O-20260924-1730 CEO 即时律（认领与开动同轮·禁排未来轮次）；T-2026-10-01-141 s1 引擎线第 189 波【bm-a 第一百一十四枚自有波【机面 derive：engine_owner==bm-a 行 113+本候选以 probe leg0 机证为准】】。（波号=注册表 W198 席后首个自由号·单态零席位空档；中位公示 MSG-2026-10-09-1507-bma-w199-seat 先推 origin 3a875bf43 r565 律；lane-free；dept:研究）。',
    '@SCANFACE@': '扫描面=pre-W199 全一百九十六行注册 N1 带表（表尾 W198 行·leg0 机证 196 行）',
    '@R250@': 'R250：W199 带从未指派·测量面零结果可锁',
    '@PRCR@': 'results/_r918bma_w199_probe_receipt.json',
    '@RUNNERW@': 'W2..W198 落地 runner 的 wave 参数化复用',
    '@BATCHNAME@': '批名=**PERPETUAL-N1-W199**',
    '@POOL@': '累计 null 池=433,520（W198 落账实测）+2,200（本波）=**435,720 投影**',
    '@MATCOND@': '自见 W199 行并点火自烧',
    '@GATECMD@': '--prereg research/PERPETUAL_N1_W199_PREREG.md',
    '@BENTRY@': 'entry rng=**452_604+j**（与 A[j] 同源配对语义逐字·runner 实证 entry=A_SEED_BASE+j）',
    '@PROBEW@': '本波设计=W2..W198 逐字复用',
    '@DISJ@': 'W199 带与 v1 在用带（10_000..10_099/20_000..20_019）、W1 ext 带（10_100..12_099/20_100..20_299）、W2..W198 带（**全注册单态**）',
    '@POOL4@': '已落账净值（起稿窗实流 W1..W198 已落账 433,520 实测·derive 禁手抄）+本波 2,200',
    '@LEDGER@': 'batch_name="PERPETUAL-N1-W199", batch_trials=2200, file_name="results/perpetual_faces/n1_w199_results.json"',
    '@CLI@': '--wave 199/finalize --wave 199',
    '@ENG6@': '【n1_w199/ 分片计数增长·唯一点火证据·r325 律】',
    '@SHARD@': 'results/p2cal_ext/n1_w199/shard-<k>-of-12.json',
    '@RFN@': 'results/perpetual_faces/n1_w199_results.json',
    '@FINPRE@': 'finalize 键序前置=**起稿窗零在飞上游席（W197/W198 finalize 均已落 origin·ls-tree 机证）**——跑时按 registry 键 derive 复核·FAIL-CLOSED r307 两态例恒在）。',
    '@EOBD@': '（engine_owner==bm-a 113 行注册 + 本候选——以 probe leg0 机证为准）',
    '@BGATE@': '（p2_calibration v1/v2 canon；v1 ext；v2..W198 落地）',
    '@S7@': '待 W199 finalize 窗】\n- （占位·finalize one-pass 后机械回填：账本恒等式+合并池 K+merged mu/w-only mu/mu_delta+sigma+se_mu+skill_line_v2 K-lift+A 档 p95+§5 四预键机证+canon flip 态+audit.finalize_only+voids_applied）。',
    '@S8@': '【finalize 同窗回填·待 W199 finalize 窗】\n- （占位·§5.5 W200+ 投影承接+宝藏/方法论捕获问+诚实披露面·finalize 收口窗机械回填）。',
    '@WAVEFREE@': '波号 199=注册表 W198 席后首个自由号'
}
assert len(BACK) == len(OLD_BACK) == 40, (len(BACK), len(OLD_BACK))
assert set(BACK) == set(OLD_BACK), "token set drift: %s" % (
    set(BACK) ^ set(OLD_BACK))

# ---- two-phase vmap (DRY whole-file gate, zero-write-first) ----
src = io.open(SRC, encoding="utf-8").read()
assert src.count("\r\n") == 0, "src blob expected LF"
src = src.replace("SEED_REGISTRY \u5168\u952e 195 \u503c",
                  "SEED_REGISTRY \u5168\u952e @@REGN@@ \u503c")
out_t = src
for tok, old in OLD_BACK.items():
    n = out_t.count(old)
    assert n == 1, "TOK %s count=%d (old head=%r)" % (tok, n, old[:80])
    out_t = out_t.replace(old, tok)
for tok, new in BACK.items():
    out_t = out_t.replace(tok, new)
out_t = out_t.replace("SEED_REGISTRY \u5168\u952e @@REGN@@ \u503c",
                      "SEED_REGISTRY \u5168\u952e %d \u503c" % REG_N)
resid = re.findall(r"@[A-Z0-9]+@", out_t)
assert not resid, "unsubstituted tokens remain: %s" % resid[:5]
bad = [mm.group() for mm in
       re.finditer(r"(\d{3})_(\d{3})\.(\d{3})_(\d{3})", out_t)
       if int(mm.group(3)) < int(mm.group(1))]
assert not bad, "malformed windows: %s" % bad[:4]
assert out_t.count("PERPETUAL-N1-W199") == 3, "batch id count drift"
assert out_t.count("\n") == src.count("\n"), "line structure drift"
for stale in ("FIFTY-EIGHTH", "450_204..452_203", "450_404..450_603",
              "450_204..450_403", "450_404..452_403", "450_404+j",
              "452_404+j", "PERPETUAL-N1-W198",
              "PERPETUAL_N1_W198_PREREG", "n1_w197_results.json",
              "n1_w198/", "433,540", "845,545",
              "1.1877", "1.1876", "0.3307", "0.245094",
              "W197-only \u5b9e\u6d4b", "0.0812", "line_pre 1.1876",
              "n_eff 845,545", "_r915bma", "525630e39",
              "MSG-2026-10-09-1355", "283379899",
              "engine_owner==bm-a 112",
              "\u7b2c 188 \u6ce2", "\u7b2c\u4e00\u767e\u4e00\u5341\u4e09\u679a",
              "\u6cf5\u7b2c 196 \u679a", "W2..W197",
              "W1..W197", "\u5f85 W198 finalize \u7a97", "W199+ \u6295\u5f71",
              "engine_owner \u884c 187", "W196/W197 finalize",
              "pre-W198", "r914 v2", "r916\u00b7buildgen",
              "r915 probe \u5355\u8dd1"):
    assert stale not in out_t, "stale token survives: %r" % stale
assert M + "0.0928" in out_t and M + "0.0971" in out_t, "U+2212 forms"
assert out_t.count(M + "0.0001/W191") == 1
assert "W191=bm-a r894 freeze\uff08e5e4af81b\uff09" in out_t
assert "\uff1bW196=bm-a r912 freeze\uff0802cf6b44d\uff09\uff1bW197=bm-a " \
    "r915 freeze\uff08522a0aef5\uff09\uff1bW198=bm-a r916 freeze" \
    "\uff0882b881a4f\uff09\u3002" in out_t
assert out_t.count("n1_w198_results.json") == 2
assert out_t.count("W1..W198 N1 finalize \u5df2\u5168\u90e8\u843d\u5730") \
    == 2
assert out_t.count("n1_w199") == 4
assert "FIFTY-NINTH" in out_t
assert "W198-only \u5b9e\u6d4b" in out_t, "anchor w-only face missing"
assert "849,945" in out_t and "433,520" in out_t and "435,720" in out_t
assert "452_604..454_603" in out_t and "454_604..454_803" in out_t
assert "847,745" in out_t, "n_eff face missing (legit survivor)"
assert out_t.count("431,320") == 1, "W197 K historical ref must be exactly 1"
assert out_t.count("847,745") == 2, "n_eff + W197 ledger refs must be exactly 2"
assert out_t.count("522a0aef5") == 2, "W197 freeze sha refs (chain+seatblock)"
assert "0.3279" in out_t and "0.245097" in out_t and "0.000372" in out_t
assert "1.1878" in out_t and "line_pre 1.1878" in out_t

open(OUT, "wb").write(out_t.replace("\n", "\r\n").encode("utf-8"))
chk = io.open(OUT, encoding="utf-8", newline="").read()
assert chk == out_t.replace("\n", "\r\n"), "CRLF roundtrip drift"
print("W199 prereg built: %s bytes=%d crlf=%d" %
      (OUT, len(chk.encode("utf-8")), chk.count("\r\n")))
print("post-transform asserts PASS (counts, residue-zero, malformed-zero,"
      " stale-sweep CLEAN, U+2212 forms, anchor=W198 actuals r590)")
