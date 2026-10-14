"""r997 bm-a closeout: round report line + state + heartbeat updates."""
import json, time, datetime, io

NOW = datetime.datetime.now().astimezone()
ISO = NOW.isoformat(timespec="seconds")
EPOCH = int(time.time())
ROUND = 997

# ---------- 1) round report line ----------
REPORT = (
    "%s | r997 bm-a | WM-VERDICT: green (red=false lane=healthy; satengine ALIVE rc0 idle queue0; "
    "W242 waits-upstream: W241 shards 12/12 landed 19:19-19:30 but finalize face (perpetual_faces/n1_w241_results.json) "
    "absent = bm-c chain leg pending; moneyflow first-pull in-flight 2152/5222 done-count growing, IC prereg fires on panel-complete) | "
    "本轮: S0 sync behind=0/ahead=0 clean + D19 orders delta consumed (sha 97682335 advanced; 3 new rows ALL group/BigStream domain "
    "O-1745 主AGENT群审/O-1855 全面开工夜令[回测各道按既令并行=本司议程不变零新专项]/O-19:2x Phase1-α部署 — zero BigMoney directives, "
    "dec unchanged c61d7884; fleet/orders 差集零未回执) + smoke 49/49 + S6 chain 32 legs bad=0 (27 data + 5 CEO legs; paper legs "
    "no-op = 10-14 bar 未发布于 klc_kl.js 面) + **sina 日线双面发布差判谳**: 双探针实锤 CN_MarketDataService jsonp 已有 10-14 bar "
    "(510300 close 4.294) 而 akshare fund_etf_hist_sina(klc_kl.js face) 尾停 10-13 + git 史锚 klc 面惯例 21:00-23:00 发布 "
    "(10-13 bar=22:56 落/10-12≈00:27/09-30=21:22) → 正常源滞后非缺陷·后续轮自愈·禁换端点硬拉(双面基准未对证会造 seam) + "
    "pit-data mini-split (最旧 r496/r503 2800B verbatim→research/pit-data-refresh.md 3463B; 主件 30273→28668B 回线≤30KB; "
    "字节守恒 ok; receipt results/_r997bma_pit_data_minisplit.json; prescan rc3 登记簿命中=D-20261002-06 授权迁移面 r700 范式) + "
    "新坑律入律 1 条 (sina 日线双面发布差·r997) | 验证: chain log _r997bma_s6_chain.log bad=0 + attrition guard CLEAN + "
    "S7 quartet green (loop pin=8 no-op/watchdog 19:49/双爪 installed) + idle --worked (rounds=0) + orphan 0/26 | "
    "下轮: r998 = W242 materialize (prereg derive+five-face freeze+engine self-burn) fires on W241 finalize landing "
    "(bm-c chain·shards 齐等 finalize); moneyflow IC prereg on panel-complete (first-pull in-flight ~3.6h); "
    "10-14 bar 落地后续轮 S6 自愈带 paper/marks 链 | 本地未达 origin commit 数=0 (push 后 rev-parse 自证)"
)
with io.open(r"round_reports-bm-a.md", "a", encoding="utf-8") as f:
    f.write("\n" + REPORT + "\n")

# ---------- 2) state-bm-a.json ----------
SP = r"state-bm-a.json"
st = json.load(io.open(SP, encoding="utf-8"))
now_active = (
    "r997: S0 clean + D19 ORD delta 3 rows consumed (all group/BigStream domain, zero BigMoney directives) + "
    "smoke 49/49 + S6 chain 32 legs bad=0 (10-14 bar klc-face 正常滞后自愈判谳·双探针+git 史锚) + "
    "pit-data mini-split + 新坑律 1 条; W242 materialize = next product on W241-finalize landing (shards 12/12 齐等 bm-c finalize)"
)
did = (
    "r997: S0-1 anchor + orphan 0/26 + fetch behind=0 + D19 probe/update (ord 97682335 advanced, dec unchanged) + "
    "orders-delta 3 rows consumed (O-1745/O-1855/O-19:2x all group domain) + fleet/orders diff empty + smoke 49/49 + "
    "S6 chain 32 legs bad=0 + dual-endpoint probes (CN_MarketDataService vs klc_kl.js) + git-history bar-landing anchors + "
    "pit-data mini-split (2800B→pit-data-refresh.md) + r997 pit entry + S7 quartet + attrition CLEAN + idle --worked"
)
nxt = (
    "r998: W242 materialize (prereg derive + five-face freeze + engine self-burn 12/12) fires on W241 finalize landing "
    "(bm-c chain; shards 12/12 landed 19:19-19:30); moneyflow IC prereg on panel-complete (first-pull 2152/5222 in-flight); "
    "10-14 bar lands late-evening klc face -> next S6 absorbs + paper/marks legs fire; HANDOVER 5x rolls to r1000; "
    "month exam 10-31; C-20261014-01 revisit 10-16"
)
verdict = (
    "green (wm-red=false; satengine ALIVE rc0 idle queue0; W242 waits-upstream W241-finalize bm-c lane (shards 12/19-30 齐等 finalize); "
    "moneyflow first-pull in-flight panel grows; dualrun streak 31; orphan 0/26; S6 32 legs bad=0)"
)
verify = (
    "green (smoke 49/49 + S6 chain bad=0 + attrition CLEAN + quartet green + idle rounds=0 + pit-data size conservation ok) "
    "+ push behind=0 self-verified"
)
artifact = (
    "results/_r997bma_s6_chain.log (32 legs 19:44-19:47 bad=0) + results/_r997bma_daily_source_probe.json + "
    "research/pit-data-refresh.md (mini-split sub-file) + results/_r997bma_pit_data_minisplit.json"
)

st["round"] = ROUND
st["last_round"] = ROUND
st["loop_round"] = ROUND
st["round_no"] = ROUND + 1
st["round_no_label"] = "r997"
st["now_active"] = now_active
st["current"] = now_active
st["current_task"] = now_active
st["task"] = "r997 S6 chain + pit-data minisplit + waits-upstream watch"
st["did"] = did
st["next"] = nxt
st["next_milestone"] = "W241 finalize landing (bm-c, shards 12/12 done) -> W242 materialize <=48h; month exam 10-31; C-20261014-01 revisit 10-16"
st["verdict"] = verdict
st["verify"] = verify
st["last_action"] = "r997 S6 chain + D19 ack + pit-data minisplit"
st["last_artifact"] = artifact
st["latest_artifact"] = artifact
st["recent_artifact"] = artifact
st["last_round_at"] = ISO
st["last_round_closed"] = ISO
st["last_round_ts"] = ISO
st["last_run"] = ISO
st["last_seen"] = ISO
st["ts"] = ISO
st["updated"] = ISO
st["updated_at"] = ISO
st["orphan_face"] = 0
st["orphan_faces"] = 0
st["idle_rounds"] = 0
st["agenda_starved"] = False
st["heartbeat_epoch_utc"] = EPOCH
st["heartbeat_epoch_utc_type_int"] = True
st["last_heartbeat_epoch_utc"] = EPOCH
st["clock_read"] = ISO
st["last_orders_read_at"] = ISO
st["last_decisions_read_at"] = ISO
# d19-written watermark keys stay as written by d19_watermark.py update (ord=97682335...)

with io.open(SP, "w", encoding="utf-8") as f:
    json.dump(st, f, ensure_ascii=False, indent=1)

# read-back asserts
back = json.load(io.open(SP, encoding="utf-8"))
assert isinstance(back["heartbeat_epoch_utc"], int), "epoch must be JSON int"
assert back["round_no"] == ROUND + 1
assert back["clock_read"].count("T") >= 1, "clock_read must be ISO8601 with T"

# ---------- 3) heartbeat fleet/machines/bm-a.json ----------
HB = r"fleet/machines/bm-a.json"
hb = json.load(io.open(HB, encoding="utf-8"))
hb["machine_id"] = "bm-a"
hb["now_active"] = now_active
hb["current"] = now_active
hb["current_task"] = now_active
hb["task"] = "r997 S6 chain + pit-data minisplit + waits-upstream watch"
hb["did"] = did
hb["next"] = nxt
hb["verdict"] = verdict
hb["last_action"] = "r997 S6 chain + D19 ack + pit-data minisplit"
hb["last_artifact"] = artifact
hb["latest_artifact"] = artifact
hb["recent_artifact"] = artifact
hb["last_round"] = ROUND
hb["loop_round"] = ROUND
hb["round"] = ROUND
hb["round_no"] = ROUND + 1
hb["last_seen"] = ISO
hb["last_round_at"] = ISO
hb["last_round_closed"] = ISO
hb["last_run"] = ISO
hb["ts"] = ISO
hb["updated"] = ISO
hb["updated_at"] = ISO
hb["clock_read"] = ISO
hb["idle_rounds"] = 0
hb["agenda_starved"] = False
hb["heartbeat_epoch_utc"] = EPOCH
hb["heartbeat_epoch_utc_type_int"] = True
hb["last_heartbeat_epoch_utc"] = EPOCH
hb["orphan_face"] = 0
hb["orphan_faces"] = 0
hb["health"] = "green"
with io.open(HB, "w", encoding="utf-8") as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)
back_hb = json.load(io.open(HB, encoding="utf-8"))
assert isinstance(back_hb["heartbeat_epoch_utc"], int), "hb epoch must be int"
assert isinstance(back_hb["round_no"], int)

print("CLOSEOUT WRITTEN: state round_no=%d epoch=%d clock=%s" % (back["round_no"], back["heartbeat_epoch_utc"], back["clock_read"]))
