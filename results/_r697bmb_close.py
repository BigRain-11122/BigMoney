# r697 bm-b S7 close: round report append (bytes-mode, idempotency gate) +
# state.json round_no absolute write + heartbeat refresh.
# -*- coding: utf-8 -*-
import json
import time
from datetime import datetime, timezone, timedelta

ROOT = r"C:\Fluxgroup\FluxGroup\quant\bigmoney"
REPORT = ROOT + r"\logs\iteration-loop\round_reports.md"
STATE = ROOT + r"\state.json"
HB = ROOT + r"\fleet\machines\bm-b.json"

tz = timezone(timedelta(hours=8))
now = datetime.now(tz)
clock = now.strftime("%Y-%m-%dT%H:%M:%S+08:00")
epoch = int(time.time())

row_parts = [
    " | round 697 (bm-b) | watermark 绿（red=false；py_watermark verdict=py_low_with_work_cands=合法 RAM 门窗：free RAM 2.2GB<4GB floor·trio NULLS 在烧占位至 10-06T17·3 个 ready-unclaimed N2 分片+CONTEST-RC 依法候窗非违令·r691 帽律按在飞批 ETA）",
    "｜当前活=trio NULLS 三族烧录在飞（V ~10-06T17/Q ~10-07T11/D ~10-08T0x 收口）+N2-W15 screen 12 分片池化并行（bm-c SHARD-0 在烧·本机 SHARD-2 已认领候 RAM 窗 daemon 自燃）",
    "｜最近实物=docs/live_usage/LIVE-2026-10-04.md+docs/daily_report/REPORT-2026-10-04.md+results/daily_scorecard.html（22:0x 再生·国庆假日数据 cutoff 2026-09-30·market_clock CALL=ORANGE_COOL sleeves=4 activated=0）",
    "｜下个里程碑=10-05 晨轮承接 W3 judge 产物验收（bm-c 重 spawn pid 26052·ETA ~10-05T02:00·其单席）；trio 收口后 RAM 窗内 CONTEST-RC anchor+mirror 双相+余 N2 分片自燃（窗 10-06 晚~10-07）→10-08 治理日 219-measured CEO 面闭环（窗≤48h）",
    "｜S0=churn absorb f31b0f48b+merge origin 11 commits 净路 45bd7135c 零 UU 零 marker",
    "｜S0.5=orders 154/154 双侧同口径零未回执+D-19 双 MATCH（decisions sha256/orders sha1 双键口径复核）",
    "｜S1=smoke 48/48",
    "｜S6=38/38 rc0（假日全 collector no-op@cutoff 09-30·b_layer mask 再生·t35 export 幂等再生·scorecard 6/28/7 卡·token_meter 快照）",
    "｜post_review REPORT-20261004 面=✓45/✗0/🟡5 零活红",
    "｜inbox=bm-c→ALL（W3 judge 75% 处静默死亡穷查+重 spawn 实录）已读已移 processed·本机遵守其夜间重批 spawn 纪律（本机 RAM 同紧张窗零重批）",
    "｜trio watch 三证 OK；attrition 4 台账 CLEAN；pool_dualrun ZERO-DRIFT streak=6；本产品面=假日维护轮（面板/报告再生·1 分诚实记账·RAM 门下无新算力批合法）",
    "｜本地未达 origin commit 数=0（push_verify DELIVERED 实证）",
]
line = clock + "".join(row_parts)

with open(REPORT, "rb") as f:
    blob = f.read()
marker = b"round 697 (bm-b)"
cnt = blob.count(marker)
assert cnt == 0, "round 697 marker already present count=%d" % cnt
if not blob.endswith(b"\n"):
    blob += b"\n"
enc_line = line.encode("utf-8")
with open(REPORT, "wb") as f:
    f.write(blob)
    f.write(enc_line)
    f.write(b"\n")

st = json.load(open(STATE, encoding="utf-8"))
assert st.get("round_no") == 696, "unexpected state round_no=%r" % st.get("round_no")
st["round_no"] = 697
st["round_no_label"] = "round 697 (bm-b)"
st["note"] = ("r697: holiday maintenance round under RAM gate -- S0 churn absorb+merge origin 11 clean; "
              "orders 154/154 acked; D-19 dual MATCH; smoke 48/48; S6 38/38 rc0 (collectors no-op@09-30 "
              "holiday cutoff, LIVE/REPORT/scorecard regenerated); post_review 0 active red; "
              "trio NULLS burning (V/Q/D closes 10-06..10-08), N2-W15 SHARD-2 claimed awaiting RAM window")
st["last_round_at"] = clock
st["ts"] = clock
st["updated"] = clock
st["last_seen"] = clock
st["clock_read"] = clock
st["next"] = ("(a) 10-05 morning round: W3 judge landing watch (bm-c respawn pid 26052 ETA ~02:00, bm-c seat, "
              "verify chain _r487bmc_w3_judge_verify.py); (b) trio NULLS V close ~10-06T17 / Q 10-07T11 / "
              "D 10-08T0x -> RAM window -> CONTEST-RC anchor+mirror self-ignite + N2-W15 remaining shards "
              "daemon self-claim; (c) N2 screen finalize = all-12-done then first-arrival; (d) update_lhb "
              "min-interval retry re-verify next round; (e) 10-09 post-holiday data-chain check")
json.dump(st, open(STATE, "w", encoding="utf-8"), ensure_ascii=True, indent=1)

hb = json.load(open(HB, encoding="utf-8"))
hb["round_no"] = 697
hb["round_no_label"] = "round 697 (bm-b)"
hb["last_seen"] = clock
hb["heartbeat_epoch_utc"] = epoch
assert isinstance(hb["heartbeat_epoch_utc"], int), "epoch must be JSON int"
hb["clock_read"] = clock
hb["ts"] = clock
hb["updated"] = clock
hb["updated_at"] = clock
hb["current_task"] = ("r697 closed: holiday maintenance round (S6 38/38, LIVE+REPORT regenerated, orders/D-19 "
                      "clean, post_review 0 red); next = 10-05 morning W3 judge landing watch (bm-c seat) -> "
                      "trio V/Q/D closes 10-06..08 -> RAM window CONTEST-RC + N2-W15 shards self-ignite -> "
                      "219-measured CEO face by 10-08")
hb["verdict"] = ("healthy burning (trio NULLS three-family in flight RAM-held to 10-06T17; N2-W15 screen "
                 "12-shard pool parallel; CONTEST-RC B-plan staged awaiting RAM window; py_low_with_work_cands "
                 "= legal RAM-gated window per r691 cap law)")
json.dump(hb, open(HB, "w", encoding="utf-8"), ensure_ascii=True, indent=1)

json.loads(open(STATE, encoding="utf-8").read())
h2 = json.loads(open(HB, encoding="utf-8").read())
assert isinstance(h2["heartbeat_epoch_utc"], int)
with open(REPORT, "rb") as f:
    b2 = f.read()
assert b2.count(marker) == 1, "post-append marker count=%d" % b2.count(marker)
print("OK r697 close: state=697 hb_epoch=%d report_marker=1 clock=%s" % (epoch, clock))
