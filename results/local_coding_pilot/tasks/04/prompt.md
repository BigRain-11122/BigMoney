# T-70 local-coding pilot — task 04 frozen prompt (identical for both arms)

任务：fleet 任务板 aging 报表（claimed 时长/状态计数）
目标文件：scripts/board_aging.py（新建；仅此一件产物）
约束：Python 3.14 可跑；零第三方新依赖（仅标准库）；selftest 子命令=离线断言；exit 0=通过
验证命令：python scripts/board_aging.py selftest
输入样例与输出契约：
1. 扫描对象：board_dir 目录（live 模式位置参数，缺省="fleet/tasks"，相对当前工作目录）下全部 *.json 票件。读取面=宽松消费：
   a. 读取编码 utf-8-sig（容忍 BOM）；JSON 解析失败或顶层非 object（list/str/num 等）=记 1 件 parse_fail，继续处理其余件不中断；
   b. 在册键（未知键一律忽略不违规）：id（字符串；缺席=文件名去 .json 后缀）、status（字符串；缺席=按 "unknown"）、claimed_at（ISO 8601 字符串，如 "2026-09-26T00:15:00+08:00"；缺席或解析失败=None）、claimed_by（字符串；缺席=""）；
   c. machine 归属=claimed_by 首个空白分隔 token（如 "bm-a (OS iteration loop, round 195; ...)" → "bm-a"；空串→""）。
2. 状态计数：open / claimed / done / other（other=一切非前三的 status 字符串，含 "unknown"）；parse_fail 单列计数（不进四类）。
3. aging 计算（只对 status=claimed 件）：
   a. age_h=(now - claimed_at) 的小时数（float，输出 1 位小数）；claimed_at 缺席或解析失败=age_h 取 -1.0；
   b. now=本机当前时刻（timezone-aware）；claimed_at 无时区标记时按本机时区补齐；age_h 为负（未来时间戳）=如实打印不计 stalled；
   c. stalled48h=age_h > 48 的 claimed 件数（age_h=-1.0 不计 stalled）；
   d. max_age_h=claimed 件有效 age_h（≥0）的最大值；零 claimed 件或全无效时=-1.0（输出 "-1.0"）。
4. 输出（stdout）：
   a. 摘要行（ASCII 单行）：`BOARD total=<t> parse_fail=<pf> open=<o> claimed=<c> done=<d> other=<x> stalled48h=<s> max_age_h=<m>`（total=四类计数之和；m 输出 1 位小数）；
   b. 每件 claimed 一行（按 age_h 降序；age_h 相同按 id 升序）：`CLAIMED <id> age_h=<a> by=<machine>`（a 输出 1 位小数）。
5. CLI 三模式：
   - 无参数：stdout 打印一行用法说明，exit 2；
   - selftest：不读任何仓库文件、不写任何文件，用内嵌合成样例断言（核心函数吃 (文件名, 原始文本) 对列表+冻结 now）——合法样例至少 2 组（其一=混合状态四类计数齐全且含 1 件 parse_fail、其二=claimed aging 数学精确断言如 2.5h/100h）；边界/违规样例至少 6 条（claimed_at 缺席→age_h -1.0 且不入 stalled 且 max 忽略、invalid JSON 文本→parse_fail 不中断、顶层非 object→parse_fail、machine 首 token 提取、stalled 100h→stalled48h=1、排序=最老在前+并列按 id 升序）；全部断言通过=打印断言计数与 "ALL PASS" 后 exit 0，任一失败=打印失败明细 exit 1；
   - [board_dir]（可选位置参数）：live 扫描；目录不存在或零 *.json=stderr 一行 + exit 2；正常=摘要行+claimed 逐件行 + exit 0（stalled48h=0）或 exit 1（stalled48h≥1）。
6. 输出纪律：所有 stdout/stderr 输出为 ASCII 可打印字符；不写任何文件；零网络。
7. 交付形态：输出=单个完整 Python 文件内容（唯一 ```python 代码块），文件之外无任何解说文本。

---
arm placement protocol (不属于提示词，跑前注记): A 臂产物=results/local_coding_pilot/tasks/04/A/board_aging.py；B 臂产物=results/local_coding_pilot/tasks/04/B/board_aging.py；双臂验证=python <arm>/board_aging.py selftest（与冻结验证命令语义恒等）。
