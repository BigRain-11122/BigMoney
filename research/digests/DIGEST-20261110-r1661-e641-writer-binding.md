# DIGEST-20261110-r1661 — E641: 计数函数里的双深写入，容器绑在哪里

**轮：** r1661 bm-b ｜ **卡：** E641 ｜ **面：** `results/state_tilt/WRITERBINDING.json`

## 问题

E640 只回答了「写的是不是同一个**键**」：E633 的 13 条计数读行落在 6 个函数里，其中 3 个带
双深写入，共 10 个写点，**0 个命名该行的计数键**。但「写别的键」不等于「写不到那本账」——
如果写点穿过的是读行用的那个容器，那么 `k` 的只读性就不成立了。E641 就是这一问。

## 做法

对 E640 发布的每个写点：取该 (line, column) 处**最外层** Subscript，沿 `.value` 链走到根
Name（那就是写穿过的容器），再在函数内解析这个名字——参数 / 循环目标 / 局部赋值（并记下绑
定表达式的种类）/ 模块作用域 / 解析不出。最后比对：这个名字是不是同函数里某条计数读行的
接收者名。

## 读数

- 6 个计数函数，3 个带双深写入，**10 个写点**。
- 容器绑定：**5 个不同容器，10/10 都是函数内新建的局部**（7 × dict 字面量 / 3 ×
  `json.loads(...)` 调用）；**0 个来自参数或模块作用域，0 个 unresolved**。
- **0 个写点的容器名等于任何计数读接收者的名字**（同函数读接收者共 6 个：P / faces /
  doctored4 / r / ports / sleeves）。
- 逐函数：`cn_core_ddctl_p1.run` 写 `per_year`（`per_year = {}`）；`e382_key_projection_delta.build`
  写 `numbers`（`numbers, verdicts = {}, {}`）；`e504_name_compose.selftest` 写 `doctored` /
  `doctored3` / `doctored5`（`json.loads(json.dumps(face))` 出来的副本）。
- 判定：写侧在作用域内是局部的，**结构上无法别名到调用方的映射**。

## 教训

1. **判「写能不能碰到这本账」要看容器，不看键名。** 10 个写点全写别的键，但它们若穿过同一
   个映射，结论会反过来；正解是把写点的 `.value` 链折到根名，再问这个根名在函数里从哪来。
2. **名字相等不是别名证明。** 两个不同名参数可以持同一个对象，同一个名字也可以在写与读之间
   被重新绑定。所以本面只发布每行的证据（容器名 + 绑定种类 + 绑定行号 + 是否同名于读接收
   者），不发布「可达/不可达」的判决性断言——能证的是这批 10 个写点绑在函数内新建的容器上。
3. **元组赋值会把「值的种类」读成元组的种类。** 首版把 `numbers, verdicts = {}, {}` 的
   `numbers` 记作 `sequence_literal`（那是元组），于是 e382 的 5 个写点全部被描述成「写穿一个
   序列」。按位置配对后是 `dict_literal`，直方图从 {call:3, sequence_literal:5} 变成
   {call:3, dict_literal:7}——**名即语义**（E207 族），一个描述错的名字比没有名字更糟。

## How

凡「A 的写会不会污染 B 的读」，先答三问：①A 的容器是哪个名字（折 `.value` 链）；②这个名字
在本作用域里从哪来（参数/循环/局部/模块）；③它是不是 B 的接收者名（或能追到同一个来源）。
第三问答不出「是」时，只能发布证据不能发布别名结论。

## 证据

`scripts/e641_writer_receiver.py`（selftest 18/18、check/verify `problems=[]`、复建字节同一
sha `7f2fe87928e1`）+ `results/state_tilt/WRITERBINDING.json` + `writerbinding_latest.json`
+ `scripts/run_e641_smoke_leg.py`（1/1 PASS、`--doctor` 1/1 红且面字节复原 sha 同）
+ smoke_test.py leg E641 + `Tools/s6_chain_bmb.py` leg `writer_binding` rc=0 0.06s
+ POOL E641 done / E644 seeded。