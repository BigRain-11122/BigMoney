# bypass-tick 2026-10-07T00:0x bm-a: retreat-line appender (concurrent r799 main-body detected)
# read-only wrt everything except one append line to round_reports-bm-a.md
import datetime, sys

P = "round_reports-bm-a.md"
raw = open(P, "rb").read()
tail = raw[-6000:]

enc = None
for e in ("utf-8", "gbk"):
    try:
        tail.decode(e)
        enc = e
        break
    except UnicodeDecodeError:
        pass
if enc is None:
    print("ENCODE_DETECT_FAIL"); sys.exit(2)

ts = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
line = (
    ts + " | round 799 旁路退避 tick (bm-a, dept:工程/舰队) | "
    "[占用退避] 探测到本机 r799 主体会话活迹（W166 冻结链进行中：_r799bma_w166_* 工具族 23:37→23:52 递进 + "
    "perpetual_faces*.py 23:52 修改 + research/PERPETUAL_N1_W166_PREREG.md 23:50 新建——同仓单执行体铁律）→ "
    "本轮只读维护后静默退避：零 commit、零心跳写、state round_no=798 未动、工作树零触碰（除本行） | "
    "读令（未代执行）：O-20261006-2358 致 bm-a 三面（tailnet P0 入网+心跳口径修复+RAM 承接）23:58 已上 origin，"
    "本 tick fetch 读到——ack 窗 ≤00:13、执行回执 ≤10-07 18:00；归 r799 主体 S7 双扫认领，"
    "若主体被 25min wrapper 杀无 closeout，00:08 tick 按 r471 猝死半成品处置律接管 dirty 面+补 ack | "
    "验证：origin tip a945dd1b0（fetch 干净）；占用判据=6min 内三文件 mtime 递进；编码探测 " + enc + " 严格解码过 | "
    "下轮指针：00:08 tick 先核 r799 终态（自然收口=正常轮；阵亡=收养 W166 冻结链 dirty 面）→ O-2358 ack/执行→"
    "tailnet 装机（需 CEO 后台批准则如实报阻点勿阻塞） | 本地未达 origin commit 数=0（本 tick 零 commit）"
)

nl = b"\r\n" if b"\r\n" in tail[-300:] else b"\n"
data = line.encode(enc) + nl
if raw and not raw.endswith(b"\n"):
    data = nl + data
with open(P, "ab") as f:
    f.write(data)

raw2 = open(P, "rb").read()
ok = len(raw2) == len(raw) + len(data) and raw2.endswith(data)
print("APPEND_OK" if ok else "APPEND_VERIFY_FAIL", enc, len(raw), "->", len(raw2))
