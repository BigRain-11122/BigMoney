"""r453 bm-c S7b bookkeeper: fund-nulls evidence + state-bm-c + heartbeat +
round-reports line + CODELY.md order-execution record. Programmatic writes
(r645 state tail-comma law) + json.loads self-checks + epoch int + clock
T-separator law (R170/R178/R262)."""
import datetime
import json
import os
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
now = datetime.datetime.now()
ts = now.strftime("%Y-%m-%dT%H:%M:%S") + "+08:00"
ts_space = now.strftime("%Y-%m-%d %H:%M:%S") + "+08:00"
ts_loose = now.strftime("%Y-%m-%d %H:%M") + "x"
epoch = int(time.time())

# ---------- 1) fund-nulls watch evidence ----------
FAMS = ["fund_value_p1", "fund_quality_p1", "fund_divlowvol_p1"]
famdata = {}
for fam in FAMS:
    d = os.path.join(ROOT, "results", fam)
    faces = {}
    cells_total = 0
    if os.path.isdir(d):
        for fn in sorted(os.listdir(d)):
            if fn.endswith(".jsonl"):
                p = os.path.join(d, fn)
                with open(p, "rb") as f:
                    rows = sum(1 for _ in f)
                mt = datetime.datetime.fromtimestamp(
                    os.path.getmtime(p)).strftime("%m-%d %H:%M")
                faces[fn] = {"rows": rows, "mtime": mt}
                if fn.startswith("cells_"):
                    cells_total += rows
    famdata[fam] = faces
ev = {
    "probe": "r453bmc fund NULLS watch (bm-b canonical burn, read-only)",
    "probe_time": ts,
    "families": famdata,
    "expected": {"cells_per_family": 802, "sens_per_family": 500,
                 "nulls_cap": 2000},
    "delta_vs_r452": {
        "nulls_rows": {f: famdata[f]["nulls.jsonl"]["rows"] for f in FAMS},
        "delta": {"fund_value_p1": famdata[FAMS[0]]["nulls.jsonl"]["rows"] - 629,
                  "fund_quality_p1": famdata[FAMS[1]]["nulls.jsonl"]["rows"] - 477,
                  "fund_divlowvol_p1": famdata[FAMS[2]]["nulls.jsonl"]["rows"] - 339},
        "note": "rows V629/Q477/D339 vs r452 (zero delta = burn between-checkpoint window, mtime 10-04 07:34, bm-b canonical lane)",
    },
}
with open(os.path.join(ROOT, "results", "_r453bmc_fundnulls_watch.json"),
          "w", encoding="utf-8") as f:
    json.dump(ev, f, ensure_ascii=False, indent=1)

# ---------- 2) metrics (sampled by PS wrapper) ----------
with open(os.path.join(ROOT, "results", "_r453bmc_metrics.json")) as f:
    m = json.load(f)
cpu = float(m["cpu_pct"]); ram = float(m["idle_ram_gb"]); gpu = int(m["gpu_free_vram_mib"])

# ---------- 3) state-bm-c.json ----------
sp = os.path.join(ROOT, "state-bm-c.json")
with open(sp, encoding="utf-8") as f:
    st = json.load(f)
assert st["round_no"] == 452, f"unexpected round_no {st['round_no']}"
st["round_no"] = 453
st["clock_read"] = ts
st["cpu_pct"] = cpu
st["current_task"] = ("r453 done (GM double-ruling O-20261004-0808 consumed+acked; S6 37/37 rc0; "
                      "watchdog re-registered after missing 2nd consecutive round; FUND NULLS watch V629/Q477/D339 zero-delta); "
                      "next: fund-trio finalize window opens 10-05 10:30 watchers (G-SEG frozen path per O-0808), "
                      "O-2115+O-2030 acceptance 10-08, HANDOVER 5x at r455")
st["did"] = ("r453 bm-c golden-week watch round + GM double-ruling consumption: "
             "(1) S0: round-start 3 dirty faces = own lane daemon faces (treadmill normal); origin behind=1 = "
             "GM double ruling O-20261004-0808 -> r437 intersection-EMPTY FF-merge a025a7899 zero conflict. "
             "(2) S0.5 order diff = 1 un-acked (O-20261004-0808-bm-a): read full text in-round, executed = "
             "ruling-1 W14 parking MAINTAIN (bm-c N1-closed face zero-action confirmed; reform first-burn supply "
             "redirect 3-way + 10k-cap suspension for candidate-search waves noted; baseline/nulls unaffected) + "
             "ruling-2 G-SEG frozen insufficient-sample path MAINTAIN (fund-trio finalize window 10-05..09 closes "
             "per ruling, zero judgment-line touch, watch posture unchanged) + holiday compute track alignment "
             "(bm-c watch posture = all in-track; in-track items hosted bm-a/bm-b lanes; sec.3 six data gaps = "
             "GM-to-CEO face, not bm-c lane); ack triple-landed (orders_ack + round-report receipt + CODELY line). "
             "D-19 decisions watermark EB14B510 MATCH-unchanged (raw-blob python sha256); group orders.md SHA-1 "
             "68947C17 MATCH; inbox 0. (3) S1 smoke 48/48 (fund_statements selftest leg new, all green); "
             "S2 boards empty (job_list 0, fleet tickets 0 open/166). (4) S3: satengine rc0 alive (N1 queue closed "
             "W115 per O-2115 sec-2); watermark red=false next_pick=claimed other-lane; post_review zero new rows "
             "(tail 07:26:51 unchanged); pool ready x3 = FUND trio NULLS other-owner faces (r622/r629 division law, "
             "watch-only). (5) MAIN OUTPUT: S6 37/37 rc0 NON-ZERO=none, full-leg log results/_r453bmc_s6_log.txt "
             "(dualrun ZERO-DRIFT streak 51; compute_audit zero flags; py_watermark board-clear legal idle; "
             "REPORT/LIVE-2026-10-04 faces regenerated; lane-guard legs honest no-op) -- per-round driver form "
             "results/_r453bmc_s6_chain.py + parity guard PASS (r452 leg-identical, canon Tools/_r433bmc_s6.py "
             "untouched). (6) FUND trio NULLS watch: V629/Q477/D339 of 2000 (zero delta vs r452, burn "
             "between-checkpoint window), evidence results/_r453bmc_fundnulls_watch.json. (7) S7 self-heal: loop "
             "pin5 no-op healthy (first fire 08:05), watchdog MISSING -> re-registered (2nd consecutive round, "
             "first fire 08:04, D-20261002-02 logon=default face noted for watch, diagnose at 3rd recurrence), "
             "dual claws parity TRUE, attrition CLEAN (4 ledgers, 2 bm-a healed historical notes); orders "
             "double-scan zero-diff after ack; inbox 0.")
st["gpu_free_vram_mib"] = gpu
st["heartbeat_epoch_utc"] = epoch
st["idle_ram_gb"] = ram
st["last_decisions_read_at"] = ts
st["last_round"] = ("r453 bm-c: GM O-20261004-0808 double-ruling consumed+acked (W14 parked maintain / "
                    "G-SEG frozen path maintain / holiday compute in-track); S6 37/37 rc0 _r453bmc_s6_log.txt "
                    "(streak 51, driver parity PASS); smoke 48/48; orders/D19/group-orders triple MATCH; "
                    "watchdog re-registered (missing 2nd consecutive round)")
st["last_round_at"] = ts
st["last_round_ts"] = ts
st["last_seen"] = ts
st["last_ts"] = ts
st["next"] = ("(a) FUND trio finalize window 10-05..10-09 (D ETA 10-05 10:30 per bm-b r652; G-SEG frozen "
              "insufficient-sample path confirmed by O-20261004-0808, no mid-flight change; VALUE passive crash "
              "bm-b fix pending). (b) O-2115 acceptance pack final run + O-2030 treasure-protection acceptance "
              "10-08. (c) W116+ N1 supply reassess after fund-trio finalize (reform first-burn supply redirected "
              "per O-0808 ruling-1: theme-tactic family / non-banned factors with sec.1.1 self-proof; 10k cap "
              "suspended for candidate-search waves until CEO lifts D-41 sec.6-C). (d) HANDOVER 5x at r455. "
              "(e) Watchdog vanishing pattern (2 consecutive rounds missing at S7) - diagnose at 3rd recurrence. "
              "(f) Market reopen 10-09: data lanes resume verification.")
st["updated"] = ts_space
st["updated_at"] = ts
st["verify"] = ("S6 37/37 rc0 NON-ZERO=none (results/_r453bmc_s6_log.txt in-repo); smoke 48/48; orders 154/154 "
                "after ack (double-scan zero-diff); D-19 EB14B510 raw-bytes MATCH; group orders.md SHA-1 "
                "68947C17 MATCH; attrition CLEAN; dual claws parity TRUE; fund-nulls evidence "
                "results/_r453bmc_fundnulls_watch.json; heartbeat epoch int + clock T-sep self-checked")
with open(sp, "w", encoding="utf-8") as f:
    json.dump(st, f, ensure_ascii=False, indent=1, sort_keys=True)
chk = json.load(open(sp, encoding="utf-8"))
assert chk["round_no"] == 453
assert isinstance(chk["heartbeat_epoch_utc"], int) and not isinstance(chk["heartbeat_epoch_utc"], bool)
assert "T" in chk["clock_read"] and "+08:00" in chk["clock_read"]
print("STATE_OK round=453 epoch=" + str(epoch))

# ---------- 4) heartbeat fleet/machines/bm-c.json ----------
hp = os.path.join(ROOT, "fleet", "machines", "bm-c.json")
with open(hp, encoding="utf-8") as f:
    hb = json.load(f)
NEW_ORDER = "O-20261004-0808-bm-a.md"
if NEW_ORDER not in hb["orders_ack"]:
    hb["orders_ack"].append(NEW_ORDER)
hb["round_no"] = 453
hb["activity_now"] = ("FUND trio NULLS burn watch (bm-b canonical, finalize window opens 10-05 10:30, G-SEG "
                      "frozen path per O-20261004-0808); N1 W116+ closed per O-2115 sec-2; GM double-ruling "
                      "O-0808 consumed+acked; golden-week maintenance all-green")
hb["clock_read"] = ts
hb["cpu_pct"] = cpu
hb["cpu_idle_pct"] = round(100.0 - cpu, 1)
hb["cpu_util_pct"] = cpu
hb["current_task"] = st["current_task"]
hb["free_ram_gb"] = ram
hb["idle_ram_gb"] = ram
hb["ram_free_gb"] = ram
hb["gpu_free_mb"] = gpu
hb["gpu_free_vram_mb"] = gpu
hb["gpu_free_vram_mib"] = gpu
hb["gpu_idle_vram_mb"] = gpu
hb["gpu_idle_vram_mib"] = gpu
hb["gpu_vram_free_mb"] = gpu
hb["health"] = "ok"
hb["heartbeat_epoch_utc"] = epoch
hb["last_seen"] = ts
hb["last_seen_at"] = ts
hb["latest_artifact"] = ("results/_r453bmc_s6_log.txt (S6 37/37 rc0 full-leg evidence; streak 51) + "
                         "results/_r453bmc_fundnulls_watch.json @ " + ts)
hb["next_milestone"] = ("FUND trio finalize window 10-05..10-09 (D ETA 10-05 10:30; G-SEG frozen per O-0808); "
                        "O-2115/O-2030 acceptance 10-08; market reopen 10-09")
hb["prod_lanes"] = ("FUND trio NULLS bm-b in-flight (watch only); N1 closed per O-2115 sec-2 (fund-trio has "
                    "fire); O-2115 acceptance pack live; GM O-20261004-0808 double-ruling consumed (W14 parked "
                    "/ G-SEG frozen / holiday compute in-track)")
hb["updated_at"] = ts
hb["verdict"] = ("green (golden-week maintenance all-green; GM O-0808 double-ruling consumed+acked; S6 "
                 "evidence chain continuous; board/pool/orders lawful; lane divisions respected; waiting state "
                 "declared: finalize window opens 10-05)")
with open(hp, "w", encoding="utf-8") as f:
    json.dump(hb, f, ensure_ascii=False, indent=1, sort_keys=True)
chk = json.load(open(hp, encoding="utf-8"))
assert chk["round_no"] == 453
assert NEW_ORDER in chk["orders_ack"] and len(chk["orders_ack"]) == 154
assert isinstance(chk["heartbeat_epoch_utc"], int) and not isinstance(chk["heartbeat_epoch_utc"], bool)
assert "T" in chk["clock_read"] and "+08:00" in chk["clock_read"]
print("HB_OK acked=154 epoch_int=" + str(isinstance(chk["heartbeat_epoch_utc"], int)))

# ---------- 5) round report line ----------
entry = (
    "2026-10-04 08:0x+08:00｜r453｜dept:工程（golden-week 值守+GM 双裁令消费）｜"
    "watermark verdict=绿（red=false·lane healthy·probe py 0.0%=板空合法 idle 白名单〔N1 关闭 per O-2115 sec-2·"
    "池 ready x3 全他机属主·板 0 open〕）｜当前活=GM O-20261004-0808 双裁令消费+S6 全链值守｜"
    "最近实物=results/_r453bmc_s6_log.txt（S6 37/37 rc0·streak 51）+results/_r453bmc_fundnulls_watch.json｜"
    "下个里程碑=fund-trio finalize 窗 10-05 10:30 开（bm-b 正主·G-SEG 冻结路径 per O-0808）+O-2115/O-2030 "
    "验收 10-08（≤48h）｜S0: 轮首 3 脏面=本机 lane daemon 面（treadmill 正常）·fetch 后 behind=1（fleet/orders "
    "新令）→交集空=r437 FF-merge 净路 a025a7899 零冲突｜S0.5 令差集=1：O-20261004-0808-bm-a GM 双裁令全文读毕"
    "同轮消费——①W14 停泊维持（RESI/CNTD 档存留册·293 隔离维持·改革首烧供给改道三面〔轨道五件事/题材战法族/"
    "非禁族因子面〕+万帽悬置=候选搜索类波次禁用大帽·基线/nulls 不受限）→本机 N1 关闭面零动作确认；"
    "②G-SEG 维持冻结 insufficient-sample 路径（在飞判决禁中途换分段法·稠密起点=另跑新预注册面·10-06..09 "
    "裁决窗以本裁决结案）→fund-trio watch 姿态不变零判线触碰；③假期算力轨道对齐（轨道内在飞件均 bm-a/bm-b "
    "车道·§3 六项数据缺口=GM 呈 CEO 件非本机面）→ack 三面落（orders_ack+1·轮报回执·CODELY 行）·D-19 水位 "
    "EB14B510 MATCH-unchanged（raw-blob python 法）·group orders.md SHA-1 68947C17 MATCH·inbox 0｜S1 smoke "
    "48/48（fund_statements selftest 新腿全绿）｜S2 板空（job_list 0·fleet tickets 0 open/166）｜S3: satengine "
    "rc0 活（N1 W115 队列关闭态）·post_review 零新行（尾行 07:26:51 不变）·pool ready x3=FUND trio NULLS 他机"
    "属主面（r622/r629 分工律 watch-only）｜S6 37/37 rc0 NON-ZERO=none（dualrun ZERO-DRIFT streak 51·"
    "compute_audit 零旗·ORANGE shadow·REPORT/LIVE-2026-10-04 再生·车道守卫腿诚实 no-op·driver parity PASS"
    "〔r452 逐腿恒等·canon Tools/_r433bmc_s6.py 零触碰〕）｜FUND NULLS watch: V629/Q477/D339 of 2000（行数较 "
    "r452 零增·mtime 10-04 07:34 checkpoint 间窗）｜S7: loop pin5 no-op 健康（first fire 08:05）·watchdog 缺失→"
    "重注册（连续第 2 轮缺失·first fire 08:04·D-20261002-02 面观察·第 3 次复发即诊断）·双爪 parity TRUE·"
    "attrition CLEAN（4 ledgers·2 bm-a healed 历史注记）·orders 双扫（ack 后零差）·inbox 0｜"
    "本地未达 origin commit 数=0（commit 前基线·push_verify 收口自证）｜下轮指针=r454 值守（finalize 窗前夜·"
    "watchdog 复发观察·HANDOVER 5x at r455）"
).replace("2026-10-04 08:0x+08:00", ts)
rp = os.path.join(ROOT, "round_reports-bm-c.md")
with open(rp, "rb") as f:
    f.seek(-1, 2)
    last = f.read(1)
with open(rp, "a", encoding="utf-8", newline="") as f:
    if last not in (b"\n", b"\r"):
        f.write("\r\n")
    f.write("\r\n" + entry)
print("REPORT_APPENDED len=" + str(len(entry)))

# ---------- 6) CODELY.md order-execution record ----------
cline = (
    "- [2026-10-04 08:0x r453 bm-c] O-20261004-0808-bm-a GM 双裁令执行记录（全文读毕同轮消费）："
    "①W14 停泊维持=本机 N1 关闭面零动作确认（RESI/CNTD 档存留册不解冻·293 隔离维持·改革首烧供给改道三面入册"
    "〔轨道五件事/题材战法族/非禁族因子面须过 §1.1 引用例外自证〕·万帽悬置=候选搜索类波次禁用大帽〔CEO 解除 "
    "D-41 §6-C 前持续〕·基线/nulls 投资不受限 V-NULLS 线照跑）；②G-SEG 分段=维持冻结 insufficient-sample 路径"
    "（在飞基金三判决禁中途换分段法·稠密起点如需采用=新预注册面另跑禁移植·10-06..09 裁决窗以本裁决结案不再另裁）；"
    "③假期算力轨道对齐=本机 watch 姿态与轨道内全域一致（轨道内在飞件均 bm-a/bm-b 车道·§3 六项数据缺口=GM 呈 "
    "CEO 件非本机面）；ack=orders_ack+轮报回执+本行三面。"
).replace("2026-10-04 08:0x", ts_loose)
cp = os.path.join(ROOT, "CODELY.md")
with open(cp, "rb") as f:
    f.seek(-1, 2)
    last = f.read(1)
with open(cp, "a", encoding="utf-8", newline="") as f:
    if last not in (b"\n", b"\r"):
        f.write("\r\n")
    f.write("\r\n" + cline)
print("CODELY_APPENDED len=" + str(len(cline)))
print("BOOKKEEP_DONE ts=" + ts)
