"""r457 bm-c S4: append pit line to repo CODELY.md (bytes mode, EOL-probe,
size gate <=50KB after append per D-20260925-01 water-mark trigger)."""
import os

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
P = os.path.join(ROOT, "CODELY.md")
LINE = (
    "- [2026-10-04 09:1x r457 bm-c] 池 claim 自锁坑=r288 keepalive owner==myid 门×活烧无主窗"
    "（FUND-QUALITY-P1-NULLS 实弹）：r637 四面手术只修了其触碰的 2/3 分片（VALUE/DIVLOWVOL），"
    "漏网 QUALITY 自 off-caliber 释放后 ownerless 近 24h——烧录机 daemon 因 owner!=myid 永不续戳"
    "（自锁环：claim 缺失→keepalive 跳过→claim 恒缺），他机 daemon 每 tick 试领（bm-a 09:02 "
    "fuse_refused 571 次实录·仅 crash fuse 拦=r617 版本键边界一破即第 5 次双烧）。正法=第三方外科恢复"
    " owner 行（r637 rightful-owner 先例+r400 action-time+shard note 溯源）→r288 门即过→烧录机 daemon "
    "下 tick 自领养自续戳=自愈闭环；手术门序=treasure_guard rc0+local==origin 恒等+needle count==1+"
    "reparse+trio pre/post delta+numstat 外科断言。连带：r629 加字段镜像坑=原末字段后插新字段必须补"
    "尾逗号（首试 reparse 门当场拦零伤害）；多分片手术必枚举全部受影响 entry 禁只修亲手触碰面。"
    "How to apply：池面观测见「活烧+owner=None」先按 r489 origin 真值复核，确认即走本条恢复路；"
    "他机 daemon keepalive 消息列单缺某在飞分片=自锁环指征。\n"
)

with open(P, "rb") as fh:
    raw = fh.read()
crlf = raw.count(b"\r\n")
lf_only = raw.count(b"\n") - crlf
eol = b"\r\n" if crlf > lf_only else b"\n"
ends_nl = raw.endswith(b"\n")
addition = (LINE.encode("utf-8")).replace(b"\n", eol)
if not ends_nl:
    addition = eol + addition
new = raw + addition
# size gate: repo-root CODELY.md must stay <=50KB after append (else hot-cold NOW)
size_kb = len(new) / 1024.0
print("pre=%dB post=%dB (%.1fKB) eol=%s ends_nl=%s" % (
    len(raw), len(new), size_kb, "CRLF" if eol == b"\r\n" else "LF", ends_nl))
if size_kb > 50.0:
    print("ABORT: >50KB trigger -- hot-cold reorg required this window, do not append raw")
    raise SystemExit(1)
with open(P, "wb") as fh:
    fh.write(new)
# self-verify: tail readback
with open(P, "rb") as fh:
    tail = fh.read()[-160:]
print("TAIL-OK %s" % (b"r457 bm-c" in tail))
