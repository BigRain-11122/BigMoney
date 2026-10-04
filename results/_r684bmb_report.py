# r684 bm-b: round report append (r679 idempotence gate: marker count==0
# before append; mixed-encoding file -> bytes mode append per r641/pit-encoding)
import io

FP = r"logs/iteration-loop/round_reports.md"
marker = "| r684 (bm-b)"
raw = io.open(FP, "rb").read()
n = raw.decode("utf-8", "replace").count(marker)
assert n == 0, "r684 marker already present (%d)" % n

LINE = (
    "2026-10-04T17:59:30+08:00 | r684 (bm-b) PRODUCT (dept:策略+工程): "
    "[watermark verdict: GREEN (red=false; satengine alive rc0 hb fresh "
    "queue=23 RAM-floor gate 2.9GB<4.0GB machine discipline self-ignite; "
    "dualrun ZERO-DRIFT streak 51; post_review REPORT-20261004 zero active "
    "red)] | 当前活: T-148 试用期大赛 pending-legs 收口面——lowamp-2 两员 "
    "YTD 烧录落表 + RC-10 池单元 RAM-gated 排队 + FUND trio NULLS 三族在烧 "
    "(V861/Q674/D512 of 2000 @17:06, owner=bm-b keepalive 鲜活, ETA V "
    "10-06T15 / Q 10-07T09 / D 10-08T03) | 最近实物: scripts/contest_ytd_"
    "legs.py (17:53, pending-legs 烧录 runner: lowamp 腿=lowamp_p3 冻结机制 "
    "verbatim 复用+全窗 reuse-parity 锚点全中 [ret_full 0.604283/0.554954]; "
    "revcensus 腿=census 机制镜像+公布 shard 行 census-stats parity 锚点 "
    "abort-on-drift; RAM floor 16GB exit 3; selftest 9/9) + "
    "contest_table.json 刷新 (17:55, A1.5 合并: 209 measured [185 ranked + "
    "24 listed] + 10 pending, LX-LA-EDGE-deep-base ytd +0.49% rank #43 / "
    "-x2 ytd +0.51% rank #41, 176d lockbox 窗如实披露, 表 sha16 "
    "e70010c053da57a6 重跑字节恒等) + CONTEST-TABLE.md CEO 面刷新 + 池单元 "
    "CONTEST-YTD-P1-RC-0OF1 autofill submit 落池 (host_gates p1c 缓存门 + "
    "data_deps 4 路径 + workers 4 BelowNormal) | 下个里程碑: RC-10 烧录 "
    "(RAM floor 清空即 autofill 点火, trio ETA 10-06..10-08 覆盖双机) -> "
    "assemble 重跑 = 全池 219-measured 终表, 10-08 治理日前交付 CEO 面 "
    "(窗内 48h) | 本轮同窗: S0 fetch 同步零动作 + orders/D-19 双扫双键 "
    "MATCH (154/154 零未回执; decisions 4e5be321 SHA-256 / orders "
    "68947c17 SHA-1 逐键口径) + smoke 48/48 + 板扫 169 票 0 open + S6 "
    "38/38 rc0 (results/_r684bmb_s6_log.txt; REPORT/LIVE-2026-10-04 再生 "
    "ORANGE_COOL) + 自愈 4/4 (loop pin=2 no-op/watchdog 18:00 首燃/双爪在 "
    "位) + attrition 4 ledgers CLEAN | 本地未达 origin commit 数=0 (commit "
    "后 push+fetch+ls-tree 自证)\n"
)
with io.open(FP, "ab") as f:
    f.write(LINE.encode("utf-8"))
chk = io.open(FP, "rb").read().decode("utf-8", "replace")
assert chk.count(marker) == 1
print("round report appended (marker count 1)")
