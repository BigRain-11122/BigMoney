# T-70 local-coding pilot — task 08 frozen prompt (identical for both arms)

任务：options 采集道 checkpoint 对账器（cells 行数/代码集 vs panel.universe/attempted 对账）
目标文件：scripts/opt_cells_recon.py（新建；仅此一件产物）
约束：Python 3.14 可跑；零第三方新依赖（仅标准库）；selftest 子命令=离线断言；exit 0=通过
验证命令：python scripts/opt_cells_recon.py selftest
输入样例与输出契约：

1. 冻结输入面（两件，均相对 results_dir，文件名冻结）：
   | 件 | 角色 | 形态 |
   |---|---|---|
   | options_update_cells.jsonl | checkpoint 逐合同行 | JSONL（每行一 JSON 对象） |
   | options_update_status.json | panel 面 | JSON dict（键 panel 内含对账基准） |
   panel 键契约：panel.universe（int）、panel.attempted（int）、panel.appended（int）、panel.last_pass_date（str "YYYY-MM-DD"）、panel.fails（list）、panel.mismatches（list）。
2. 读取面：一律 utf-8-sig 读（容 BOM）。live 模式从 results_dir 读两件：
   - 任一件不存在/不可读 → stderr 一行 + exit 2（输入面错误，非对账判读）；
   - status 件 JSON 解析失败或顶层非 dict → stderr 一行 + exit 2；
   - cells 件按行解析（见第 3 条），行级病计入 malformed 计数（不 exit 2）。
3. cells 行分类（逐行确定性，四类互斥）：
   - blank：strip 后为空串 → 计 blank，跳过；
   - malformed：JSON 解析失败 / 解析成功但非 dict / 行契约违例 → 计 malformed；
   - valid：其余全部（行契约=「code」为 str 且非空、「pass」为 str、「kind」为 str、「status」为 str；「appended」若在场必须为 int，缺席按 0 计入合计；任一违例=malformed）；
   - 计数恒等式：lines = blank + malformed + valid（lines=原始总行数，含 blank 行）。
4. 派生统计（仅基于 valid 行）：
   - codes_unique=distinct code 值个数；dup_codes=出现次数>1 的 code 个数；
   - kind_live=kind=="live" 行数；kind_extra=kind=="extra" 行数；kind_other=其余（仍 valid，计入 kind_other）；
   - status_ok=status=="ok" 行数；status_fail=其余（仍 valid）行数；
   - appended_sum=valid 行 appended 合计（缺席按 0）；
   - pass 集合=distinct pass 值；pass 渲染规则：恰一个值→原值；>1 个值→MULTI；0 个 valid 行→"-"。
5. 对账六检查（冻结，c0-c5，ok=1 过/ok=0 败）：
   | 检查 | 判据 | 渲染值 |
   |---|---|---|
   | c0_malformed | malformed == 0 | malformed |
   | c1_count | valid == panel.attempted | valid, attempted |
   | c2_universe | codes_unique == panel.universe | codes_unique, universe |
   | c3_pass | pass 渲染值 == panel.last_pass_date（pass 为 MULTI 或 "-" 时恒败） | cells_pass, panel_pass |
   | c4_appended | appended_sum == panel.appended | cells, panel |
   | c5_status | status_fail == 0 AND len(panel.fails) == 0 AND len(panel.mismatches) == 0 | cells_fail, panel_fails, panel_mismatches |
   panel 键缺席渲染规则：universe/attempted/appended/last_pass_date 缺席或非 int（日期为非 str）→ 该值渲染为 "-"，对应检查恒败（诚实警示，不崩溃）；fails/mismatches 缺席或非 list → 按 list 长度 -1 渲染且 c5 恒败。
6. 输出（stdout，行序固定，全 ASCII）：
   a. 头行：`RECON lines=<n> blank=<b> malformed=<m> valid=<v> codes_unique=<u> dup_codes=<d> kind_live=<kl> kind_extra=<ke> kind_other=<ko> status_ok=<so> status_fail=<sf> appended_sum=<as> pass=<render>`
   b. 检查行（固定序 c0-c5）：
      `CHECK c0_malformed malformed=<m> ok=<0|1>`
      `CHECK c1_count valid=<v> attempted=<a> ok=<0|1>`
      `CHECK c2_universe codes_unique=<u> universe=<univ> ok=<0|1>`
      `CHECK c3_pass cells_pass=<render> panel_pass=<lp> ok=<0|1>`
      `CHECK c4_appended cells=<as> panel=<pa> ok=<0|1>`
      `CHECK c5_status cells_fail=<sf> panel_fails=<pf> panel_mismatches=<pm> ok=<0|1>`
   c. 判读行：`VERDICT MATCH`（六检查全过）或 `VERDICT MISMATCH fails=<k>`（k=败检查数）。
7. CLI 三模式：
   - 无参数：stdout 打印一行用法说明，exit 2；
   - selftest：不读任何仓库文件、不写任何文件，内嵌合成样例对纯函数做断言（纯函数签名语义固定：recon(cells_lines, panel_text)，cells_lines=list[str]（原始行文本），panel_text=str（status 件全文）；返回 dict 含全部计数/派生值/六检查 ok 位/verdict/fails 计数）：
     * 样例一（对齐面，5 行全 ok：2 live+3 extra、pass 同值、appended 合计 3、panel universe=5 attempted=5 appended=3 last_pass_date 同值、fails/mismatches 空）：断言全计数逐位（lines=5 blank=0 malformed=0 valid=5 codes_unique=5 dup=0 kind_live=2 kind_extra=3 status_ok=5 appended_sum=3）、六检查全 ok=1、verdict=MATCH、fails=0、头行与六检查行=逐字节字符串比对（含 c4 渲染 cells=3 panel=3）；
     * 样例二（计数缺口）：4 valid vs attempted=5、universe=4 → 断言仅 c1 败、verdict=MISMATCH fails=1；
     * 样例三（重复 code）：行 code 序 a,b,c,a（4 valid、codes_unique=3、dup=1）、attempted=4、universe=4 → 断言 c1 ok、c2 败、dup_codes=1、fails=1；
     * 样例四（pass 双值）：两行 pass 值不同、panel last_pass_date 取其一 → 断言 pass 渲染=MULTI、c3 败、fails 计数只含 c3（其余检查按构造全过）；
     * 样例五（appended 缺口+status 面）：appended_sum=3 vs panel.appended=2 → c4 败；另构造一 status!="ok" valid 行 → status_fail=1 → c5 败；panel.fails=["10011425"] 单元素 → c5 败（同一检查只计一次）；
     * 边界/违规族至少 7 条：① 空白行（"  " 与 ""）→ blank 计数不进 malformed；② "{not json" → malformed；③ "[1,2]" 非 dict → malformed；④ dict 缺 code 键 → malformed；⑤ code 非 str（int 5）→ malformed；⑥ appended 为 str "1" → malformed；⑦ panel.universe 缺席 → c2 ok=0 渲染 universe=-；⑧ panel.last_pass_date 缺席 → c3 ok=0 渲染 panel_pass=-；⑨ 全行 malformed（0 valid）→ pass 渲染 "-"、c3 败、c1 按 attempted>0 败；⑩ panel.fails 缺席 → panel_fails=-1 渲染、c5 败；
     全部断言通过=打印断言计数与 "ALL PASS" 后 exit 0，任一失败=打印失败明细 exit 1；
   - live 模式 `opt_cells_recon.py [results_dir]`：results_dir 缺省="results"（相对当前工作目录）；results_dir 不存在或非目录=stderr 一行+exit 2；正常=头行+检查行+判读行；六检查全过 → exit 0，任一败 → exit 1（诚实警示位）。
8. 输出纪律：所有 stdout/stderr 输出为 ASCII 可打印字符（pass 值等动态面若含非 ASCII 照原样打印但本试点输入面全 ASCII）；不写任何文件；零网络。
9. 交付形态：输出=单个完整 Python 文件内容（唯一 ```python 代码块），文件之外无任何解说文本。

跑前勘误段（2026-09-26，commit 另行留痕；B 臂尚未消费本提示词=双臂信息面恒等保持）：规则 3 括注原文「lines=非 blank 原始行数；文件总行数减去 blank 行」与同句恒等式「lines = blank + malformed + valid」互斥——裁定以恒等式为准（其列于先且为结构性契约），括注更正为「lines=原始总行数，含 blank 行」。缺陷修正不影响 PASS/FAIL 判向（task05 先例范式）。

---
arm placement protocol (不属于提示词，跑前注记): A 臂产物=results/local_coding_pilot/tasks/08/A/opt_cells_recon.py；B 臂产物=results/local_coding_pilot/tasks/08/B/opt_cells_recon.py；双臂验证=python <arm>/opt_cells_recon.py selftest（与冻结验证命令语义恒等）。
