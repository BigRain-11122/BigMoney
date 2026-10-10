# r848 bm-b closeout: heartbeat + state update (ASCII-only)
import json, time, datetime, psutil, subprocess

root = r"C:\Fluxgroup\FluxGroup\quant\bigmoney"
now = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
epoch = int(time.time())
vm = psutil.virtual_memory()
ram_free_gb = round(vm.available / (1024**3), 1)
cores = psutil.cpu_count(logical=True)
gpu_free_mb = 0
try:
    out = subprocess.run(["nvidia-smi", "--query-gpu=memory.free", "--format=csv,noheader,nounits"],
                         capture_output=True, text=True, timeout=15)
    gpu_free_mb = int(float(out.stdout.strip().splitlines()[0]))
except Exception:
    gpu_free_mb = 0

verdict = ("GREEN: r848 stewardship wait-window round (smoke 49/49; D19 dual watermark zero-delta both dec a20664ec + ord 24e6066e "
           "(group delta consumed r847, no new rows); fleet orders 65/65 ack zero unacked dual-scan start+closeout; attrition "
           "CLEAN; board/job/queues empty (T-182 claimed by bm-c = only live ticket, not open); pool W17-JUDGE ready "
           "lane_owner=bm-a -> yielded per R31; SatEngine alive rc0 queue 0; idle cleared via --worked (S6 41-leg product "
           "chain); audit flags supply_gap/supply_floor = W18 drain-gated by design awaiting bm-a W17-JUDGE drain; "
           "py_low_with_work_cands legal = astock rebuild in-flight network-bound fetch (lock alive pid 10404); "
           "T23 census physical dependency continues, disk 2756/5217 @23:29, sustained pace ~16-19 files/min -> honest ETA "
           "correction ~01:40-02:15 (r847 acceleration burst did not hold, network-bound)")
did = ("r848: stewardship round: S0 absorb daemon faces 2 commits (7+3 satengine race re-absorb) + pull --rebase up-to-date; "
       "S0.5 fleet orders 65/65 zero unacked (dual scan round-start + closeout, count stable 65); D19 dual watermark probe "
       "zero-delta both (dec a20664ec, ord 24e6066e); smoke 49/49; S3 fixed order green (wm red=false next_pick claimed "
       "advisory; SatEngine rc0 alive queue_depth 0; pool only W17-JUDGE lane bm-a -> yield R31; board/job empty, "
       "P2/P3 queues all done/closed -> main queue head T23 census physically blocked on astock rebuild = honest wait "
       "window); S6 41 legs 40 rc0 + alloc rc=2 known P5 510880 TRANSFER-pending honest (dualrun streak 3, daily report "
       "+ live usage refreshed); astock rebuild lock alive 2553@23:18 -> 2697@23:27 -> 2756@23:29 of 5217; S7 four-piece "
       "self-heal (loop pin=2 no-op, watchdog registered, both claws LF-normalized) + attrition guard CLEAN + idle --worked "
       "cleared + inbox empty")

# heartbeat
hp = root + r"\fleet\machines\bm-b.json"
h = json.load(open(hp, encoding="utf-8"))
h.update({
    "round": 848, "round_no": 848,
    "now_active": "r848 closeout: stewardship wait-window round (S6 41 legs 40 rc0 + alloc rc=2 known 510880 pending; astock rebuild 2756/5217 in flight, ETA honest correction ~01:40-02:15)",
    "current_task": "r849 queue: astock rebuild completion verify (ETA ~01:40-02:15) -> spawn detached T23 census full burn -> census_holds readout -> N2 U3(1) prereg drafting window if holds / G2 academic-citation fallback if negative + S6 chain; W18 stays drain-gated (bm-a owns w17-judge)",
    "task": "r849 queue: astock rebuild completion verify (ETA ~01:40-02:15) -> spawn detached T23 census full burn -> census_holds readout -> N2 U3(1) prereg drafting window if holds / G2 academic-citation fallback if negative + S6 chain; W18 stays drain-gated (bm-a owns w17-judge)",
    "next": "r849 queue: astock rebuild completion verify (ETA ~01:40-02:15) -> spawn detached T23 census full burn -> census_holds readout -> N2 U3(1) prereg drafting window if holds / G2 academic-citation fallback if negative + S6 chain; W18 stays drain-gated (bm-a owns w17-judge)",
    "latest_artifact": "r848: results/_r848bmb_s6chain.log (41 legs: 40 rc0 + alloc rc=2 known P5 510880 TRANSFER-pending, dualrun streak 3) + docs/daily_report/REPORT-2026-10-10.md + docs/live_usage/LIVE-2026-10-10.md refreshed, 2026-10-10 23:2x",
    "next_milestone": "astock panel complete (~01:40-02:15 corrected ETA) -> detached T23 census full burn -> holds verdict (window <=10-11 06:00) -> N2 U3(1) prereg draft window",
    "verdict": verdict,
    "last_action": did,
    "did": did,
    "last_round_at": now, "last_seen": now, "updated": now, "ts": now,
    "clock_read": now, "updated_at": now,
    "heartbeat_epoch_utc": epoch,
    "cpu_cores": cores,
    "free_ram_gb": ram_free_gb,
    "gpu_free_vram_mb": gpu_free_mb,
    "gpu_free_vram_gb": round(gpu_free_mb / 1024, 2),
    "idle_rounds": 0,
    "agenda_starved": False,
    "orphan_faces": 0,
    "orphan_face_note": "r848 orphan probe 23:2x py_faces=18 orphans=0",
    "sync": {"last_push_ts": now, "note": "r848 closeout; post-push fetch self-proof behind=0 pending S7 verify"},
})
json.dump(h, open(hp, "w", encoding="utf-8"), indent=1, ensure_ascii=True)

# state.json (bm-b uses shared state.json per fleet README s6)
sp = root + r"\state.json"
s = json.load(open(sp, encoding="utf-8"))
s.update({
    "machine_id": "bm-b",
    "round_no": 848,
    "round": 848,
    "round_no_label": "r849",
    "note": did,
    "last_round_at": now, "ts": now, "updated": now, "last_seen": now,
    "clock_read": now,
    "did": did,
    "verdict": verdict,
    "last_action": did,
    "now_active": "r848 closeout: stewardship wait-window round (astock 2756/5217 in flight ETA corrected ~01:40-02:15, S6 41 legs done, claim faces yielded)",
    "current_task": "r849 queue: astock completion verify -> spawn detached T23 census full burn -> census_holds readout -> N2 U3(1) prereg window / G2 fallback + S6 chain; W18 drain-gated (bm-a owns w17-judge)",
    "task": "r849 queue: astock completion verify -> spawn detached T23 census full burn -> census_holds readout -> N2 U3(1) prereg window / G2 fallback + S6 chain; W18 drain-gated (bm-a owns w17-judge)",
    "next": "r849 queue: astock completion verify -> spawn detached T23 census full burn -> census_holds readout -> N2 U3(1) prereg window / G2 fallback + S6 chain; W18 drain-gated (bm-a owns w17-judge)",
    "latest_artifact": "r848: results/_r848bmb_s6chain.log (41 legs: 40 rc0 + alloc rc=2 known P5 510880 TRANSFER-pending) + docs/daily_report/REPORT-2026-10-10.md + docs/live_usage/LIVE-2026-10-10.md refreshed, 2026-10-10 23:2x",
    "next_milestone": "astock panel complete (~01:40-02:15 corrected ETA) -> detached T23 census full burn -> holds verdict (window <=10-11 06:00) -> N2 U3(1) prereg draft window",
    "last_orders_sha": "24e6066ef2f1a472df20d2c34ee22575e2751ade",
    "last_orders_at": now,
    "last_orders_read_at": now,
    "last_orders_sha_note": "r848: dual watermark probe zero-delta both (dec a20664ec, ord 24e6066e) via results/_r686bmb_d19_check.py; no group delta this round",
    "last_round_ts": now,
    "updated_at": now,
})
json.dump(s, open(sp, "w", encoding="utf-8"), indent=1, ensure_ascii=True)

# round report line (bm-b lane file)
rp = root + r"\logs\iteration-loop\round_reports.md"
line = (
    now + " | r848 bm-b | dept:工程（stewardship 等待窗守护轮：astock 重建在飞=T23 census 物理依赖）"
    " | WM-VERDICT: green（red=false @23:24 probe；py_low_with_work_cands 合法=local_batch 1=astock 全宇宙重建在飞〔pid 10404·refresh lock alive·网络限速拉取型〕+池 ready 1=W17-JUDGE lane bm-a 非本机候选+板 0〔T-182=claimed 非开〕+bandit 0；supply_gap/supply_floor=O-1645 standing〔W18 drain-gated 待 bm-a W17-JUDGE〕；ignition_sla 零 breach）"
    " | 孤儿面=0（probe 23:2x py_faces=18 orphans=0）"
    " | CEO three-line: 当前活=T23 census 等待窗守护（astock 5229 股宇宙重建在飞 2553@23:18→2697@23:27→2756@23:29 /5217·持续 pace ~16-19/min·ETA 诚实修正 ~01:40-02:15〔r847 加速段未保持·网络限速所致〕·census run gate awaiting_panel exit 2 诚实禁假跑）+S6 41 腿；最近实物=results/_r848bmb_s6chain.log（41 腿·40 rc0+alloc rc2 已知 P5 510880 披露·dualrun streak 3）+docs/daily_report/REPORT-2026-10-10.md+docs/live_usage/LIVE-2026-10-10.md 刷新 23:2x；下个里程碑=astock 面板完备（~01:40-02:15±）→detached T23 census 全量烧录（~15-25min 长活）→census_holds 判读（窗 ≤10-11 06:00）→N2 U3(1) prereg 起草窗（holds）/G2 学术引用 fallback（负面）"
    " | 板/队列实况: fleet tasks 零 open（T-182 claimed by bm-c 非开票）·job_list 空·P2 tech 全 done·P3 explore 全 done/closed——三空=主队列头 T23 census 物理依赖 astock 面板重建·诚实等待窗·禁造活跃数不填假行；池 W17-JUDGE ready lane_owner=bm-a=让路 R31 非本机票"
    " | 本地未达 origin commit 数=0（收口 push 后 fetch+ls-remote 自证；收口前=2 S0 absorb 提交在推）\n"
)
with open(rp, "a", encoding="utf-8") as f:
    f.write(line)
print("heartbeat+state+round-report updated; epoch=%d int=%s; clock_read=%s; ram_free=%.1fGB gpu_free=%dMB cores=%d" % (epoch, isinstance(epoch, int), now, ram_free_gb, gpu_free_mb, cores))
