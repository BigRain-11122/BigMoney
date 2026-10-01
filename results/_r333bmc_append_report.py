# r333 bm-c round-report appender + closeout JSON self-checks (r504 json.loads law,
# r170/R262 heartbeat F7 field laws).
import json, sys

P_REPORT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\round_reports-bm-c.md"
P_HB = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\fleet\machines\bm-c.json"
P_STATE = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\state-bm-c.json"

LINE = ("2026-10-01T20:26:30+08:00｜r333｜dept:研究（W23 收口观察+引擎账本送达核验+T-134 第八件选件）"
"｜watermark verdict=绿（red=false·py_low_board_clear 假日板清合法 idle·引擎 W23 烧毕后空载=链序等待态如实〔W22 finalize bm-b 依赖〕）"
"｜S0-1 bm-c 锚定·S0 收敛 0 behind/0 ahead·S0.5 令差集=0（轮首+S7 双扫·139 全 ack）"
"·D-19 SHA MATCH-unchanged（753f99e8 raw-blob python 法·r333 治 d19 助手件 GBK 良性崩〔verdict 行后 UnicodeEncodeError·_r333bmc_d19.py utf-8 reconfigure 治愈〕）·S1 smoke 47/47"
"｜主产出=**W23 烧毕+引擎账本首活批全链路核验闭环**（W23 **12/12 分片 origin 三面复核实**·appender 归属修正：批1=拒后重建 **2204b8772** 推送成〔20:10:52·与孤儿首试 b2a67d637 字节恒等 6/6 diff --quiet rc0·r332 next(e) 闭账〕·批2=**8d30b64d4**〔余 6 片同刻推送成〕=appender 拒→重建→重试路径 live 验证·**T-141 s2 SLICE-2 观察闭账**〔首活批端到端+账本零幻影面维持〕）"
"+**T-134 s2 第八件选件定谳**（回执 results/_r333bmc_t134_pick8.json：pick=**scripts/p1e_ic_batch.py**〔4/4 池烧史=剩余 single_core 最烧·WM next_pick 已排 moneyflow IC 批于其 event-attention 车道·4-7min/shard 串行·~1.9s/单元≫100ms 门槛=r327 反例不适用·launcher 硬闸未转换拒其新池登记=转换即解锁排队批〕·r332 指名 t33/t36 诚实探轻〔17.3s/0KB drill〕降序·O-1738 动员令无串行冻结·O-2355 在后控面·转换=下轮首动作）"
"｜W23 finalize=链序阻塞如实〔W22 未落三查 20:16/20:2x/20:24·prev=活头 derive 410,748+·r310 完备门 12/12 已备〕·W26 冻结=own-prev 锚模式候 W23 finalize 后〔轮值槽 bm-c〕"
"｜S6 37/37 rc0（detached 自日志 PID 38052〔r324 分离律〕·holiday no-ops·dualrun ZERO-DRIFT streak 19/3·regime ORANGE days=4 shadow·t35_open_fill stale-takeover 合法〔bm-a 心跳>20min〕·REPORT/LIVE 幂等再生·token delta=0）"
"·S7 绿（pin5 no-op 20:25 次 fire·Watchdog schtasks 在场·claw MATCH·attrition CLEAN〔healed-2 照录〕·inbox MSG-202x〔W21 finalize prev-face VERIFIED=bm-a 链性回执〕processed 归档）"
"｜实况三行：当前活=W23 烧毕待 finalize（W22 bm-b 依赖）+p1e_ic_batch 转换备料｜最近实物=results/p2cal_ext/n1_w23/ 12/12（origin 2204b8772+8d30b64d4·20:10）+results/_r333bmc_t134_pick8.json｜下个里程碑=W23 finalize（W22 落后即跑·窗≤48h）+p1e 转换落地·月界首考 10-31"
"｜产品分=1（验证证据件+选件回执=文件实物·烧录归引擎自治面）｜本地未达 origin commit 数=0（closeout push 后 fetch 复核）"
"｜next: (r334)(a) W23 finalize 按 r310 完备门（W22 bm-b 先行·prev=活头 derive）(b) T-134 第八件转换=p1e_ic_batch ProcessPool（续作点=_r333bmc_t134_pick8.json）(c) W26 冻结候 W23 finalize 后（轮值槽·r511 穷尽扫描）(d) HANDOVER 5x stamp r335 (e) 月界首考 10-31")

raw = open(P_REPORT, "rb").read()
nl = b"\r\n" if raw.count(b"\r\n") >= raw.count(b"\n\r") and raw.count(b"\r\n") > 0 else b"\n"
# CRLF if any CRLF present, else LF
if b"\r\n" in raw:
    nl = b"\r\n"
else:
    nl = b"\n"
sep = b"" if raw.endswith(nl) else nl
with open(P_REPORT, "ab") as f:
    f.write(sep + LINE.encode("utf-8") + nl)
print("report appended, nl =", repr(nl.decode()))

hb = json.load(open(P_HB, encoding="utf-8"))
ack = hb["orders_ack"]
print("heartbeat OK; orders_ack n =", len(ack), "| dup entries:", len(ack) - len(set(ack)))
assert isinstance(hb["heartbeat_epoch_utc"], int), "epoch must be int (R170/R178)"
assert "T" in hb["clock_read"] and "+" in hb["clock_read"], "clock_read must be T-format ISO (R262)"
st = json.load(open(P_STATE, encoding="utf-8"))
assert isinstance(st["heartbeat_epoch_utc"], int)
assert st["round_no"] == 333
print("state OK; round_no =", st["round_no"], "| epoch =", st["heartbeat_epoch_utc"], "| clock =", st["clock_read"])
print("ALL CLOSEOUT CHECKS PASS")
