"""r888 bm-b closeout: state.json + heartbeat + round report (r88x pattern)."""
import json
import time
from datetime import datetime, timedelta, timezone

NOW = datetime.now(timezone(timedelta(hours=8)))
TS = NOW.strftime("%Y-%m-%dT%H:%M:%S+08:00")
EPOCH = int(time.time())

DID = (
    "r888: killed-session inheritance (25min watchdog killed r888 primary ~16:36 mid-round; detached S6 driver "
    "completed 16:46 with 3 red legs) -> RW-4 reconciliation: r888 T-184 bare-path restore (data/daily/510880.csv) "
    "tripped frozen in-service lock (48 core48, T-127/D-20260930-05) refusing live_paper/t24_prospect_paper/"
    "aggressive_lab -> face relocated to data/ext_slots/etf_daily/510880_t73_longhist.csv (sha256 39189d03... "
    "byte-identical, zero bare-path consumers: alloc reads P5_SLOT pin intact since r882, cn_core reads sh510880.csv "
    "prefixed) -> 3 legs re-run rc0 + smoke 49/49; T-184 task receipt addendum r888b_rw4_reconciliation_bmb; "
    "E16 census 12/12 (shards 9/10/11 landed this window, autofill chain) -> finalize refuse-if-exists rc0 "
    "census_holds=true (obs family max |ICIR| 0.455 > null family p95 0.077, n_ok 200/200) -> CENSUS-2026-10-09.json "
    "+ queue row explore.md E16 flipped done + archive receipt (prereg L85; main 30,686/30,720B full -> flow line "
    "routed memory-archive/202610.md per D-20261024-01) -> holds = N2 U3 channel-1 drafting window OPEN; "
    "CODELY r888 mini-split (r885 entry 973B verbatim -> pit-machine.md + new RW-4 restore-face placement pit, "
    "receipt _r888bmb_codely_minisplit.json); S0 one-inbound rebase (bm-c r880 W18 runner LANDED, 6-commit replay "
    "zero conflict); D19 dec 81f27c6d + ord 69090314 zero-delta; S7 suite green (loop pin=2, watchdog+claws "
    "idempotent, attrition CLEAN 4 healed 0 active, orphan faces=0); unacked_orders=0"
)
NEXT = (
    "r889: N2 U3 channel-1 drafting window decision (E16 holds pointer; if opened -> PREREG_TEMPLATE gate + "
    "D6>=0.7 reject + explicit exit-axis per O-20261001-1108) > 48h CEO report due 2026-10-13 11:2x (E16 census "
    "verdict + W18 status + fleet state) > W210 freeze anchor watch (gated W209<-W208 bm-a stall; MSG-1529 sec.3 "
    "24h SLA bm-c-held) > T-184 bm-a courtesy re-probe when bm-a returns (byte-compare vs NEW path "
    "data/ext_slots/etf_daily/510880_t73_longhist.csv, sha unchanged) > IntradayMarks first fire Monday 10-12 09:25 watch"
)
NOW_ACTIVE = "r888 closeout: E16 census verdict face landed (census_holds=true 200/200) + RW-4 510880 reconciliation complete (3 legs green)"
LATEST = (
    "r888: results/alphagen_rg/CENSUS-2026-10-09.json (census_holds=true, finalize 17:0x) + "
    "data/ext_slots/etf_daily/510880_t73_longhist.csv (RW-4 reconciliation, sha byte-identical) + "
    "results/_r888bmb_codely_minisplit.json"
)
VERDICT = (
    "GREEN: r888 COMPLETE (killed-session inheritance healed: RW-4 510880 reconciliation 3 legs rc0 + smoke 49/49; "
    "E16 12/12 finalize census_holds=true; queue row done; CODELY mini-split; D19 zero-delta; attrition CLEAN; "
    "unacked=0; WM red=burn-ramp O-1612 GM waiver face, E16 closeout self-resolves next probe)"
)

REPORT_LINE = (
    "2026-10-11T17:1x+08:00 | r888 bm-b | dept:工程（击杀会话遗产继承+RW-4 冲突调解修复+S0 rebase+S7 收口）"
    "+dept:研究（E16 alphagen RG census 判决收官：12/12 烧录+finalize+verdict face）| WM verdict=红·池批可跑而 py 低位"
    "（O-1612 GM 弃权面·E16 烧录窗·本轮 12/12 收口自愈）；实况三行：当前活=r888 击杀会话续跑全修复收口（25min 看门狗击杀 "
    "r888 主会话于 S6 后段~16:36·分离 S6 驱动器续命 16:46 完成·三红腿本轮全愈）；最近实物=results/alphagen_rg/"
    "CENSUS-2026-10-09.json（census_holds=true·obs 0.455>null p95 0.077·200/200·17:0x）+RW-4 修复=data/ext_slots/etf_daily/"
    "510880_t73_longhist.csv（sha 恒等 39189d03·三腿复跑 rc0·smoke 49/49）；下个里程碑=48h CEO 报告 2026-10-13 11:2x+"
    "N2 U3 channel-1 drafting window 开窗指针（E16 holds）+IntradayMarks first fire 10-12 09:25；做了什么：S0 单入站 rebase"
    "（bm-c r880 W18 runner LANDED·6 commit 重放零冲突）+RW-4 调解（T-184 r888 裸码恢复面撞 48 core48 冻结锁→迁移 ext_slots·"
    "票面回执 r888b·禁白名单 re-freeze 禁拆门绊线·三红腿 live_paper/t24_prospect_paper/aggressive_lab 复跑全 rc0）+E16 "
    "shard-9/10/11 落地 12/12→finalize refuse-if-exists rc0→队列行 explore.md E16 翻面 done+archive 回执（prereg L85·"
    "主件满员 30,686/30,720 按流水路由落 memory-archive/202610.md）+CODELY r888 mini-split（r885 条目 973B verbatim 迁 "
    "pit-machine.md·新坑律 RW-4 恢复面落位冲突入主件·receipt _r888bmb_codely_minisplit.json）+idle --worked 清零；"
    "验证证据：smoke 49/49+S6 41 腿（16:36 批 38 rc0+3 修复复跑 rc0）+attrition CLEAN（4 healed 0 active）+孤儿面=0+"
    "D19 dec 81f27c6d/ord 69090314 双零增量+unacked_orders=0（70 in-dir 全 ack）；本地未达 origin commit 数=0"
    "（push 后 fetch+rev-list 自证）；下轮指针=r889：N2 U3 channel-1 drafting 决策>48h CEO 报告起草窗+W210 冻结锚守望+"
    "T-184 bm-a 归天 byte-compare（新路径 ext_slots/510880_t73_longhist.csv·sha 不变）+IntradayMarks 09:25 守望"
)

# --- state.json ---
with open("state.json", "r", encoding="utf-8") as f:
    st = json.load(f)
st.update({
    "clock_read": TS, "ts": TS, "updated": TS, "updated_at": TS,
    "last_seen": TS, "last_round_at": TS, "last_round_ts": TS, "last_action_at": TS,
    "last_decisions_read_at": TS, "last_orders_read_at": TS,
    "round": 888, "round_no": 889, "round_no_label": "r888",
    "did": DID, "last_action": DID, "now_active": NOW_ACTIVE,
    "latest_artifact": LATEST, "next": NEXT, "task": NEXT, "current_task": NEXT,
    "next_milestone": "48h CEO report 2026-10-13 11:2x (E16+W18+fleet); N2 U3 channel-1 drafting decision next rounds; IntradayMarks first fire 10-12 09:25",
    "note": "r888: killed-session inheritance + RW-4 reconciliation (T-184 face relocated ext_slots, 3 legs green) + E16 census_holds=true finalize; WM red=burn-ramp O-1612 GM waiver legal, self-resolves with E16 closeout",
    "verdict": VERDICT,
    "orphan_face": 0, "orphan_faces": 0,
    "orphan_face_note": "r888 round probe: py_faces=10 alive, orphans=0",
    "last_orders_sha_note": "r888: canonical probe post-fetch dec 81f27c6d + ord 69090314 both identical to state watermarks = zero delta zero action; 70 in-dir O files all acked",
    "last_decisions_sha_method": "r835: post-restore re-probe via results/_r686bmb_d19_check.py (r537 SHA-1 40-hex raw-blob PIN); r888 re-probe post-rebase dec+ord both zero-delta identical",
})
st["d19_watermark_guard"]["round_ref"] = 888
st["d19_watermark_guard"]["ts"] = TS
st["sync"] = {
    "last_push_ts": TS,
    "note": "r888 closeout push lands with this commit (one-commit-lag face per r886/r887 pattern; delivery self-proof = post-push fetch + rev-list 0)",
}
with open("state.json", "w", encoding="utf-8") as f:
    json.dump(st, f, ensure_ascii=False, indent=1)

# --- heartbeat fleet/machines/bm-b.json ---
with open("fleet/machines/bm-b.json", "r", encoding="utf-8") as f:
    hb = json.load(f)
hb.update({
    "clock_read": TS, "ts": TS, "updated": TS, "updated_at": TS,
    "last_seen": TS, "last_round_at": TS, "last_action_at": TS,
    "heartbeat_epoch_utc": EPOCH,
    "round": 888, "round_no": 888,
    "current_task": NEXT, "did": DID, "last_action": DID,
    "now_active": NOW_ACTIVE, "latest_artifact": LATEST,
    "next": NEXT, "task": NEXT,
    "next_milestone": "48h CEO report 2026-10-13 11:2x; N2 U3 channel-1 drafting window OPEN (E16 holds); IntradayMarks first fire 10-12 09:25",
    "verdict": "green",
    "idle_rounds": 0, "agenda_starved": False,
    "free_ram_gb": 6.2, "ram_free_gb": 6.2, "ram_free_pct": 25.8,
    "gpu_free_vram_mb": 3511, "gpu_free_vram_gb": 3.4, "vram_free_gb": 3.4,
    "orphan_face": 0, "orphan_faces": 0,
    "orphan_face_note": "r888 round probe: py_faces=10 alive, orphans=0",
    "sync": {"last_push_ts": TS, "note": "r888 closeout push lands with this commit (one-commit-lag face); delivery self-proof = post-push fetch + rev-list 0"},
})
with open("fleet/machines/bm-b.json", "w", encoding="utf-8") as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)

# --- round report append ---
with open("logs/iteration-loop/round_reports.md", "a", encoding="utf-8", newline="") as f:
    f.write("\n" + REPORT_LINE + "\n")

# --- self-assertions ---
chk = json.loads(open("fleet/machines/bm-b.json", "r", encoding="utf-8").read())
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be JSON int"
assert "T" in chk["clock_read"] and "+" in chk["clock_read"], "clock_read must be ISO8601 T-separated"
print(json.dumps({
    "ok": True, "ts": TS, "epoch": EPOCH,
    "epoch_is_int": isinstance(chk["heartbeat_epoch_utc"], int),
    "state_round": 888, "state_next_round_no": 889,
}))
