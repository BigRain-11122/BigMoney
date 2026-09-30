# r473 bm-b S7 close: state bump 472->473 + heartbeat + round report line
import json, time, datetime

now = datetime.datetime.now().astimezone()
ts = now.strftime("%Y-%m-%dT%H:%M:%S+08:00")
epoch = int(time.time())
assert isinstance(epoch, int)

# ---- state.json round bump
raw = open("state.json", "rb").read()
st = json.loads(raw)
prev = st.get("round_no")
st["round_no"] = 473
st["updated_at"] = ts
crlf = b"\r\n" in raw[:600]
body = json.dumps(st, indent=1, ensure_ascii=False)
data = (body.replace("\n", "\r\n") if crlf else body).encode("utf-8")
if raw.endswith(b"\n") and not data.endswith(b"\n"):
    data += b"\r\n" if crlf else b"\n"
open("state.json", "wb").write(data)
json.loads(open("state.json", "rb").read())
print("state.json round_no", prev, "->", 473)

# ---- heartbeat fleet/machines/bm-b.json
hb_path = "fleet/machines/bm-b.json"
raw = open(hb_path, "rb").read()
hb = json.loads(raw)
hb["last_seen"] = ts
hb["heartbeat_epoch_utc"] = epoch
hb["clock_read"] = ts
hb["current_task"] = "r473 rebase double-collision window CLOSED (r472 landed origin/main 03a1cfb91 after 21+18 UU canon resolution) + W14 park executed per D-20260930-41/MSG-1755 (pool ready->waiting double-file, zero burn N=0, no objection, receipt MSG-20260930-1845-bmb-ALL)"
hb["cpu_cores"] = 16
hb["free_ram_gb"] = 6.6
hb["ram_free_gb"] = 6.6
hb["idle_ram_gb"] = 6.6
hb["gpu_free_vram_gb"] = 2.1
hb["gpu_free_vram_mb"] = 2161
hb["cpu_util_pct"] = 3.2
hb["round_no"] = 473
hb["round"] = 473
hb["loop_round"] = 473
hb["last_round_at"] = ts
hb["verdict"] = ("W14 PARKED per D-20260930-41 sec.1.2 + MSG-20260930-1755-bma-ALL (bm-b r473 receipt, NO objection; "
                 "TRIAL-LABOR-W14-GENERATE pool ready->waiting double-file, zero burn w14_candidates.json absent N=0, "
                 "runner+probe facts archived as unfreeze-ready berth) | CURRENT: r473 rebase double-collision closed "
                 "(r472 landed origin/main 03a1cfb91; 21+18 UU canon-resolved; sides re-probed per rebase round per r461 law; "
                 "r261 phantom-continue handled) + S6 spine rc0 (dualrun ZERO-DRIFT 140/51, audit FLAG:supply_floor lawful post-park, "
                 "watermark py_low_board_clear) + smoke 47/47 | LAST-ARTIFACT: results/runnable_pool.json(+lane) park flip 18:4x + "
                 "fleet/inbox/MSG-20260930-1845-bmb-ALL-w14-park-receipt.md + T-2026-09-30-128 progress receipt | "
                 "NEXT: RETAIL_QUANT_TRACK sec.2 five-priorities non-P1 supply step prereg draft (<=48h, by r475); "
                 "10-01 month-first trio (science_audit+briefing+self_review) + REGIME_GUARD v3 date-gate hands-off")
crlf_hb = b"\r\n" in raw[:600]
body = json.dumps(hb, indent=1, ensure_ascii=False)
data = (body.replace("\n", "\r\n") if crlf_hb else body).encode("utf-8")
if raw.endswith(b"\n") and not data.endswith(b"\n"):
    data += b"\r\n" if crlf_hb else b"\n"
open(hb_path, "wb").write(data)
back = json.loads(open(hb_path, "rb").read())
assert isinstance(back["heartbeat_epoch_utc"], int), "epoch must be JSON int"
print("heartbeat ok epoch=", back["heartbeat_epoch_utc"], "clock=", back["clock_read"])

# ---- round report line
line = ("2026-09-30T18:5x+08:00 | r473 bm-b | dept:工程/研究 | WM=py_low_board_clear 绿（池空=裁定后合法态，supply_floor 旗如实携带）"
        "| 断头 rebase 双撞车窗收口：r472 终 pick 撞 bm-a r483（21 UU 全按正典解：CODELY memory-union ours+r472 条 6,725B<10KB 硬线过、"
        "compute_audit union 202→cap201 保最新、快照逐件 ts 探针取新、双 LHB parquet 自然键恒等取新回填侧零行损失、"
        "r261 幻影拒走=add 脏态件法收口）→ push 撞 bm-a r484 → 二轮 rebase（18 UU·ours/theirs 逐轮翻转=r461 律重探针·全取 ours 新）"
        "→ push 落 origin/main=03a1cfb91（W14 runner+池条目+MSG-1748 机队全可见）"
        "| W14 停泊执行（D-20260930-41+MSG-20260930-1755 回执·无异议·池 ready→waiting 双文件+T-128 progress 回执+"
        "零烧面实证 w14_candidates.json 缺席 N=0 无在飞 worker+回执 MSG-20260930-1845·供给转五件事）"
        "| S6 脊柱+车道腿 rc0：dualrun ZERO-DRIFT 140/51·compute_audit FLAG:supply_floor·wm py_low_board_clear·"
        "update_daily 0 新行 cutoff 09-29·astk/etf/revosc/minute no-op·token delta=0·共享再生面本轮让位 bm-a r484（18:0x 新鲜）减 churn 如实注记 "
        "| S1 smoke 47/47 | 当前活：五件事转轨供给扫描 | 最近实物：pool 翻泊双文件+MSG-20260930-1845+resolver 留痕 _r473bmb_×5 | "
        "下里程碑：RETAIL_QUANT_TRACK §二五件事非P1 项首个供给步预注册草案（≤48h）| 下轮指针：读 §二全表→选非P1 可执行项→"
        "PREREG_TEMPLATE §1.2/§8 起草；decisions.md 直读面未定位（消费面=MSG-1755+正典 v1.0）如实注记 [via bm-b]")
rp = "logs/iteration-loop/round_reports.md"
raw = open(rp, "rb").read()
nl = b"\r\n" if raw.endswith(b"\r\n") else b"\n"
if not raw.endswith(b"\n"):
    raw += nl
open(rp, "wb").write(raw + line.encode("utf-8") + nl)
print("round report appended", len(line), "chars")
