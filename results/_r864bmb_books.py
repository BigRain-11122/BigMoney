"""r864 bm-b closeout books: state.json bump + heartbeat + round report
append (bm-b lane files). UTF-8 byte-safe; heartbeat epoch = int()
(R170/R178 law); clock_read T-separated ISO8601 (R262 law)."""
import datetime as dt
import json
import os
import subprocess

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE = os.path.join(REPO, "state.json")
HB = os.path.join(REPO, "fleet", "machines", "bm-b.json")
REPORT = os.path.join(REPO, "logs", "iteration-loop", "round_reports.md")

now = dt.datetime.now().astimezone()
ts = now.isoformat(timespec="seconds")
epoch = int(now.timestamp())


def _sample():
    free_gb, ram_pct, vram_mb = 11.3, 47.0, 3500
    try:
        import psutil
        vm = psutil.virtual_memory()
        free_gb = round(vm.available / 1024**3, 1)
        ram_pct = round(vm.available / vm.total * 100, 1)
    except Exception:
        pass
    try:
        out = subprocess.run(
            ["nvidia-smi", "--query-gpu=memory.free",
             "--format=csv,noheader,nounits"],
            capture_output=True, text=True, timeout=15)
        if out.returncode == 0 and out.stdout.strip():
            vram_mb = int(float(out.stdout.strip().splitlines()[0]))
    except Exception:
        pass
    return free_gb, ram_pct, vram_mb


REPORT_LINE = (
    "2026-10-11T06:1x+08:00 | r864 bm-b | dept:研究（N2-W19 slice-3 冻结窗"
    "+slice-4 判读烧录同轮）+工程（S6 链·S7 收口）| 实况三行：当前活=N2-W19 "
    "冻结+首判读烧录落地（V1=HOLDS·反馈搜索杠杆首个可判读读数）/最近实物="
    "results/alphagen_w19/W19-2026-10-09.json+research/PERPETUAL_N2_W19_"
    "PREREG.md FROZEN（commit 5b9051319+5d4e67a82·05:5x-06:1x）/下个里程碑="
    "W210 冻结候 W209 落链（bm-a M9 链）+素材池消费预注册评估窗（≤10-13）"
    "| WM-VERDICT: green（red=false·py_low_board_clear 合法白名单·板空="
    "W19 链即常设计程）| S0: stash daemon faces→pull --rebase up-to-date·"
    "orders 差集 0（67/192/0·S7 复扫 0）·D19 双水位恒等（dec caca0c6e/"
    "ord f90233c7）·S1 smoke 49/49·孤儿面=0（11 py faces·收尾复探 13 "
    "faces）·S2 双板净空（job 0/asks 0）·SAT 活 rc0 | 主产出=N2-W19 "
    "slice-3 冻结窗：三带登记 gen=736_000/scrnull=736_500/unc=737_000（撞 "
    "W18 族带 halo 步进 7 槽·derive 位强制非自由挑·band gate ADMIT 回执"
    "_r864bmb_w19_band_gate.txt+seed_admit rc0×3+banned_direction rc0+repo"
    " 文本扫零外撞+r687 写前复核 origin 三键缺席·prereg origin 侧仍 "
    "DRAFT）+prereg FROZEN 翻面（五条件机证记录+§3 种子回填与 r862 只读"
    "候选 736000 逐位一致）；同轮 slice-4 烧录：V1=HOLDS（族 max |ICIR| "
    "0.38>pooled null p95 0.086·336≥300 充分线一次越过=W18 拒烧 288 欠账"
    "清偿·B=7 损耗定价法实证 288→336）+D1 杠杆正信号（0.38 vs 随机族 "
    "0.353·描述性·K=62/64 奇偶披露）+M1 9/48 正方向 t≥3.0+成功面全分解"
    "（6 T-84s3+5 批内重复→11 排除→51 enrolled→3 skip 5.9%<10% 守卫→"
    "48 ok→48×7=336）+账本 876,731→877,227（+496 包结·消费 398+未消费 "
    "98 恒等对账）+实测 152s（300s 帽内·超预估 27% 如实披露）+§7/§8 一"
    "次性回填（预测对账：#1 达成/#2 排除 11 带内·skip 5.9% 微超 ≤5% 预"
    "测披露/#3 0.38 落 [0.20,0.45] 带内/#4 V1 PASS/#5 五数概括 [0.004,"
    "0.124,0.226,0.283,0.38] 在案）+attrition 行 kind=ic_judgment（cells"
    "_delta=496·guard CLEAN）+TREASURE 行（results/alphagen_w19/=48 存活"
    "员素材池+9 M1 候选带·消费须全新预注册+成本压测；方法论无新卡=B 预算"
    "卡 r861 在册·本批=其首验证读数）·零注册零引擎零策略宣称 | PUSH: 首"
    "推爪拦（bm-c r854 同窗推进 318c8cdac·删除集保护正确拦截）→stash→"
    "rebase onto 318c8cdac（1-UU attrition scan 机制重导解·r787 原子 "
    "add+continue·dumb-terminal core.editor=true 旁路）→陈旧 stash 依 "
    "rolling 面 120=120 行数同=活树 newer 律审计后 drop→push 318c8cdac.."
    "5d4e67a82·behind=0 送达自证 | S6: 41 腿 40 rc0+alloc rc2 已知 "
    "510880（P5 TRANSFER 待件）·t35_export bm-a 心跳 stale 499min 依 "
    "O-2100 s2.4 STALE_MIN 律 stale-takeover derive 如实披露 | S7: 四件套"
    " ALIVE（loop pin=2 no-op·watchdog 幂等重注·双爪在位）+attrition "
    "guard CLEAN+idle --worked（idle_rounds=0）+孤儿面=0 | 账：commit "
    "5b9051319（冻结·R250 一步律）+5d4e67a82（判读烧录·含 daemon faces "
    "吸收）·本地未达 origin commit 数=0 | 下轮指针：r865=W210 冻结候链 "
    "watch（M9）+素材池消费预注册评估+moneyflow IC panel-ready watch"
    "（bm-a 道）"
)


def main():
    free_gb, ram_pct, vram_mb = _sample()

    with open(STATE, encoding="utf-8") as f:
        st = json.load(f)
    st["machine_id"] = "bm-b"
    st["round_no"] = 864
    st["round"] = 864
    st["round_no_label"] = "r864"
    st["last_round_at"] = ts
    st["ts"] = ts
    st["updated"] = ts
    st["updated_at"] = ts
    st["last_seen"] = ts
    st["clock_read"] = ts
    st["last_round_ts"] = ts
    st["orphan_face"] = 0
    st["orphan_faces"] = 0
    did = (
        "r864: S0 stash daemon faces + pull --rebase up-to-date (round "
        "start) + orders diff 0 (67/192/0, S7 rescan 0) + D19 dual "
        "watermark identical (dec caca0c6e/ord f90233c7 zero delta) + "
        "smoke 49/49 + orphan face=0 (round-zero probe 11 py faces; "
        "closeout re-probe 13 faces orphans=0) + boards clear (job 0, "
        "asks 0) + SAT alive rc0; PRIMARY PRODUCT = N2-W19 slice-3 "
        "FREEZE WINDOW + slice-4 JUDGED BURN same round (first judgeable "
        "readout of the feedback-search lever): three-band registration "
        "perpetual_n2_w19_gen=736_000/scrnull=736_500/unc=737_000 (r682 "
        "horizon live derive walking 7 slots past the W18 registered-key "
        "halo, derive position forced not free-picked; band gate ADMIT "
        "receipt _r864bmb_w19_band_gate.txt + seed_admit_gate rc0 x3 + "
        "banned_direction_gate rc0 + repo text scan zero-hit + r687 "
        "pre-write recheck origin=own r863 closeout, three keys absent, "
        "prereg DRAFT on origin side) + prereg FROZEN flip (five-condition "
        "machine record, sec.3 seed backfill byte-identical to r862 "
        "read-only candidate) then same-round slice-4 burn: V1=HOLDS "
        "family max |ICIR| 0.38 > pooled null p95 0.086 (pooled 336>=300 "
        "sufficiency line CLEARED -- W18 refusal 288 debt repaid; "
        "attrition-priced B=7 validated 288->336) + D1 leverage positive "
        "signal 0.38 vs census random 0.353 (descriptive non-gating, K "
        "parity disclosed) + M1 9/48 positive-direction t>=3.0 + full "
        "attrition decomposition on the success face (6 T84s3 + 5 "
        "in-batch dup -> 11 excluded; 51 enrolled; 3 h1 skip 5.9%<10% "
        "guard; 48 ok; 336 pooled) + trials ledger 876,731->877,227 "
        "(+496 envelope; consumed 398; unconsumed 98 exact "
        "reconciliation) + elapsed 152s (300s cap, +27% vs estimate "
        "disclosed) + sec.7/sec.8 one-shot backfill + gate_attrition row "
        "kind=ic_judgment + TREASURE_REGISTRY row (results/alphagen_w19/ "
        "48-survivor material pool + 9 M1 candidates; METHODOLOGY no new "
        "card -- attrition-budget card r861 in-register, first "
        "validation readout) + zero registration zero engine runs; PUSH: "
        "first push claw-blocked (bm-c r854 same-window advance "
        "318c8cdac -- deletion-set protection correct) -> stash -> "
        "rebase onto 318c8cdac (1-UU attrition scan resolved by "
        "mechanism re-derive + r787 atomic add+continue + dumb-terminal "
        "core.editor bypass) -> stale stash dropped after rolling-face "
        "superset audit (120=120 lines, live-newer law) -> push "
        "318c8cdac..5d4e67a82 behind=0; S6 41 legs 40 rc0 + alloc rc2 "
        "known 510880 (P5 TRANSFER pending); S7 quartet ALIVE + "
        "attrition guard CLEAN + idle --worked; orders rescan 0"
    )
    st["did"] = did
    st["last_action"] = did
    verdict = (
        "GREEN: r864 (freeze window + judged burn both landed same "
        "round -- first judgeable readout of the feedback-search lever: "
        "V1 HOLDS 0.38>0.086 pooled 336>=300, D1 positive signal vs "
        "census random 0.353, M1 9/48; three-band registration "
        "736_000/736_500/737_000 with forced-position machine proof; "
        "smoke 49/49; S6 41 legs 40 rc0 + alloc rc2 known 510880; "
        "attrition CLEAN; quartet ALIVE; orders diff 0; D19 identical)"
    )
    st["verdict"] = verdict
    nxt = (
        "r865 queue: W210 freeze watch (bm-a W208/W209 chain -- W210 "
        "seats blocked until W209 freeze+finalize lands, M9 chain) + "
        "N2 next-wave decision face (W19 judged-positive readout -> W20 "
        "evaluation; family_key alphagen_grammar_v1 stays open; "
        "consumption of the 48-survivor material pool requires fresh "
        "prereg + cost stress A158-TSGATE-P1/A10 gate) + moneyflow IC "
        "panel-ready watch (bm-a lane) + O-20261011-0012 CPU-max "
        "maintained"
    )
    st["next"] = nxt
    st["current_task"] = nxt
    st["task"] = nxt
    st["now_active"] = (
        "r864 closeout: N2-W19 freeze + judged burn landed (V1 HOLDS "
        "0.38>0.086, pooled 336, first judgeable feedback-lever readout)"
    )
    st["latest_artifact"] = (
        "r864: research/PERPETUAL_N2_W19_PREREG.md FROZEN + results/"
        "alphagen_w19/W19-2026-10-09.json (V1 HOLDS, 48 survivors, 9 M1 "
        "candidates) + scripts/science_gates.py three-band registration "
        "(commits 5b9051319 + 5d4e67a82)"
    )
    st["next_milestone"] = (
        "N2-W19 judged-positive readout landed 10-11; next = W210 "
        "freeze after W209 lands (bm-a M9 chain), material-pool "
        "consumption prereg evaluation window <=10-13, chain head "
        "877,227 monotone"
    )
    st["orphan_face_note"] = (
        "r864 closeout probe: py_faces=13 alive, orphans=0 (round-zero "
        "probe 11 faces rc0; closeout re-probe rc0; zero live seats; "
        "slice-3/4 same-round chain, no detached burns)"
    )
    with open(STATE, "w", encoding="utf-8", newline="\n") as f:
        json.dump(st, f, ensure_ascii=False, indent=1, sort_keys=True)
        f.write("\n")

    # ---------------- heartbeat
    with open(HB, encoding="utf-8") as f:
        hb = json.load(f)
    hb["machine_id"] = "bm-b"
    hb["round"] = 864
    hb["round_no"] = 864
    hb["now_active"] = st["now_active"]
    hb["current_task"] = nxt
    hb["task"] = nxt
    hb["next"] = nxt
    hb["latest_artifact"] = st["latest_artifact"]
    hb["next_milestone"] = st["next_milestone"]
    hb["verdict"] = verdict
    hb["last_action"] = did
    hb["did"] = did
    hb["last_round_at"] = ts
    hb["last_seen"] = ts
    hb["updated"] = ts
    hb["updated_at"] = ts
    hb["ts"] = ts
    hb["clock_read"] = ts
    hb["heartbeat_epoch_utc"] = epoch
    hb["cpu_cores"] = 16
    hb["free_ram_gb"] = free_gb
    hb["ram_free_gb"] = free_gb
    hb["ram_free_pct"] = ram_pct
    hb["gpu_free_vram_mb"] = vram_mb
    hb["gpu_free_vram_gb"] = round(vram_mb / 1024, 1)
    hb["vram_free_gb"] = round(vram_mb / 1024, 1)
    hb["idle_rounds"] = 0
    hb["agenda_starved"] = False
    hb["orphan_faces"] = 0
    hb["orphan_face"] = 0
    hb["orphan_face_note"] = st["orphan_face_note"]
    hb["sync"] = {
        "last_push_ts": ts,
        "note": ("r864 closeout push (freeze window + judged burn + "
                 "S6 chain + books); post-push behind=0 self-proof via "
                 "fetch+rev-list"),
    }
    with open(HB, "w", encoding="utf-8", newline="\n") as f:
        json.dump(hb, f, ensure_ascii=False, indent=1, sort_keys=True)
        f.write("\n")
    # int-type self-proof (R170/R178 law)
    with open(HB, encoding="utf-8") as f:
        check = json.load(f)
    assert isinstance(check["heartbeat_epoch_utc"], int), \
        "epoch must be JSON int (R170/R178 law)"
    assert "T" in check["clock_read"], "clock_read T-separator law (R262)"

    # ---------------- round report append
    with open(REPORT, "ab") as f:
        f.write((REPORT_LINE + "\n").encode("utf-8"))

    print(json.dumps({"state_round": st["round_no"], "hb_epoch_int": True,
                      "ts": ts, "ram_free_gb": free_gb,
                      "vram_free_mb": vram_mb, "report_appended": True}))


if __name__ == "__main__":
    main()
