# DIGEST 2026-11-09 · r1450 bm-c · 再平衡许可面

正身 = `scripts/etf_book_rebalance_permission.py`（selftest 9/9 · `check` 6/6 0.1s）
+ `results/etf_book_rebalance_permission.json`
+ `research/ETF_BOOK_REBALANCE_PERMISSION.md`
+ 方法论卡 `knowledge/METHODOLOGY_ASSETS.md` E457
+ S6 腿 `rebalance_permission`（0.1s，紧接 `etf_book_size_rulers`）

## 问题

r1449 的五格表回答「争论有多宽」（15.14pp），没回答 2026-11-11 再平衡能不能保持
在途仓位 k=0.460253（CNY 459,796 / NAV 1,000,000）。

## 规则（先冻结）

1. **支持** = 读数落在钱之上或与钱同高（k ≥ k_now − 0.5pp）。一个会把你配得**更大**的读数
   确实允许现在的仓位；落在钱下方的读数否决它。「等于钱」不是支持的判据（那只有题面自己）。
2. 读数分三类，且**没有一类是默认**：
   - `circular`——票面自己的构造。它的 k 与 k_now 差在发布精度内（票面印 6 位，构造面存全精度），
     恒等一旦不成立整张面拒绝分类（UNREADABLE），不许把「恒等没验过」当成「这条读数独立」。
   - `static`——读数自己的注记声明是静态组合（分母面：今日 5 名全投入 ÷ covered weight）。
   - `path`——在决策 bar 上量出来的（bars ≥ 60）。少于 60 根的格子判 unreadable，不默认进 path。
3. `permitted_k` = 可读 **path** 读数的最小值；`keep_allowed` ⇔ 有 path 读数落在钱之上。

## 读数

| 读数 | k | vs 钱 (pp) | 类别 |
|---|---|---|---|
| baseline_published | 0.460253 | +0.00 | circular（票面自己的构造） |
| universe | 0.432195 | −2.81 | path |
| window | 0.412669 | −4.76 | path |
| window_x_universe | 0.393073 | −6.72 | path |
| denominator | 0.544424 | +8.42 | static（静态组合，非路径） |

判决 = **KEEP_STANDS_ON_NON_PATH_ARGUMENT**：三条决策路径全在钱下方（最高 0.432195），
唯一在钱上方的是那把静态组合分母。因此 2026-11-11 再平衡应落到 **k=0.393073（CNY 392,616）**，
即减仓 **CNY 67,180（6.72pp）**，除非先落一份口径预注册（r1446 的四项要求）。

供应侧（读来照印、不重判）：`nobond_vt08_adopted` = CONDITIONAL，唯一失败项
Y4_top2_share 0.7108 vs 线 0.70。

## 三条可复用

1. **「有尺子说能更大」≠「现在的仓位被允许」**。把 max 当许可读完瞬时是 keep（0.5444），
   而没有任何决策路径站在钱上方。面上同时印出这个陷阱与正确判词。
2. **自指读数必须显式排除**：题面自己的构造永远在场，取最小值就永远等于钱本身，那张表会
   永远回答「保留」。区分 circular/path 而不是简单取 min/max，是这张面唯一有内容的地方。
3. **恒等断言按发布精度比，不按浮点精度比**：票面 k 印 6 位（0.460253），构造面存
   `0.460253452`；用 1e-9 判恒等会让整张面在舍入上拒绝运行（本窗首跑 rc1 实弹，改正后
   9/9 + 6/6）。

## 本面未测

- 包装层的逐年形状（beta 叠层 + GC001 现金腿从未过年度闸，r1438）：k 变小不等于书变好。
- 哪把尺子是**正确**的度量：四格跨度是尺子选择，口径预注册未落地（r1446）。
- 减仓成本：票面自己的重定价 delta（CNY 91.7 @ 11-06 bar）没进闸，6.72pp 的减仓再付一轮 8bp。