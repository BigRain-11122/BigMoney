# LHB 席位级全史拉取预注册（LHB_SEAT_PULL）· 跑前写死

> 认领：**MSG-20260923-1958（先于本批任何拉取）**·车道：P-A 线续作（R15 指针⑤ 探针已毕=FEASIBLE）。
> 性质：**纯数据工程**（零 IC、零引擎跑、试验账本 N 不动）；数据消费（lhb_seat_top5_conc 复活因子批）=数据落地后**另开预注册**。

## §1 来源与探针实证（跑前事实）

- 探针（scripts/pa_seat_source_probe.py v1/v2 两轮，results/shortline/pa_seat_source_probe.json）：**FEASIBLE**
  - v1 教训（如实记）：vendor 接口要 `YYYYMMDD`（我传 ISO 致 TRADE_DATE 过滤器拼接损坏）+ vendor 无 UA 触发 datacenter 限速（与 R16 诊断的 push2 家族同病）；`stock_lhb_stock_detail_sina` 在 akshare 1.18.96 中不存在
  - v2 实证：vendor 正确格式=通；**直连+浏览器 UA=通**（首航取 2026-09-21 两股 5/5 席位、000667@2015-06-15 10/10 席位=**2015 历史深度可达**）
- 端点：`https://datacenter-web.eastmoney.com/api/data/v1/get`，reportName=`RPT_BILLBOARD_DAILYDETAILSBUY`（**单报告含买卖双侧**：BUY/SELL/NET/OPERATEDEPT_NAME+CODE/TOTAL_BUYRIO/TOTAL_SELLRIO/TRADE_DATE/SECURITY_CODE/TRADE_ID/EXPLANATION 等）
- 在库事件基线：`Money02/data/lhb/lhb_detail.parquet` 227,662 个股-日（P-A 去重口径）用于首窗码集交叉验证

## §2 拉取设计（写死）

- 覆盖：2007-01-01 → 2026-09-22（开区间尾）；**十日历日窗口**（2015 热月最大块保险），窗口内无码过滤（全市场）+ `pageNumber` 步进 `pageSize=500`，页上限 2000/窗
- 礼貌性：请求间 0.4s；失败退避 5s/15s/45s ×3；**窗口级持续失败=写检查点即停（exit 3，可续传）**——不复读机式硬顶限速源
- 断点续传：`Money02/data/lhb_seat/state.json`（windows_done 清单/rows_total/errors/next_window）；重启跳过已完窗口
- 存储：`Money02/data/lhb_seat/lhb_seat_YYYYMM.parquet` 月块（UTF-8 原生 parquet；续传时读旧块合并后**全列精确去重**再写）
- 状态镜像（tracked）：`results/seat_pull_status.json` 每窗更新（updated/windows_done/rows_total/done_pct/last_error/done）——机队可见+compute_audit 产出证据
- 控制台输出纯 ASCII（防 PS 控制台编码坑）

## §3 校验门（首窗硬门，不过=停不拉后续）

1. 行数>0（首窗取 2026-09-11→09-21=已知有事件段）
2. 必需字段在（TRADE_DATE/SECURITY_CODE/OPERATEDEPT_NAME/BUY/SELL）
3. 全部 TRADE_DATE ∈ [窗起,窗尾)
4. **码集重叠**：本窗 SECURITY_CODE 集合 vs 在库同窗事件代码集合，重叠率 ≥ **0.90**（源侧榜单口径可能略有差异，0.90 为「同一宇宙」判定线）

## §4 预测（跑前写死，跑后对账）

1. 总行数 **200-450 万**（227,662 事件 × 8-20 席位行/事件）
2. 总时长 **2-4 小时**（~5,100-9,700 请求 @ ~1.3s 含礼貌间隔；~480 空窗 1 请求/窗）
3. 最大月块=2015-05/06（单月 15-40 万行）
4. 失败模式=限速突发（退避+检查点停护栏）；若 2026 首窗即空=源口径变更（诚实停+复盘，不换过滤语法硬试）
5. 2007-2010 早期席位数据可能稀疏/营业部口径变更（如实记录，不裁不补）

## §5 账本与禁令

- 纯数据工程：**引擎账本 N 不动**（P-A/P-4-2a 先例）；无 IC 计算
- 跑后禁令：不裁数据、不重拉已完窗口、不因「看起来不对」改过滤；数据质量读数=消费端预注册的事
- 写域红线：仅 `Money02/data/lhb_seat/` 新目录 + `results/seat_pull_status.json` 镜像；不碰既有任何文件

## §6 产物

`scripts/lhb_seat_pull.py`（一次性定稿+可续传）→ `Money02/data/lhb_seat/`（月块+state）+ `results/seat_pull_status.json`；§7 结果段跑毕一次追加（跨夜跑期间以状态镜像为实况）

## §7 跑后实证（跑前禁触）

（空——跑毕填写）

## §3.1 跑后修正案（证据型 · 2026-09-23 20:05 · 首窗门触发诚实停后的诊断定案）

- **触发**：首窗码集重叠 0.8894 < 0.90 → 按预注册停（未拉后续窗口）
- **诊断**（scripts/lhb_seat_diag.py 全留痕）：缺口 24/217 码在 **bulk 窗口报告与 SELL 报告双缺**（union 补 0/24）；**但个股详情端点对 3 试缺码全覆盖（各 5 买+5 卖席位行）**→ 缺口性质=**bulk 报告覆盖差（~11%），非源缺数据**
- **修正案（三项，全部证据驱动）**：
  1. 门改「**覆盖记录制**」：实测覆盖记录入档（硬下限 0.50=拉取坏才停）——原 0.90 为跑前对「同宇宙」的猜测，诊断证明缺口可补救，按原设计意图（全在库事件覆盖）改两段式而非放宽门
  2. **两段式设计**：Stage 1=bulk 窗口（预计 ~89% 事件覆盖）+ **Stage 2=个股端点回补**（在库去重事件 − Stage 1 已覆盖，逐事件 1 调用——BUY 报告含双侧；~11%≈2 万级调用）
  3. **礼貌间隔 0.4s→2.0s**（bm-b r39 同网络实证：EM datacenter 家族突发限流、建议 ≥3-5s 级限速+指数退避；取 2.0s+既有退避/检查点停护栏折中）
- **修正后预估**：Stage 1 约 3-6h + Stage 2 约 8-14h（2s 间隔）→ 跨夜至次日，全程可断点续传、状态镜像每窗/每百事件更新（算力审计可见产出）
- 修正案性质声明：此为**数据工程覆盖门的证据型修订**（bulk 报告覆盖性质实测后按原设计意图补救），非统计门放宽；跑后禁令对因子层照旧不变
