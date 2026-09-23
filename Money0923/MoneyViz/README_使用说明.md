# MoneyViz《进化竞技场》使用说明

## 怎么打开（3步）

1. 用 Tuanjie Hub 打开 `MoneyViz` 工程（编辑器此刻应已开着）。
2. 让编辑器重新编译（切回编辑器窗口即自动刷新；或菜单 Assets→Refresh）。
   - 可选验证：菜单 **Tools → MoneyViz → 数据自检**，Console 会打出全绿报告（不需要按 Play）。
3. 按 **▶ Play**：`VizLauncher` 自动接管任意场景，程序化搭建整个竞技场（无需手工摆任何物体）。

## 画面怎么看

| 区域 | 内容 | 数据来源 |
|---|---|---|
| 顶部中央 | 当前进化代数 / best / mean 分数 | evolution.history（每2秒刷新） |
| 左侧擂台 | Top10 循环迭代擂台：小人=选手，地台高度=真实适应度；种群收敛期自动切"最近各代最优"并如实标注 | evolution.top10（已去重，防克隆军团） |
| σ 风暴条 | 变异步长热度（停滞自适应触发时变红+闪电特效） | history.sigma_boost |
| 右侧冠军殿堂 | 现任冠军+样本外指标；冠军换人时有登台+皇冠落下+彩带加冕动画 | champion.* |
| 左下账户 | 现金/轨道权益/高水位/持仓数/今日晋升尝试 | account / paper_track |
| 底部 | 账户权益像素曲线（冠军定型后逐日推进；首日为虚线占位） | paper_track |
| 右上时钟 | 开市倒计时/交易时段（读交易日历） | data/trade_dates.csv |
| 顶部警报 | 风控停机/日熔断红晕脉冲 | risk.* |
| 市场风格行 | 趋势/因子风格/宽度/波动/当前最适族 | regime.snapshot |
| 锦标赛行 | 周度锦标赛战报（百人同台，最佳选手+收益） | arena.last_tournament |

## 两种模式

- **实时模式**（默认）：自动向上级目录找到 `Money/state/state.json`，每 2 秒刷新——交易系统在跑，画面就是活的。
- **演示模式**：找不到 state.json 时自动合成数据，保证打开即有画面（左上角会红字标注"演示模式"）。

## 已修复的关键问题（2026-09-19）

1. `VizBootstrap`：`GameObject.color/sortingOrder` → SpriteRenderer（编译错误，此前 Assembly-CSharp.dll 从未编译成功）
2. `StateFeeder`：double→float 显式转换 ×5
3. `MiniJson.SkipWs`：不再把逗号当空白跳过（此前每个对象只解析出第一个键，数据链路整体截断）
4. 交易系统 `evolve.py`：top10 快照按（策略+参数全值）去重（此前擂台显示一排克隆人）

## 验证链（无头，可复跑）

```
cd tools/csharp_check
dotnet build MoneyVizCompile   # 引用真实 Tuanjie 程序集编译全部脚本
dotnet run --project MiniJsonHarness   # 38项数据契约断言 vs 真实 state.json
```
