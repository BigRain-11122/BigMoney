# T-70 local-coding pilot — task 07 frozen prompt (identical for both arms)

任务：S6 维护链逐腿新鲜度矩阵（各腿 last-run 年龄表）
目标文件：scripts/leg_freshness.py（新建；仅此一件产物）
约束：Python 3.14 可跑；零第三方新依赖（仅标准库）；selftest 子命令=离线断言；exit 0=通过
验证命令：python scripts/leg_freshness.py selftest
输入样例与输出契约：

1. 冻结腿清单 LEGS（嵌入常量，7 腿，表序即序）：
   | name | 状态件名（相对 results_dir） | ts 字段名 |
   |---|---|---|
   | ah_panel | ah_panel_status.json | ts |
   | daily | update_status.json | updated |
   | fundamental | fundamental_status.json | updated |
   | lhb | lhb_update_status.json | updated |
   | moneyflow | moneyflow_update_status.json | ts |
   | regime | regime_state.json | updated |
   | token_meter | token_usage.json | generated |
2. 读取面：一律 utf-8-sig 读（容 BOM）。live 模式逐腿读 results_dir/<状态件名>：
   - 文件不存在或不可读 → status=missing；
   - JSON 解析失败或顶层非 dict → status=missing；
   - ts 字段缺席、值非 str、或按第 3 条不可解析 → status=bad_ts；
   - 否则 status=ok。
3. ts 解析规则：只接受两形态——"YYYY-MM-DD HH:MM:SS"（空格分隔）与"YYYY-MM-DDTHH:MM:SS"（T 分隔）；秒的小数部分允许存在（解析时截断小数部分）；两形态均 naive 无时区。其余一切（带时区后缀/缺时间段/空串等）=不可解析 → bad_ts。
4. age_h（年龄整数小时）=(now - ts).total_seconds() // 3600（floor；未来 ts 产出负 age_h，status 仍 ok，如实输出）；now 缺省=墙钟 datetime.now()（naive 本地）；missing/bad_ts 腿无 age_h（渲染为"-"）。
5. stale 位：age_h >= 24 → stale=1，否则 0（负 age_h → 0）；missing/bad_ts 腿恒 0。
6. 输出（stdout，行序固定）：
   a. 头行（ASCII 单行）：`FRESHNESS legs=<k> ok=<n_ok> missing=<n_missing> bad=<n_bad> stale=<n_stale> now=<YYYY-MM-DD HH:MM:SS>`（now 用空格分隔秒精度截断渲染；k 恒 7；n_*=各计数）；
   b. 逐腿行（固定排序 = status 档 asc（ok=0, bad_ts=1, missing=2）→ age_h desc → name ASCII asc；无 age 的腿在其档内按 name 排）：`LEG <name> age_h=<h|-> ts=<渲染> status=<ok|bad_ts|missing> stale=<0|1> src=<状态件 basename>`；ts 渲染规则：status=ok → 原字符串；bad_ts 且字段缺席 → `absent`；bad_ts 且值非 str → `nonstr`；bad_ts 且 str 超 60 字符 → 截断至首 60 字符；bad_ts 且 str ≤60 字符 → 原字符串；missing → 恒 `absent`；
   c. stale 计数 n_stale=stale=1 的腿数。
7. CLI 三模式：
   - 无参数：stdout 打印一行用法说明，exit 2；
   - selftest：不读任何仓库文件、不写任何文件，内嵌合成样例对纯函数做断言（纯函数签名语义固定：digest(observations, now)，observations=元素 (name, src_basename, raw_text_or_None, ts_field) 的列表，返回逐腿 status/age_h/ts 渲染与头行计数的 dict）：
     * 合法样例一（5 腿全 ok，冻结 now，ts 用 now 减固定间隔构造）：age_h 49h/25h/1h/0h/0h（1h 腿=now-90min；0h 两腿=now-59min 与 now-30min）：断言头行 ok=5 stale=2、行序=49h,25h,1h,0h,0h 且两 0h 腿间按 name ASCII 升序、59min 腿 age_h=0（floor 边界）；
     * 合法样例二（混合 3 腿：1 ok + 1 bad_ts + 1 missing；bad_ts 腿=ts 字段缺席形态）：断言 ok=1 bad=1 missing=1、行序 ok 在前 bad_ts 居中 missing 最后、逐行渲染字段（bad_ts 腿 ts=absent、missing 腿 ts=absent 且 stale=0）；
     * 边界/违规样例至少 6 条：① raw_text=None → missing；② 顶层非 dict JSON（如 "[1,2]"）→ missing；③ JSON 解析失败文本 → missing；④ ts 字段缺席 → bad_ts 且渲染 absent；⑤ ts 值非 str（如 int 5）→ bad_ts 且渲染 nonstr；⑥ 无时间段字符串（如 "2026-09-26"）→ bad_ts；⑦ 空格与 T 两形态解析出相同 age_h；⑧ 带小数秒与不带小数秒解析出相同 age_h；⑨ 未来 ts（now+2h）→ age_h=-2、stale=0、status=ok；
     全部断言通过=打印断言计数与 "ALL PASS" 后 exit 0，任一失败=打印失败明细 exit 1；
   - live 模式 `leg_freshness.py [results_dir [now_str]]`：results_dir 缺省="results"（相对当前工作目录）；now_str 缺省=墙钟，给定则必须为 "YYYY-MM-DD HH:MM:SS" 形态（不可解析=stderr 一行+exit 2）；results_dir 不存在或非目录=stderr 一行+exit 2；正常=头行+逐腿行；全部腿 ok → exit 0，任一 missing/bad_ts → exit 1（诚实警示位）。
8. 输出纪律：所有 stdout/stderr 输出为 ASCII 可打印字符；不写任何文件；零网络。
9. 交付形态：输出=单个完整 Python 文件内容（唯一 ```python 代码块），文件之外无任何解说文本。

---
arm placement protocol (不属于提示词，跑前注记): A 臂产物=results/local_coding_pilot/tasks/07/A/leg_freshness.py；B 臂产物=results/local_coding_pilot/tasks/07/B/leg_freshness.py；双臂验证=python <arm>/leg_freshness.py selftest（与冻结验证命令语义恒等）。
