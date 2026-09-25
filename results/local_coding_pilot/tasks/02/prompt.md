# T-70 local-coding pilot — task 02 frozen prompt (identical for both arms)

任务：watermark_red.json schema 校验器（字段/类型/红牌键）
目标文件：scripts/wm_red_lint.py（新建；仅此一件产物）
约束：Python 3.14 可跑；零第三方新依赖（仅标准库）；selftest 子命令=离线断言；exit 0=通过
验证命令：python scripts/wm_red_lint.py selftest
输入样例与输出契约：
1. 校验对象：results/watermark_red.json（Tools/watchdog.ps1 C7 每 30min tick 写一次的机内水位红牌件；ASCII 写出）。
2. 顶层结构：必须为 JSON object；顶层恰含 8 个键（缺任一=违规，多未知键=违规）：
   a. ts：字符串，严格匹配 ^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$；
   b. machine：非空字符串；
   c. red：JSON 布尔（true/false；数字 0/1 或字符串=违规）；
   d. lane：非空字符串；
   e. py_series_tail：列表；每个元素=数字或可 float() 的字符串（如 "1.9" / 0.5）；空列表合法；
   f. zombies_killed：列表；每个元素=非空字符串（如 "pid=123 lane=x"）；空列表合法；
   g. next_pick：必须为 null 或 object——object 时恰含 3 个非空字符串子键 lane/candidate/status（子键缺失或值非字符串或 strip 后空=违规；多出的未知子键=违规）；该键整体缺席=合法（PowerShell 5.1 空值序列化变体，如实容忍）；
   h. order_ref：非空字符串。
3. CLI 三模式：
   - 无参数：stdout 打印一行用法说明，exit 2；
   - selftest：不读任何仓库文件，用内嵌合成样例断言——至少 2 条合法样例全判 PASS（其一 red=false 且 next_pick 键缺席、其二 next_pick 为含 3 子键的 object）；至少 7 类违规全被抓（顶层非 object / 顶层 JSON 解析失败 / 缺必需键 / red 非布尔 / ts 格式错 / py_series_tail 元素非数值 / next_pick object 子键缺失或空 / 顶层多未知键）；全部断言通过=打印断言计数与 "ALL PASS" 后 exit 0，任一失败=打印失败明细 exit 1；
   - <file.json>：显式 utf-8（容忍 utf-8-sig）读取，逐条校验，每个违规打印一行（键名+原因，ASCII 措辞），末尾打印违规总数；无违规 exit 0，有违规 exit 1；文件不存在=stderr 一行 + exit 2；JSON 解析失败=打印一行解析违规后 exit 1。
4. 输出纪律：所有 stdout/stderr 输出为 ASCII 可打印字符；lint 模式不写任何文件；零网络。
5. 交付形态：输出=单个完整 Python 文件内容（唯一 ```python 代码块），文件之外无任何解说文本。

---
arm placement protocol (不属于提示词，跑前注记): A 臂产物=results/local_coding_pilot/tasks/02/A/wm_red_lint.py；B 臂产物=results/local_coding_pilot/tasks/02/B/wm_red_lint.py；双臂验证=python <arm>/wm_red_lint.py selftest（与冻结验证命令语义恒等）。
