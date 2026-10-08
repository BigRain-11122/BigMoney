# r890 bm-a closeout bookkeeping: state round bump + heartbeat + round report line
# (per-round scratch; reads idle_trigger face for RAM/VRAM; epoch int per R170/R178;
#  clock_read T-separated per R262; report -> ROOT round_reports-bm-a.md per r844 law)
import json, os, time, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MID = "bm-a"

# --- state bump
sp = os.path.join(ROOT, "state-bm-a.json")
st = json.load(open(sp, encoding="utf-8"))
st["round_no"] = 890
json.dump(st, open(sp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# --- metrics faces
idle = json.load(open(os.path.join(ROOT, "results", "idle_trigger.bm-a.json"), encoding="utf-8"))
ram_free_pct = idle.get("ram_free_pct")
vram_free_gb = idle.get("vram_free_gb")
import psutil
ram_free_gb = round(psutil.virtual_memory().available / (1024**3), 1)

# --- heartbeat
hp = os.path.join(ROOT, "fleet", "machines", f"{MID}.json")
hb = json.load(open(hp, encoding="utf-8"))
now_dt = datetime.datetime.now().astimezone()
epoch = int(time.time())
hb.update({
    "last_seen": now_dt.isoformat(timespec="seconds"),
    "current_task": "r890 closed: satengine P0 repair (W189 ignited) + T-177 leg-2 F1/CTA_P1 D6 probe CLEARED (max|corr| 0.0344) + S6 40/40 rc0 (10-08 sina bar still unpublished, retry next) + QA r890 5/5 + bm-b 29h-starvation lane disclosure to ALL (GM reroute pending)",
    "cpu_cores": os.cpu_count(),
    "free_ram_gb": ram_free_gb,
    "gpu_free_vram_gb": vram_free_gb,
    "verdict": "r890: WM green (red=false lane healthy); engine repaired dead->alive same-round (1736s stall -> re-register+tick -> W189 0of12 ignited queue 11); T-177 CEO ticket leg-2 next-ptr-1 done: F1 vs CTA_P1 max|corr|=0.0344 <<0.70 D6 CLEARED_TO_OWN_PREREG (stale-ffill exposure bug caught by sanity check, fixed before verdict consumed, vol 43%->21% honest); S6 40/40 rc0 sina 10-08 reopen bar absent at source honest no-op; QA pack r890 5/5 (PIL chart, matplotlib absent on box); ORD unacked=0; DEC consumed ee70cef0->54b242ac (D-05/D-06 adopted, D-06 machine-suffix law applied to new probe artifact); bm-b 29.2h stale -> 4 lanes starving disclosure MSG-ALL, GM reroute options A/B pending; W189 finalize next rounds",
    "idle_rounds": 0,
    "agenda_starved": False,
    "heartbeat_epoch_utc": epoch,
    "clock_read": now_dt.isoformat(timespec="seconds"),
    "ts": now_dt.isoformat(timespec="seconds"),
})
json.dump(hb, open(hp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
chk = json.load(open(hp, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be JSON int"
assert "T" in chk["clock_read"] and " " not in chk["clock_read"], "clock_read T-separated"
print("heartbeat written; epoch int ok; clock T ok; ram_free_gb=", ram_free_gb, "vram=", vram_free_gb)

# --- round report line (append to ROOT round_reports-bm-a.md per r844/r872 law)
rp = os.path.join(ROOT, "round_reports-bm-a.md")
ts = now_dt.isoformat(timespec="seconds")
line = (
    f"{ts} | r890 | bm-a | dept:research/engine+data (perpetual line+CEO ticket T-177+engineering) | "
    "WM-VERDICT: green (red=false lane healthy; next_pick moneyflow IC claimed=advisory panel-source-blocked; py_watermark rc0) | "
    "当前活: r890 收尾 (孤儿面=0·19 py faces; 饱和引擎 P0 同轮修复: status 1736s dead -> re-register+tick 19:53 -> alive W189 0of12 点火 queue 11 实弹) | "
    "实物: ①results/regime5_bull_scan/f1_ctap1_corr_probe.bm-a.json (T-177 leg-2 下步指针-1: F1 ETF 动量轮动 vs CTA_P1 冻结构造 verbatim D6 日收益口径 9 cells, max|corr|=0.0344 <<0.70 -> CLEARED_TO_OWN_PREREG; 探针健全性查抓 stale-ffill 出场权重永续 bug (replace(0->NaN)+ffill 使 k=2 暴露涨至 3-4x vol 43%) -> 修复为再平衡全向量替换后 vol 21% 合理·verdict 两态皆 <<0.7 稳健·bug 修复先于判决消费; 机器后缀产物名=D-20261008-06 律首例) "
    "②qa/smoke-r890.md+equity-curve-r890.png+smoke-r890.log (QA 5/5 PASS: 93 trades determinism=True 同冻结 fixture 与他机互证; matplotlib 本机缺->PIL 画图; F-03 过渡律=r890 路径无前 committer 零撞名如实) "
    "③results/_r890bma_s6_chain.json (S6 40/40 rc0 bad NONE; sina 10-08 节后首 bar 源面未发布诚实 no-op·下轮续试; paper 腿待 bar) "
    "④fleet/inbox/MSG-20261008-200x-bma-ALL.md (bm-b 心跳 29.2h 停滞+四车道饿道披露: etf_daily/minute_feed/astock_daily/rev_osc_export SIG 09-30 止 -> system_v1_paper awaiting_signal; GM 改派选项 A/B 呈请·R31 单写者律尊重零单方面翻 guard) | "
    "下轮指针: ①F1 预注册起草 (PREREG_TEMPLATE+出场轴显式门+science_gates g1/g2 共享判据; D6 已过) ②sina bar 发布后 S6 补跑 (REGIME_GUARD enforce+live.paper+marks settle=r889 挂账尾) ③W189 finalize (引擎自主 12/12 后) ④GM bm-b 改派裁定消费 ⑤HANDOVER 产物清单本窗已刷 | "
    "验证: smoke 49/49 + S6 40/40 rc0 + QA 5/5 + attrition CLEAN (4 ledgers) + ORD 双扫 unacked=0 + DEC ee70cef0->54b242ac 消费 (D-05 收讫注记/D-06 后缀律/D-07/D-08 知悉; F-20261007-01 r866 已自翻=零动作; F-03 open 候裁定已适用过渡律) + 引擎 alive W189 0of12 + 本地未达 origin commit 数=0 (push 后 fetch+ls-tree 自证) + token: L1 零 API [via bm-a r890]"
)
with open(rp, "a", encoding="utf-8", newline="\n") as f:
    f.write(line + "\n")
print("round report appended; lines now:", len(open(rp, encoding='utf-8').read().splitlines()))
