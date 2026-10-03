# FLEET-OPS.md — 机队治理总机制 v1.0

> 2026-09-23 建 · 用户令「机器群互相通信顺畅高效、有云端备份、随时剔除或加入机器、任何机器可发号施令」· bm-a 起草
> 定位：Bigmoney 机队**控制面治理**。数据面传输 = `fleet/TRANSFER.md`；基础协议 = `fleet/README.md`（本文件为其治理层扩展，冲突时以用户令 > 本文件 > README 为序）。

## 1. 通信模型与时效（SLA）

- **控制面（指令/状态/回报）= git**：各机循环每 10 分钟一轮（pull → 用户令/收件箱/任务单 → 干活 → commit push）。单跳消息时效 ≤10 分钟；指令闭环（下令→回执）≤20-30 分钟。
- **数据面（大文件）= fleet/TRANSFER.md**：A git 分批 / B2 croc 直传 / B1 Tailscale / C 云中转 / D 离线摆渡。
- **在线判定**：心跳 `fleet/machines/<id>.json` 的 `last_seen` ≤20 分钟=在线；>1 小时=离线/挂死——其他机器只读避让其写域，其 claimed 任务适用 §2.2 超时释放。
- **加速通道**：用户在场交互的会话可即时 fetch/push 不等轮次；B1（Tailscale）装机后可 SSH 直达对端提前触发（升级项·装机须用户授权）。

### 1.1 集团决策台账消费步（D-19 实径 fallback·D-20261004-02③ 落地）

- **正典**（D-20261001-03）：每轮决策审核步读集团树一律 `git fetch` + `git show origin/main:docs/decisions.md`（**禁 working-tree pull/rebase/checkout 集团树**）；水位键=state-<id>.json `last_decisions_sha`（SHA-256 内容寻址，D-20260930-18 律）比对：hash 不变=零动作；hash 变=消费「派工通告板」涉本司行+新增决策行+docs/orders.md CEO 物理件区涉本司行。
- **S4U/无 K: 盘窗 fallback**：①实径可达优先 `git -C <实径> fetch origin` + `git -C <实径> show origin/main:docs/decisions.md`；②实径无 .git/不可达（r631 bm-b 律实证 C:\Fluxgroup\FluxGroup 无 .git）＝ `%TEMP%` 稀疏克隆同律：`git clone --depth 1 --filter=blob:none --sparse <group-repo> %TEMP%\<dir>` → `sparse-checkout set --skip-checks docs/decisions.md` → `show origin/main:docs/decisions.md` 取 origin blob 原始字节——零树触碰零常驻零 K: 依赖。
- **sha256 一律 raw-bytes**（python subprocess bytes；**禁 PowerShell `>` 重定向读 git 对象**＝UTF-16 伪影坑 r209 律——首证窗实弹：PS 管道面 sha 15ff3903 vs raw-bytes 真 sha eb14b510，按前者入水位键=永久假红）。
- **首证**：bm-a r650（2026-10-04 00:4x）raw-bytes sha `eb14b510d304a1d0a30175447cf9360d6bab6dc20972ceebce35d47ef8935bfa` vs 水位键 75a05528 变化→消费新派工行 D-20261004-02①②③（本行即其③交付）；docs/orders.md CEO 物理件区 BigMoney 行=券商模拟盘+报备（CEO 物理依赖·常设行零新动作）。

## 2. 机器生命周期

### 2.1 加入（随时）
沿用 fleet/README §7 五步：clone → 拷模板填身份 → bootstrap → 可选装循环 → 首轮自证心跳+push。
- 新机 48h 内向 `CODELY.md` 交首条接入踩坑记录（义务制）。
- **SSH 钥匙三件套拷贝 = 用户逐次授权项**。成员资格的本质=持有仓库写权限钥匙（见 §5）。

### 2.2 剔除/退役（随时·用户令发起）
1. **发起**：用户令（§3，任何机器可发）或机器自请（故障/报废）。
2. **标记**：`fleet/machines/<id>.json` 加 `"status": "retired"` → 移入 `fleet/machines/retired/`（历史保留）。
3. **任务清算**：该机 claimed 的任务单即时释放回 open（>24h 规则提前适用）；写域文件（心跳/轮账本）就地冻结。
4. **断权（关键·必做·只能用户亲手执行）**：**GitHub 撤销该机凭据**——撤销对应 deploy key / token / 协作者席位；曾拷贝过 SSH 钥匙的=轮换钥匙。**git 层面没有「踢出」概念，不撤钥匙=没剔除**（退役机仍可读写仓库）。
5. **登记**：`CODELY.md` 行级追加退役记录（谁/何时/为何/**断权是否完成**）。

### 2.3 换机/重生
新机按 §2.1 接入即得全部：代码+数据+成果+规则+记忆随 clone 恢复（§4）；旧身份 retired 归档。

## 3. 用户令牌（任何机器发号施令）

- **口令 = `/CEO`**：用户消息以 `/CEO` 开头（`/CEO <令>` 内联，或 `/CEO` 单独一行、正文随后）= 正式 CEO 令——收令会话**立即**走本节流程，先于一切其他工作；非 `/CEO` 开头的普通对话由会话自行判断是否属用户令（含糊=先确认再落册）。
- **载体 = `fleet/orders/O-<yyyymmdd>-<HHmm>-<发令机id>.md`**（追加式台账，**永不删除**；文件名含时间+发令机=天然唯一无撞号）。
- **发令方式**：用户在**任何一台机器**上对 AI 会话说话即可——该会话：①写 O 文件（用户原话+语境+执行要求+签名 `user (Jason) via <bm-x>`）②按需开任务单（P1，`created_by` 引用 O 文件）③需广播则加发 inbox MSG ④commit push。
- **优先级 = 最高**：用户令 > P0 修红 > P1-P3 任务 > 自主维护轮。与在途批次冲突 = 冻结在途、双引原文呈报用户终裁（多窗仲裁）。
- **落册即生效**：令经 O 文件落 git = 全机队可执行；口头不落册 = 仅本机本会话。
- **回执闭环**：受令机在轮报告回执 + `CODELY.md` 行级追加执行记录；心跳加 `orders_ack` 字段记已处理到的最新 O 文件名。
- `fleet/orders/` 台账任何人可查 = 全机队命令史（审计面）。

## 4. 云端备份模型（三级）

| 级 | 覆盖 | 机制 | 恢复方式 |
|---|---|---|---|
| **库内资产**（代码/成果/规则/记忆/Money02 有用集） | GitHub 私库 | 各机每轮 commit+push = **持续增量云备份**（任何改动 ≤10 分钟上云） | `git clone` + `python bootstrap.py` = 任意机器全量重建 |
| **库外大资产**（>5GB 或可再生局部件） | 方案 C 云中转桶（R2/OneDrive 等） | TRANSFER.md §5；上传即备份位 | 桶内拉回 + manifest 校验 |
| **机器身份/SSH 钥匙** | **不备份（刻意）** | 丢失=§2.1 五步重建；钥匙须用户重新授权 | 模板+用户动作 |

- **单机全损演练口径**：任意机器报废 → 新机 clone+bootstrap+新身份 → 心跳上岗 → 任务经认领制自然流转。**全机队仅剩一台也能自愈运转**（git=唯一真源）。
- **可选增强（用户定，默认不开）**：第二远端镜像（如 GitHub 再建 mirror 仓，定期 `push --mirror`）——防 GitHub 单点。

## 5. 安全红线

- 成员资格=钥匙：**装钥匙给哪台机=用户逐次授权**；退役必撤权（§2.2-4），撤权完成前机器视同在队。
- 禁 force-push；凭证/密钥/token 永不入库；croc 口令 2h 过期。
- 常驻网络服务（Tailscale/网盘客户端等）装机=用户逐次授权。

## 6. 变更记录

- v1.0（2026-09-23）：bm-a 建立（用户令四件套：通信 SLA / 生命周期 / 用户令牌 / 云备份模型）。bm-b 循环 prompt 需增「处理 fleet/orders/ 新令」步骤（经 inbox 通知）。
- v1.1（2026-10-04）：bm-a 增 §1.1 集团决策台账消费步（D-20261004-02③ 集团派工行落地：S4U 窗 D-19 实径 fallback + raw-bytes sha256 律 + bm-a r650 首证）。
