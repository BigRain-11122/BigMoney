# T-70 local-coding pilot — task 06 frozen prompt (identical for both arms)

任务：token 台账 per-leg 增量分解工具（读 token_usage.json 派生表）
目标文件：scripts/token_breakdown.py（新建；仅此一件产物）
约束：Python 3.14 可跑；零第三方新依赖（仅标准库）；selftest 子命令=离线断言；exit 0=通过
验证命令：python scripts/token_breakdown.py selftest
输入样例与输出契约：
1. 输入面：token_usage.json（live 模式位置参数 1，缺省="results/token_usage.json"，相对当前工作目录；utf-8 JSON）。顶层必需键=generated（str）、per_round_context（dict）、machines（dict）、total_state_tokens_est（int）、total_report_tokens_est（int）；缺任一必需键、或 per_round_context/machines 非 dict、或两个 total_*_tokens_est 非 int（bool 视为非 int）→ stderr 一行错误说明 + exit 2（错误态分类，非 SystemExit 崩溃）。
2. leg 派生（从 machines 逐机派生，不从顶层汇总读）：
   a. context 腿 2 条：`mandate`=per_round_context["mandate_read_tokens_est"]、`codely`=per_round_context["codely_read_tokens_est"]；键缺席或值非 int（bool 视为非 int）→ 该腿按 0 计；
   b. 机器腿：machines 每成员 `<mid>` → 2 条腿 `<mid>/state`=state_tokens_est、`<mid>/report`=report_tokens_est（mid 保留原字符串含可能的 "-" 前缀）；成员值非 dict → malformed 计数 +1、该机不产任何腿；腿字段缺席或值非 int（bool 视为非 int）→ 该腿按 0 计；
   c. grand=全部腿 tokens 之和（int）；k=腿总条数。
3. 对账面（cross，派生 vs 声明）：derived_state=全部机器 state 腿之和、derived_report=全部机器 report 腿之和；与 total_state_tokens_est/total_report_tokens_est 用 == 比较，相等=true 否则 false。
4. share_pct：整数半进位（half-up，禁用 float round 的银行家舍入）公式 `share_x10=(n*1000+grand//2)//grand`，输出 x10/10 的 1 位小数；grand=0 → 全部腿 share_pct=0.0。
5. 输出（stdout，行序固定）：
   a. 摘要行（ASCII 单行）：`TOKENS grand=<g> legs=<k> malformed=<mf> state_derived=<ds> report_derived=<dr>`；
   b. 逐腿行（按 tokens 降序，tokens 相同按腿名 ASCII 升序）：`LEG <name> tokens=<n> share_pct=<p>`（p 恒 1 位小数）；
   c. 对账行：`CROSS state=<true|false> report=<true|false>`；
   d. 增量行：delta_vs_prev 为 dict → `DELTA state=<s> report=<r> mandate=<m> vs=<prev>`（s/r/m=delta_vs_prev 对应键 state_tokens_growth/report_tokens_growth/mandate_growth，键缺席按 0；值恒带显式符号：正=+、负=-、零=+0（如 +1871/-3/+0）；prev=delta_vs_prev["prev_generated"] 字符串原样，键缺席=unknown）；delta_vs_prev 缺席或非 dict → `DELTA absent`。
6. CLI 三模式：
   - 无参数：stdout 打印一行用法说明，exit 2；
   - selftest：不读任何仓库文件、不写任何文件，内嵌合成 dict 样例断言纯函数（输入=完整 usage dict，输出=错误分类或派生 dict+渲染行列表）：合法样例至少 2 组（其一=两机 4 腿+context 2 腿+delta 在场：grand/腿数/降序腿序/对账 true/DELTA 行逐字段含显式符号断言精确；其二=对账失配样例：declared≠derived → cross false）；边界/违规样例至少 6 条（①成员值非 dict→malformed=1 且该机零腿、②缺必需顶层键→错误分类、③per_round_context 键缺席→两腿 0 计、④grand=0（machines 空且 context 两腿 0）→全部 share_pct=0.0 且摘要 grand=0、⑤delta_vs_prev 缺席→DELTA absent、⑥share 半进位钉死例：n=5、grand=16 → share_pct=31.3（float round 会得 31.2/31 视实现而定，半进位必须 31.3））；全部断言通过=打印断言计数与 "ALL PASS" 后 exit 0，任一失败=打印失败明细 exit 1；
   - [usage_json_path]（一个可选位置参数）：live 分解；文件不存在=stderr 一行 + exit 2；JSON 解析失败=stderr 一行 + exit 2；错误态（第 1 条）=stderr 一行 + exit 2；正常=摘要行+逐腿行+对账行+增量行；cross 任一 false → exit 1（对账警示位）；全 true → exit 0。
7. 输出纪律：所有 stdout/stderr 输出为 ASCII 可打印字符；不写任何文件；零网络。
8. 交付形态：输出=单个完整 Python 文件内容（唯一 ```python 代码块），文件之外无任何解说文本。

---
arm placement protocol (不属于提示词，跑前注记): A 臂产物=results/local_coding_pilot/tasks/06/A/token_breakdown.py；B 臂产物=results/local_coding_pilot/tasks/06/B/token_breakdown.py；双臂验证=python <arm>/token_breakdown.py selftest（与冻结验证命令语义恒等）。
