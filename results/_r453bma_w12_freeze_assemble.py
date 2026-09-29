# r453 bm-a: assemble frozen W12 prereg = freeze banner + (a)-(e) verbatim + draft body verbatim
import io

src = io.open('research/TRIAL_LABOR_W12_CANDIDATE_RSQR_PREREG_DRAFT.md', encoding='utf-8').read()

i_checklist = src.index('## 收编机复用前必做清单')
i_body = src.index('——以下正文=')
i_neg = src.index('> **候选血统四件套')
negatives_block = src[i_neg:i_checklist].rstrip()
body = src[i_body:]

banner = """# TRIAL_LABOR_W12_PREREG ——【T-99 千人试用期大考 wave-12 波级预注册（MASS CANDIDATE TRIAL PROGRAM 第十二波·趋势拟合强度门）·FROZEN】

> **【状态：FROZEN——已冻结·2026-09-30 02:3x·bm-a r453（收编机当轮冻结步·泊位开放条款兑现·起草=bm-a r447=收编机同人直贯先例·谱系 AMP→W9/MOM→W10/STD→W11/RSQR→W12 四连收编）】**编译窗撞查先行全绿：本轮 pull --rebase 已拉 origin 最新（拉入 bm-b r444 波收口=74da996dd 基之后零 W12 冻结面他人 commit）·job_list 零 in-flight·fleet\\tasks 零 open·TRIAL_GRAMMAR_LEDGER 尾部零 wave-12 行=无撞认领。**冻结触发器①（已满足·机械回执）**=W11 全链消费落地活读复验：TRIAL-LABOR-W11-JUDGE judge-finalize 落地 2026-09-30 01:47:40〔results/trial_labor_w11/w11_judge.json **229/229 judged·九面合计零 G1 零 G2**·eligible_g2 空=lawful-zero intake·**ledger head 冻结轮实读 total=350,247 linear**〔w11_judge trials_ledger prev 350,018+229·跑时活读链头〕〕+48h CEO 报面板已落 docs/trial_labor/CEO-REPORT-WAVE11-20260930.md〔窗止 2026-10-02 01:47:40〕+W11 prereg §7/§8 已回填〔bm-b r444〕+attrition 两行在册+TRIAL_GRAMMAR_LEDGER wave-11 行在册+**判官池零在飞批**〔池面机械核 T-123 done·229/229 ckpt〕。
> **⑥W11 SCREEN/JUDGE 实测=冻结横幅携带（draft §5.2 起草时点未落·冻结轮活读兑现）**：SCREEN null p95 **0.5148** IN 预测带 [0.50,0.52]（W1-W10 带延续同口）·存活 **229/1262=18.15%**·STD 轴分段富集 std10_hi 73/296=24.66% > none 121/688=17.59% > std20_hi 35/278=12.59%（首个 STD screen 面·正 10 日/负 20 日不对称=r237 探针漂移面注记）+MOM 续航 1.25x（vs W10 1.88x 跨波衰减研究事实）；JUDGE：九面合计零 G1·top cell W11-B-3023 sharpe 0.997 vs 判线 1.1944·top DSR 0.6273<0.95·E[FP]=11.45·n_eff 351,480。**DSR n_trials 活链头=350,247（跨波不重置·W12 judge 跑时 live 读=W12-JUDGE 落地前链头·冻结步实读携带）。**
> **冻结步四件齐**：commit 冻结件+SEED_REGISTRY 三键同 commit（R250 一致律·**20320500/20321000/20321500**）+波级票 **T-2026-09-30-124** 开票同轮认领（O-1730 即时律·W8=T-120/W9=T-121/W10=T-122/W11=T-123 谱系）+F-04 MSG 声明同轮（leg1=本 commit·leg2=fleet inbox MSG）；**冻结时点起本件烧批效动生效**（fill_ladder prereq_frozen 门放行·Tools/fill_ladder_catalog.json TRIAL-LABOR-W12-GENERATE 门控条目本轮预告·runner_exists 门待 runner 构建切片）。
> **Seeds 三步律兑现（draft ⑤ 条款·冻结轮活读非预检）**：泊位 20320500/20321000/20321500（+500 自然推位自 W11 20317000/20317500/20318000）三步律全绿——**step1** 130 键 live-import 面（science_gates.SEED_REGISTRY import 真值·r244 律禁源文正则）零精确撞带零键名撞；**step2** 首元 int(default_rng(s).integers(0,2**31))=**1294340368/1873818339/561143918** 新基间互异且对全部既有基零撞；**step3** 派生带 scrnull 20321000..20321199（K=200）与 unc 20321500..20321700（B=2000 block·P=2000 sign-flip·rng([base,cell_idx])）零重叠·gen 20320500 无派生面；**起草-冻结窗差额**：起草时点尾读 max=20320000 vs 冻结轮活读 max=**20322000**（=innovation_quota_w4_volregime·bm-c r245 W4 SLOT-4 后到·非撞带如实注记）；rg 全仓命中分类=泊位声明文档×2（draft ⑤+MSG-2225）+data volume 列数值位巧合（t34/batch-69 先例面）+registry 尾注+自有 close 件零种子面命中；**事实件=results/_r453bma_w12_seed_law_facts.json·复验器=results/_r453bma_w12_seed_law.py（r441 范式复刻·rg 腿 GBK 读线坑 r236 族已 encoding-safe 补录）**。
> **收编单十项清单兑现回执（draft 头部清单①⑩逐项·冻结轮活读）**：①冻结触发器活读复验✓（上述机械回执）；②轴系=十五元组 R/X/S/T/STOP/GATE/VOL/YANG/VCONF/STREAK/TSTATE/AMP/MOM/STD/**RSQR**（RSQR∈{none,rsqr20_hi,rsqr10_hi}·三值轴=W4 VOL/W11 STD 先例·轴组组合模板=W11 31,352,832×3=**94,058,496**·rsqr10vsrsqr20 互开 23.75%/24.4% 部分冗余如披露·去重门承接）；③排除簿=**十二源**（W1/MASS/W2-W11 十二源全落地·W11-JUDGE 已并入；generate 时点实读·前波无 rsqr 轴按 rsqr=none 补全类匹）；④G-RSQR 探针复验=r447 探针件在位（仓内冻结 runner verbatim-import·decidable 3,363/open 341/9.79%/首可判 120/rsqr10 332/slope 213/128 逐位·六冻结事实件全绿·收编机免复核面）；⑤seeds 三步律✓（上述）；⑥判读参照带=W1-W10 p95 带并入+W11 实测 0.5148 横幅携带✓；⑦机制段交叉注记保留✓（五折坑随冻结携带·见下节）；⑧judged 例给 declare 窗=十二源（W11-JUDGE 落地后·generate 跑前仍重读 live prev 增量并入加权 declare）；⑨外源 digest 复用零重做✓（O-1721 同源事·r234 digest+A158-TSGATE-P1/GATE-RECHECK 双源仓内件随本件整体有效）；⑩波级票=T-2026-09-30-124 开票同轮认领✓。

"""

out = banner + negatives_block + "\n\n" + body
out = out.replace(
    "— bm-a r447 起草泊位落地；收编窗口=冻结触发器①满足起至任何健康机认领止（泊位开放条款·W9 §9 先例）。",
    "— bm-a r447 起草泊位落地；bm-a r453 收编冻结落地（泊位开放条款兑现·同人直贯）；runner 构建切片=下一开工面（scripts/trial_labor_w12.py·W11 r442 范式·G-RSQR fail-closed 门随 §3）。")
io.open('research/TRIAL_LABOR_W12_PREREG.md', 'w', encoding='utf-8').write(out)
print('frozen prereg written, lines:', out.count('\n') + 1)
sec7 = out[out.index('## §7'):out.index('## §8')]
print('sec7-empty-check:', '（空——收编机冻结后跑批回填。）' in sec7)
