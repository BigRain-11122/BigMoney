# T-70 local-coding pilot — task 10 frozen prompt (identical for both arms)

任务：fleet 心跳 epoch 类型 lint（全机 heartbeat_epoch_utc int 扫描 + clock_read 面核验 = smoke F7 面）
目标文件：scripts/hb_epoch_lint.py（新建；仅此一件产物）
约束：Python 3.14 可跑；零第三方新依赖（仅标准库）；selftest 子命令=离线断言；exit 0=通过
验证命令：python scripts/hb_epoch_lint.py selftest

输入样例与输出契约：

1. 输入面（live 层）：machines_dir 内全部 *.json（每件=一台机的心跳文件；机器名=文件名去 .json 后缀；非 .json 件忽略；n=*.json 件数）。逐件读全文：不存在或不可读 → 该机 text=None；可读 → text=文件字节按 utf-8（errors=replace）解码后的全文。

2. 解析面（逐机独立）：
   - text=None → state=missing；
   - text 先剥单个前导 U+FEFF（BOM 容忍，剥后进入下一步），再 json.loads；解析抛错 → state=bad_json；解析成功但顶层非 dict → state=bad_json；解析成功且顶层为 dict → state=ok。

3. 字段面（仅 state=ok 时求值；其余态字段缺席）：
   - heartbeat_epoch_utc（下称 epoch）：
     * 键缺席 → epoch_type=missing；
     * 值为 bool → epoch_type=bool（**bool 判定必须在 int 判定之前——isinstance(True, int) 为 True 的假阳性陷阱，JSON true 必须判 bool 非 int**）；
     * 值为 str → epoch_type=str；
     * 值为 float → epoch_type=float；
     * 值为 int → epoch_type=int；
     * 其余（None/list/dict 等）→ epoch_type=other。
   - epoch_pos：epoch_type=int 时值为 >0 → yes，否则（int 且 ≤0）→ no；epoch_type 非 int → `-`。
   - clock_read：
     * 键缺席 → clock=missing；
     * 值为 str 且含子串 "T" → clock=ok；
     * 值为 str 但不含 "T" → clock=bad；
     * 值非 str → clock=bad。
   - verdict：PASS ⟺ state=ok AND epoch_type=int AND epoch_pos=yes AND clock=ok；其余一切情形（含 missing/bad_json）=FAIL。

4. epoch 渲染（epoch 字段的显示值）：
   - int → 十进制数字串（如 1790359975）；
   - bool → true/false（小写）；
   - str → json.dumps(该串)（带双引号，ASCII 转义）；
   - float → repr(该值)（如 1790359366.0）；
   - None → null；
   - list/dict → json.dumps(该值)；
   - 键缺席 → `-`。
   epoch_pos 渲染 yes/no/`-`；clock 渲染 ok/bad/missing。

5. 输出（stdout：每机一行 + 末行 VERDICT，全 ASCII，字段间单空格）：
   `MACHINE <name> state=<s> epoch_type=<t> epoch=<v> epoch_pos=<p> clock=<c> verdict=<PASS|FAIL>`
   - 行序=机器名升序（Python str 比较序）；
   - state ∈ {missing, bad_json, ok}；epoch_type ∈ {int, bool, str, float, other, missing}；
   - state=missing 或 bad_json → 该行 epoch_type/epoch/epoch_pos/clock 全渲染 `-`、verdict=FAIL；
   - 末行：`VERDICT pass=<k>/<n>`（k=PASS 机数，n=*.json 机数）；n=0 → 仅 VERDICT 行 `VERDICT pass=0/0`（k=0）。

6. CLI 三模式：
   - 无参数：stdout 打印一行用法说明，exit 2；
   - selftest：不读任何仓库文件、不写任何文件，内嵌合成样例对纯函数做断言。纯函数签名语义固定：lint(machines)，machines=dict[str, str|None]（键=机器名，值=该机文件全文或 None=missing）；返回 dict 含 machines（dict：每机全部字段：state=str、epoch_type=str、epoch=str[渲染值]、epoch_pos=str、clock=str、verdict=str；missing/bad_json 态下 epoch_type/epoch/epoch_pos/clock=None）、pass_count(int)、n(int)、lines(list[str]，=按第 5 条模板渲染的全部行，恰 len(machines)+1 条）：
     * 样例一（全 PASS 三机）：
       bm-a：`{"machine_id":"bm-a","heartbeat_epoch_utc":1790359975,"clock_read":"2026-09-26T02:12:55+08:00"}`
       bm-b：`{"machine_id":"bm-b","heartbeat_epoch_utc":1790359366,"clock_read":"2026-09-26T02:02:46+08:00"}`
       bm-c：`{"machine_id":"bm-c","heartbeat_epoch_utc":1790257907,"clock_read":"2026-09-24T21:51:47+08:00"}`（陈旧期值仍 PASS——本件=类型面非新鲜度面）
       断言：pass_count=3、n=3；三机全字段值（state=ok、epoch_type=int、epoch_pos=yes、clock=ok、verdict=PASS、epoch 逐机数字串）；lines 4 条逐字节字符串比对，含末行 `VERDICT pass=3/3`。
     * 样例二（epoch 类型病族）：
       bm-a：`{"heartbeat_epoch_utc":"1790359975","clock_read":"2026-09-26T02:12:55+08:00"}`（字符串期=违例实录形态）→ epoch_type=str、epoch 渲染 `"1790359975"`、FAIL；
       bm-b：`{"heartbeat_epoch_utc":true,"clock_read":"2026-09-26T02:02:46+08:00"}` → epoch_type=bool、epoch 渲染 true、epoch_pos=`-`、FAIL；
       bm-c：`{"heartbeat_epoch_utc":1790359366.0,"clock_read":"2026-09-24T21:51:47+08:00"}` → epoch_type=float、epoch 渲染 1790359366.0、epoch_pos=`-`、FAIL；
       断言：pass_count=0、n=3、三行 verdict=FAIL、末行逐字节 `VERDICT pass=0/3`。
     * 样例三（结构病族）：
       bm-a：None → state=missing、四字段 None、FAIL；
       bm-b：`{oops` → state=bad_json、四字段 None、FAIL；
       bm-c：`{"machine_id":"bm-c"}`（两键全缺席）→ state=ok、epoch_type=missing、epoch=`-`、epoch_pos=`-`、clock=missing、FAIL；
       断言：pass_count=0、n=3、lines 含 `MACHINE bm-c state=ok epoch_type=missing epoch=- epoch_pos=- clock=missing verdict=FAIL` 逐字节。
     * 样例四（clock 面+epoch_pos 面）：
       bm-a：`{"heartbeat_epoch_utc":1790359975,"clock_read":123}` → clock=bad、FAIL；
       bm-b：`{"heartbeat_epoch_utc":1790359366,"clock_read":"2026-09-26 02:02:46+08:00"}`（空格代 T）→ clock=bad、FAIL；
       bm-c：`{"heartbeat_epoch_utc":0,"clock_read":"2026-09-24T21:51:47+08:00"}` → epoch_type=int、epoch=0、epoch_pos=no、FAIL；
       断言：pass_count=0、n=3。
     * 边界/违规族至少 10 条：① bool False → epoch_type=bool、epoch 渲染 false、FAIL；② epoch 键值 null → epoch_type=other、epoch=null、epoch_pos=`-`、FAIL；③ clock_read="" → clock=bad；④ `{}` 空对象 → epoch_type=missing、clock=missing、FAIL；⑤ `{"heartbeat_epoch_utc":4611686018427387904,"clock_read":"2026-09-26T02:12:55+08:00"}`（2**62 大 int+合法 clock）→ PASS（epoch_pos=yes）；⑥ 前导 BOM 文本 `\ufeff{...合法...}` → state=ok 照常解析（BOM 剥离律，样例一 bm-a 文本加 BOM 前缀重跑断言全 PASS）；⑦ 顶层非 dict 四态：`[1,2]` / `"x"` / `123` / `null` → 全部 state=bad_json、FAIL；⑧ 行序稳定性：machines 输入序 {bm-c, bm-a, bm-b}（dict 插入序乱序）→ lines 前三行序恒为 bm-a/bm-b/bm-c；⑨ epoch 负 int（如 -5）→ epoch_type=int、epoch_pos=no、FAIL；⑩ clock_read="None"（str）→ 不含 "T" → clock=bad。
     全部断言通过=打印断言计数与 "ALL PASS" 后 exit 0，任一失败=打印失败明细 exit 1；
   - live 模式 `hb_epoch_lint.py [machines_dir]`：machines_dir 缺省="fleet/machines"（相对当前工作目录）；不存在或非目录=stderr 一行+exit 2；*.json 按文件名升序逐件读入（utf-8 errors=replace，剥 BOM 在解析层）构造 machines dict 喂纯函数；正常=打印全部行；n>0 且 pass_count==n → exit 0；否则（含 n=0）exit 1。

7. 输出纪律：所有 stdout/stderr 输出为 ASCII 可打印字符；不写任何文件；零网络。
8. 交付形态：输出=单个完整 Python 文件内容（唯一 ```python 代码块），文件之外无任何解说文本。

---
arm placement protocol (不属于提示词，跑前注记): A 臂产物=results/local_coding_pilot/tasks/10/A/hb_epoch_lint.py；B 臂产物=results/local_coding_pilot/tasks/10/B/hb_epoch_lint.py；双臂验证=python <arm>/hb_epoch_lint.py selftest（与冻结验证命令语义恒等）。
