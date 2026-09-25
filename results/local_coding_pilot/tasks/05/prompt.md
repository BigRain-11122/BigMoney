# T-70 local-coding pilot — task 05 frozen prompt (identical for both arms)

任务：inbox 定向消息 aging/未处理扫描器（逐件 ETA 行）
目标文件：scripts/inbox_aging.py（新建；仅此一件产物）
约束：Python 3.14 可跑；零第三方新依赖（仅标准库）；selftest 子命令=离线断言；exit 0=通过
验证命令：python scripts/inbox_aging.py selftest
输入样例与输出契约：
1. 扫描对象：inbox_dir（live 模式位置参数 1，缺省="fleet/inbox"，相对当前工作目录）顶层 MSG-*.md 文件（glob 前缀 MSG- 且后缀 .md；不递归子目录，processed/ 不扫）；活性面=machines_dir（位置参数 2，缺省="fleet/machines"）下全部 *.json 心跳件。
2. 文件名契约（宽松消费，不匹配=name_fail 计数继续处理其余件不中断）：`MSG-<YYYYMMDD>-<HHMM>-<recipient>-<topic>.md`，正则 `^MSG-(\d{8})-(\d{6})-(ALL|bm-[a-z0-9]+)-(.+)\.md$`（大小写敏感）；不匹配该正则的 MSG-*.md 件=记 1 件 name_fail，无逐件行。
3. 时间与活性：
   a. filed_at=文件名日期时间按 `%Y%m%d-%H%M` 解析、naive 按本机时区补齐（timezone-aware）；解析失败（如月 13/时 25）=age_h=-1.0；
   b. age_h=(now-filed_at) 小时数（float，输出 1 位小数）；now=本机当前时刻 timezone-aware；age_h<0（未来时间戳）=如实输出不计 stalled；
   c. 机器活性=心跳件 last_seen 字段（ISO 字符串，naive 按本机时区补齐）；liveness_min=(now-last_seen) 分钟数；心跳件缺失/JSON 解析失败/last_seen 缺席或解析失败=活性 unknown；
   d. recipient 具体机 id：该机心跳件活性即收件机活性；recipient=ALL：取全部心跳件中最新的 last_seen 为有效活性。
4. ETA 分类（逐件一行；age_h 有效指 ≥0）：
   - age_h 有效且收件机活性 fresh（liveness_min ≤ 20）→ `eta=due_next_pull`；
   - age_h 有效且收件机活性 stale（liveness_min > 20）或 unknown → `eta=stranded`；
   - age_h 无效（-1.0：时间戳解析失败或未来时间戳）→ `eta=clock_anomaly`。
5. 输出（stdout）：
   a. 摘要行（ASCII 单行）：`INBOX total=<t> name_fail=<nf> unprocessed=<u> stalled1h=<s> stranded=<x> max_age_h=<m>`（total=扫描到的 MSG-*.md 件数；unprocessed=total-name_fail；stalled1h=age_h>1.0 的有效件数；stranded=按第 4 条判为 stranded 的件数；m=有效 age_h（≥0）最大值输出 1 位小数，无有效件=-1.0 输出 "-1.0"）；
   b. 逐件行（仅非 name_fail 件；按 age_h 降序，age_h 相同按文件名升序）：`MSG <filename> to=<recipient> age_h=<a> eta=<class>`（a 输出 1 位小数）。
6. CLI 三模式：
   - 无参数：stdout 打印一行用法说明，exit 2；
   - selftest：不读任何仓库文件、不写任何文件，用内嵌合成样例断言（核心函数吃 (文件名, 心跳件 dict={machine_id: last_seen 字符串或 None}, 冻结 now) 对列表）——合法样例至少 2 组（其一=混合态：1 件 fresh due_next_pull + 1 件 stale stranded + 1 件 stalled1h 计数与 max_age 数学精确断言、其二=ALL 收件机取全机最新活性判 fresh）；边界/违规样例至少 6 条（name_fail 正则不匹配件计数、时间戳解析失败→age_h -1.0+eta=clock_anomaly、未来时间戳→age_h<0 不计 stalled、收件机心跳件缺失→unknown→stranded、排序=最老在前+并列按文件名升序、零有效件 max_age_h=-1.0）；全部断言通过=打印断言计数与 "ALL PASS" 后 exit 0，任一失败=打印失败明细 exit 1；
   - [inbox_dir] [machines_dir]（两个可选位置参数）：live 扫描；inbox_dir 不存在=stderr 一行 + exit 2；machines_dir 不存在=按空心跳集处理（活性全 unknown）不报错；正常=摘要行+逐件行 + exit 0；stalled1h ≥ 1 时 exit 1（警示位）；total=0=摘要行 total=0 + exit 0（空 inbox=健康态非错误）。
7. 输出纪律：所有 stdout/stderr 输出为 ASCII 可打印字符；不写任何文件；零网络。
8. 交付形态：输出=单个完整 Python 文件内容（唯一 ```python 代码块），文件之外无任何解说文本。

---
arm placement protocol (不属于提示词，跑前注记): A 臂产物=results/local_coding_pilot/tasks/05/A/inbox_aging.py；B 臂产物=results/local_coding_pilot/tasks/05/B/inbox_aging.py；双臂验证=python <arm>/inbox_aging.py selftest（与冻结验证命令语义恒等）。
