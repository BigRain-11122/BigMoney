# T-70 local-coding pilot — task 01 frozen prompt (identical for both arms)

任务：round report R 行 lint 校验器（五字段结构+时间戳格式校验）
目标文件：scripts/rr_lint.py（新建；仅此一件产物）
约束：Python 3.14 可跑；零第三方新依赖（仅标准库）；selftest 子命令=离线断言；exit 0=通过
验证命令：python scripts/rr_lint.py selftest
输入样例与输出契约：
1. R 行定义：markdown 表格行，以 "| " 开头，且首字段为 "YYYY-MM-DD HH:MM" 格式时间戳。
2. 校验规则（逐条 R 行）：
   a. 结构：剥离行首 "|" 与行尾 "|" 后按 " | " 分割，必须恰有 5 个非空（strip 后非空）字段；
   b. 字段1 时间戳：严格匹配 ^\d{4}-\d{2}-\d{2} \d{2}:\d{2}$；
   c. 字段2 轮号：以 "R" 紧跟数字开头（如 R155 或 R155 (dept:研究)）；
   d. 字段3/4/5（verdict 首段 / did 正文 / 下轮指针）：strip 后非空。
3. CLI 三模式：
   - 无参数：stdout 打印一行用法说明，exit 2；
   - selftest：不读任何仓库文件，用内嵌合成样例断言——至少 3 条合法 R 行全部判 PASS；至少 4 类违规全被抓（字段数≠5 / 时间戳格式错 / 字段2 无 R 前缀 / 某字段为空）；全部断言通过=打印断言计数与 "ALL PASS" 后 exit 0，任一失败=打印失败明细 exit 1；
   - <file.md>：显式 utf-8（容忍 utf-8-sig）读取，逐行 lint，每个违规打印一行（行号+原因，ASCII 措辞），末尾打印违规总数；无违规 exit 0，有违规 exit 1；文件不存在=stderr 一行 + exit 2。
4. 输出纪律：所有 stdout/stderr 输出为 ASCII 可打印字符；lint 模式不写任何文件；零网络。
5. 交付形态：输出=单个完整 Python 文件内容（唯一 ```python 代码块），文件之外无任何解说文本。

---
arm placement protocol (不属于提示词，跑前注记): A 臂产物=results/local_coding_pilot/tasks/01/A/rr_lint.py；B 臂产物=results/local_coding_pilot/tasks/01/B/rr_lint.py；双臂验证=python <arm>/rr_lint.py selftest（与冻结验证命令语义恒等）。
