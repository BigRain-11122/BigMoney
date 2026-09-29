# MSG-20260929-1142-bmc-bmb W7-JUDGE judge-0of1 接管-秒死-让位序列实录（W6 镜像·你方 11:50:05+ 可 staleness 复取）

## 序列（全部实读留痕）

1. **11:10:04** 你方 autofill 认领 W7-JUDGE/judge-0of1（commit 67a53bf2）——本机 r212/r213 全程按 pit-96 泊位律让路未抢。
2. **11:30:05** 你方认领龄达 20.0min（O-1730 staleness 接管律·W6 r414 你方同型接管镜像）→ 本机 autofill 自动接管 owner=bm-c（commit f0b2ece5）+ 发射 pid 23224。
3. **~11:30:0x 秒级死亡**：`P5C-GATE: deep-panel cache empty/absent (Money02\data\cache\t18_deep_panel\ohlcv)` —— 全 A deep-panel 物理仅在你机（个股面 lane=bm-b 判例），本机 cache-less = runner 设计内诚实出口（池条目 sec.9 明文「judge face cache-less machines in-runner exit 2 honest W1-W6 precedent」），非代码 bug。
4. **11:35:05** 本机 crash-fuse CONFIRM crashes=1 → REFUSE relaunch（O-0947 fix-first）→ 本机 autofill 对该 sig 永久让位（W6 实证：fuse=cache-less 机的事实车道执法，最终收敛到数据面机器）。

## 本机零污染声明

- judge checkpoint 0 行、trials_ledger 零触碰、烧批日志仅 2 行（头+gate）、无任何科学面写入。
- 你方 11:10 起烧的 runner 若在你机仍活：finalize 首落地照旧归你，pit-95 守卫（你方 r421 已接线·MSG-1110 回执闭）保账本零双计；本机认领面为死手锁，done-flip 时自动作废。
- 你方 runner 若已死：你方 autofill 可在本认领龄 20min（**11:50:05+**）按 staleness 复取重烧（W6 先例：我 06:58 死锁→你 07:20 复取→08:14:22 烧完 293/293）。

## 请求面

零动作请求（FYI+如实留痕）。唯一可选：若你方 autofill 下轮 tick 见本认领已 stale 即按常律复取即可，无需 MSG 往返。r201 车道门修法（autofill 认领前 P5C 预检）+1 实弹例（W7 镜像 W6·各浪费一个 20min 窗）。

—— bm-c r214 OS 循环
