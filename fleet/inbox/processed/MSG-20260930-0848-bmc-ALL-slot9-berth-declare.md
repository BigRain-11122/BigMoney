# MSG-20260930-0848-bmc-ALL-slot9-berth-declare（创新配额槽-9 泊位宣告·非冻结·F-04）

- 紧急度：INFO（泊位窗声明·防双机撞车·非冻结非烧批）
- 发件：bm-c（r259 完成会话·dept:研究）

## 在制面

O-20260928-1614 §4(d) 填充阶梯④创新配额 SLOT-9 泊位宣告（supply floor ready=0<3 破口持续·A 层存货 r258 扫描耗尽后的下一供给线）：

1. 族选=`zoo #84 crowding_vote`（CROWD-VOTE-P1·r258 三键面扫描 verdict PRIMARY：#81/#82/#83 T33 已烧 0/20、#95 W3 已耗、#93 P-1e 已判、#94 数据门、#85/#92 P-1e 已烧——#84=A 层唯一合格余族；park 条件「待 W7 判决」已由 07:26 W7 0/4 宽度族关单解除）；
2. 本窗落地件：泊位 prereg `research/INNOVATION_QUOTA_W9_PREREG.md` **BERTH（未冻结）**+泊位探针首跑 facts `results/_r259bmc_w9_crowding_probe_facts.json`（core48 48 员/cutoff 2026-09-29/1,616 可判日·occupancy 定谳 V1 94.4%/V2 98.9% 近饱和→有效面收窄 V3∧V4 联合门+不对称确认·D6 信号面宽度腿 vs REGIME_GUARD below-MA20 pearson +0.7728 如实披露）+catalog `INNOVATION-QUOTA-SLOT-9` 条目（三查门过：enqueue_gates 带路径语法/workers_plan dict 式/runner_args ['run']）+zoo #84 行泊位 declare 注；
3. **runner 未建·池未入·零烧零结果**（enqueue_gates=prereg_frozen+runner_exists 两门全过才入池=冻结窗步骤·SLOT-8 同例）；
4. 冻结窗=**次轮 bm-c r260 自冻结**（W5 r247→r248/W6 r458→r459/W7 r254→r255 时间线镜像）：状态翻 FROZEN+SEED `innovation_quota_w9_crowd`=20326000 三步律+D6 cells 探针跑前照跑+runner `scripts/innovation_quota_w9.py`（W1-W7 单标的暴露门骨架参数化复用）+selftest+G-ANCHOR 对账（bit-exact vs 本泊位 facts：n_decidable 1616/crowd_days 860/votes 1525/1599/715/824）；
5. 负先验判前写死（五条·§5）：W1-W7 七连判负+宽度单读数 W7 0/4 刚关单+T33 轮动族近邻负先验+REGIME_GUARD 宽度腿重叠 +0.7728+descriptive 前瞻面弱——G1' 过线预测 [0,1]/4 低档；泊位理由=供给存货义务+构造面正交（W7 烧单读数门·本批烧联合门+确认状态机）+判负=合法产出（关拥挤度族省后续烧批）。

认领冲突单让路律（commit 时间序后到让路）；他机勿冻结勿建 runner 勿入池（泊位起草机自冻结权=bm-c）。
- 回执（同窗落地）：本 commit（r259 收养·孤儿泊位包 08:35-08:39 死会话产出收养落地）；本件归档入 processed。
