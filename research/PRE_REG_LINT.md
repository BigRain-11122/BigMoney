# 预注册能不能被定价（r1963）

工具：`Tools/pre_reg_lint.py`（selftest 8/8）· 证据：`results/pre_reg_lint.json` · 语料：`research/**` 文件名含 prereg 的 449 份（另跳过 1 份 digest=文件名撞词，非预注册）

## 一句话

在这套公司里，一份预注册的价值在于「它的结果事后能不能被定价」——而定价要有试验数 N。全语料里 **435/449 份写了 N**，剩下 **14 份没有**（10 份是活的批，4 份是单事件 CASE 复盘）；更要紧的是**模板自己漏了出场轴字段**，所以 449 份里有 96 份没写出场轴不是作者疏忽，是模板没教。

## 六栏覆盖（逐栏=该栏能从文件正文里读到）

| 栏 | 覆盖 | 漏掉意味着什么 |
|---|---|---|
| 批件身份 | 449/449 | 无 |
| 试验数 N（批内格数） | 435/449 | **无法做 DSR 校正**——夏普变成一句没有分母的话 |
| evidence_cutoff | 439/449 | 样本外锁盒无法复核 |
| 出场轴 | 353/449 | 判词测的是「策略+引擎缺省出场」的混合物 |
| α 机制（D6） | 112/449 | 讲不出为什么该有超额，也不知道谁付钱 |
| 种子闸记录 | 135/449 | 随机对照的选点不可复现 |

六栏全齐的只有 **12/449**。

## 模板自己的一栏

`research/PREREG_TEMPLATE.md` 被本工具读出漏 `exit_axis`：模板从头到尾没有「出场轴三选一」这一节（O-20261001-1108 §4 要求必填）。因果很直接——模板不教，作者不写，96 份缺出场轴里绝大多数是照模板抄的。**这不是 96 个人的错，是一处模板缺口放大了 96 倍。** 修模板=改共享面，本轮在竞争窗内，留待落窗后补。

## 没有 N 的 10 份活批（点名）

| 文件 | 缺 |
|---|---|
| research/A158_TSGATE_P1_PREREG.md | trials, exit_axis, seed_gate |
| research/AGGR_FAMILY_PREREG.md | trials, exit_axis, seed_gate |
| research/ETF_BOOK_SIZING_PREREG.md | trials, cutoff, exit_axis, mechanism, seed_gate |
| research/GATE_RECHECK_A158_PREREG.md | trials, exit_axis, seed_gate |
| research/GATE_RECHECK_MP1_PREREG.md | trials, seed_gate |
| research/INNOVATION_QUOTA_W11_PREREG.md | trials, exit_axis, seed_gate |
| research/PREREG-20261113-Y4-SCALE-FREE.md | trials, cutoff, exit_axis, mechanism, seed_gate |
| research/SCIENCE_AUDIT_S9C_AMEND_PREREG.md | trials, cutoff, exit_axis, mechanism, seed_gate |
| research/SYSTEM_V1_PREREG.md | trials, cutoff, exit_axis, mechanism, seed_gate |
| research/shortline/OPTIONS_IV_PREREG_ROADMAP.md | trials, cutoff, seed_gate |

其中 `ETF_BOOK_SIZING_PREREG.md` 最贵：它把 ±12.18pp 的 k 带宽钉死（306 bar 窗口读出），却没写这次钉带宽用了几次尝试。带宽的宽窄本身就是可调参数，没有 N 就没有「这根带子是不是为了好看才这么宽」的答案。

## 这个数字为什么是钱

r1960 已经算过：这本书原始夏普 1.101，但把搜索租金按可核尝试数扣掉（N=5 就要夏普 1.131）它跌破 DSR 0.95 线。也就是说**同一个 11.16% 年化，在「写了 N」和「没写 N」两种世界里是两个结论**：写了 N 你能知道它够不够；没写 N 你只能选择相信或不信，而这两种都不是证据。

## 边界（本面不宣称的）

- 读法是正则，不是语义。一栏写在散文里（例如「我们试了三种带宽」）本工具读不到，会算缺；反过来写了个数字也不代表数字是真的。工具治的是「一个字都没写」，治不了「写了假数」。
- 4 份 `CASE_PREREG_*` 是单事件复盘，试验数可能天然不适用——本面把它们单列（case 4），不算进活批缺口。
- 只扫文件名含 prereg 的 md。预注册写在别的文件名里的（若存在）看不见。

## 怎么用

```bash
python Tools/pre_reg_lint.py --selftest                  # 8/8
python Tools/pre_reg_lint.py research/FOO_PREREG.md      # rc0=FROZEN_OK / rc1=点名缺栏
python Tools/pre_reg_lint.py --scan                      # 全语料 -> results/pre_reg_lint.json
```

冻结门接法（落窗后）：新批 commit 前跑 `python Tools/pre_reg_lint.py research/<BATCH_ID>.md`，rc≠0 = 不冻结不烧。
