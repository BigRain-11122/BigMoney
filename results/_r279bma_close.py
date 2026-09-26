# R279 bm-a S7 close writes: state-bm-a.json + round_reports-bm-a.md + heartbeat (5-face probe each, R271 one-now() law)
import json
import datetime
import time
import sys

now = datetime.datetime.now()
ts_iso = now.isoformat(timespec="seconds")
ts_flat = now.strftime("%Y-%m-%d %H:%M:%S")

def probe_write(path, mutate):
    raw = open(path, "rb").read()
    face = {"bom": raw.startswith(b"\xef\xbb\xbf"), "crlf": b"\r\n" in raw, "ends_nl": raw.endswith(b"\n")}
    d = json.loads(raw.decode("utf-8-sig"))
    mutate(d)
    body = json.dumps(d, ensure_ascii=False, indent=1)
    if face["crlf"]:
        body = body.replace("\n", "\r\n")
    if face["ends_nl"]:
        body += "\n"
    open(path, "wb").write((("\ufeff" + body) if face["bom"] else body).encode("utf-8"))
    return face

DID = ("R279 dead-R278 adoption + harvest close: wreckage verified (py_compile+selftest 19/19+anchor_all_ok 64 lines) "
       "adopted cf16fa35->57a6d9fe with provenance; S0 rebase 2-UU resolved per skill (_r279bma_resolve{,2}.py: pool "
       "only-face proof owner=bm-a first-claim S4 vs bm-b 00:00:04 stale-read void; autofill launches union 50 cap); "
       "FUSION-P1-NAV harvest flip done 8effe41b (r244 law, closes claim race for all watchdogs); orders 89/89 "
       "(O-2330/2335 receipts registered, execution evidence GM-session+135ac808+9c89c19e in册); decisions tail D-11 "
       "zero new; T-86 s1 canonical deliverable LANDED research/FACTOR_CENSUS_REGISTRY.md (bm-b r279 probe had found "
       "absent, R278 died pre-write; 28 engine+zoo r218+GTJA191/WQ101/A158+sina-MF+LHB/heat+bench rs, zero-invention)")
VERDICT = ("green: watermark red=false healthy; smoke 25/25; S6 21 legs rc=0 (audit CLEAN pool-supply-gap "
           "ready=1 REV-OSC waiting autofill next tick; clock ORANGE_COOL sleeves=4 activated=0 idempotent; "
           "moneyflow+AH self-heal spawns; REPORT-2026-09-27 written; token L2=0); board 0 open; post_review "
           "latest run 31 YES/0 NO/5 WAIT zero active NO")
NEXT = ("r280: autofill burn REV-OSC-STOCK-P1 (judged cells x2+2000 nulls, CEO O-2330 first-priority) then harvest; "
        "T-85 s2/s3 fusion-grid prereg freeze BEFORE judged runs (R99); T-86 s2 census runner+pool entry consumes "
        "FACTOR_CENSUS_REGISTRY rows; T-88 s3 repo collectors; MF_IC_P1 parked source-blocked; 09-28 Monday first-bar "
        "chain; 10-01 month-first trio + REGIME_GUARD v3 date gate; R280 5x HANDOVER")

def m_state(d):
    d["round_no"] = 279
    d["did"] = DID
    d["verdict"] = VERDICT
    d["next"] = NEXT
    for k in ("ts", "last_round_ts", "updated_at", "last_run", "last_round_at", "updated"):
        d[k] = ts_flat if k != "last_round_ts" else ts_flat
    d["current_task"] = "R279 done: dead-R278 adopted+harvest-closed; T-86 s1 registry landed; orders 89/89"
    d["last_round"] = 279
    d["last_seen"] = ts_iso

f1 = probe_write("state-bm-a.json", m_state)

# round report append (append-ledger-md: my machine's file, one line)
line = (f"{ts_flat} | R279 | bm-a dept:研究·工程·舰队（无人值守轮·死轮收养+收尾）| 水位=绿（red=false healthy·"
        f"audit CLEAN pool-supply-gap ready=1=REV-OSC 待 autofill 下 tick·py 4.4-5.3% 周末合法面）| did: "
        f"S0 收养死轮 R278 残骸（25min 预算 23:53:01 被杀·S7 前死于 overlay 锚修正+批产物落盘后）=py_compile+"
        f"selftest 19/19+anchor_all_ok 64 行三验后 cf16fa35 带出处收养；S0 pull --rebase 双 UU 撞车按 skill 正典解"
        f"（runnable_pool only-face 证明 owner=bm-a 23:50:03 首认+实际执行者·bm-b 00:00:04 陈旧读认领 void per S4·"
        f"autofill launches union cap50·last_tick 内部 ts 比较保 00:00:01 最新）+FUSION-P1-NAV harvest flip 入链"
        f"8effe41b（r244 律·对全机 watchdog 关闭重复点火窗）；S0.5 双扫 orders 89/89（O-2330/2335 回执补登记=R278 "
        f"未竟腿·执行证据已在册 135ac808+9c89c19e）+decisions 尾 D-11 零新行零本仓例；S1 smoke 25/25；S2 板 0 open"
        f"（34 claimed）；S3 主交付=**T-86 s1 正典件 research/FACTOR_CENSUS_REGISTRY.md**（单源因子普查登记簿·"
        f"A28 引擎+zoo r218 族+GTJA191/WQ101/A158+sina-MF 四档+LHB/人气+bench rs2·零发明行行锚源码·s2 消费契约"
        f"=登记行外禁入·R278 死轮缺口=bm-b r279 探针实证缺位后补齐）+票面 progress_r279bma 字段级写回；S6 21 腿"
        f" rc=0（audit CLEAN·clock ORANGE_COOL sleeves=4 activated=0 幂等·lhb 30min 节流·heat 周末·futures+options"
        f" cutoff 覆盖零网络·moneyflow rank-pass spawn+AH refresh spawn=EM 源阻断自愈环活·fundprem bm-c 车道护栏·"
        f"fundamental 2.5h 新鲜·blf 全门·dsc 6 员·dailyrep REPORT-202609-27 faces=4 token=1·token L2=0）+周日无新"
        f"bar→paper/t35v/t24/promotion/aggr/grid/alloc/export 条件腿合法跳过；S7 schtasks 四任务健康（R49 法）"
        f"| evidence: 57a6d9fe+8effe41b+69ed3fc3 三 commit 链+selftest 19/19+navs_summary anchor_all_ok+orders_diff"
        f" empty 89/89+smoke 25/25+S6 21x rc0+_r279bma_resolve 双腿解后 json.loads 过闸 | next: r280 autofill 烧 "
        f"REV-OSC judged 批+收割；T-85 s2/s3 fusion-grid prereg 冻结先行（R99）；T-86 s2 census runner 消费登记簿；"
        f"09-28 新 bar 链；10-01 月首轮三件套+REGIME_GUARD v3 日期门；R280 5x HANDOVER [via bm-a]\n")
with open("logs/iteration-loop/round_reports-bm-a.md", "a", encoding="utf-8") as f:
    f.write(line)

def m_hb(d):
    d["last_seen"] = now.strftime("%Y-%m-%d %H:%M")
    d["heartbeat_epoch_utc"] = int(time.time())
    d["clock_read"] = now.astimezone().isoformat()
    d["verdict"] = "green"
    d["current_task"] = "R279 done: dead-R278 adopted+harvest-closed; T-86 s1 registry landed; orders 89/89; REV-OSC pooled ready for autofill"
    d["round_no"] = 279
    d["cpu_cores"] = 32

f3 = probe_write("fleet/machines/bm-a.json", m_hb)

d3 = json.loads(open("fleet/machines/bm-a.json", "rb").read().decode("utf-8-sig"))
assert isinstance(d3["heartbeat_epoch_utc"], int)
assert "T" in d3["clock_read"] and "+" in d3["clock_read"]
assert len(open("logs/iteration-loop/round_reports-bm-a.md", "rb").read().decode("utf-8-sig")) > 0
d4 = json.loads(open("state-bm-a.json", "rb").read().decode("utf-8-sig"))
assert d4["round_no"] == 279
print(f"close writes ok: state round_no=279, report line appended, hb epoch_int={d3['heartbeat_epoch_utc']} clock={d3['clock_read']}")
sys.exit(0)
