"""Append the round 2123 row to round_reports-bm-c.md (multi-writer face: fresh read, append, write)."""
import io
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
PATH = "round_reports-bm-c.md"

ROW = (
    "| 2026-11-26 09:0x | 2123 | **PRODUCT（产品优先律·watermark=绿 red=false lane=healthy·孤儿面=0·竞争窗 rc=0 CLEAN 单宿主）**："
    "本轮两件，都是「东西早就算出来了，只是没人发布/没人放行」。"
    "①**把四轮没能发布的整代产物发了**：r2115/r2119/r2121/r2122 每轮轮首都因「470 件脏面（已死前任会话留下的整代链产物）」按纪律只定向 add 而不敢整批提交，"
    "于是纸盘账户（PROS/AGGR/GRID）、每日数据追加、派生研究页这一代**只在这台盘的磁盘上**——远端读者看到的比本机自检打分的还要旧。"
    "本轮先证明这代是「跑完了」而不是「还在写」：竞争窗 rc=0 CLEAN（单宿主）、HEAD==origin、470 件 mtime 全在 291min 以内（16 件 <1h / 454 件 1-6h）且无写手存活、"
    "treasure_guard prescan 零命中、暂存 470 件 17.7MB 无二进制无整文件删除 → 提交 **3f360c0515** 直推 origin/main（2ca825bc6b..3f360c0515），fetch 后 **0/0**，"
    "ls-tree 抽查 5 件在位（LIVE-2026-11-26.md / LIVE-BOOK-20261126.md / DECLARATION-2026-11-26.md / audit 分片 / face_consumer_census.json）。"
    "②**关掉「涨停池停了两个交易会话」那条红**（读者面自己写着「上面的数不是今天的盘面」）：采集器自 11-23 起每轮 `OVERLAP MISMATCH zt 2026-11-23` exit 3、不写不说是哪不同。"
    "探针（`results/_r2123bmc_zt_overlap_probe.py` 只读）把差异摆出来：stored **143** 行 / source **146** 行，**只增不减**（+001360/002623/600838），"
    "且共享的 143 行里还有两行价还在动（000700 10.0→9.992372、603706 10.139860→9.981430）——零删除+迟到新增+两行未定值=**这一天的切片写在了收盘定盘之前**，"
    "不是终态被改史；另三面（zbgc 24 / dtgc 3 / strong 56）逐行比价全 match。"
    "按采集器自己文档写的那道门（「benign-completion amendment = a later round with evidence, not a silent accept」）出裁定：`data/zt_pool/amendments.json` 追加 "
    "`LATE_COMPLETION_SUPERSET`——只替换这一天这一面，其余逐日不动，并记下为什么改；整改脚本在「存的切片已不是探针看过的那一份」时硬拒 rc3（写得进=可审计）。"
    "**自捕一枚真坑**：整改首版把这一天写坏了——`fetch_day()` 返回的源帧**没有日期列**（日期是采集器自己盖的），reindex 后 146 行落地时日期为 NaN、11-23 那 143 行整片消失（面板 1894→1897 行、33→32 天）；"
    "复读文件当场发现，`git checkout HEAD -- data/zt_pool/zt.parquet` 复原，补三处：盖 `日期=FLAT`（面板口径 YYYYMMDD 无横杠）、`代码` 补零到 6 位（R58 行壳防御）、"
    "**写之前断言 `len(merged)==len(old)-len(old_day)+len(new_day)`**。重跑后：stored 146 / refetched 146 **match=True**、value-diff 0，面板 1897 行 33 天口径统一、11-23 146 行。"
    "｜**未做（如实）**：①采集器**这一轮没能真正拉 11-24/11-25**——30 分钟最小尝试间隔被 08:57:58 那次「拒绝写入」的尝试花掉了，下一次窗 ≈**09:28**；"
    "本轮**不打洞绕过**（那次尝试确实打到了源，压源计数器是诚实的），四面的闸已全部 match，到窗自动补两天（8 次调用）；已挂一次性死信核查（09:3x 验它是否真的推进，未推进则点名）；"
    "②全量冒烟**未跑**——上一轮分离进程 pid 96660（08:42 起）仍在写 `logs/smoke_2122_after.log`，本窗不重跑、**不宣称套件总数**；"
    "③r2122 登记的其他 carried 红（paper book NAV 身份差 6.5e-09、phase_atlas_arms 三臂重烧、toll-ladder 等）本轮未碰，未改任何判据线去修绿。"
    "｜S0：machine.json=**bm-c**｜`orphan_face_probe` py_faces=6 **orphans=0**（resident_servers=2）｜`repo_write_contention --lookback-min 45` **rc=0 CLEAN**（单宿主 pid 98740）｜"
    "fetch 后 ahead=0 behind=0｜S0.5：`fleet/orders` 117 件 vs 心跳 orders_ack → **未回执 0**；集团 decisions 水位未动（自持 sha 79e3083b…，本轮零新决策面）｜"
    "S3：水位 **red=false / lane=healthy**；饱和引擎 `Tools/saturation_engine.py status` **rc0 alive**（last_verdict=idle·claimable 0）｜"
    "S7：`attrition_ledger_guard scan` **CLEAN**（4 账本·2 处历史缩行 healed 照录）｜"
    "**CEO 三行**：当前活＝把「涨停池停在 11-23」这条红用证据裁定放行（改的是数据切片，不是判据线）｜"
    "最近实物=`K:\\Fluxgroup\\FluxGroup\\quant\\bigmoney\\qa\\zt-pool-late-completion-r2123.md`（09:0x·探针表 + 裁定 + 首版写坏与复原全过程）+ "
    "`K:\\Fluxgroup\\FluxGroup\\quant\\bigmoney\\docs\\live_usage\\LIVE-2026-11-26.md`（随 470 件整代产物发布）｜"
    "下个里程碑＝09:28 后采集器补 11-24/11-25 两个会话、CEO 页「读数陈旧」那行消失（≤2h，死信核查已挂）｜"
    "记账：轮报告 1 处 + QA 1 件 + state 1 处 + 心跳 1 处 + amendments 账 1 处 = 5 |\n"
)

with io.open(PATH, encoding="utf-8", newline="") as fh:
    text = fh.read()
if "| 2026-11-26 09:0x | 2123 |" in text:
    print("row already present, skipped")
else:
    if not text.endswith("\n"):
        text += "\n"
    text += ROW
    with io.open(PATH, "w", encoding="utf-8", newline="") as fh:
        fh.write(text)
    print("appended round 2123 row, file now %d bytes" % len(text.encode("utf-8")))
