# Assemble the W11 frozen prereg from the bm-c r237 candidate draft
# (whole-package adoption per berth clause; header banner rewritten to
# FROZEN with live-receipt facts; draft berth-collision re-take banner
# included; two in-body status lines updated; tail berth clause removed).
import io, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

draft = io.open("research/TRIAL_LABOR_W11_CANDIDATE_STD_PREREG_DRAFT.md", encoding="utf-8").read()

# --- split draft into header / four-disclosures / adoption-checklist / body ---
i_disc = draft.find("**诚实邻接四披露（候选面先行声明·收编机必须随冻结携带）**：")
i_chk = draft.find("## 收编机复用前必做清单（增量面·STD 核心机械不动）")
i_body_marker = draft.find("——以下正文=**W11 增量面全写**")
assert i_disc > 0 and i_chk > i_disc and i_body_marker > i_chk
disclosures = draft[i_disc:i_chk].rstrip()
body = draft[draft.find("# TRIAL_LABOR_W11", i_body_marker):].rstrip()

# remove the tail berth clause (fulfilled by this adoption; facts live in banner)
tail_marker = "\u2014 bm-c r237 起草泊位落地；收编窗口="
if tail_marker in body:
    body = body[:body.find(tail_marker)].rstrip()
# de-candidate the title
body = body.replace(
    "# TRIAL_LABOR_W11（候选骨架） —— T-99 千人试用期大考 wave-11 波级预注册（MASS CANDIDATE TRIAL PROGRAM 第十一波·高波发散确认门）",
    "# TRIAL_LABOR_W11 —— T-99 千人试用期大考 wave-11 波级预注册（MASS CANDIDATE TRIAL PROGRAM 第十一波·高波发散确认门）", 1)
# claim line: draft-time candidate state -> frozen-step reality
old_claim = "- 认领：候选面无票无认领（本 draft）；冻结步开票+同轮认领（W5-W10 先例）；认领依据=TRIAL_LABOR_LAW §1 常供律例行供给步。"
new_claim = "- 认领：波级票 T-2026-09-29-123 冻结步开票+同轮认领（O-1730 即时律·W5-W10 先例=T-120/T-121/T-122 谱系）；认领依据=TRIAL_LABOR_LAW §1 常供律例行供给步（起草时点候选面无票无认领=bm-c r237 draft 状态如实保留）。"
assert old_claim in body
body = body.replace(old_claim, new_claim, 1)

banner = """# TRIAL_LABOR_W11_PREREG —— T-99 千人试用期大考 wave-11 波级预注册（MASS CANDIDATE TRIAL PROGRAM 第十一波·高波发散确认门）

> **【状态：FROZEN——已冻结·2026-09-29 21:1x·bm-b r441（收编机当轮冻结步·泊位开放条款兑现=bm-c r237 STD 候选架整体收编·AMP→W9/MOM→W10/STD→W11 三连收编先例范式）】**起草=bm-c r237（2026-09-29 20:1x·DRAFT 泊位态·TRIAL_LABOR_LAW §1 常供律+锦标赛预先承诺姿态〔DECISION_CHAIN v1.2 §四.7：下一批假设须在前批 verdict 前冻结——起草于 W10 verdict 未落窗=合法·JUDGE 落地=泊位窗死线非前置·r237 判例〕·泊位=commit+MSG-20260929-2015 双信号声明）；冻结认领=本 commit（fetch-gate 21:0x 零 rival——origin/main=16d00201a=本机 r440 收口头·无任何 W11 冻结面/他人新 commit·job_list 空+fleet\\tasks 零 open+TRIAL_GRAMMAR_LEDGER 尾部零 wave-11 行=三查先行全绿）。**冻结触发器（已满足·机械回执 2026-09-29 21:0x 冻结轮当场再读·活条件非历史条件）**=W10 全链消费落地（TRIAL-LABOR-W10-JUDGE judge-finalize 落地 2026-09-29 20:31:29·results/trial_labor_w10/w10_judge.json **283/283 judged 零 G1 零 G2** eligible_g2 空·w10_intake lawful-zero·**ledger head 冻结轮实读 total=346,553 linear**〔head file=w10_judge.json·prev 346,270+283·r441 复验〕·48h CEO 呈报已落 docs/trial_labor/CEO-REPORT-WAVE10-20260929.md〔窗止 2026-10-01 20:31:29〕·W10 prereg §7/§8 已回填〔bm-b r440〕+attrition 两行 27 行在册+TRIAL_GRAMMAR_LEDGER wave-10 行在册）**∧ 判官零在飞批**（池面机械核 21:0x 实读：runnable_pool entries **123/123 done**·零 ready 零在飞）。
> **冻结步四件齐套**=commit 冻结+SEED_REGISTRY 三键同 commit（R250 一步律·**20317000/20317500/20318000**·撞带重取后值）+波级票 **T-2026-09-29-123** 开票+同轮认领（O-1730 即时律·W8=T-120/W9=T-121/W10=T-122 谱系）+F-04 MSG 声明同轮；**冻结时点起本件烧批效力生效**（fill_ladder prereq_frozen 门放行·Tools/fill_ladder_catalog.json TRIAL-LABOR-W11-GENERATE 门控条目本轮预布线·runner_exists 门待 runner 构建切片）。
> **【seeds 撞带重取横幅·draft ⑤条款兑现】**draft 起草泊位 20316000/20316500/20317000 中 **20316000/20316500 与 bm-a r445 A12-PREDCOND 双键撞带**（t101_v4_a12_predcond_scrnull/unc=20316000/20316500·A12 落地 20:4x 晚于 draft 起草窗 20:1x=合法竞态·draft ⑤明文预置「冻结时点三步律复验非本件预检·撞带=重取+横幅注记〔W9 两连撞先例〕」条款）→ **+500 推位重取=20317000/20317500/20318000**（draft 泊位第三键 20317000 原位保留）。重取三步律复验全绿（r441 bm-b 冻结轮活读：registry 全盘 **123 int 基零精确撞带/键名零撞**〔解析 science_gates.py SEED_REGISTRY 全键值面〕+首元素互异〔正典=int(default_rng(s).integers(0,2**31))·新基首元 **673516273/1869008098/1084768275** vs 全部既有基零撞+新基间互异〕+null 派生带 20317500..20317699 与 unc 派生带 20318000..20318200 零重叠〔vs W11 gen 带 20317000 无派生面·vs A12 带 20316xxx 500 净隙〕+rg 全仓命中分类=泊位声明文档×2〔draft ⑤+MSG-2015〕+零命中+data/daily volume 列数值巧合×3〔sh515580/sz159873/sz159991 成交量列=t34/batch-69 先例面〕；事实件=results/_r441bmb_w11_seed_law_facts.json·复验器=results/_r441bmb_w11_seed_law.py）。
> **收编十项清单兑现回执（draft 头部清单①-⑩·逐项·冻结轮活读）**：①**冻结触发器活读复验**=上述机械回执（w10_judge.json 283/283·CEO-REPORT-WAVE10 在位·attrition 27 行·登记簿 wave-10 行·W10 §7/§8 回填·池 123/123 done）✓ ②**轴系=十四元组** R/X/S/T/STOP/GATE/VOL/YANG/VCONF/STREAK/TSTATE/AMP/MOM/**STD**（STD∈{none,std20_hi,std10_hi}·三值轴=W4 VOL 先例）=W10 10,450,944×3=**31,352,832** 轴组合/模板（§3 冻结·std10vsstd20 互开 50.13%/49.12% 部分冗余如实披露·去重门承接）✓ ③**排除簿=十一源**（judged declare 窗 W1/MASS/W2-W10 十一源全落地〔W10-JUDGE 20:31:29 已并入〕+screen 十一清单〔W10_screen 存活 283 已落地 19:42:03 并入〕·generate 时点实读·cell key 增 std 轴·前波无 std 轴者按 std=none 补全类匹）✓ ④**G-STD 探锚复验**=冻结轮重跑 results/_r237bmc_stdq90_w11_probe.py **全锚逐位复现**：decidable **3,363**/open **391**/开窗率 **11.23%**/std10 **399·11.46%**/首可判 bar-idx **==120**（fail-closed 断言）/八门 256 格 非空 103·空 153·min 1·max 41·全可判 3,305/core48 开窗率 min 7.11%·median 9.82%·max 13.43%（48/48 非退化）/政体面 bear 10.97 vs bull 11.4·wild 内 21.17 vs calm 内 2.50·yang 12.32 vs red 10.92·surge 13.6 vs dry 9.67/W4 邻接 88.92%+38 独有日+wild 面内 305/1,441 再劈/MOM 互开 42.6%/43.85%+221 独有/std10vsstd20 50.13%/49.12%/前向差分 20 日 +1.97%（t=6.18）·5 日 +0.89%（t=4.47）/**漂移面 std∧calm 18 日 −2.83% vs std∧wild +1.90%（t=−4.37）**/确定性交叉核 r417/r423/r431/r228/r234 五冻结事实件全绿/极端日七面逐位同（facts=results/_r237bmc_stdq90_w11_probe_facts.json 冻结轮覆写同值）✓ ⑤**seeds 泊位**=撞带重取三步律全绿（见撞带横幅）✓ ⑥**判读参照带**=W1-W10 p95 带并入（W10 SCREEN 实读 **0.516361**·§5.2 预测带 [0.50,0.52] 同 W10 口径）✓ ⑦**机制段交叉注记保留**=四披露 (a)-(d) 随冻结携带（见下节）✓ ⑧**judged 供结 declare 窗=十一源**（W10-JUDGE 已落地·generate 跑前仍重读 live prev 增量并入加权 declare）✓ ⑨**外源 digest 复用零重扫**（O-1721 同源律：r234 digest+A158-TSGATE-P1/GATE-RECHECK 双源仓内件随本件整体有效·A158 STD 构造复核=探针 L240 逐字对位已完成=收编机免复核面）✓ ⑩**波级票**=T-2026-09-29-123 开票+同轮认领（O-1730 律·谱系先例）✓。

"""

out = banner + disclosures.strip() + "\n\n" + body + "\n"
io.open("research/TRIAL_LABOR_W11_PREREG.md", "w", encoding="utf-8", newline="\n").write(out)
print("frozen prereg written:", len(out), "bytes")
