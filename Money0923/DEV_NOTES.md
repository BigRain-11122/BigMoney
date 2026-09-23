# 开发状态笔记（进行中工作/待办/下一步）
> 新会话从本文件接续开发。AI/人可随时编辑；HANDOFF.md 每周期自动把本文件全文嵌入 §6。
> 记法：日期 + 状态（进行中/待办/观察/遗留）+ 上下文。完成的事项保留一行结论后移到底部归档区。

## ⛔ 全系统停机令（2026-09-22 21:50，用户指令"money有关的自动化全部取消掉"）

**Money 一切自动化已全部停止，任何新会话未经用户明确指令不得重启：**
- 守护进程：已树杀（最后 PID 62396），进程清零已验证
- 看门狗计划任务 MoneyAutoGuardian：**已禁用（Disabled）**，登录/每5分钟触发均失效
- state\watchdog_pause：在位（双保险，防误触发拉起）
- 会话级 cron：空（前一轮已清）
- 数据无损：state.json/联赛 28028 局/进化 2900+ 代/认证池 200/HANDOFF 全部保留在磁盘
- 停机时点状态：冠军 multifactor（0.5794）、三仓 S1 multifactor/S2 etf_trend/S3 small_reversal、账户 99,965（-0.03%）、守护已停故明日无模拟盘会话与备单

**恢复命令（仅用户明确下令时执行）**：
1. 删除 state\watchdog_pause
2. schtasks /Change /TN "MoneyAutoGuardian" /ENABLE
3. schtasks /run /tn MoneyAutoGuardian（或直接 python run.py auto）

## 进行中 / 待办

### 2026-09-22（本日）
- **15:17 一次性 cron（Codely 会话内）**：收盘后流程=全量 pytest → 看门狗单点重启，载入四项磁盘代码：
  ① arena.py 报表权益修复（verdict/top10 曾把现金当权益错报 -56.19% 假浮亏，改读 paper_track 收盘权益）；
  ② 国债逆回购全链路（quant/repo.py + paper/backtest/futures_backtest/decide/config/run.py 接线 + tests/test_repo.py）；
  ③ 周期交接文档体系（quant/handoff.py + HANDOFF.md + DEV_NOTES.md + tests/test_handoff.py，四钩子：守护启动/盘前会话/收盘结算/闭市进化轮）；
  ④ Token 经济机制（run.py ctx 极简快照 + HANDOFF §0 按任务选读表/危险文件警告 + 代码drift三态检测[空快照=未知] + README 顶部AI指引 + Codely记忆库105KB→4KB蒸馏，原文归档 .codely-cli/memory/archive_20260922_codely_full.md）。
  **新会话接手时先看 HANDOFF §6 "代码版本"行**：若显示 ✅ 一致则本条已完成；若 ⚠️ 有 drift 且 cron 已过期，按铁律收盘后自行执行"测试→看门狗重启"。
- **明晚观察项（2026-09-23 收盘起）**：模拟盘首次逆回购借出（日报应有"国债逆回购：借出 X 元"行）；eval_cache 因逆回购参数入指纹全量冷重刷（16-24 worker 分钟级重建属预期，勿误判为故障）。

## 观察项
- **新冠军 multifactor/inv_vol**（2026-09-22 01:36 上位，样本外分 0.5794）：S1 持仓仍是 low_vol 遗产 5 只（min_hold 3 日锁，2026-09-24 起可按 multifactor 目标调仓）——观察首次全仓周期的换仓行为。
- **联赛认证通胀控制**：200人×~1秒/局后认证流速暴涨，game_evo 流量带自动收紧（qualify_floor 0.48 实测），观察是否收敛到目标带 0.02~0.12人/局。
- **cta_trend（期货CTA）**：已进联赛未认证；认证需连续3局晋级。观察其 vs 股票族战绩（盈稳分口径）。
- **19 只 ETF 曾冻结在 2026-09-18**（多为 159xxx 深市，源限流）：若 S2 etf_trend 信号基于滞后尾部会在备单日志留痕，注意核实。

## 遗留（已知，按优先级）
- QMT 未装（用户自装客户端后系统启动时自动发现接入；mode=paper 期间勿催）
- ML 预测族（外部 SYSTEM_DOC 路线图项：LightGBM IC≈0.17）——待装包+训练管线，属下一个大特性
- 北向/龙虎榜数据层、深耕池参数敏感性 ±20% 扰动（外部路线图参考项）
- 股票池近似时点成分（幸存者偏差未根除，README 已录）
- 期货换月 splice 重写历史 → eval_cache 陈旧性（晋升闸用新数据复验，属设计内）

## 归档（已完成一行结论）
- 2026-09-22：国债逆回购三端一致上线（repo.py 全链路+六测试）；arena 权益 bug 修复；MoneyViz 加 200 人联赛直播线+认证星雨；分仓制首日实弹（09:25 六单成交）
- 2026-09-21：29→35 族；风险线按风格分级（S1 10%/S2 20%/S3 无停机线）；联赛批级常驻池 14秒→1秒/局；污染清除数据纪元机制；出局机制改革（收盘口径+毁灭线80%）；期货 CTA 全链路开闸
- 2026-09-20：晋升可观测性补丁；数据真实性闸；防降级换血修复
