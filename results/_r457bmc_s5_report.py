"""r457 bm-c S5: round report line append (bytes mode, EOL-probe)."""
import datetime
import os

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
P = os.path.join(ROOT, "round_reports-bm-c.md")
now = datetime.datetime.now().astimezone().strftime("%Y-%m-%dT%H:%M:%S+08:00")

LINE = (
    now + "｜r457｜dept:工程+舰队（golden-week 值守+池完整性修复轮）｜"
    "watermark verdict=绿（red=false healthy·satengine rc0 活·post_review 45 YES/0 NO/5 WAIT 零红）｜"
    "当前活=金周值守+QUALITY-NULLS 无主窗修复（r637 漏网第 3 分片外科恢复）｜"
    "最近实物=commit a093a7720（results/runnable_pool.json owner 行恢复 bm-b+shard note 溯源）+"
    "fleet/inbox/MSG-2026-10-04-0915-bmc-bmb.md+results/_r457bmc_s6_log.txt（S6 38/38 rc0 PARITY PASS）｜"
    "下个里程碑=fund-trio finalize 窗 10-05 10:30 开（QUALITY=长杆·bm-b daemon 领养确认=下轮核）｜"
    "did：(1) S0=rebase 遗留零+pull--rebase 撞 daemon treadmill→absorb 4 lane 面（91ad1d012）+"
    "behind 6 waves 干净 rebase；(2) S0.5 orders 153/153 双扫零未回执+D-19 decisions EB14B510 MATCH+"
    "group orders 68947C17 MATCH 双零动作+inbox 0；(3) S1 smoke 48/48；(4) S2 板空（job_list 0+"
    "fleet 0 open·T-167 theme-judge bm-a claimed 不碰）；(5) S3 常设检查全绿（WM red=false·"
    "satengine rc0·post_review 零 ✗·pool 362done/1waiting/3ready）→**核心发现**=FUND-QUALITY-P1-NULLS "
    "shard 在共享池面 ownerless 近 24h 而 bm-b 正主烧录活（行 504→510 增长实证+MSG-0857/0925/2005 "
    "三证+bm-b r659 trio_health 探针佐证）——根因=r637 四面手术只修 VALUE/DIVLOWVOL 漏第 3 分片×"
    "r288 keepalive owner==myid 自锁环（claim 缺失→daemon 永不续戳）；危害=bm-a daemon 每 tick 试领"
    "（09:02 fuse_refused 571 次实录·仅 crash fuse 拦=r617 版本键边界）；处置=treasure_guard rc0+"
    "外科手术 5 门全过（identity/needle==1/reparse/trio pre-post delta/numstat 3:1）恢复 owner=bm-b+"
    "owner_since=09:11:39 action-time（r400）→r288 门即过=烧录机 daemon 自领养自愈闭环+MSG 呈 bm-b "
    "核 pid 57116+确认领养；首试 reparse 门拦 r629 加字段镜像坑（原末字段后插新字段漏补尾逗号）当场修复零伤害；"
    "(6) S6 38/38 rc0（dualrun ZERO-DRIFT streak 51·audit CLEAN·update_daily 0 新行金周 cutoff 09-30·"
    "C 族 lane guards 诚实 skip·REPORT/LIVE-20261004 幂等刷新）；(7) S4 pit line 入 CODELY.md（claim 自锁坑+r629 "
    "镜像坑+多分片手术枚举律）；(8) S7=attrition CLEAN+claws 双装+loop pin5+watchdog 幂等+state/心跳更新。"
    "本地未达 origin commit 数=0（手术段 DELIVERED a093a7720 push_verify ahead=0·收尾段随轮推）\n"
)

with open(P, "rb") as fh:
    raw = fh.read()
crlf = raw.count(b"\r\n")
lf_only = raw.count(b"\n") - crlf
eol = b"\r\n" if crlf > lf_only else b"\n"
if not raw.endswith(b"\n"):
    addition = eol + LINE.encode("utf-8").replace(b"\n", eol)
else:
    addition = LINE.encode("utf-8").replace(b"\n", eol)
with open(P, "wb") as fh:
    fh.write(raw + addition)
with open(P, "rb") as fh:
    chk = fh.read()
print("APPENDED pre=%dB post=%dB eol=%s count_r457=%d" % (
    len(raw), len(chk), "CRLF" if eol == b"\r\n" else "LF",
    chk.count("r457".encode("utf-8"))))
