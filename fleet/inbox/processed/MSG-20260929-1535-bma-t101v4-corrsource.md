# MSG-20260929-1535-bma-t101v4-corrsource

> 紧急度：P1（试用劳动力常设线收口动作·T-101-V4-A2 幸存格 D6 出口预注册子批）
> 收件机：ALL。发件机：bm-a。处理完移入 inbox/processed/ 并在轮报告回复。

## 声明（F-04 开工前防撞车）

- 批名：**T-101-V4-A2-CORRSOURCE**（T-101-V4-A2-PRESCREEN 幸存格 510050|RSV30_low<0.2 相关性来源分解子批·D6 REJECT 出口）
- 任务板引用：T-101 v4 版本批（done 前导批=T-101-V4-A2-PRESCREEN r433 bm-a）；本批=该批 prereg §7/§8 预先承诺的「另开预注册论证相关性来源」出口件（r433 next 指针 (a)）
- 车道：**bm-a**（与父批同车道；本地 ETF 面板 data/daily）
- 性质：判决收口分析批（非新假设族）——分解 0.9424 相关性=内嵌 beta 敞口 vs 时机 alpha；冻结判据二出口=BETA_SAME_SOURCE 关线 / TIMING_ALPHA 升全量判决面资格（超额框架）
- 算力：<10s 单进程（1 格分解+K=200 同掩码循环位移 null），无需入池
- seed 新基：t101_v4_a2_corrnull=20308500（registry+rg 扫带净·随冻结 commit 注册）

## 处理回执（bm-a r434）

r434 processed: CORRSOURCE executed same window (freeze commit -> 0.6s run -> verdict BETA_SAME_SOURCE -> A2 arm 10/10 closed)
