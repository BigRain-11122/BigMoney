# DIGEST-20261108-r1555 — E528: 自递归转发到底有没有被终止臂读到？

**轮次**：r1555 bm-b ｜ **日期**：2026-11-08 ｜ **卡**：E528 ｜ **正身**：`scripts/e528_recursive_read.py`

## 一句话

E525 把 6 个「又交回同一个函数」的 parcel 记成一个类名就收了手；本轮逐个打开：**6/6 全部被终止臂读到**（5 个走 `_resolve` 的「深度计数 + 类型测试」双保险，1 个走 `is_literal_side` 的类型测试），**0 个无守卫递归、0 个有守卫但值没人读**。

## 上游

`results/state_tilt/onwardresidue_latest.json`（E525，r1554）里的
`the_same_function_again_so_the_chain_closes_inside_one_body` 边界（6 个 parcel，去重后落在
2 个函数：`scripts/e379_unkeyed_face_reader.py::_resolve` 5 个、`scripts/e483_leg_debt.py::is_literal_side` 1 个）。

## 方法

对每个 parcel 回到 `source:line`，把所在函数的 AST 全读一遍：

1. **臂（arm）**：只看递归调用**之外**对参数的使用——直接进 `return` = 交给调用方；读属性/下标/
   容器元素 = 读了不返回；只出现在 `isinstance`/`None` 比较里 = 只测类型；裸表达式语句 = 丢弃；
   完全没有 = 递归外从不提。**递归调用本身永不计为一次读。**
2. **守卫（guard）**：沿递归调用自己的祖先链看——`depth + 1` 递进去且函数体内有
   `depth > 常数` 的比较 = 深度守卫；祖先 `if` 测的正是该参数（或该参数被遍历的容器，
   含 `for x in param:` 与推导式）= 类型守卫；两者都有 = 双守卫；都没有 = 无守卫。
3. **判决**：有守卫且臂能终止 → `read_by_a_terminating_arm`；无守卫 → `the_recursion_is_unguarded`；
   有守卫但臂是丢弃/从不提 → `guarded_but_the_value_is_never_read`。

## 读数

| 项 | 值 |
|---|---|
| 自递归 parcel | 6（2 个函数 / 2 个模块）|
| 被终止臂读到 | **6** |
| 无守卫递归 | 0 |
| 有守卫但值没人读 | 0 |
| 臂分布 | 交给调用方 5 / 读了不返回 1 |
| 守卫分布 | 深度+类型 5 / 类型 1 |
| 递归调用行 | `_resolve` 10 处；`is_literal_side` 3 处 |

**判决**：`read_by_a_terminating_arm`

## 手读注记（不在自动面内，逐行可查）

`_resolve` 的深度守卫是 `if depth > 6: return None`（第 122-123 行）——递归确实会停，但停法是
**返回 None**，调用方拿到的「解析不到」里混着「真的解析不了」和「递归深度用尽」。这不是本卡
问的「能不能读到」，但它是这个终止臂的真实代价，留给「深度耗尽被算成否定答案」类问题。

`is_literal_side` 没有计数器，靠的是结构性类型测试（Constant/Tuple/List/Set/Dict/UnaryOp 逐一
分派，只往子节点下降），终止性是结构保证而不是深度保证——这两类守卫不能混成一个「有守卫」。

## 三枚可复用判例

1. **递归调用不是读**——把递归调用算进「值被使用」会让每个递归函数都自动变成「有人读」；
   臂必须在递归调用之外测量。
2. **参数不是载体**（承 E525 的「一个物理跳点被多行共享」）——`all(typed(e) for e in expr)`
   递进去的是推导变量 `e`，真正被函数臂处理的是 `expr`；不顺着 `for`/推导式把变量折回容器，
   就会把值判成「递归之外从不出现」。
3. **返回一个由值算出来的表达式 ≠ 返回那个值**——`return all(...)` 里对容器的读是读，
   不是把值交回调用方；判「交给调用方」必须要求 Return 路径上不经过推导式/布尔组合。

## 验证

- `build` rc0 / `check` problems=0 / `verify` problems=0 / `selftest` 8/8
- S6 腿 `recursive_read` rc0（0.05s）
- smoke 腿 `# E528` 1/1 绿；`--doctor` 1/1 红，面字节还原 sha `41210d9facc1`
- face：`results/state_tilt/RECURSIVEREAD-2026-11-08.json` + `recursiveread_latest.json`