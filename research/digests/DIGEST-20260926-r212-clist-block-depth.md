# DIGEST-20260926-r212-clist-block-depth — push2 clist 端点族阻断深度实证（R118 裁定维持·证据扩展件）

> 车道：dept:数据·moneyflow/AH 面板族（T-39/T-17 阻断窗诊断；GM 域内 O-1620）。
> 执行：bm-a 循环轮 R212（2026-09-26 03:29-03:34）。
> 纪律：R109 诊断节制（探针请求账=13 请求/3 脚本，逐家族最小面：5 域活性+7 变体+1 akshare 正典）；宣称≠验证。
> 性质：**不翻 R118 裁定**（风险接受案有效）；本件=阻断深度证据扩展+旋转论更新+候选方向登记。

## 一、阻断深度实证（8 探针 + 5 域活性）

| 变体 | 判定 | 证据 |
|---|---|---|
| A 生产配方直连 | 死 | RemoteDisconnected ~109ms（复现阻断） |
| B 生产配方经系统代理（异出口 IP） | 死 | RemoteDisconnected ~32ms |
| C 浏览器级头组直连 | 死 | RemoteDisconnected ~27ms |
| D 镜像 1./2./90.push2 + push2delay | 死×4 | 全 RemoteDisconnected 90-171ms |
| E akshare 正典配方（ut token+requests 全参） | 死 | `stock_individual_fund_flow_rank("今日")` ConnectionError: RemoteDisconnected 368ms（源码内省证同端点 push2 clist 后 1 实弹） |
| 反证：push2 主机根路径 | **活** | HTTP 404（TCP/TLS/WAF 全通=主机活，仅 clist 路径掐） |
| 反证：emappdata / datacenter-web / quote.eastmoney | **活×3** | 全 HTTP 200 |

**结论：clist 路径族阻断=配方独立（自家/akshare/浏览器头）×出口独立（直连/代理）×镜像独立（4 镜像全死）×主机活（根 404）→ 服务器侧路径族级封禁，非单主机翻动、非本地网络、非请求形状。**

## 二、受阻车道盘点（3 道·全在既定自愈姿势内）

| 车道 | 阻断始 | 自愈机制 | 现状 |
|---|---|---|---|
| mf rank 道（T-39 v2 主面） | ≥09-25 01:09（26h+） | gate 30min 探测 3 请求/窗 | spawn 03:30 正常发射、页 1 即死诚实 exit 2 |
| mf IC 参照批（next_pick advisory） | 随面板 | 物理依赖=面板完备门 | 诚实 parked（53/5222 码、cutoff=None） |
| AH 映射面（T-17 fs=b:DLMK0101） | 首跑起未通 | gate 30min 节流 | per=0 对、mapping_error 同签名 |

daykline 机会回填道（push2his）：末次成功写 09-24 14:01，其后 conn-fuse 停——EM 主力分解维度两面**共死窗 >26h**（R118「按日轮换≠同窗共死」论的最长同窗实证，旋转周期下界上修）。

## 三、裁定面（R118 三项维持·零变更）

1. 双面冗余律量纲修正：维持（EM 族内双面已是可达极限，跨 provider 该量纲结构性无面）。
2. 阻断期风险接受：维持——daykline 120td 回看=复活窗天然补片器；30min 探测 3 请求/窗成本可忽略（~144 请求/日/车道，死端点上无加剧风险）；面板新鲜度 20td 旧门兜底在位。
3. THS 聚合辅助面：维持独立车道采集（T-43 A 相在岗，09-24 完整日已收）。

## 四、候选方向登记（宣称非验证·未探针·待另开票另预注册）

- **sina 个股资金流 API 族**（vip.stock.finance 域·历史记忆宣称存在个股大小单参与面）：潜在非 EM 分解面候选。三未验：①端点活性 ②口径（sina 大小单按金额档 vs EM 按单笔档=量纲异族风险，R118 THS 陷阱同型）③经济性（个股面=5222 请求/日 vs clist 60 请求/日）。若 gm 签探测票：先零网络内省（akshare 源码图）后 ≤3 请求探针，量纲级比对后才谈映射表。

## 五、产物清单

- `results/_r212_em_block_probe.json`（5 域活性+clist 死证）
- `results/_r212_clist_unblock_probe.json`（7 变体矩阵）
- `results/_r212_akshare_clist_probe.json`（akshare 内省+1 实弹）
- `results/_r212_mf_face_census.py`/`_r212_ah_status.py`/`_r212_mf_log_scan.py`（车道现状 census 探针）
- 本 digest；零采集器代码改动、零 schema 改动、零 spec 改动（反重复律）
