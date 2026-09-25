# T-70 local-coding pilot — task 09 frozen prompt (identical for both arms)

任务：分离刷新道日志进度解析器（options/ah/mf 三 log → 逐道一行进度 + 一行总判读）
目标文件：scripts/lane_log_digest.py（新建；仅此一件产物）
约束：Python 3.14 可跑；零第三方新依赖（仅标准库）；selftest 子命令=离线断言；exit 0=通过
验证命令：python scripts/lane_log_digest.py selftest

输入样例与输出契约：

1. 冻结输入面（三件，均相对 logs_dir，文件名冻结；三件彼此独立，任一件缺席/不可读不影响其余两件解析，该道按 missing 处理非崩溃）：
   | 件 | 道 |
   |---|---|
   | options_refresh.log | 期权前向采集分离刷新道 |
   | ah_refresh.log | AH 面板分离刷新道 |
   | moneyflow_refresh.log | 资金流分离刷新道 |

2. 行面契约（各道识别的行形状；「取最后一条」=同一形状多条匹配时取文件序最后一条）：
   options_refresh.log：
   - progress 行（行首匹配）：`[opt-refresh] <i>/<N> appended=<a> fuse=<f>`（i/N/a/f 均 int）→ 取最后一条：progress="<i>/<N>"、appended、fuse；
   - census 行（行首前缀匹配，其 months= 尾部忽略）：`[opt-refresh] enumerated=<int> disk=<int> extra_sweep=<int> sweep_skip=<int> ckpt_done=<int> pending=<int> ` → 取最后一条：pending；
   - done 行（行首匹配至行尾）：`[opt-refresh] done pass_ok=<True|False> appended=<int> mismatches=[...] fails=[...] last_pass=<token>`（token=行尾非空白序列）→ 取最后一条：done_pass、done_appended、done_mismatches、done_fails、last_pass；
   - fuse_events=以 `[opt-refresh] conn-fuse:` 开头的行数。
   列表元素计数（mismatches/fails 的方括号内容）：strip 后为空=0；否则=其中逗号数+1（`[]`=0、`['a']`=1、`['a', 'b']`=2）。
   ah_refresh.log：
   - done 行（整行匹配）：`refresh done: pairs=<int> done=<int> quarantined=<int> pulled_rows=<int> cutoff=<token> complete=<True|False> exit=<int>` → 取最后一条：pairs、done_pairs、quarantined、pulled_rows、cutoff、complete、exit；
   - em_unavail=以 `EM mapping unavailable:` 开头的行数；fuse_stops=以 `fuse stop at ` 开头的行数。
   moneyflow_refresh.log：
   - done 行（整行匹配）：`refresh done: +<int> rows, <int> failures, <int> mismatches, complete=<True|False>, panel cutoff=<token>` → 取最后一条：rows、failures、mismatches、complete、cutoff；
   - blocks=以 `source-level block suspected` 开头的行数；rank_fails=以 `rank pass failed:` 开头的行数；rank_pass_events=以 `rank pass ` 开头且不以 `rank pass failed:` 开头的行数。

3. 道状态（四态互斥，逐道独立）：
   - missing：文件不存在或不可读；
   - empty：文件存在可读且全部行 strip 后为空串；
   - done：done 行至少命中一条；
   - in_progress：其余情形（存在非空白行但无 done 行命中）。

4. ok 判定（冻结）：
   - options ok ⟺ state=done 且 done_pass=True；
   - ah ok ⟺ state=done 且 complete=True 且 exit=0；
   - mf ok ⟺ state=done 且 complete=True。

5. 输出（stdout 恰 4 行，行序固定 options→ah→mf→VERDICT，全 ASCII，字段间单空格）：
   `LANE options state=<s> progress=<i>/<N> appended=<a> fuse=<f> pending=<p> fuse_events=<c> done_pass=<v> done_appended=<n> done_mismatches=<m> done_fails=<c2> last_pass=<v2>`
   `LANE ah state=<s> pairs=<n> done_pairs=<n2> quarantined=<q> pulled_rows=<r> cutoff=<v> complete=<v2> exit=<e> em_unavail=<c> fuse_stops=<c2>`
   `LANE mf state=<s> rows=<n> failures=<f> mismatches=<m> complete=<v> cutoff=<v2> blocks=<c> rank_fails=<c2> rank_pass_events=<c3>`
   `VERDICT ok=<k>/3`（k=ok 道数）
   渲染细则：
   - state ∈ {missing, empty, in_progress, done}；done_pass/complete 渲染 True/False 原样；cutoff/last_pass 渲染原始 token（可为 None）；
   - state=missing → 该道行除 state 外全部字段渲染 `-`；
   - 其余态：结构字段=最后一条匹配值，无匹配=`-`；计数字段=非负整数（无匹配=0）；
   - mf rows 渲染为去掉前导 `+` 的整数。

6. CLI 三模式：
   - 无参数：stdout 打印一行用法说明，exit 2；
   - selftest：不读任何仓库文件、不写任何文件，内嵌合成样例对纯函数做断言。纯函数签名语义固定：digest(options_text, ah_text, mf_text)，三参各为 str（文件全文）或 None（=missing）；返回 dict 含 lanes（options/ah/mf 三键，各含该道全部字段：结构字段=解析值（int/bool/str），缺席=None；计数字段=int；state=str）、ok（int）、lines（list[str]，恰 4 条=按第 5 条模板渲染的行）：
     * 样例一（全 ok 三道）：
       options 文本含 5 行：start 行 `[opt-refresh] pass target=2026-09-24 start 2026-09-26T01:00:00`；census 行 `[opt-refresh] enumerated=142 disk=200 extra_sweep=58 sweep_skip=0 ckpt_done=0 pending=200 months={'510050': ['202610', '202612', '202703'], '510300': ['202610', '202612', '202703']}`；progress 行两条 `[opt-refresh] 25/200 appended=0 fuse=0`、`[opt-refresh] 200/200 appended=0 fuse=0`；fuse 行 `[opt-refresh] conn-fuse: 3 consecutive fails, stop`；done 行 `[opt-refresh] done pass_ok=True appended=0 mismatches=[] fails=[] last_pass=2026-09-24`；
       ah 文本含 3 行：`EM mapping unavailable: em page 1: RemoteDisconnected: Remote end closed connection without response`（2 条）+ done 行 `refresh done: pairs=6 done=6 quarantined=0 pulled_rows=1200 cutoff=2026-09-24 complete=True exit=0`；
       mf 文本含 3 行：`rank pass failed: page 1: RemoteDisconnected -> exit 2 (nothing written)`、`source-level block suspected (3 consecutive connection failures) -- stopping, checkpoint intact, gate retries after throttle window`、done 行 `refresh done: +3600 rows, 3 failures, 0 mismatches, complete=True, panel cutoff=2026-09-24`；
       断言：ok=3；三道 state=done；options 全字段值（progress="200/200"、appended=0、fuse=0、pending=200、fuse_events=1、done_pass=True、done_appended=0、done_mismatches=0、done_fails=0、last_pass="2026-09-24"）；ah 全字段值（pairs=6、done_pairs=6、quarantined=0、pulled_rows=1200、cutoff="2026-09-24"、complete=True、exit=0、em_unavail=2、fuse_stops=0）；mf 全字段值（rows=3600、failures=3、mismatches=0、complete=True、cutoff="2026-09-24"、blocks=1、rank_fails=1、rank_pass_events=0）；lines 4 条逐字节字符串比对（含 `VERDICT ok=3/3`）。
     * 样例二（options 在途）：options 只有 census 行+progress 行 `[opt-refresh] 50/200 appended=0 fuse=0`，无 done 行；ah/mf 同样例一 → 断言 options state=in_progress、progress="50/200"、done 系五字段=None（渲染 `-`）、fuse_events=0、ok=2、VERDICT 行逐字节=`VERDICT ok=2/3`。
     * 样例三（mf 受阻）：mf 文本含 rank 成功行 `rank pass 2026-09-25T23:15:00: +3600 rows, 3 same-day skips, 2 not in rank face, 1 not in universe, 0 mismatches`、rank 失败行 3 条、block 行 2 条、done 行 `refresh done: +120 rows, 3 failures, 0 mismatches, complete=False, panel cutoff=2026-09-23`；options/ah 同样例一 → 断言 mf state=done、rows=120、complete=False、cutoff="2026-09-23"、blocks=2、rank_fails=3、rank_pass_events=1、mf 不 ok、ok=2。
     * 样例四（三道 missing）：digest(None, None, None) → 三道 state=missing、除 state 外全部字段 None/计数渲染 `-`、ok=0、lines 4 条逐字节（含 `VERDICT ok=0/3`）。
     * 边界/违规族至少 8 条：① options done 行 `mismatches=['a', 'b'] fails=['c']` → done_mismatches=2、done_fails=1；② options done 行 `last_pass=None` → last_pass="None"（原始 token）；③ options 文本仅空白行（空串与空格行）→ state=empty、fuse_events=0、结构字段全 None；④ ah done 行 complete=True exit=3 → state=done 但 ah 不 ok（exit≠0）；⑤ ah 文本仅 3 条 `EM mapping unavailable: ...` 行 → state=in_progress、done 系七字段=None、em_unavail=3；⑥ options 两条 done 行（先 pass_ok=False 后 pass_ok=True）→ done_pass=True（最后一条胜）；⑦ options 两条 `[opt-refresh] conn-fuse:` 行 → fuse_events=2；⑧ ah done 行 complete=False → ah 不 ok；⑨ mf done 行 `panel cutoff=None` → cutoff="None"。
     全部断言通过=打印断言计数与 "ALL PASS" 后 exit 0，任一失败=打印失败明细 exit 1；
   - live 模式 `lane_log_digest.py [logs_dir]`：logs_dir 缺省="logs"（相对当前工作目录）；不存在或非目录=stderr 一行+exit 2；三件逐件以 utf-8（errors=replace）读全文，单件不可读按 None 传入纯函数；正常=打印 4 行；ok==3 → exit 0，否则 exit 1。

7. 输出纪律：所有 stdout/stderr 输出为 ASCII 可打印字符；不写任何文件；零网络。
8. 交付形态：输出=单个完整 Python 文件内容（唯一 ```python 代码块），文件之外无任何解说文本。

---
arm placement protocol (不属于提示词，跑前注记): A 臂产物=results/local_coding_pilot/tasks/09/A/lane_log_digest.py；B 臂产物=results/local_coding_pilot/tasks/09/B/lane_log_digest.py；双臂验证=python <arm>/lane_log_digest.py selftest（与冻结验证命令语义恒等）。
