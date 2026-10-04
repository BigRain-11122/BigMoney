# r700 bm-b: round report line append (bytes mode, idempotent marker gate per r679 law)
LINE = ("2026-10-04T23:32:00+08:00 | round 700 (bm-b) | watermark 绿（red=false·py_low_with_work_cands=合法 RAM 门窗 "
        "free RAM 2.5-3.4GB<4GB floor·trio NULLS 三族在飞+N2 SHARD-2 RAM-gated=r691 帽律合法窗）｜当前活=trio NULLS V/Q/D "
        "三族烧录在飞（至 10-06T17/10-07T11/10-08T0x）+N2-W15 screen 11/12（我 SHARD-2 ready RAM-gated 待 daemon 自动点火）｜"
        "最近实物=CODELY.md 主件回弹处置批一（102,013→23,907B·87 条坑律 verbatim 分域迁入 11 pit 件·零丢失断言+receipt "
        "results/_r700bmb_d06_batch1_receipt.json @23:26）+D-20261004-05 四腿 bm-b 面回执（D-02 principal 三源自证件 "
        "results/_r700bmb_d02_principal_selfattest.json+D-03 scripts 面 selftest 11 legs PASS+D-05 pf selftest 9/9 PASS）｜"
        "下个里程碑=N2-W15 sec.9.1 具体化冻结窗 ≤10-08（screen 12/12+bm-a finalize 后）、judge 池烧 ≤10-12、D-06 域件 "
        "≤30KB 流水下沉腿 ≤10-07｜做了什么：S0-1 锚定 bm-b+state round 699→S0 fetch origin 零落后 0 拉取零冲突；D-19 双键检 "
        "出双 CHANGED→sparse-clone 读集团面（r677 配方）：decisions 疑回退取证（12:06 blob 4E5BE321 len=245,810 含 "
        "D-20261003×6/D-20261004×13 → 23:08 commit 06e9a1a blob 937A373D len=228,846 双双归零=−16,964B 10-03/10-04 两批行整面抹除·"
        "r639 回退族第二例·按律处置：水位随 origin 实况+已消费回执以轮报为准+MSG-2026-10-04-2330-bmb-ALL 总控定谳请求（含 发件 行）；"
        "orders O-20261004-2300=@Biggame 非本司零动作+P-2026-10-04-01/02 雷达两行=集团机制行本司 OH 切片过目面随候；S0.5 双扫 "
        "154/0 未回执（首尾两扫）；S1 smoke 48/48；S3 饱和引擎 status 活（gate:free RAM 2.5GB<4GB floor=RAM 门窗）+job_list 空+"
        "S3 主活=D-20261004-05 到窗四行收口 bm-b 面（原 10-05 00:00 顺延窗内提前）：D-20261002-02=principal 三源自证（XML 直读 5 任务 "
        "S4U×4+InteractiveToken×1·r576 活 S4U 保留判例+脚本 default 单源头注在位·偏差在 CEO 复裁面·零单方动作·python utf-16 解码假空窗 "
        "经 PS 直读双形交叉定谳=r661 律兑现+新坑律一条入主件）+D-20261002-03=scripts 面 selftest 11 legs PASS（活体验证腿·F-20261004-01 "
        "公司级回执补 bm-a/bm-b 面）+D-20261002-05=selftest 9/9 PASS（中位钉腿呈证）+D-20261002-06=对账行/md5 已由 F-20261004-01 呈+"
        "主件回弹处置=本批一（treasure_guard prescan：pit-* 登记簿命中=加性 append 维护正道·CODELY.md 非命中迁移合法·零删除）；S6 33/33 rc0 "
        "（25-28 黄金周诚实跳）；S7：loop 任务 no-op 针位 2 ✓+watchdog 重建（default principal per D-02）+双爪在位+attrition scan CLEAN+"
        "state round_no=700+心跳 epoch int 自证｜验证证据=results/_r700bmb_d06_batch1_receipt.json（87 条 sha16+字节恒等式 PASS）+"
        "_r700bmb_d02_principal_selfattest.json+_r700bmb_s6_chain.log（33 legs rc0）+smoke 48/48｜下轮指针=(a)W3 judge finalize 落地观察 "
        "bm-c 座 ETA ~10-05T02:00（_r487bmc_w3_judge_verify.py）(b)N2 SHARD-2 RAM-gated 自动点火 (c)N2-W15 冻结窗 ≤10-08 (d)MF IC 参考 "
        "批 bm-a lane 自愈候 (e)D-06 域件流水下沉腿+decisions 回退定谳跟催 (f)10-09 节后数据链检查｜本地未达 origin commit 数=0（commit 后 "
        "push+fetch+ls-tree 自证）")
raw = open("logs/iteration-loop/round_reports.md", "rb").read()
marker = b"| round 700 (bm-b) |"
if marker in raw:
    print("marker already present, ABORT (r679 idempotent gate)")
    raise SystemExit(1)
eol = b"\r\n" if b"\r\n" in raw[-200:] else b"\n"
body = raw[:-1] if raw.endswith(b"\n") else raw
line_b = LINE.encode("utf-8")
open("logs/iteration-loop/round_reports.md", "wb").write(body + eol + eol + line_b + eol)
after = open("logs/iteration-loop/round_reports.md", "rb").read()
assert after.count(marker) == 1, "marker count != 1"
print("appended round 700 line; marker count=1; new len", len(after))
