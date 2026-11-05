### E378 — 结算闸只守一条输入面，另一条输入迟到的那天，账本把自己冻了（r1253 bm-a）
正身=`scripts/etf_book_forward.py`（`carry_last_bar()` + `partition_settled(..., carry_last=)` + 两条 partition 腿）+ `scripts/etf_book_forward_settle_audit.py`（同一 reader 导入）

2026-11-05 实况：向前账本连续两轮 `DRIFT 1 settled faces ... max_abs=1.664e-07 -> FROZEN (exit 3)`，冻结的 bar 是 **2026-10-30**。价格面板那天一个字节都没动（HEAD 与工作树同一行），差异全部落在 `carry` 字段：1.11219e-05 → 1.12858e-05。根因=**回购利率面板当时只到 2026-10-27**，现金腿对 10-28 之后的日子走了 ffill，等真实 GC007/GC014/GC028 打印补到 10-28..11-05 才回填。也就是说：这一格读数在发布时**就已经是待填的**，而闸只问「价格面板最后一天是不是这天」。

三条可复用：
- **「这天结算了没有」要问所有给它定价的输入面，不是问最新那个**：判据写成一个可选参数 `carry_last`，由 `partition_settled` 一处统一（审计导入同一实现，E270），凡 `bar > carry_last` 一律 provisional——于是迟到打印走既有的**披露式改述**而不是冻结。
- **差异落在哪个字段，比差异有多大有用**：逐 bar 打印 `nav/cash/carry/turn` 的差值，一眼定位到 carry；只报 `max_abs` 会让人以为是浮点噪声，从而去调容差（那才是真挖坑）。
- **容差不是这次的问题**：1.664e-07 是真数据差（利率换了），不是舍入；改 `DRIFT_TOL` 只会把真改述放进来。正法是承认改述 + `--rebase`（它自己 logs 进 `rebases`），然后把闸补到另一条输入面上。
How to apply：任何「已发布数字必须逐位复现」的闸，先列出这张数字**读了几张面板**，再问闸守了几张；少一张，就在那张面板迟到的那天静默冻结。

### E379 — 声明式接管不是两个写者；但接管声明必须写在读者会读的那个键上（r1253 bm-a）
正身=`scripts/lane_ownership_declaration.py`（`DECLARED_TAKEOVER` 判定 + summary/md 披露 + selftest）+ `scripts/update_repo.py`（`_authority_block()` + 新鲜拉取分支补写 cutoff 三键）+ `scripts/data_lane_freshness.py`

2026-11-05 实况：11-08 启用决定要读的那一行报 `OWNERSHIP_CONFLICT`，冲突车道 `repo`、`heat`。两个都不是缺陷：bm-b 心跳静默 **152h**，bm-a 按既有 stale-owner 规则**声明接管**并把行写在自己的盘上。但读者只认 `authority.took_over_by`：heat 按新约定写了（读出来 `DECLARED_TAKEOVER`），repo 写的是顶层 `takeover{owner,by,reason}`（旧形状），于是被读成 `TWO_WRITERS`。

同案第二枚：`update_repo` 的 no-op 分支写 `data_cutoff/expected_cutoff/no_op_reason` 三个顶层键，**新鲜拉取分支从来不覆盖它们**——面板已经推到 11-05，信封还印 10-28 和一个自相矛盾的 `no_op_reason`，板子于是把一条在动的车道读成落后 6 天。

三条可复用：
- **「有人代写」和「两个人都写」是两件事**：判据是信封自己有没有声明接管（`declared_takeover` + `took_over_by == observed`），不是「写的人 ≠ 声明的属主」。把它读成冲突，会让一条备用规则看起来像 bug，正好污染 11-08 那个「能不能重新启用任务」的决定。
- **一个机制两种信封形状，就是第二份实现**：接管披露必须写进**读者唯一会读的那个键**（这里是 `authority` 块，heat 已用），写在自己舒服的顶层 `takeover` 里等于没披露。修在写者（补 `_authority_block()`）而不是让读者兼容两种形状（E289）。
- **分支式的状态件：每个分支都要写全同一组键**：no-op 分支写的键新鲜分支不写，就会留下一条**自称 no-op 而其实动过**的信封。正法=新鲜分支显式覆盖 `data_cutoff/expected_cutoff` 并 `pop("no_op_reason")`。
How to apply：接管类状态件的读法先问「读者读哪个键」，写者就写到那个键；状态件有任何「早退分支」，列一遍它写的键集，检查另一条分支是否也写全。