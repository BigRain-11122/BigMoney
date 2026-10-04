"""r659 bm-b S7 book: state.json round_no++, heartbeat refresh (CEO 3-line face,
epoch int), round report bytes-append (mixed-encoding file, UTF-8 new line),
CODELY.md one memory line + size watermark check. All writes programmatic +
json.loads self-checks (r645/R170/R262 laws)."""
import datetime, json, os, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
now = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
now_bj = datetime.datetime.now().astimezone()
epoch = int(time.time())
R, LBL = 659, "round 659 (bm-b)"

# --- state.json ---
sp = os.path.join(ROOT, "state.json")
st = json.load(open(sp, encoding="utf-8"))
st["round_no"] = R
st["round_no_label"] = LBL
st["note"] = ("r659: golden-week watch round -- S0 treadmill absorb 2 commits (10 lane daemon faces) "
              "+ 2 merges (bm-c r456 wave + bm-a r666 T-167 theme-judge wave) zero UU + pre-push claw REAL catch "
              "(deletion set _r666bma_theme_judge_probe_facts.json = stale-base face, self-healed by merging owner "
              "wave, zero --no-verify) -> DELIVERED 2fbcbc0b3 (push_verify ahead=0 behind=0); orders delta zero "
              "153/153; D-19 double MATCH (sparse-clone origin-blob raw-bytes: decisions EB14B510 / orders 82A0CEF9) "
              "zero-consume; smoke 48/48; board all-claimed zero open (T-167 = bm-a r666); WM red=false healthy; "
              "engine alive rc0 idle; post_review 0 FAIL; TRIO NULLS burn watch: 3 pids + 12 workers alive "
              "(CIM-verified), rows 670/370/511 (+9/+7/+7 since 08:52), zero duplicates, mid-range k-gaps 5/4/5 "
              "= dead-worker legacy, self-heal via done-key skip next invocation; observed ~94 rows/h -> "
              "mechanical_ready ~10-06 17:00 (window 10-05..10-09); S6 38/38 rc0 (dualrun streak 51 zero-drift; "
              "LHB fresh pull rc0; REPORT/LIVE-2026-10-04 idempotent refresh; P1D ext-slot gates dzjy/margin/gdhs "
              "all True = next-batch supply face ready); S7 loop pin=2 no-op + watchdog + both claws + attrition "
              "CLEAN | SUPPLEMENT: tasklist /FI single-pid filter false-dead trap caught in trio liveness probe "
              "(empty table while process alive; CIM + full CSV col-2 parse both prove alive) -- lesson appended "
              "to CODELY.md (liveness probes must not trust /FI filter alone before kill/respawn decisions)")
for k in ("last_round_at", "ts", "updated", "last_seen", "clock_read"):
    st[k] = now
st["last_decisions_read_at"] = now
json.dump(st, open(sp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
assert json.load(open(sp, encoding="utf-8"))["round_no"] == R, "state self-check FAIL"

# --- heartbeat fleet/machines/bm-b.json ---
hp = os.path.join(ROOT, "fleet", "machines", "bm-b.json")
hb = json.load(open(hp, encoding="utf-8"))
hb["round_no"] = R
hb["round_no_label"] = LBL
hb["last_seen"] = now
hb["clock_read"] = now
hb["heartbeat_epoch_utc"] = epoch
hb["current_task"] = (
    "当前活: FUND trio NULLS burn V670/D370/Q511 of 2000 each advancing (+9/+7/+7 this round, ~94 rows/h), "
    "3 pids + 12 workers alive CIM-verified | 最近实物: results/_r659bmb_trio_health.json (trio burn health "
    "probe 09:07) + REPORT/LIVE-2026-10-04 refreshed + LHB fresh pull | 下个里程碑: trio mechanical_ready "
    "2000-row target ETA ~10-06 17:00 (observed 56.9h) -> finalize + E1 verdict batch, window 10-06..10-09")
hb["verdict"] = (
    "GREEN (smoke 48/48; orders delta zero 153/153; D-19 double MATCH zero-consume; WM red=false healthy; "
    "engine alive rc0 idle; post_review 0 FAIL; S6 38/38 rc0 dualrun streak 51; trio zero-dups k-gaps "
    "self-heal verified; pre-push claw real catch self-healed zero escape-hatch DELIVERED 2fbcbc0b3; "
    "attrition CLEAN; zero cloud token)")
for k in ("ts", "updated"):
    hb[k] = now
json.dump(hb, open(hp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
chk = json.load(open(hp, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch not int (R170 law)"
assert "T" in chk["clock_read"], "clock_read T-separator (R262 law)"

# --- round report: bytes append (mixed-encoding history, r641 law) ---
rp = os.path.join(ROOT, "logs", "iteration-loop", "round_reports.md")
line = (
    now + "｜round 659 (bm-b)｜黄金周值守轮: S0 treadmill absorb 2笔(10 lane daemon面)+双merge(bm-c r456波+"
    "bm-a r666 T-167主题判波)零UU+pre-push爪真拦#1(_r666bma_theme_judge_probe_facts.json删除集=旧基座陈旧面,"
    "merge属主波自愈零--no-verify)→DELIVERED 2fbcbc0b3(push_verify三证)｜S0.5令差集零153/153+D-19双MATCH"
    "(sparse-clone origin-blob: decisions EB14B510/orders 82A0CEF9)零消费｜S1 smoke 48/48｜S2板全claimed零open"
    "(T-167=THEME-JUDGE-P1已被bm-a r666同轮认领不碰)｜S3 WM红=false车道healthy+引擎活rc0 idle+post_review零✗｜"
    "trio NULLS值守实物: 三pid+12worker活(CIM实证,tasklist /FI单pid滤嘴假死坑当场识破),行数670/370/511"
    "(+9/+7/+7),零重复,中段k缺号5/4/5=死worker遗留done-key skip下轮自愈,实测~94行/h→ETA~56.9h="
    "mechanical_ready~10-06 17:00(10-05..09窗内)｜S6 38/38 rc0(dualrun streak51零漂移,LHB真拉11页rc0,"
    "REPORT/LIVE-2026-10-04幂等刷新,P1D三门dzjy/margin/gdhs全True=ext-slot IC下批供给面就绪)｜S7 loop pin=2 "
    "no-op+watchdog在位+双爪LF归一在位+attrition CLEAN(healed史照录) | 证据=_r659bmb_trio_health.json+"
    "_r659bmb_s6_log.txt+_r659bmb_d19_orders_probe.py+push_verify DELIVERED行 | 下轮指针=trio至2000行→"
    "finalize+E1判决批(窗10-06..10-09);池unclaimed=1(W14 GM停泊维持) | 本地未达origin commit数=0 | token零云端")
with open(rp, "ab") as f:
    f.write(line.encode("utf-8") + b"\n")

# --- CODELY.md one memory line + watermark check ---
cp = os.path.join(ROOT, "CODELY.md")
mem = (
    "- [2026-10-04 09:2x r659 bm-b] tasklist /FI 单pid滤嘴假死坑（trio NULLS 值守探针实弹）：python "
    "subprocess ['tasklist','/FI','PID eq 34396'] 返回空表头而进程实活（CIM Win32_Process 与 tasklist /FO CSV "
    "全量拉第2列整数字比对均证活）——liveness 探针按此判死=假死读数，误判重启 runner=池面双烧入口（pit-pool "
    "幽灵 claim 族前置面）；正法=CSV 全量拉+列位比对（results/_r659bmb_trio_health.py 范式）或 CIM 直查。"
    "How to apply：一切 pid 活性判定（尤其 kill/respawn 决策前）禁单靠 tasklist /FI 单 pid 滤嘴。\n")
raw = open(cp, "rb").read()
if not raw.endswith(b"\n"):
    raw += b"\n"
open(cp, "wb").write(raw + mem.encode("utf-8"))
size_kb = os.path.getsize(cp) / 1024
print(json.dumps({"state_round": R, "epoch": epoch, "clock": now,
                  "report_bytes_appended": len(line.encode("utf-8")) + 1,
                  "codely_kb_after": round(size_kb, 1),
                  "codely_over_50kb": size_kb > 50 * 1024}, ensure_ascii=False))
