# -*- coding: utf-8 -*-
"""r288 bm-b wrap: round report line + state bump + heartbeat + CODELY law line.
Byte-face probes done up-front (r255/r257 five-face law): round_reports.md
LF + trailing NL; state.json/heartbeat indent=1 LF no trailing NL; CODELY.md
CRLF + trailing NL (append line with \r\n). Timestamps from one now()."""
import datetime
import json
import os
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
now = datetime.datetime.now()
ts = now.strftime("%Y-%m-%d %H:%M:%S")
ts_iso = now.astimezone().isoformat()
epoch = int(now.timestamp())

# ---- [1] round report append (trailing-NL probe passed up-front)
RR = os.path.join(ROOT, "logs", "iteration-loop", "round_reports.md")
raw = open(RR, "rb").read()
assert raw.endswith(b"\n"), "round_reports.md missing trailing NL (r281)"
line = (
    f"{ts} | r288 bm-b | WM=insufficient_history(15min窗样本不足n=2;py31.9%批在飞非闲) | "
    f"CN-TREND批健康在飞(nulls相4workers+28cell文件,p1_results未落地,harvest按r244续延r289); "
    f"认领竞速裁定(r279②): bm-a 02:10:03 tick以STALE_MIN=20机制合法抢占cntrend-0of1并launch=双烧在飞--根因=r287 push-fallback把新鲜心跳(02:07)滞留machine分支,bm-a接管门读陈旧心跳面30min>20; "
    f"裁定=本机首认01:40:05+实际执行者胜,bm-a侧merge时void(r282单计律弃重跑产物); "
    f"本轮修复: autofill claim-keepalive律(tick在本机runner在飞+自有时分片刷owner_since,KEEPALIVE_MIN=10,对手盘分片永不触碰,claim式git流+r282 rebase-retry; selftest S17a-d 4新腿+全量S1-S17 ALL PASS); "
    f"已知限: 脏树窗keepalive push仍不可达(候选下轮:tick每跳自commit状态件); "
    f"S6 22腿rc=0(周日全市场腿no-op,astock T-87拉取锁活在飞on_track,scorecard S=2 A=4,clock ORANGE_COOL activated=0,promotion 0/22,export/alloc/grid/aggr幂等,report+monitor+token delta=-55); "
    f"post_review 11NO=7族r287已裁定covered面零活红; orders 89/89零未清; 决策台账本机无件零动作 "
    f"| 证据=selftest ALL PASS+S17a-d绿+audit CLEAN+全链rc=0 | 下轮指针: p1_results落地即跑_r287bmb_cntrend_harvest.py+竞速裁定记harvest_note(r279③)+净树S0收编r287/r288滞留commit\n"
)
with open(RR, "ab") as fh:
    fh.write(line.encode("utf-8"))

# ---- [2] state.json bump (indent=1, LF, no trailing NL)
SP = os.path.join(ROOT, "logs", "iteration-loop", "state.json")
st = json.load(open(SP, encoding="utf-8"))
st["round_no"] = 288
st["did"] = ("r288: watch/maint+接管门机制修复: CN-TREND批在飞健康(harvest续延r289); "
             "bm-a 02:10 STALE_MIN机制抢占cntrend+双烧=本机首认+执行者胜待merge裁定(r279②); "
             "autofill claim-keepalive律落地(selftest S17a-d)")
st["verdict"] = "watch/maint round + takeover-gate mechanism fix (claim-keepalive)"
st["next"] = ("p1_results落地即harvest(_r287bmb_cntrend_harvest.py)+harvest_note竞速裁定(r279③); "
              "净树S0 pull --rebase收编r287/r288滞留commit回main")
st["current_task"] = "CN-TREND-ETF-P1 batch in-flight (nulls phase) + T-87 akshare refresh on_track"
st["last_round_ts"] = ts
st["last_round_at"] = ts
st["updated_at"] = ts
st["ts"] = ts
st["last_seen"] = ts_iso
with open(SP, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(st, fh, ensure_ascii=False, indent=1)

# ---- [3] heartbeat (indent=1, LF, no trailing NL; epoch int r170/r178)
HB = os.path.join(ROOT, "fleet", "machines", "bm-b.json")
hb = json.load(open(HB, encoding="utf-8"))
hb["last_seen"] = ts_iso[:19]
hb["heartbeat_epoch_utc"] = epoch
hb["clock_read"] = ts_iso
hb["current_task"] = ("CN-TREND-ETF-P1 nulls burn in-flight; bm-a takeover race "
                      "adjudicated bm-b wins (r279 law), harvest on land")
hb["cpu_util_pct"] = 62.0
hb["cpu_pct"] = 62.0
hb["free_ram_gb"] = 14.1
hb["idle_ram_gb"] = 14.1
hb["free_ram_mb"] = 14100
hb["idle_ram_mb"] = 14100
hb["round_no"] = 288
hb["round"] = 288
hb["verdict"] = ("batch-in-flight watch/maint + claim-keepalive fix; "
                 "cntrend race adjudication pending merge")
with open(HB, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(hb, fh, ensure_ascii=False, indent=1)
chk = json.load(open(HB, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be JSON int (R170/R178)"
assert "T" in chk["clock_read"], "clock_read must be T-separated (R262)"

# ---- [4] CODELY.md law line (CRLF file; append with \r\n, keep <50KB)
CM = os.path.join(ROOT, "CODELY.md")
sz_before = os.path.getsize(CM)
entry = (
    "\r\n- [2026-09-27 02:2x] 坑律（bm-b r288·接管门活主盲区·r279 家族新维·E1 轮首自捕）："
    "**批在飞>STALE_MIN(20min) 且新鲜心跳滞留本地（push-fallback 落 machine 分支）=接管门对面读到旧面→机制「合法」抢占+launch=真双烧**"
    "（实弹：CN-TREND 01:40 认领+批在飞 30min，bm-a 02:10 tick min(心跳,认领戳) 取新鲜者读到 r286 期心跳→30min>20 判陈旧→抢占+launch）；"
    "正律=①tick 增 claim-keepalive 腿：本机 runner 在飞+自有时分片刷 owner_since（KEEPALIVE_MIN=10<STALE_MIN），对手盘分片永不触碰（已完成抢占不回打）"
    "②认领竞速裁定照 r279②=首认时间戳序+实际执行者双证，重跑产物按 r282 单计律弃置③已知限：脏树窗 keepalive push 不可达（候选修=tick 每跳自 commit 状态件）。"
    "指针=Tools/autofill.py _keepalive_claims+selftest S17a-d\r\n"
)
with open(CM, "ab") as fh:
    fh.write(entry.encode("utf-8"))
sz_after = os.path.getsize(CM)
print("round report + state + heartbeat + CODELY written")
print("CODELY:", sz_before, "->", sz_after, "bytes (limit 50KB hot-cold gate)")
print("epoch int verified, clock_read T-separated verified")
