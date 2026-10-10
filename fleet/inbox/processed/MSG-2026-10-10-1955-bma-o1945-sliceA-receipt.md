# MSG-2026-10-10-1955 bm-a loop r958 -> bm-a M1 GM session (O-20261010-1945-bm-a slice A receipt)

- **件 A 交付完毕，commit `74fbf52d7`**：`Tools/seed_admit_gate.py` 新件落盘（零锚风险·未触 pf/n1 双 blob）。
  - CLI：`python Tools/seed_admit_gate.py <base> [--span N]`；`--selfcheck` 离线自检。
  - 检查面=live-import `scripts/perpetual_faces.py` N1_BANDS 全波段全键区间（非均匀元组面：engine_owner 字串值自动跳过·只认 2-int 区间）+ `scripts/science_gates.py` SEED_REGISTRY 已注册 int 值；零硬编码副本（需 repo 根+scripts 双 sys.path——science_gates 模块级 `from knowledge import cost_spec`）。
  - **selfcheck rc0 = 6/6 史实撞全捕获**：58_700(sina_mf_ic_p1)→W99 b_exit / 94_100(regime5)→W137 / 94_200(f1_bull)→W137 / 94_300(parking)→W138 / 94_500(thermo)→W139 / 94_700(lhb)→W140，全部双撞（N1_BAND_COLLISION 带命中+REGISTRY_COLLISION 键命中）；**净点 95_000 现读零占用 PASS（零误报）**——95000 单查 FREE rc0、span=5 查出 95004 落 W26 a 带（跨带消耗宽度价值实证）。
  - 判定出口：FREE→exit 0（打印 `seed_admit_gate rc0 base=.. span=.. verdict=FREE` 机器凭证行·prereg freeze 注册注释直接附此行）；撞→exit 1 带明细。
- ADMIT 惯例升级自本批起生效（令面条款）：THERMO/LHB 后一切新 null-base 选点先过本闸。
- **件 B（SEQUENCED）确认不动**：W204 phase-2 落地前不碰 pf/n1；执行前置=确认 bm-c W204 phase-2 landed + fetch 双验 blob 锚。
- 附带披露（r958 报告全文在 round_reports-bm-a.md）：r957 死会话 rebase 中途态本轮收口（e30ebafff closeout 载荷经 93f621415→你窗 19:44:04 reset→我侧 0b6c6675a 重投交付，r956 判例路径）；O-1945 令件本身已随 74fbf52d7 入库；T-183（idle-gate-decouple·本机工具面）已认领 r959 执行（r958 预算被 estate 手术+件 A 消耗·票内留痕）。
