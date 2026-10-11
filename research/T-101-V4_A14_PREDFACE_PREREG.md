# T-101-V4-A14 预注册（v4 22 门库 A13 式预测器扩展臂·纯预测器信息面）

> 状态：**FROZEN v1.0——冻结于跑前·2026-10-11 r872 bm-b（T26 slice-2·起草机同轮一次冻结·A13/A9/A10/A11/A12 臂线批先例：一次冻结即烧）**。**冻结五条件证链（r872 全绿）**：①selftest 复跑 16/16×2（scripts/t101_v4_a14_predface.py·hermetic 十二腿：连续性 fail-closed/位移 null 确定性/LOO 去均值手值/块自助单调排零+常数 NaN/判据四条款边界/IC nan 过滤/RAW fwd 手值/池 p 算术/单次烧录守卫/MP1 名册身份钉 gate_recheck_mp1.json 实读/锚行数钉/resid master LOO 手值）；②起草探针复跑字节恒等（results/_r872bmb_a14_draft_probe.json md5 9af05782500f·确定性零漂移）；③banned_direction_gate --prereg 本件 **ADMIT rc0 matched=[]**（回执 results/_r872bmb_banned_gate.txt）；④origin 写前复核=prereg 不在 origin/main（DRAFT 态·HEAD==origin tip 零漂移）；⑤状态翻面 FROZEN 与 runner 交付+SEED_REGISTRY 两键登记（20615500/20616500）+F-04 声明（fleet/inbox/MSG-20261011-0905-bmb-a14-predface-freeze.md）**同 commit**。冻结后禁改 §0-§6 判据面；跑后只回填 §7/§8，要改判据要重跑。
> 血统：A13 §8 下游指针兑现（「f_c2 连续预测面→A1/C1 双温度计复合臂指名输入特征〔bm-b 车道〕」——本批=该指名输入特征的供料批）+ DIGEST-20261011-w21 Q2 裁定（「A13-style predictor extension on the v4 22-gate library」=**唯一开放用法面**：A9/A10/A11/A12 四类用法关闭在册·MP1-5 预测器用法 never-tested=非换皮新面）+ tech.md T26 行（r871 bm-b 登记+同轮认领 commit 1bbd0bdfd·queue_seed_gate rc0）。
> 批型：**纯预测器信息面判决批**（A13 同型·forecast/walk-forward）——测量「门掩码均值特征→20 日前瞻收益」的秩相关预测技能本身，非任何仓位构造。功能形=条件期望建模（Spearman IC·stride-20 非重叠再平衡日历）。与 A13 的功能形恒同（§8 冻结表述），特征面=**v4 22 门库扩展**（A158 17 确认门+MP1 5 确认门）。
> 统摄律：BACKTEST_SCIENCE.md v2 + COMPUTE_AUDIT.md 批件纪律 + r433 同门换用法判例 + A13 §2 新批新 cutoff 律 + TRIAL_LABOR_LAW §4 N_eff 跨波累计。

## §0 批件身份【必填·跑前】

- 批名：**T-101-V4-A14-PREDFACE**·批内格数：**30**（特征 3 × 成员 5 × 收益面 2）；null 对照 K=200/格·另计不膨胀格数。本批=**信息面判决批**（入 trials_ledger，batch_trials=30）。
- 认领：tech.md T26 行（r871 bm-b 登记+同轮认领·登记即锁）；pool 提交前 F-04 声明=fleet/inbox/ MSG（D-20261010-1945 declaration gate 面·防双机撞车）。
- 部门归属：dept:研究（链条研究线·T-101 v4 输入特征路线 A14 位）。
- 算力预算：本地 CPU 确定性——五员特征构造（A158 157 因子+MP1 89 式×5 员）+30 格×(200 位移 null×3 段+2000 块自助×2 段)。A13 40 格 27.8s 实测同机械缩放+MP1 因子面增量→est 1-3min 单进程→**池批面**（>120s 短批帽·O-2130 多核律）：入池 `results/runnable_pool.json` 条目 `T-101-V4-A14-PREDFACE`（runner ProcessPool 腿=parallel_runner import 面·per-member jobs）；autofill/daemon 烧录合法；批报告必带 audit 段。
- 车道：lane-free（特征构造全部仓内单源机器件·锚门 in-runner fail-closed=任何健康机可烧）。
- 意义审计三验：①可判负假设（22 门库扩展特征的信息面 IC 不显著=供给注记空·f_c2 对照不复制=A13 发现负更新·两者皆合法产出）✓；②指名消费面（A13 §8+A1/C1 复合臂输入名册·consumer_plan 见 §6）✓；③判负处置预案（全灭=v4 门库预测器扩展面关板·A13 发现维持 f_c2 单面在册·下游复合臂供给面回 A1/C1 双闸后置裁定）✓。
- **撞批三查**（r440 律）：job_list 空✓+fleet/tasks 零 open✓+git fetch 近 30min 他人 commit 扫标题（零 A14 面冲突）+SEED_REGISTRY 尾 live-read（20615500/20616500 零撞）✓。

**§0-X 特征与预测器形态【冻结·禁搜参·全冻死·A13 §0-X 逐字律】**：
- **特征（3·全冻结·零新发明）**：
  - `f_c2v4`=**22 门掩码均值**（fv.GATES17 的 A158 17 确认门 ∪ gate_recheck_mp1.json library_entries 的 MP1 5 确认门·overlap=0·union=22 探针实证）——A13 f_c2 的 v4 库扩展面；
  - `f_mp1`=**MP1 5 门掩码均值**（CORR(OPEN,VWAP,10)_q90·CORR(MA(CLOSE,10),VWAP,10)_q90·CORR(HIGH,MUL(CLOSE,HIGH),20)_q90·DELTA(MAX(RET,30),5)_q90·MA(LOW,30)_q10）——MP1 门族信息面首测（W19/W20→MP1 时序门→RECHECK 全链无预测器面=never-tested 新面）；
  - `f_c2`=**17 门掩码均值（对照面）**——A13 已测特征在**新 cutoff 2026-10-09 的复制锚**（A13 §2 律：新批新 cutoff 合法·非重跑；批内对照=A13 发现的截止日延伸复制读数+f_c2v4 增量贡献的差分基座）。
  - 掩码构造单源：A158 面=`probe.alpha158_factors`+`probe.gate_universe`（rolling(252,min_periods=120) q10/q90）；MP1 面=`mp1_tsgate_probe.mp1_factors`（t23.evaluate 单源）+`mp1_tsgate_probe.gate_universe`（同参数 252/120/q10/q90=两侧同构）。decidable=成分门 decidable 全 AND（A13 c2dec 同律）。
  - **方向零假设**：IC 面测符号本身·无升序/降序选择（A13 同律）。
- **预测目标**：`fwd20(t)=close[t+20]/close[t]−1`（20 交易日·stride-20 非重叠再平衡日历=族律）。
- **收益面（2·冻结·A13 逐字）**：RAW 面=成员自身 fwd20（β 主导面如实携带）；RESID 面=`r_resid_i(t)=fwd20_i(t)−mean_{j≠i} fwd20_j(t)`（LOO 同侪去均值=成员相对面）。
- **格（30·冻结序=face(raw→resid) × member(510300→510050→510500→512100→588000) × feature(f_c2v4→f_mp1→f_c2)·cell_idx 0..29）**。
- **FV 可判格=9**：RAW 面×{510300,510050,510500}×3 特征（IS 段≥15 对·探针实测 IS=49/137/49/39/39/41 全过门）。**读数层 21 格**（RESID 全 15 格+RAW{512100,588000} 6 格=结构 OOS-only：512100 上市 2016-11·588000 上市 2020-11→master 交集窗全在 2017 后）→p/z 如实披露·无 FV 资格·p_OOS<0.05 命中=「供给注记」旗（A13 同律）。

## §0.5 禁开方向硬闸【必填·跑前】

- 冻结 commit 前必过：`python Tools/banned_direction_gate.py --prereg research/T-101-V4_A14_PREDFACE_PREREG.md` 退出 0（decision=ADMIT·matched=[]·回执随冻结 commit）。
- **BAN-05 引用披露（例外类型=不适用·本批非该禁向主张）**：BAN-05（market-temperature/breadth timing as a precondition·原否证=retail-quant-conclusions-v2#3）闸的对象=A1/C1 双温度计**复合臂择时前置**用法——**本批不主张该用法**：A14=纯预测器信息面（IC 测量·零择时零前置零仓位构造），原否证所测的「前置过滤删信号」机制面在本批结构上不存在（无策略收益序列可被前置过滤）。A1/C1 复合臂本体起草仍=BAN-05+情绪族双判负档双闸后置（DIGEST Q3 裁定逐字）·本批产物只供其输入特征名册·不构成对闸的绕行（复合臂自身的开闸论证另窗另批）。
- 本批正文其余节不涉任何禁向词面（信息面测量·零策略宣称）。

## §1 α 机制段【必填·D6】

四选一：**[x] 行为偏差**——恐慌过度反应+锚定效应的连续值版（A13 §1 血统照携）：22 门库=超卖/恐慌/结构极端态的聚合识别面（A158 17 门=波动/分布/价格水位族极端态；MP1 5 门=价格水位锚〔MA(LOW,30) 低位〕+开盘-成交均价关系〔买卖盘进攻态〕+高价-收益结构极端态）→极端态聚合高=恐慌抛售者交出筹码→20 日窗均值回归修复。f_c2v4=聚合扩展面·f_mp1=MP1 子集面·f_c2=17 门对照面（A13 发现复制锚）。由谁付出代价=预测面无对手盘构造（信息面）——**诚实披露：信息面测量不构造策略收益流·其下游任何转化仍须过 D6 beta 同源门**（A2/A9/A10/A11/A12 判例族 0.57-0.97 结构同源·A13 §1 预声明逐字续用）。
- **散户凭什么赢【§1.2】**：本批=信息面批无直接交易面（A13 同型：测量信息存在性·不构造可交易收益流·「赢」的判定不在本批射程内=如实申报）；可消费面=A1/C1 复合臂输入特征名册+供给注记旗（consumer_plan §6）·其任何下游转化过 D6 门=预声明。
- **同族相关性准入检查【D6·跑前预声明】**：信息面无收益流→D6 收益流判线**不适用于本批本体**（A13 预声明逐字续用）；下游转化预声明=A2/A9/A10/A11/A12 判例族 beta 同源门恒在·本批过线≠注册资格·仅=信息面存在性判决+s4 供给注记资格。**特征互相关披露面（探针实测·读数不 kill）**：f_c2v4~f_mp1=+0.849·f_c2~f_c2v4=+0.800·f_c2~f_mp1=+0.423（510300·n=3336）——嵌套分解构造性高相关如实披露（f_c2v4 含 f_c2 的 17/22 成员·f_mp1 与 f_c2v4 共享 5 门）；三特征非同格克隆（f_c2~f_mp1=0.423<0.7=独立信息面主张成立）；批内三特征=**同机制族分解面**（聚合/子集/对照）非三独立假设——判读按族内连贯读·多重检验有效独立数<9 如实披露。

## §2 数据与面板【必填·跑前探针事实·r872 探针实测】

- 宇宙=冻结五员 O-1555={510300, 510050, 510500, 512100, 588000}；数据锚四元组（G-ANCHOR-FACE）=`data/daily/sh<码>.csv`+pd.read_csv raw 直读+**cutoff 2026-10-09 截断+尾行断言**（runner 自有 loader·A13 §2 律：新批新 cutoff·fv.ANCHOR_ROWS 09-28 锚与 A13_ANCHOR_ROWS 09-29 锚均禁跨批挪用）。
- **冻结行数锚（@2026-10-09·本批探针实测）**：510300=3,490 / 510050=5,255 / 510500=3,293 / 512100=2,409 / 588000=1,429；尾行一律 2026-10-09（runner 断言·A14_ANCHOR_ROWS）。
- **evidence_cutoff=2026-10-09**（面板当前真值·MP1/GATE-RECHECK-MP1 同刻 binding·周日无新 bar）；cutoff 后新 bar 不回流；结果 JSON 顶层必带 `science_gates.cutoff_meta(evidence_cutoff)`（C2 律）。
- **G-ANCHOR-MP1 复现门（runner fail-closed）**：510300 DELTA(VOLUME,30)_q10 decidable==3341·open==390·first_decidable_idx==149（r867 探针事实·本批探针同 cutoff 复现实测三值恒等）——MP1 门机械 import 正确性 in-runner 证明。
- **可判窗（探针实测·runner 实算如实落 JSON）**：
  - RAW 面：decidable 起 f_c2v4/f_mp1={510300:2013-01-10·510050:2005-10-11·510500:2013-11-07·512100:2017-06-23·588000:2021-07-05}·f_c2 各员提前约 40-49 bar（A158 门 warmup 短于 MP1 门）；对数（full/is/oos）：510300={166/49/117·f_c2=168/51/117}·510050={255/137/118·f_c2=256/139/117}·510500={156/39/117·f_c2=158/41/117}·512100={112/0/112}·588000={63/0/63}。
  - RESID 面：U5 master 交集 2020-11-16→2026-10-09（1,428 行）·全 AND decidable→f_c2v4/f_mp1=63 对·f_c2=65 对·IS 结构近空（0 对）=OOS-only 如实记（A13 同构）。
- 面板列面：date/open/high/low/close/volume/amount（mp1._leaves_from 需求面·探针实证在位）。

## §3 方法学【必填】

- **执行机器零重实现（import 单源·A13 §3 逐字律+r836 全参数显式）**：`a158_tsgate_probe`（probe：alpha158_factors/gate_universe/N_FACTORS）+`t101_v4_a158_fv`（fv：GATES17/g_p1_check/g_accept_check）+`t101_v4_a2_prescreen`（tpl：SPLIT 族常量）+`mp1_tsgate_probe`（mp1：mp1_factors/gate_universe/t23.evaluate 单源·G-ANCHOR-MP1 复现门）+`science_gates`（sg：append_ledger/SEED_REGISTRY/cutoff_meta）+`scipy.stats.spearmanr`（秩相关）+`parallel_runner`（run_cells_parallel/worker_cap·ProcessPool 腿=池多核律）。
- **特征构造（冻结）**：per member：Fa=probe.alpha158_factors(panel)（len==N_FACTORS 断言）→ga=probe.gate_universe(Fa) 字典化；Fm=mp1.mp1_factors(panel)（89 式断言）→gm=mp1.gate_universe(Fm) 字典化；MP1_CONFIRM 5 门在位断言（缺一=VOID）。f_c2=17 掩码 concat 均值·dec=17 门 AND；f_mp1=5 掩码 concat 均值·dec=5 门 AND；f_c2v4=concat[f_c2,f_mp1] 均值·dec=c2dec & mp1dec。RAW 面窗=成员自身日期轴上特征 decidable 起（A13 cell_pairs_raw 逐字）；RESID 面=master 交集+全成员 AND decidable（A13 resid_pairs_master 逐字·A11 build 同法）。
- **再平衡日历**：stride-20·rebal_idx=arange(0,n,20)（族律）；尾 rebal 不满 20d 前瞻窗者弃（p+20≤n−1）。
- **位移 null（批自对照·核心·A13 逐字）**：K=200/格·特征再平衡对数组 circular shift 随机偏移（偏移∈[1,n_pairs−1]·保对数组自相关结构+特征边际分布）→empirical 双侧 p=(1+#{|null|≥|IC|})/(K+1)·z=(IC−mean_null)/std_null（nan-safe r442 律）。**冻结流声明**：full 段流=rng([**20615500**, cell_idx])·OOS 段派生流=rng([**20615500+100000**, cell_idx])（段流分离·cell_idx=冻结 30 格表序）。
- **块自助 CI（不确定性面·A13 逐字）**：circular block bootstrap B=2000·block=10（对再平衡对索引重采样重算 IC）；percentile CI 2.5/97.5（full+OOS 段）。**冻结流**：full=rng([**20616500**, cell_idx])·OOS 派生流=rng([**20616500+100000**, cell_idx])。**声明=实跑同基**（A12 rebind 正法·不经 fv.dual_nulls·UNC_BASE 直读直用零继承基错配面）。
- **种子三步律+登记（跑前完成·全绿证链）**：`seed_admit_gate 20615500/20616500 rc0 FREE`；零精确撞带（207 int 基全查）；正典首元 int(default_rng(base).integers(0,2**31))=445511398/1163362 与全部既有基互异；派生带 base..base+29 与 +100000 面全净；带区间开断言=不在任何 annotated band（[20333000,20445400) furnace 带等全避·W16 判例律）+自然 +500 梯上位（then-max band end 20615200→20615500/20616500 净距 300/1300）；rg 代码面（scripts/Tools/research）与 data/daily 面**双零命中**（两基皆全绿·无数据列巧合面）。两键随冻结 commit 登记 `science_gates.SEED_REGISTRY`（t101_v4_a14_predface_scrnull=20615500·t101_v4_a14_predface_unc=20616500·注释带三步律证链）。
- **账本**：`sg.append_ledger("T-101-V4-A14-PREDFACE", 30, "t101_v4_a14_predface.json", evidence_cutoff="2026-10-09")`（finalize 落·线性·**返回值必落 out["trials_ledger"] 键 r442 律**）。
- **闭合族对号声明【M3】**：本批 family_key=**t101_v4_predface**（A13 同族键·**不在册** CLOSED_FAMILIES 九键内=open 照跑）；W21 同族 alphagen 波=换皮禁开已裁定（W20 §8 RP2=2/2）——本批**非 alphagen 供给波**（=v4 门库消费面·DIGEST Q2 裁定），与 banned gate 面互证。
- **出场轴显式声明（三选一·O-20261001-1108）**：本批=信息面判决批无持仓无模拟无出场事件——**②持有到底声明+runner 显式禁用引擎缺省出场栈**适用（runner 零引擎调用面=构造性保证·纯统计机械·A13/MP1 同构豁免论证）。

## §4 判据【必填·跑前写死，禁看结果调线·A13 §4 逐字镜像】

**FV-PASS（9 可判格·四条合取）**：
1. **|IC_OOS| ≥ 0.10**（20d 横标指数级量级线·A13 同值）；
2. **位移 null p_OOS < 0.05**（双侧 empirical）；
3. **IS/OOS 同号**（n_IS≥15 可判格·gate_verify 反号族处置延续）；
4. **full/OOS 同号**（全期一致性）。
- FV-PASS 格→s4 供给注记资格（下游转化另批·D6 门恒在）；FV-FAIL→判负如实入 §7+attrition。
- 读数层（21 格）：p_OOS<0.05 命中→「供给注记」旗（A1/C1 输入特征面候选披露·非策略宣称·无 IS 确认结构诚实）。
- **f_c2 对照面判读（批内预声明）**：f_c2 RAW 三员 FV 格=A13 发现（510050/510500 双 PASS）的**新截止复制读数**——复制成立（同号过门）=A13 发现稳健性+1 更新；复制破裂（反号或不过线）=A13 发现负更新如实披露（不粉饰不翻案·判读面=本 §4 冻结条款机械适用·f_c2 无特殊待遇）。
- 多重检验税披露：FV 可判 9 格 E[FP]=0.05×9=**0.45**；读数层 21 格纯披露不入判；族内三特征高相关（§1 披露）→有效独立检验数<9 如实记；N_eff 累计照 TRIAL_LABOR_LAW §4 跨波不重置（活头实读 877,723→+30 预期 877,753·finalize 实值为准）。
- **新因子 t 面申报【M1】**：t 面=批内位移 null z 直接面（每格 z_full/z_oos 落 JSON=缺 t 面=missing_input 拒收面满足）；m1_t_value_gate（t≥3.0）判读=FV-PASS/供给注记格**附加披露面**（t 面读数如实落账·非本批判线——本批判线=A13 家族四条款恒等·信息面判决非注册面·注册轴缺席=M1 注册门不适用同 MP1 探针批豁免论证）。

## §5 跑前预测【必填·写死于跑前】

1. **f_c2 对照复制主预期=成立**：A13 raw|510050 OOS +0.2363/raw|510500 +0.1945（cutoff 09-29）→新 cutoff 10-09 仅 +8 交易日（再平衡点几乎不动）→同号且量级相近主预期；若反号/跌破 0.10=A13 发现负更新（§4 预声明面）。
2. **f_c2v4 主预期=与 f_c2 同向但量级近似或略移**（互相关 0.800·17/22 成员共享）——MP1 5 门增量贡献主预期小（掩码均值被 17 门主导）；f_c2v4 与 f_c2 的 IC 差=MP1 增量的批内差分读数。
3. **f_mp1 主预期=弱正可能·量级 <0.10**：MP1 5 门在条件均值面 RECHECK-CONFIRM（OOS med_t 正）→连续值版可能同向；与 f_c2 互相关最低（0.423）=信息面独立性最强但 5 门聚合噪声更大；p<0.05 命中=供给注记旗主预期落点。
4. **RESID 面主预期=多数不显著**：63-65 对小样本低功效+A11 成员相对 rank 已判负族先例；A13 resid|512100|f_c2 +0.2857 先例存在→零星供给注记可能·FV 结构不可能（IS 空）。
5. **极端日先验（§1.3 硬界三件套 (c)）**：本批=IC 秩相关面无逐日 max 硬界（分布界=rank 统计天然稳健·单日极端值在秩面上有界=Spearman 构造性防护·如实申报豁免论证）；窗内极端微观结构日（2015-07 救市/2016-01 熔断日落 IS 段·2024-02-28/09-24/09-30/2025-04-07/2026-01-19 落 OOS 段）影响=再平衡点落在极端日前后的 fwd20 读数面·已由 A13 同窗实跑覆盖（无 VOID 面）。
6. **总判**：FV 0-3/9（含 f_c2 对照复制 0-2）·供给注记 0-4 主预期；f_c2 复制破裂为最重判读事件（A13 供给面负更新）；零供给注记=MP1 预测器用法面关板（合法负收口）。

## §6 产物

- 结果：`results/t101_v4_a14_predface.json`（顶层 evidence_cutoff+cutoff_meta+audit 段+30 格全量三段 IC/p/z/CI+null 池统计+特征互相关矩阵+FV 9 格判决+读数层 21 格+供给注记旗）
- runner：`scripts/t101_v4_a14_predface.py`（run --shard 0 --shards 1〔checkpoint jsonl 断点续烧+pool-claim 握手〕/finalize〔refuse-if-exists+append_ledger〕/selftest〔hermetic 工程门〕）
- 池条目：`results/runnable_pool.json` entry `T-101-V4-A14-PREDFACE`（slice-3·供给 floor ready 0→1 响应面）
- **consumer_plan（O-1820 意义律）**：FV-PASS/供给注记格→A1/C1 双温度计复合臂**输入特征名册**（A13 §8 指名消费方·复合臂本体起草=双闸后置另窗）+T-101 v4 臂表 A14 行（DECISION_CHAIN_BENCHMARKS §五）+§7/§8 回填；判负格→attrition 台账。
- 轮报告回执 + `results/gate_attrition.bm-b.json` 追加行（若判负格存在）。

## §7 跑后实证【跑前必须为空——占位纪律：写数字即造假】

（一次定稿；r872 bm-b 续航轮 finalize 后回填。burn：r872 前驱会话中途死（RAW 5/20 记录后 runner 崩于 RESID 主重索引缺 `.reindex(master_dates)` 转录漏·A13 verbatim 恢复·selftest 16/16×2·checkpoint 保全零重烧）→resume 15 resid 6s→finalize 47.1s。）

- **FV 2/9 PASS = A13 f_c2 锚复刻全成立**：raw|510050|f_c2 OOS IC +0.2363（shift-null z 2.44·boot CI [0.087,0.378] 排零）+ raw|510500|f_c2 +0.1945（z 2.11·CI [0.030,0.352] 排零）——与 A13 cutoff 09-29 锚**4 位小数恒等**（+8 交易日 stride-20 OOS 再平衡点集不变）。
- **供给侧注记 2 格**（IS 空单窗·A13 注记先例逐格复刻）：raw|512100|f_c2 OOS +0.2643、resid|512100|f_c2 +0.2857。
- **判负 7 格→attrition 台账**（gate_attrition.bm-b.json 追加行）：f_c2v4 raw×3 + f_mp1 raw×3 + f_c2 raw|510300——22 门聚合面与 MP1-5 门面 FV 可判格全灭（最接近格 f_c2v4|510500 OOS +0.1410 z1.57 CI 含零、f_mp1|510500 OOS +0.1636 z1.43 CI [-0.001,0.348] 含零：方向同号但显著性不达线）。
- 读数层 21 格如实入 results JSON（RESID 面 63-65 对小样本·512100/588000 raw 单窗）。
- 台账：trials_ledger 877723→877753（batch_trials=30·single-shot law）·evidence_cutoff 2026-10-09·产物 `results/t101_v4_a14_predface.json`。

## §8 批后复盘【必填·s7-T】

## §8 批后复盘【必填·s7-T】

- **预测对账（§5 六主预）**：①f_c2 复刻主预**成立**（2/2 恒等复刻·「复制破裂」最重要判读事件未发生）；②f_c2v4 与 f_c2 同向量级略移**成立**（同号·510050 +0.0608 vs +0.2363 下移·510300 f_c2 -0.0055 近零符号面噪音）；③f_mp1 弱正量级<0.10 **部分落空**（510050 +0.1124/510500 +0.1636 超 0.10 但 z<2+CI 含零=FV 判负·方向对显著性错）；④RESID 多数不显著**成立**（resid|512100|f_c2 +0.2857=注记复刻·resid|510500|f_c2 +0.2844 正但读数层）；⑤极端日检验无 VOID；⑥总判 FV 落在预声明 0-3/9 带内（实收 2/9）。
- **血统去重**：f_c2 格=A13 同构造同数据对照复制面（17 门均值·非新试验）；f_c2v4/f_mp1=真新面首测（22 门聚合/MP1-5 门），首测即判负。
- **下游指针**：f_c2 FV-pass 双格=A1/C1 双温度计复合臂**输入特征名册供给固化**（复合臂本身 BAN-05+情绪族双闸未过=后置另案·DIGEST-w21 Q3）；MP1 预测器用法面由 never-tested 转 **tested-negative**（r871 scout 开面→本批收口·换皮重开须新数据源+例外三问）。
- **边界**：复刻恒等的机械因=stride-20 窗口推进未触再平衡点集；IS 空单窗注记格恒非注册面；boot CI 与 A13 微差=rng 流差异（SEED 20615500/20616500 vs A13 20318500/20320000）非数据面差异；工程面=r872 前驱会话死因 runner dec 主重索引转录缺漏（r494 复制粘贴键漂移族·A13 verbatim `.reindex(master).fillna(False)` 恢复·RAW 5 记录 checkpoint 保全零重烧零双记）。

（跑后回填：预测对账+血统去重+下游指针+边界。）

**全起点分布【§1.3】**：信息面单窗确定性测量批——无策略起点分布面（A13 同型豁免·如实申报）；IS/OOS/full 三段分割=SPLIT 2017-01-01 族常量单分割（非多起点扫描）。
**试验量归因【§1.4】**：本批新增试验数=30（RETAIL_QUANT_TRACK §四 30 天 ≤500 预算内）——一句话归因：A13 正信息发现（2/12）的下游指针兑现+MP1 5 门 never-tested 新面首测，30 格=3 特征×5 员×2 面的最小完备覆盖（嵌套分解三面不可再省）。
