# DIGEST 2026-11-10 r1673 bm-b —— E655：唯一 loader 路由在站点上是什么

**问题**：E652 找到的那一条严格通路（`scripts/run_e590_smoke_leg.py` 经 `importlib.import_module`
到达 `e590_cash_silence`，同时携带计数行键 `bar`/`rows`）到底**读**还是**写**它拼的那个键？
「文件携带键」只说键在文件里出现过，不说站点做了什么，也不说写进去的对象是不是读者读的容器。

**做法**：三条臂分开发布。①静态：每个等于计数键的字符串常量，按父节点判角色
（dict 字面键／下标／调用实参／比较／纯文本），dict 写点额外发布赋值根与该根自己的定义；
②调用：loader 的实测字符串绑到它绑定的句柄上，收集这个句柄上被调用的所有属性，保留住在这些属性内的
计数读行；③运行：speller 跑两遍（plain 与 `--doctor`），tracer 只开在读数模块上，
命中按**语句 span** 判（多行调用只报首行）。

**读数**：1 条路由 / 3 个键站点（`call_argument` 2、`dict_literal_key` 1）；唯一写是
`blk["step_rows"] = [{"bar": …}]`，`blk = doc["tickets"][0]`，`doc` 就是 `m.face_problems(doc)` 的实参
——写容器＝读容器；e590 的 3 条计数读行（367/372/377）都在 `face_problems` 内；运行面
**plain 0 命中 / `--doctor` 2 命中**。另一键 `rows` 是 `.get("rows")`，读的是磁盘面上的
`bars_past_the_panel`，同名不同物。

**结论**：这条隐形臂不是空名——它既写又读同一个键，且写进去的正是读者读的那个容器；但那条写只在
`if doctor:` 的 else 回退分支里，所以它是**诊断件不是生产件**。文件级「携带键」不能推断站点语义。

**坑**：①只做静态会把诊断分支的写读成生产闭环（trace 是唯一能分开的东西）；
②桥若只报布尔值，读者无法复核——根、根定义、实参名三件必须同时印；
③E652 的键列表有一个真实盲点：E647 把 percent-format 子树整体记为一个 unresolved 句柄，
`… % face.get("verdict")` 里的常量因此进不了它的列表；本面更宽，多出的键只有落在该句柄语句 span 内
才被接受并计数（`keys_found_outside_e652s_list`=1），E652 有而本面无＝判红。

**证据**：`results/state_tilt/STRINGROUTEKEY.json`（`--doctor` 翻转 verdict 后逐字节回原 sha
`e65727454626`）、`scripts/e655_counted_key_route.py`（selftest 14/14）、S6 leg `counted_key_route`。
