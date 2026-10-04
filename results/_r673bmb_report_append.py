import io, datetime

RP = r"C:\Fluxgroup\FluxGroup\quant\bigmoney\logs\iteration-loop\round_reports.md"
now = datetime.datetime.now().isoformat(timespec="seconds") + "+08:00"

product = (
    "%s | r673 (bm-b) PRODUCT (dept:舰队集成收口+数据维护链): [watermark verdict: GREEN "
    "(red=false; next_pick=None; satengine alive idle heartbeat 47s; post_review REPORT face "
    "red_rows=0; py_cpu 85pct=trio burn 合法占用)] | 当前活: FUND 三族 NULLS 烧录在飞 V778/Q603/D451 "
    "of 2000 @13:40 (39.0/30.2/22.6pct, owner=bm-b, daemons alive, ETA 10-06/07/08) "
    "| 最近实物: S0 落账 r672 滞留件回送 + 31-UU canon resolve merge commit 0046dfad9 DELIVERED "
    "(13:3x, ts-freshness 19 面 theirs-newer 13:26-29 bm-a 波 / paper-family 10 面语义等价 ours / "
    "token r456 whole-face fallback / x2 行级 union +6 ours-only, r657-r675 律全过; index.lock 竞态 "
    "=autofill daemon tick 瞬态, 重试单 add 收口零伤) + 本轮 S6 38/38 rc0 (REPORT-2026-10-04 + "
    "LIVE-2026-10-04 双面再生成 13:39, regime=ORANGE 取守为攻; dualrun ZERO-DRIFT streak 51; "
    "golden-week 大多数腿诚实 no-op) + orders/D-19 双扫双键 MATCH (153/153, decisions 4E5BE321 / "
    "orders 68947C17, sparse-clone+git-show 原字节配方复跑) | 本轮同窗: smoke 48/48 + attrition guard "
    "CLEAN + 自愈 5/5 (loop pin=2 no-op/watchdog/claws 双装) + 收养轮 S7 push-race 预检 (r643 三证: "
    "reflog 全本机时戳/进程数=1/inbox 0) | 下轮指针: trio 看护续期; VALUE 烧完 (~10-06 15时) = finalize "
    "候选窗开 (10-06..09), finalize 轮必同窗池面双翻 (r668 律); 本地未达 origin commit 数=0 "
    "(0046dfad9 DELIVERED 实证 ahead=0 behind=0)\n" % now
)

with io.open(RP, "a", encoding="utf-8", newline="") as f:
    f.write(product)

t = io.open(RP, encoding="utf-8", errors="replace").read()
assert t.count("r673 (bm-b) PRODUCT") == 1, "PRODUCT line count != 1"
print("appended r673 PRODUCT line; count==1 OK")
