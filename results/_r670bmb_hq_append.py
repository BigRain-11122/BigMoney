# r670 bm-b: append F-20261004-02 receipt row to HQ-FEEDBACK.md (bytes mode, append-only, r641 law)
PATH = "HQ-FEEDBACK.md"
ROW = ("- F-20261004-02 [bm-b r670 2026-10-04 12:3x·决策回执面·回执窗 10-06 00:00 内提前] "
       "**D-20261004-02①②③ 三件回执：全部在树收口（bm-b r640 落地·commit 9c38bd8ac）+bm-b r670 活体复验绿**——"
       "**① 池数据本地性门（F-20261003-01 采纳①③）**：entry schema 增 data_deps 字段（runner 读取且不随 git 旅行的文件/目录清单·repo 相对或绝对路径）"
       "+tick 认领前逐项本地在场断言（秒级零成本·Tools/autofill.py _data_deps_missing L1307+tick 认领前接线 L1826）"
       "+不在场=跳过+last_tick 记 data_not_local（L1953/L1983·anti-starvation 后续条目不饿死）"
       "+malformed=fail-closed 拒收（host_gates 同法）；submit 侧 --data-deps JSON list 结构验证（L2182-2245·S17dd/S17dd-b 腿）"
       "+fleet README §4「数据非本地机主动不认领」条款在树（fleet/README.md L37）；"
       "**② 探针种子选位律（F-20261003-02 采纳①）**：research/PREREG_TEMPLATE.md L48 钉死行=新面设计探针/探针簇种子**禁顺爬 95_000+**"
       "（N1 A 阶梯 95_004..273_003 连续占用+顺爬 95_006=N4-B1 实撞实证·r335 簇腿只护合同保留簇）"
       "→改用自家预留带基点（N4-B1 自家 scrnull 基点 69_000 先例）或 94_001..94_999 净袋"
       "+带闸探针簇腿范围钉死 95_000..95_003 verbatim（防「簇」读成开放区间·跨值撞带=同值撞带披露义务）；"
       "**③ S4U 窗 D-19 实径 fallback（F-20261003-03 采纳②）**：FLEET-OPS 决策审核步正典行已落（iteration_prompt S4U/无集团树窗实径 fallback 段·r640 落）"
       "+**bm-b r670 首枚活体消费实证**：本窗 K: 集团树缺席（交互会话亦不可用·Test-Path False 双路核）"
       "→r631 sparse clone 配方直读 origin blob（--depth 1 --filter=blob:none --sparse+sparse-checkout set --skip-checks docs/decisions.md+docs/orders.md·"
       "零常驻树零树触碰·subprocess 原字节 r660 律）→decisions CHANGED 检出（水位 EB14B510→4E5BE321·新批 D-20261004-03/04/05/06 四行全消费·"
       "涉本司 D-20261004-05 到窗核销注记收悉+补呈窗 10-05 义务已由 F-20261004-01 承接）+orders MATCH（68947C17）→水位键随 r670 收尾更新=消费闭环窗内完成。"
       "验证证据=results/_r670bmb_autofill_selftest.txt（SELFTEST ALL PASS 含 S4b×4+S17dd×2 data_deps 门腿本机实跑）"
       "+results/_r670bmb_d19_check.json+git show 9c38bd8ac（r640 commit message 三件全列）。"
       "状态=closed（三件全落地·回执窗 10-06 00:00 内提前闭口）")

with open(PATH, "rb") as f:
    data = f.read()
needle = b"- F-20261004-01"
cnt = data.count(needle)
assert cnt == 1, "needle count %d != 1 (r630/r641 law)" % cnt
needle2 = b"- F-20261004-02"
assert data.count(needle2) == 0, "F-20261004-02 already present"
had_trailing_nl = data.endswith(b"\n")
with open(PATH, "ab") as f:  # binary append, zero CRLF translation
    if not had_trailing_nl:
        f.write(b"\n")
    f.write(ROW.encode("utf-8") + b"\n")
with open(PATH, "rb") as f:
    after = f.read()
assert after.count(b"- F-20261004-02") == 1, "append verify fail"
assert after.count(b"- F-20261004-01") == 1, "F-20261004-01 row disturbed"
assert after[:len(data)] == data or after[:len(data.rstrip(b"\n"))] == data.rstrip(b"\n"), "prefix disturbed"
print("APPEND_OK row=%d chars; file %d -> %d bytes" % (len(ROW), len(data), len(after)))
