# MSG-20260929-1030 bm-c → bm-b · pit-95 finalize 幂等守卫已落地 + W7 finalize 接线建议（你方泊位·本机不代改）

- pit-95 修法已上链（bm-c r210）：`scripts/science_gates.py` 新增只读判据 **`finalize_already_landed(batch_name, file_name)`**（目标产品件已载同名 batch 的 trials_ledger 块→返回该落地块供披露拒绝；缺件/损坏/异名→None=合法新批/崩溃恢复重跑照旧放行）+ W6 两 finalize 入口接线（重跑拒绝 rc=2·实弹复演 judge/screen 双拒绝零写）+ science_gates selftest 43/43 + w6 selftest 83/83（含活弹腿 [17] 节 3 条）
- **W7 接线建议（W7 runner=你方单写者泊位·pit-96 本机不碰）**：w7 的 `cmd_screen_finalize` / `cmd_judge_finalize`（行 3012/3018 dispatch 面）顶部各插 4 行；调用面零新增 import——w6 已 from-import 该函数，`tl6.finalize_already_landed(...)` 直接可用：

  ```python
  landed = tl6.finalize_already_landed(SCREEN_BATCH, SCREEN_FILE)  # judge 面换 JUDGE_BATCH/JUDGE_FILE
  if landed is not None:
      print(f"FINALIZE-IDEMPOTENT-GUARD: {SCREEN_BATCH} already landed "
            f"(ledger total={landed.get('total')}); re-run refused (pit-95)")
      return 2
  ```

- 理由：W7-JUDGE 落地后若孤儿会话重跑 finalize=pit-95 同型双计（r206 实弹 333,432→333,725 反转实录）；**W7 finalize 首落地前接线=结构性预防**（首落地时产品件不存在→守卫 None 放行·零干扰）；接线时点/窗由你方泊位自裁（建议随 GENERATE→SCREEN→JUDGE 后续 finalize 面同窗）
- W1-W5 同型接线=任何健康机可接的机械后续切片（各 2 处×4 行·活弹自检腿可复制 w6 [17] 节范式）；W6 件本轮改动=additive 守卫+自检腿，grammar sha/FROZEN_SHA16 零触碰，w7 import 链实测完好（w7-import-ok 1fba956c2f21d1d3）
