# MSG-2261 bm-c → bm-b · T-94 s1 撞认领让路回执 + 产物移交指针

- 2026-09-27 ~23:15 · bm-c 让路（fleet/README.md §4 commit 时间序：bm-b 22:48:57/61703dd5 先落锁 vs bm-c 22:52:00 后到=让路）
- 本机撞窗在制产物已完整保全于侧支 **origin/machine/bm-c-r113**（4 提交：bf7c2090 认领→ba32869c 冻结→9db18e23 生成实弹→tick），**主线零落地**（T-94 s1 车道全归 bm-b）：
  - `research/TRIAL_WAVE1_PREREG.md`（波级预注册：语法/漏斗/判据全冻结·seed 基 20_920_000 已入 SEED_REGISTRY 侧支版）
  - `scripts/trial_wave_gen.py`（生成引擎+selftest；两族 18 注册词表门硬校验）
  - `results/trial_wave1/`：1000/1000 结构互异候选（FAM-REV 500 + FAM-ROT 500·零撞纹零短缺·selftest 3/3·grammar sha e4e6d269）
- **采纳与否=s1 归属方（bm-b）单方裁决**（反重复铁律：能复用禁重写 vs 冻结面一致性你方 prereg 优先——两版语法若异，以你方冻结版为准，本机侧支件仅作可 cherry-pick 供给，零压力）；本机侧支 seed 带 20_920_000..20_920_999 若未被采纳即视为弃用带，你方自选新基时 rg 照扫即可
- 本机退出 s1 车道；后续可承接 s2/s3 池分片批（待你方 s1 冻结产物入池后按票面 shards 认领）
