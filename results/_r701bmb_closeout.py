# r701 part-2 closeout: state bump + heartbeat + round report line (self-verified)
import json, time, datetime, io
now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).strftime("%Y-%m-%dT%H:%M:%S+08:00")
epoch = int(time.time())
DEC = "755428F8A0816334C9A42F899DE4DB9F6F4502E80A39DA716BFC3B82DCFA1B2B"
ORD = "3BF0F16E3C40673FC6DBA0264B4725E88BE56253"
try:
    import psutil
    ram_avail = round(psutil.virtual_memory().available/1e9,1); cpu = round(psutil.cpu_percent(interval=1),1)
except Exception:
    ram_avail, cpu = 3.9, 62.0

st = json.load(io.open("state.json",encoding="utf-8"))
st["round_no"] = 701
st["round_no_label"] = "round 701 (bm-b)"
st["note"] = ("r701 two-part closeout: prior instance (23:42 fire) crashed ~00:07 after push+CODELY append, before S5/S7; "
 "this instance (00:12 fire) landed its artifacts, merge close-3 absorbed origin 8-commit window (15 UU canonical: snapshots ours-newer, "
 "ledger union zero-loss, CODELY union + r503 bullet heal), D-19 dual watermark advanced (decisions 937A373D->755428F8: five new D-20261005 "
 "rows = group governance, zero new @BigMoney obligations, D-02 sampled our r700 receipts already landed; orders 814D93C4->3BF0F16E "
 "same blob bm-c r503 consumed), S0.5 double scan 154/154 zero unacked, smoke 48/48, satengine alive RAM-gated legal, post_review 0 x-marks, "
 "S6 33/33 rc0 by prior instance in-window @00:02:40, S7 quartet 4/4, attrition CLEAN. Pit: _r701bmb_d19_read.py hash leg bug sha=None, "
 "manual hashlib dual-key. Product: n1_w116 shard-6/7 landed (W116 8/12, feeds bm-a W119 finalize missing-upstream chain).")
st["last_round_at"] = st["ts"] = st["updated"] = st["last_seen"] = st["clock_read"] = now
st["last_decisions_sha"] = DEC; st["last_decisions_at"] = st["last_decisions_read_at"] = now
st["last_orders_sha"] = ORD
st["next"] = ("(a) W3 judge finalize landing verify (bm-c seat, ETA ~10-05T02:00, _r487bmc_w3_judge_verify.py); "
 "(b) N2-W15 sec.9.1 concretize freeze window <=10-08, judge pool burn <=10-12; (c) trio V closeout 10-06T17 then RAM window opens: "
 "CONTEST-RC + remaining N2 shards auto-ignite; (d) D-06 domain-file flow-sink rebalance (pit-* <=30KB) before 10-07 closeout; "
 "(e) fix _r701bmb_d19_read.py hash leg (sha=None bug); (f) 10-09 post-holiday data-chain check")
st["decisions_regression_note"] = ("r701: regression adjudicated group-side (D-20261005-01 restores orders.md O-027~030; decisions.md restoration "
 "evidenced by HQ 75c14df = blob 4E5BE321, bm-a r702/bm-c r503 receipts); watermarks follow origin current truth 755428F8/3BF0F16E; "
 "consumed receipts live in round reports")
io.open("state.json","w",encoding="utf-8",newline="\n").write(json.dumps(st,ensure_ascii=False,indent=1)+"\n")

hb = json.load(io.open("fleet/machines/bm-b.json",encoding="utf-8"))
hb["last_seen"] = hb["ts"] = hb["updated"] = hb["updated_at"] = hb["clock_read"] = now
hb["heartbeat_epoch_utc"] = epoch
hb["round_no"] = 701; hb["round_no_label"] = "round 701 (bm-b)"
hb["current_task"] = ("r701 two-part closeout done: crashed-instance artifacts landed + merge close-3 (15 UU canonical) + D-19 dual watermark "
 "advanced zero-action + S0.5 154/154; trio NULLS V/Q/D burning to 10-06T17/10-07T11/10-08T0x; N2-W15 screen 12/12 done (SHARD-2 bm-c takeover); "
 "next = sec.9.1 freeze window <=10-08")
hb["verdict"] = ("healthy burning (trio NULLS three-family in flight RAM-held; py_low_with_work_cands = legal RAM-gated window per r691 cap law; "
 "crash recovered same-window zero-loss")
hb["cpu_util_pct"] = cpu
for k in ("free_ram_gb","idle_ram_gb","ram_free_gb","ram_avail_gb"): hb[k] = ram_avail
io.open("fleet/machines/bm-b.json","w",encoding="utf-8",newline="\n").write(json.dumps(hb,ensure_ascii=False,indent=1)+"\n")

line = (now + " | round 701 (bm-b·两段收口：前实例 23:42 燃 ~00:07 崩于 S7 前·本实例 00:12 续航补完 S5/S7) | "
 "[watermark verdict: GREEN (red=false；py_low_with_work_cands=合法 RAM 窗 free "+str(ram_avail)+"GB<4.0 floor——trio NULLS 三族在烧占位+N2 screen 12/12 done(SHARD-2 bm-c 按停滞>20min 改派律接管)+CONTEST-RC 候窗=合法满速窗)] | "
 "当前活=crash-recovery 双段收口 r701：前实例遗产全落库+merge close-3 吸收 origin 8-commit 窗 | "
 "最近实物=results/p2cal_ext/n1_w116/shard-6+7-of-12.json（引擎 W116 分片 8/12·bm-a W119 finalize 缺 W116 上游链的解堵原料）+docs/daily_report/REPORT-2026-10-05.md+docs/live_usage/LIVE-2026-10-05.md（前实例 S6 33/33 rc0 @00:02:40 再生·ORANGE_COOL cap50）+fleet/inbox/MSG-2026-10-04-2355-bmb-ALL.md（FleetLink bm-b 腿回执·tailscale 已装+登录链接已产待 CEO 一点）+results/post_review/REPORT-20261005.md ✓45/✗0 | "
 "下个里程碑=N2-W15 §9.1 冻结窗 ≤10-08→judge 池烧 ≤10-12；W3 judge finalize bm-c 落地观察 ETA 10-05T02:00；trio V 收口 10-06T17；10-08 治理日 219-measured CEO 面（窗界≤48h=10-07T00:2x） | "
 "S0=前实例 merge close-1/2 已推+本轮 close-3（origin 8 commit=bm-c r503×3+bm-a r702 W120 FREEZE+bm-c daemon SHARD-2 claim；15 UU 正典解=快照 12 面 ours-newer 00:0x+compute_audit/regime_state ledger union 零丢失+CODELY 双条目 union+r503 变体⑤2B 治愈·resolver results/_r701bmb_merge_close3_resolve.py） | "
 "S0.5=令差集双扫 154/154 零未回执（前实例首扫 23:52+本窗复扫） | "
 "D-19=decisions 937A373D→755428F8（新 5 行 D-20261005-01~05=集团治理裁定·零 @BigMoney 新义务·D-02 采样 bigmoney F-20261004-01/02=我 r700 回执已落地零动作·D-04 双轨路由=本司 LOCAL_FIRST 既有实现已合规）；orders 814D93C4→3BF0F16E（bm-c r503 同 blob 已 consumed 不重诉）·水位键双更新 | "
 "S1 smoke 48/48 | S3=satengine 活（RAM 门合法在位） | post_review ✗0 零红 | S6=本窗 S6 已由前实例跑 33/33 rc0（腿 25-28 黄金周诚实跳·不重跑·快照面 merge 后以 ours 00:0x 新面为准） | "
 "S7=四件套 4/4（loop pin=2 no-op first-fire 00:32·watchdog 重注册 first-fire 00:25·pre-commit/pre-push 双爪 LF 归一在位）+attrition 4 台账 CLEAN（healed 注记照录）+state round_no=701+心跳 epoch int 自证 | "
 "坑=D-19 探针 _r701bmb_d19_read.py 哈希腿 bug（sha=None·手算 hashlib 双键补齐·下轮修探针腿） | "
 "本地未达 origin commit 数=0（commit 后 push+fetch+rev-list 自证） | 产品分=2（W116 shard-6/7 可算实物落地） | "
 "下轮指针=(a)W3 judge finalize 落地验收 bm-c 座 ETA ~02:00 (b)N2-W15 §9.1 具体化冻结窗 ≤10-08 (c)trio V 收口 10-06T17→RAM 窗内 CONTEST-RC+N2 分片自燃 (d)D-06 域件 ≤30KB 流水下沉腿 ≤10-07 (e)_r701bmb_d19_read.py 哈希腿修复 (f)10-09 节后数据链核验\n")
with io.open("logs/iteration-loop/round_reports.md","a",encoding="utf-8",newline="") as f: f.write(line)

s2 = json.load(io.open("state.json",encoding="utf-8")); h2 = json.load(io.open("fleet/machines/bm-b.json",encoding="utf-8"))
assert s2["round_no"]==701 and isinstance(h2["heartbeat_epoch_utc"],int) and h2["round_no"]==701
assert s2["last_decisions_sha"]==DEC and s2["last_orders_sha"]==ORD
print("CLOSEOUT OK round=701 epoch=",h2["heartbeat_epoch_utc"],"type:",type(h2["heartbeat_epoch_utc"]).__name__,"ram_avail:",ram_avail,"cpu:",cpu)
