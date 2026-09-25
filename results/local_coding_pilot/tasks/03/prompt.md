# T-70 local-coding pilot — task 03 frozen prompt (identical for both arms)

任务：options 采集道健康摘要器（status→一行 verdict 生成）
目标文件：scripts/opt_lane_digest.py（新建；仅此一件产物）
约束：Python 3.14 可跑；零第三方新依赖（仅标准库）；selftest 子命令=离线断言；exit 0=通过
验证命令：python scripts/opt_lane_digest.py selftest
输入样例与输出契约：
1. 摘要对象：results/options_update_status.json（scripts/update_options.py gate 每 10min 轮写出的期权前向采集道状态件）。读面=宽松消费（未知键忽略不违规），只消费下列在册键：
   a. mode：字符串（如 "no-op: cutoff covered" / "spawn"）；缺席=按 "unknown" 处理；
   b. enum_fails：列表（元素类型任意）；缺席=按空列表处理；
   c. mismatch：object（键→值任意）；缺席=按空 object 处理；
   d. panel：object——子键 complete（JSON 布尔）、universe（int）、attempted（int）、last_pass_date（字符串）、max_collected（字符串或 null）、fails（列表）、mismatches（列表）；panel 键缺席或非 object=违规（digest 模式 exit 2，见第 4 条）。
2. verdict 判定序（首个命中即停，冻结）：
   a. panel.complete != true 或 panel.universe != panel.attempted → INCOMPLETE；
   b. panel.fails 非空 或 panel.mismatches 非空 → DATA_ISSUE；
   c. enum_fails 非空 或 mismatch 非空 → ENUM_FAIL；
   d. 其余 → OK。
3. 摘要行格式（ASCII 单行 stdout）：`OPT-LANE <verdict> universe=<u> attempted=<a> cutoff=<c> enum_fails=<n1> mismatch=<n2>`
   - u=panel.universe、a=panel.attempted（键缺席时该段打印 -1）；
   - c=panel.max_collected；为 null 或缺席时回退 panel.last_pass_date；两者皆缺席或 null 时打印 "na"；
   - n1=len(enum_fails)、n2=len(mismatch)；fails/mismatches 的计数不进摘要行（其非空态已由 verdict 承载）。
4. CLI 三模式：
   - 无参数：stdout 打印一行用法说明，exit 2；
   - selftest：不读任何仓库文件，用内嵌合成样例断言——合法样例至少 2 条（其一=完整 OK 态含全部在册键且 max_collected 有值、其二=INCOMPLETE 态 universe!=attempted）；违规/边界样例至少 4 条（enum_fails 非空触发 ENUM_FAIL、mismatch 非空而 enum_fails 空仍 ENUM_FAIL、panel 缺席、max_collected=null 时 cutoff 回退 last_pass_date）；另须断言判定序短路（panel.fails 非空与 enum_fails 非空同在时=DATA_ISSUE 而非 ENUM_FAIL）；全部断言通过=打印断言计数与 "ALL PASS" 后 exit 0，任一失败=打印失败明细 exit 1；
   - <file.json>：显式 utf-8（容忍 utf-8-sig）读取；顶层非 object 或 JSON 解析失败=stderr 一行 + exit 2；文件不存在=stderr 一行 + exit 2；正常读取=打印摘要行 + exit 0（仅 verdict=OK）或 exit 1（任何非 OK verdict）。
5. 输出纪律：所有 stdout/stderr 输出为 ASCII 可打印字符；digest 模式不写任何文件；零网络。
6. 交付形态：输出=单个完整 Python 文件内容（唯一 ```python 代码块），文件之外无任何解说文本。

---
arm placement protocol (不属于提示词，跑前注记): A 臂产物=results/local_coding_pilot/tasks/03/A/opt_lane_digest.py；B 臂产物=results/local_coding_pilot/tasks/03/B/opt_lane_digest.py；双臂验证=python <arm>/opt_lane_digest.py selftest（与冻结验证命令语义恒等）。
