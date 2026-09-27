# r348 bm-b S5/S7 close trio: state.json + heartbeat + round report line.
# Byte-careful: per-file CRLF mirror + indent mirror (r339/r234 law family).
# Self-verify: epoch isinstance(int), clock_read T-separator, ack count.
import io
import json
import time
from datetime import datetime

now = datetime.now().astimezone()
iso = now.isoformat(timespec="seconds")          # 2026-09-28T00:2x:xx+08:00
epoch = int(time.time())
ACK_NEW = "O-2026-09-27-2255-bm-a.md"


def load_mirror(path):
    raw = io.open(path, "rb").read()
    crlf = raw.count(b"\r\n") * 2 > raw.count(b"\n")
    indent = 1
    for ln in raw.split(b"\n")[:5]:
        if ln.startswith(b'  "'):
            indent = 1
            break
    return raw, json.loads(raw.decode("utf-8")), crlf, indent


def save_mirror(path, obj, crlf, indent):
    s = json.dumps(obj, ensure_ascii=False, indent=indent)
    if crlf:
        s = s.replace("\n", "\r\n")
    tail = "\r\n" if crlf else "\n"
    if not s.endswith(tail):
        s += tail
    io.open(path, "wb").write(s.encode("utf-8"))


# ---------------- state.json ----------------
sp = "logs/iteration-loop/state.json"
raw, st, crlf, ind = load_mirror(sp)
st["round_no"] = 348
st["did"] = ("r348: r348-A API-dead legacy adoption per r341 precedent "
             "(runner selftest 19/19 + generate 658 distinct + prep 6/6 -> e8d1b1e6) + "
             "S0 dual-storm fold LANDED 2621c875 (5-pick replay, 3x autofill_state UU "
             "take-HEAD whole-bytes canon, push-retry after mid-window rejection) + "
             "CEO O-2026-09-27-2255 receipt (lineA T-95 claim race yielded to bm-c "
             "23:58:06 commit-time order sec.4, storm-blocked honest yield; lineB T-94 "
             "mine in-flight) + T-94 screen batch queued TRIAL-LABOR-W1-SCREEN "
             "status=waiting + RAM flip-gate (free 1.78GB<4GB, W2-A burn ~15.5GB "
             "no-kill, autofill no-RAM-gate r348 probe, W2B r346 precedent) + "
             "W2-A burn psutil dual-proof full-core alive + S6 30/30 rc=0 + "
             "smoke 25/25 + orders 99/99")
st["verdict"] = "green"
st["next"] = ("r349: W2-A finalize harvest (w2a_results.json -> pool done-flip + "
              "T-86 bm-a ticket receipt + W2B probe ONCE gate=finalize+RAM>=12GB) + "
              "TRIAL-LABOR-W1-SCREEN flip waiting->ready when free RAM>=4GB "
              "(expected post-W2-A-finalize) -> ~2min light burn -> screen-finalize "
              "null p95 line -> judge face queue; Mon 09-28: 09:15 T-91 s3 auto-fire "
              "(SIG/BARS-09-28 replay) + 15:30 T-87 astock first increment + new-bar "
              "full chain (update_daily -> live.paper REGIME_GUARD v3 enforce first "
              "run -> t35v -> t24x2 -> aggr -> grid -> export -> scorecard -> "
              "daily_report); T-94 48h transcript window (CEO O-2255 lineB, ~09-29 "
              "23:00); r350 5x HANDOVER; 10-01 monthly trio + REGIME_GUARD v3 date gate")
st["last_round_ts"] = iso
st["last_result"] = "ok"
st["current_task"] = ("r348 closed: T-94 s2 screen queued RAM-gated waiting + "
                      "O-2255 receipt + fold landed 2621c875")
st["updated_at"] = iso
st["last_seen"] = iso
st["ts"] = iso
save_mirror(sp, st, crlf, ind)
assert json.load(io.open(sp, encoding="utf-8"))["round_no"] == 348
print("state.json: round_no=348 | crlf:", crlf, "| indent:", ind)

# ---------------- heartbeat ----------------
hp = "fleet/machines/bm-b.json"
raw, hb, crlf, ind = load_mirror(hp)
acks = hb.get("orders_ack", [])
if ACK_NEW not in acks:
    acks.append(ACK_NEW)
hb["orders_ack"] = acks
hb["n_orders_ack"] = len(acks)
hb["heartbeat_epoch_utc"] = epoch
hb["clock_read"] = iso
hb["last_seen"] = iso
hb["round"] = 348
hb["round_no"] = 348
hb["loop_round"] = 348
hb["cores"] = 16
hb["cpu_cores"] = 16
hb["cpu_pct"] = 46.6
hb["cpu_util_pct"] = 46.6
hb["free_ram_gb"] = 1.78
hb["free_ram_mb"] = 1823
hb["idle_ram_gb"] = 1.78
hb["idle_ram_mb"] = 1823
hb["total_ram_gb"] = 23.9
hb["gpu_free_vram_gb"] = 6.73
hb["gpu_free_vram_mb"] = 6889
hb["gpu_idle_vram_gb"] = 6.73
hb["gpu_idle_vram_mb"] = 6889
hb["current_task"] = ("r348 closed: T-94 s2 screen queued (RAM-gated waiting) + "
                      "O-20260927-2255 receipt (lineA yield bm-c / lineB T-94 in-flight) "
                      "+ S0 fold landed; W2-A census burn no-kill carry; next=W2-A "
                      "finalize harvest + screen flip @RAM>=4GB")
hb["verdict"] = ("green: fold landed 2621c875; W2-A burn full-core alive psutil "
                 "dual-proof; screen batch RAM-gated waiting honest; S6 30/30 rc=0; "
                 "smoke 25/25; orders 99/99")
save_mirror(hp, hb, crlf, ind)
back = json.load(io.open(hp, encoding="utf-8"))
assert isinstance(back["heartbeat_epoch_utc"], int), "epoch must be JSON int"
assert "T" in back["clock_read"] and "+" in back["clock_read"], "clock_read T-sep"
assert back["n_orders_ack"] == 99, f"ack count {back['n_orders_ack']} != 99"
print("heartbeat: epoch int", back["heartbeat_epoch_utc"], "| clock", back["clock_read"],
      "| acks", back["n_orders_ack"], "| crlf:", crlf)

# ---------------- round report ----------------
rp = "logs/iteration-loop/round_reports.md"
raw = io.open(rp, "rb").read()
crlf = raw.count(b"\r\n") * 2 > raw.count(b"\n")
line = (
    f"{iso} | round 348 bm-b (second session, r341 adoption precedent) | "
    "dept:策略+研究(T-94 线B)+工程+舰队 | WM=绿 red=false@23:30:20 lane healthy "
    "(probe 00:00:34 py 28.8% local_batch_running=W2-A burn) | did: "
    "(1) **r348-A API-死遗产收养**: 23:20 班次 predecessor 死于 gemini API 连错x15 "
    "(23:42-23:44 .err 实证) 无 S7 收尾 -- r341 判例收养不重建: runner "
    "trial_labor_w1.py selftest 19/19 复验 PASS + generate raw1000->658 distinct "
    "(T-84s3 sha256 dedup) + screen-prep 6/6 gates PASS (census==P-5C FROZEN grid "
    "leg-L 1253 p5c 整体 import / G-ANCHOR 六员 live.paper replay faithful / "
    "G-EXCLUDE armed) -> e8d1b1e6 定向收养 commit; "
    "(2) **S0 折叠双风暴全落定**: 5-pick 重放 (3 tick tails+housekeeping+收养) 撞 "
    "3x 同族 autofill_state UU -- 正典 take-HEAD 整字节 (resolver _r348bmb_resolve.py: "
    "launches 47=47 identical_sets=True 零丢失 + last_tick 23:50:02 bm-c 取新正确 "
    "r140 律 + r185 parse-verify) + push#1 被拒(窗内上游再进)->pull --rebase 二跑净 "
    "5/5->**push 落定 2621c875**; 二波 f5060470 (bm-c T-95 认领) fast-forward 净收; "
    "(3) **S0.5 令账**: 99/98 差集捕获新令 O-2026-09-27-2255-bm-a (CEO 加速筛选令 "
    "线A 决策链 v2 简化链+线B 千人试用期 48h) -> 回执+执行: 线A T-95 认领竞速 "
    "**bm-c 23:58:06 先落 f5060470 -- 本机困于 rebase 风暴窗 sec.4 commit 时间序"
    "后到让路零触碰** (r239 原子窗被风暴物理阻塞如实注记); 线B T-94=本机票在飞; "
    "decisions.md 三路缺位诚实 no-op (r104/r107); "
    "(4) S1 smoke 25/25; (5) S2 双板: 95 票 1 open=T-95 (bm-c 同窗领)+job_list 空; "
    "(6) **S3 T-94 线B 交付: screen 批入池 TRIAL-LABOR-W1-SCREEN status=waiting+RAM "
    "翻面门** (858 cells=658 候选+K=200 dual nulls, 实测 1.2s/cell 12 workers ~2min "
    "BelowNormal 轻批; 不点火因=free RAM 1.78-2.0GB<4GB 双司纪律禁新重活+"
    "autofill.py 无 RAM 门 (r348 探针实证)+W2-A burn 持 ~15.5GB no-kill -- waiting "
    "非 ready=W2B r346 判例防 tick 10min 抓跑; 翻面=RAM>=4GB 预期 W2-A finalize 后"
    "解锁; 池面纯增 34 行零 churn); "
    "(7) W2-A burn 活体 psutil 同源双证: parent 13148 (15:12:51 orchestrator)+"
    "4 workers (15:40:2x) cpu_delta 3.9-5.0s/5s 满核+RSS 合计 ~15.5GB, wall 8.5h+, "
    "w2a_results.json 未落=finalize 未到窗, no-kill 维持 (r346 坑律族); "
    "(8) S6 30/30 rc=0 周一夜族+3 new-bar 门控合法跳 (live.paper/t35v/"
    "t24_prospect_paper; 下一 bar=今日 09-28 15:30): audit CLEAN/probe py 28.8%/"
    "update_daily 0 新行/regime ORANGE shadow/scorecard 6+28+7/clock CALL-09-24 "
    "ORANGE_COOL sleeves=4/车道护栏 8+1 诚实 no-op/fundamental 新鲜跳过/b_layer "
    "all_pass/t24_promotion 0/22 如实/aggr-alloc-grid 纸盘幂等/system_v1 bm-a 道"
    "诚实 no-op/t35_export 再生/daily_report 新日期面 REPORT-2026-09-28 faces=4/"
    "build_status/token L2 今 0; post_review 尾 3 行全 YES 零 x 行=无 P0; "
    "(9) S7: schtasks 双任务在册 (Loop Running=本会话/Watchdog 就绪 00:30)+"
    "pre-commit 钳 CR 归一恒等+state round_no 348 (r347 收尾未进计数器 bookkeeping "
    "异常如实注记零科学面影响)+心跳三面自证 (epoch JSON int/clock_read T 分隔/"
    "ack 99/99)+inbox MSG-2240=本机发 bm-a 外发件留其消费+5x HANDOVER 非本轮 "
    "(r350 到期) | 验证证据=smoke 25/25+selftest 19/19+S6 30x rc=0 (_r348bmb_s6.log)"
    "+resolver 断言 identical_sets=True/取新+池面 34 行纯增+push 2621c875 落定+"
    "W2-A psutil 双证 | 下轮: r349 W2-A finalize 收割窗 (w2a_results.json 落地即 "
    "done-flip 池面+T-86 bm-a 票面回执+W2B probe ONCE gate=finalize+RAM>=12GB)+"
    "TRIAL-LABOR-W1-SCREEN 翻面 waiting->ready @RAM>=4GB (W2-A finalize 后预期解锁)"
    "->autofill 燃 ~2min 轻批->screen-finalize null p95 线->judge 面; 今日周一 "
    "09-28: 09:15 T-91 s3 auto-fire (SIG/BARS-09-28 重放)+15:30 T-87 astock 首增量+"
    "new-bar 全链 (update_daily->live.paper REGIME_GUARD v3 enforce 首跑->t35v->"
    "t24x2->aggr->grid->export->scorecard->daily_report); T-94 48h 成绩单窗 (CEO "
    "O-2255 线B ~09-29 23:00 截); r350 5x HANDOVER; 10-01 月首轮三件套+REGIME_GUARD "
    "v3 日期门"
)
nl = b"\r\n" if crlf else b"\n"
if not raw.endswith((b"\n", b"\r\n")):
    raw += nl
io.open(rp, "wb").write(raw + line.encode("utf-8") + nl)
print("round report appended | crlf:", crlf, "| line bytes:", len(line.encode('utf-8')))
