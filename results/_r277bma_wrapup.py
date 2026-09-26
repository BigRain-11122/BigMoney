# -*- coding: utf-8 -*-
"""R277 bm-a round wrap-up: ticket progress x4, state-bm-a.json, round report
line, heartbeat (orders_ack union incl O-2320/2325, epoch int + T-sep clock),
quant CODELY.md order-execution lines, root CODELY.md pit-law line.
Byte-face safe per R255/R257/R269/R271 laws (probe BOM/EOL/ascii/indent/tnl).
"""
import json, os, subprocess, time
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NOW = datetime.now()
TS = NOW.strftime("%Y-%m-%d %H:%M:%S")
NOWISO = NOW.astimezone().isoformat()
EPOCH = int(time.time())

PROGRESS = {
 "T-2026-09-26-85-P1": ("s1 NAV-harvest runner BUILT + POOLED this round: scripts/fusion_p1_nav.py "
   "(p3_portfolio.member_run frozen primitive; member specs pinned to results/t56_caliber_registry r256 A1 law, "
   "manifest raw-sha dual-gate; hard anchors fail-closed: CE backtest-block via p3.anchor_checks / PROSPECT prospect.recorded_* / "
   "overlay x2 vs frozen stress_x2; wired-overlay census = judgment-artifact recorded combos zero-invention (4 not 12); "
   "selftest 15/15 pre-pooling r263 law; pool entry FUSION-P1-NAV status=ready, autofill C8 fires next tick, "
   "64-line census = 28 members x2 + 4 wired-overlay x2; ledger +0 derivation face t24 precedent). "
   "NEXT: s2 fusion grid + s3 gates owe FROZEN PRERG BEFORE any judged run (R99): draft from research/PREREG_TEMPLATE.md, "
   "judgment via science_gates.g1_prime_v2/g2_registration_v2 shared library (no hand-copied lines), weight families per ticket "
   "(EW/inv-vol/inv-MDD/corr-cluster risk-parity/regime-conditional ORANGE x position_cap REGIME_GUARD v1.0), member subsets "
   "(topK Sharpe K=2..8 / all / corr>=0.95 collapse-to-one dedup per T-84 s3 law), rolling 6m/12m/24m + bear/bull/chop segments, "
   "dual benchmarks EW48 + B_MAXDIV (benchmark-only, T-27 veto window until 10-01 zero wiring) + 510300; x2 cost stress parallel lane"),
 "T-2026-09-26-86-P1": ("s1 registry INVENTORY complete (exploration face): 28 engine factors (engine/factors.py FACTORS dict) "
   "+ 2 bench rs faces; zoo-6 (p1e_factors: zoo85_stv/zoo85_terrified/zoo92_coin_team/zoo93_arc,vrc,src,krc); IC families "
   "GTJA191/WQ101/A158-truegap (research/shortline evidence set); sina MF four-tier T-72 (collector scripts/update_sina_mf.py ready, "
   "panel data/sina_mf machine-local); LHB faces (lhb_count_20 family, Money02/data/lhb parquet machine-local); "
   "meta-registry scripts/factor_registry.py already exists (28 engine faces -> 7 economic faces). HONEST NOTE: GM quick-strike "
   "scratch fusion_explore_p0 NOT in this checkout (other-tree session artifact; exploratory lead lowamp20 +8.1pp perm p=0.035 "
   "recorded in ticket/order, formal census must re-derive on core48). "
   "NEXT: write research/FACTOR_CENSUS_REGISTRY.md (single-source, zero invention outside registry) + census runner "
   "scripts/factor_census_p1.py: core48 panel via live.paper.build_panels, pairwise C(n,2) + triple combos, dual-sort conditional "
   "returns + rank-IC + cost-inclusive long-leg blend, x2 via CostPatch(2); uncertainty face = block bootstrap + sign-flip "
   "permutation (science_gates bootstrap_ci_sharpe + null machinery, SEED_REGISTRY new free band above 20261130); "
   "CENSUS = EXPLORATION zero judgment; outputs research/ + results/factor_census/; top families feed T-23 intake funnel; "
   "register runnable-pool entry with workers_plan (24h saturation)"),
 "T-2026-09-26-87-P1": ("s1 enumeration DELIVERED: research/SCHOOL_SUPPLY_S1.md (16-school survey verbatim rows, judged-closed map "
   "WILD-S1/GRID-SLEEVE-P1/CN-5-family, 4 infeasible-domain rows, s2 prereg supply queue #1 ts-trend row14 / #2 zhongtegu row8 / "
   "#3 K-line pattern row13 folklore-gate-first / #4 sector-leader row3 new-face-D6 / #5 market-neutral row16 CTA-boundary-note; "
   "rows 9/10 value/growth = data-audit-first; row 4 thematic deprioritized; row 5 compliance-banned never). "
   "NEXT: s2 prereg drafts #1+#2 (PREREG_TEMPLATE, G1'v2+G2 shared library, x1+x2 full-history judged cells, bear/bull/chop "
   "segments, RANDOM_LARGE_SAMPLE_LAW v1.0 binding per O-20260926-2325), then runner + pool entry with workers_plan; "
   "judged-negative = slot closed honest report; survivors -> STRATEGY_LIBRARY intake -> T-85 s4 fusion candidate pool cross-ref"),
 "T-2026-09-26-88-P1": ("claimed R277 + s1 FIRST-CUT DELIVERED: research/DOMAIN_AUDIT.md v0.1 (12-domain table: A-share P1C full-history "
   "in-repo, ETF core48 in-repo, convertible = collector-first (s2 converges T-60 in-flight line), repo GC001/R-001 = collector to "
   "build (s3, SPM cash-leg value, weekend-legal), REITs/LOF/QDII = PENDING per-domain probes, commodity/index/bond futures "
   "in-library (judged-negative families stay closed; new prereg + larger N channel per RANDOM_LARGE_SAMPLE_LAW sec-5), "
   "ETF options = forward-history gate <12mo (T-67 sec-2 freeze law), BSE = data absent honest). "
   "NEXT: s3 repo collector engineering (sina/EM GC001/R-001 daily face, S6 gate wiring per bigmoney-data-gate-wiring skill: "
   "zero-network no-op gate + checkpoint + conn-fuse + selftest subcommand); s2 convertible collector+audit follows T-60 lane; "
   "s4 next-domain selection by audit results; batches register runnable-pool entries with workers_plan"),
}

def probe(p: Path):
    raw = p.read_bytes()
    bom = raw.startswith(b"\xef\xbb\xbf")
    eol = b"\r\n" if b"\r\n" in raw else b"\n"
    txt = raw.decode("utf-8-sig" if bom else "utf-8")
    na = any(ord(c) > 127 for c in txt)
    indent = 1
    for ln in txt.splitlines():
        if ln.startswith(" "):
            indent = len(ln) - len(ln.lstrip(" "))
            break
    return raw, bom, eol, na, indent, raw.endswith(b"\n")

def write_json(p: Path, d, bom, eol, na, indent, tnl):
    out = json.dumps(d, ensure_ascii=not na, indent=indent)
    if tnl:
        out += "\n"
    data = out.encode("utf-8")
    if bom:
        data = b"\xef\xbb\xbf" + data
    if eol == b"\r\n":
        data = data.replace(b"\n", b"\r\n")
    p.write_bytes(data)

def sample_sys():
    try:
        import psutil
        cpu = round(psutil.cpu_percent(interval=2), 1)
        ram = round(psutil.virtual_memory().available / 1024**3, 1)
    except Exception:
        cpu, ram = 0.0, 0.0
    gpu = None
    try:
        r = subprocess.run(["nvidia-smi", "--query-gpu=memory.free", "--format=csv,noheader,nounits"],
                           capture_output=True, text=True, timeout=20)
        gpu = round(float(r.stdout.strip().splitlines()[0]) / 1024, 1)
    except Exception:
        pass
    return cpu, ram, gpu

def main():
    # 1) ticket progress x4 (field-level increments only)
    for tid, prog in PROGRESS.items():
        p = ROOT / "fleet" / "tasks" / f"{tid}.json"
        raw, bom, eol, na, indent, tnl = probe(p)
        d = json.loads(raw.decode("utf-8-sig" if bom else "utf-8"))
        assert d.get("claimed_by") == "bm-a", tid
        d["progress_r277"] = prog
        write_json(p, d, bom, eol, na, indent, tnl)
        print(f"progress: {tid}")

    # 2) state-bm-a.json
    sp = ROOT / "state-bm-a.json"
    raw, bom, eol, na, indent, tnl = probe(sp)
    st = json.loads(raw.decode("utf-8-sig" if bom else "utf-8"))
    did = ("R277 CEO order-execution round (O-20260926-2320 24h-saturation + O-20260926-2325 domain-unlock): "
           "T-85/86/87 claimed+started same round + T-88 claimed same round; T-85 s1 NAV-harvest runner built "
           "(scripts/fusion_p1_nav.py, caliber-pinned anchors fail-closed, selftest 15/15) and POOLED as FUSION-P1-NAV "
           "ready -> pool starvation red card (first v2.3 any-day live fire, span 251min) discharged same round "
           "(ready 0->1, autofill burns next tick); T-87 s1 school enumeration delivered "
           "(research/SCHOOL_SUPPLY_S1.md, 5-family prereg queue); T-88 s1 first-cut domain audit delivered "
           "(research/DOMAIN_AUDIT.md 12-domain table); COMPUTE_AUDIT v2.3 law fix (weekend exemption abolished, "
           "selftest 13/13 with Saturday live-fire case); decisions tail reviewed (D-20260926-10 HQ-side, zero repo action)")
    st.update({
        "round_no": 277, "did": did,
        "verdict": ("R277: order round all-green base (smoke 25/25, S6 21 legs rc=0 weekend no-op family) + "
                    "pool_starvation flag v2.3 first live fire honestly reported and DISCHARGED by FUSION-P1-NAV "
                    "pool entry (ready=1; load_state flips idle-starvation->pool-supply-gap); orders 87/87 acked "
                    "(incl O-2320+O-2325); migration executor + MF_IC_P1/AH source-block faces carried supervised"),
        "next": ("autofill burns FUSION-P1-NAV (64-line NAV census, harvest flip next round per r244 law); "
                 "T-86 s2 census runner + registry file (exploration face, pool entry); T-87 s2 prereg #1 ts-trend + "
                 "#2 zhongtegu drafts; T-88 s3 repo collector engineering (S6 gate wiring); T-85 s2/s3 fusion-grid "
                 "prereg freeze BEFORE judged runs (R99); 09-28 Monday first-bar chain; 10-01 month-first trio + "
                 "REGIME_GUARD v3 date gate; R280 HANDOVER check"),
        "ts": TS, "last_round_ts": TS, "updated_at": TS, "last_run": TS,
        "last_round_at": TS, "last_round": 277, "updated": TS,
        "current_task": ("R277 order round delivered; T-85 s1 NAV batch pooled FUSION-P1-NAV ready (autofill next "
                         "tick); T-86/87/88 s1 faces delivered, s2 preregs/census next batches"),
    })
    write_json(sp, st, bom, eol, na, indent, tnl)
    print("state-bm-a.json -> R277")

    # 3) round report line (bm-a per-machine file)
    rp = ROOT / "logs" / "iteration-loop" / "round_reports-bm-a.md"
    raw = rp.read_bytes()
    tnl_rp = raw.endswith(b"\n")
    line = (f"{TS} | R277 | O-2320+O-2325 CEO令执行轮：watermark red=false 但 py_low_with_work_cands+池饿旗 v2.3 "
            f"首火（span 251min）→同轮喂池收敛（FUSION-P1-NAV ready 0→1，autofill 下 tick 开烧）；T-85/86/87+T-88 "
            f"认领即开跑（T-85 s1 NAV 收割 runner 建成+入池 selftest 15/15 锚门 caliber 快照 fail-closed；T-87 s1 "
            f"research/SCHOOL_SUPPLY_S1.md 流派枚举+s2 队列；T-86 s1 因子清单勘探回齐（census runner 下批）；T-88 s1 "
            f"research/DOMAIN_AUDIT.md 12 域首切）；COMPUTE_AUDIT v2.3 修法（周末豁免废除+selftest 13/13 周六实弹例）"
            f"| smoke 25/25；S6 21 legs rc=0（周末 no-op 族）；池 ready=1 in-pool 证据 runnable_pool.json 尾条；"
            f"orders 87/87 ack 差集=2320/2325 双令已回执 | 下轮：autofill 烧 NAV 批+收割翻 done；T-86 census "
            f"runner+registry；T-87 prereg #1/#2；T-88 s3 repo 采集器\n")
    with open(rp, "ab") as f:
        if not tnl_rp:
            f.write(b"\n")
        f.write(line.encode("utf-8"))
    print("round_reports-bm-a.md +1 line")

    # 4) heartbeat
    hp = ROOT / "fleet" / "machines" / "bm-a.json"
    raw, bom, eol, na, indent, tnl = probe(hp)
    hb = json.loads(raw.decode("utf-8-sig" if bom else "utf-8"))
    cpu, ram, gpu = sample_sys()
    orders = sorted(os.path.basename(p) for p in (ROOT / "fleet" / "orders").glob("O-*.md"))
    acked = set((hb.get("orders_ack") or "").replace(".md", "").split())
    missing = [o.replace(".md", "") for o in orders if o.replace(".md", "") not in acked]
    new_ack = " ".join(sorted(acked | set(missing) | {"O-20260926-2320-bm-a", "O-20260926-2325-bm-a"}))
    hb.update({
        "machine_id": "bm-a", "last_seen": TS[:16], "round_no": 277,
        "current_task": st["current_task"], "task": st["current_task"],
        "cpu_cores": 32, "cpu_pct": cpu, "free_ram_gb": ram, "idle_ram_gb": ram,
        "cores": 32,
        "verdict": st["verdict"],
        "orders_ack": new_ack,
        "heartbeat_epoch_utc": EPOCH,
        "clock_read": NOWISO,
    })
    if gpu is not None:
        hb.update({"gpu_free_vram_gb": gpu, "gpu_idle_vram_gb": gpu,
                   "gpu_idle_vram_mb": int(gpu * 1024), "gpu0_free_vram_gb": gpu})
    write_json(hp, hb, bom, eol, na, indent, tnl)
    loaded = json.loads(hp.read_bytes().decode("utf-8-sig" if bom else "utf-8"))
    assert isinstance(loaded["heartbeat_epoch_utc"], int), "epoch must be JSON int (R170/R178 law)"
    assert "T" in loaded["clock_read"], "clock_read must be T-sep ISO (R262 law)"
    print(f"heartbeat: epoch={loaded['heartbeat_epoch_utc']} (int OK) clock={loaded['clock_read']} "
          f"ack_missing_was={missing} cpu={cpu} ram={ram} gpu={gpu}")

    # 5) quant-level CODELY.md order-execution lines (Project section)
    qp = ROOT.parent / "CODELY.md"
    qtxt = qp.read_text(encoding="utf-8")
    ins_lines = [
        f"- [2026-09-26 {TS[-8:]}] O-20260926-2320 24h 满载淬炼令已执行回执（bm-a R277 循环轮）：COMPUTE_AUDIT v2.3 修法上链（池饿任何日历日触发+周末豁免即刻废除+selftest 13/13 含周六实弹例）+ 三票认领即开跑——T-85 s1 NAV 收割 runner 建成入池（FUSION-P1-NAV ready·64 行普查·锚门钉 t56_caliber 快照 fail-closed·selftest 15/15·autofill 下 tick 开烧=池饿红牌同轮收敛）；T-87 s1 流派枚举件 research/SCHOOL_SUPPLY_S1.md（16 行冻结面+s2 prereg 队列 5 候选）；T-86 s1 因子清单勘探回齐（正式 census runner+registry 下批）；池饿旗 v2.3 首火 span 251min 如实上报=供给面违令态，供给线已开。",
        f"- [2026-09-26 {TS[-8:]}] O-20260926-2325 全域解锁令已执行回执（bm-a R277 循环轮）：T-88 认领即开跑——s1 首切 research/DOMAIN_AUDIT.md（12 域数据面实况表+缺口清单：转债/REITs/LOF/QDII 逐域审计批、repo GC001/R-001 采集器待建=s3 载体、期权前向史<12mo 判据门未开、北交所数据面缺照登）；s2 转债首战收敛 T-60 在飞线（采集+审计先行）；RANDOM_LARGE_SAMPLE_LAW v1.0 绑定 T-85/86/87/88 全部 judged 面注记在案。",
    ]
    anchor = "### Reference"
    idx = qtxt.find(anchor)
    if idx == -1:
        qtxt = qtxt.rstrip() + "\n\n" + "\n".join(ins_lines) + "\n"
    else:
        qtxt = qtxt[:idx] + "\n".join(ins_lines) + "\n" + qtxt[idx:]
    qp.write_text(qtxt, encoding="utf-8")
    print("quant CODELY.md +2 execution lines")

    # 6) root CODELY.md pit-law line (Reference section)
    cp = ROOT / "CODELY.md"
    ctxt = cp.read_text(encoding="utf-8")
    pit = (f"- [2026-09-26 {TS[-8:]}] 坑律（bm-a R277·T-85 s1 NAV 收割 runner 建造期·r261 权源为锚族新参·E1 selftest 首跑自捕零外泄）："
           f"**票面「wired faces」≠ 面×载体全叉积——组合类收割面必须以判决件在册组合为准**（exit_overlay_p1.json stress_x2 只录接线 4 组合"
           f"C01/C02:ov_tp_ladder+C02/ENGULF:ov_full=r256 接线面；凭票面文字铺 12 组合=发明 8 个非接线面入候选池）；正律=收割面前先读判决/注册件实况取 "
           f"wired 集合（零发明）+selftest 带 reference-keys 腿首跑即捕。连带=caliber manifest 键=裸文件名（files 在 firm/traders/ 下）+hash=raw "
           f"sha256（LF 归一双门照 R253 保留防 EOL 传输翻面）。指针=scripts/fusion_p1_nav.py _wired_overlay_cells+_manifest_ok+selftest [2][4]\n")
    cidx = ctxt.find("### Reference")
    if cidx == -1:
        ctxt = ctxt.rstrip() + "\n\n" + pit
    else:
        # append at end of file keeps Reference section trailing format
        ctxt = ctxt.rstrip() + "\n" + pit
    cp.write_text(ctxt, encoding="utf-8")
    kb = os.path.getsize(cp) / 1024
    print(f"root CODELY.md +1 pit line ({kb:.1f}KB, {'OVER' if kb > 50 else 'under'} 50KB watermark)")
    print("WRAPUP OK")

if __name__ == "__main__":
    main()
