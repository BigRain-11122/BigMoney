"""r698 bm-b closeout writer: state.json round 698 + heartbeat bm-b.json +
round report append (r645 programmatic-write law, r694 absolute round-no
law, r679 marker pre/post law, R170/R178 epoch-int law, R262 T-form
clock law). Zero console CJK (r458 family)."""
import json
import os
import subprocess
import time
import datetime

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE = os.path.join(REPO, "state.json")
HB = os.path.join(REPO, "fleet", "machines", "bm-b.json")
RR = os.path.join(REPO, "logs", "iteration-loop", "round_reports.md")

now = datetime.datetime.now()
clock = now.strftime("%Y-%m-%dT%H:%M:%S") + "+08:00"
epoch = int(time.time())

NOTE = ("r698: N2-W15 judge-stage sec.9 placeholder drafted (F-04 seat "
        "MSG-2245, MSG-2215 open-invite terms) + rehearsal probe rc0 "
        "(import faces 8/8, cutoff 2026-09-22 binding, judge band derive "
        "ADMIT X=545000, ledger head 646799) + banned gate ADMIT "
        "matched=[] (r484 law); N2 screen 11/12 (my SHARD-2 RAM-gated "
        "daemon auto-ignite); S6 38/38 rc0; smoke 48/48")

CUR_TASK = ("r698 closed: N2-W15 judge sec.9 placeholder + rehearsal "
            "receipt landed (MSG-2245 F-04 seat); N2 screen 11/12, my "
            "SHARD-2 RAM-gated waiting daemon auto-ignite (trio V/Q/D to "
            "10-06T17/10-07T11/10-08); next = screen 12/12 -> bm-a "
            "finalize seat -> sec.9.1 concretize freeze (<=10-08) -> "
            "judge pool burn <=10-12; W3 judge bm-c ETA ~10-05T02:00")

VERDICT = ("healthy burning (trio NULLS three-family in flight RAM-held "
           "+ N2 SHARD-2 RAM-gated ready; judge sec.9 drafted this "
           "window; py_low_with_work_cands = legal RAM-gated window per "
           "r691 cap law)")


def ram_gb():
    try:
        import psutil
        return round(psutil.virtual_memory().available / 2**30, 1)
    except Exception:
        return None


def gpu_free_mb():
    try:
        r = subprocess.run(
            ["nvidia-smi", "--query-gpu=memory.free",
             "--format=csv,noheader,nounits"],
            capture_output=True, text=True, timeout=20)
        if r.returncode == 0 and r.stdout.strip():
            return int(float(r.stdout.strip().splitlines()[0]))
    except Exception:
        pass
    return None


def cpu_pct():
    try:
        import psutil
        return round(psutil.cpu_percent(interval=1.5), 1)
    except Exception:
        return None


def main() -> int:
    # ---- state.json (programmatic write + json.loads self-check) ----
    st = json.load(open(STATE, encoding="utf-8"))
    assert st.get("round_no") == 697, "state round_no != 697, abort"
    st["round_no"] = 698                       # absolute (r694 law)
    st["note"] = NOTE
    st["last_round_at"] = clock
    st["ts"] = clock
    st["updated"] = clock
    st["last_seen"] = clock
    st["round_no_label"] = "round 698 (bm-b)"
    st["clock_read"] = clock
    with open(STATE, "w", encoding="utf-8") as f:
        json.dump(st, f, ensure_ascii=False, indent=1)
    chk = json.load(open(STATE, encoding="utf-8"))
    assert chk["round_no"] == 698

    # ---- heartbeat (epoch int + T-form clock + json.loads self-check) ----
    hb = json.load(open(HB, encoding="utf-8"))
    assert hb.get("machine_id") == "bm-b"
    hb["last_seen"] = clock
    hb["heartbeat_epoch_utc"] = epoch
    hb["clock_read"] = clock
    hb["round_no"] = 698
    hb["round_no_label"] = "round 698 (bm-b)"
    hb["current_task"] = CUR_TASK
    hb["verdict"] = VERDICT
    hb["ts"] = clock
    hb["updated"] = clock
    hb["updated_at"] = clock
    c = cpu_pct()
    r = ram_gb()
    g = gpu_free_mb()
    if c is not None:
        hb["cpu_util_pct"] = c
    if r is not None:
        for k in ("free_ram_gb", "idle_ram_gb", "ram_free_gb",
                  "ram_avail_gb"):
            hb[k] = r
    if g is not None:
        hb["gpu_idle_vram_gb"] = round(g / 1024, 2)
        hb["gpu_idle_vram_mb"] = g
        hb["gpu_free_vram_gb"] = round(g / 1024, 2)
        hb["gpu_free_vram_mb"] = g
        hb["gpu_vram_free"] = g
        hb["gpu_free_vram_mib"] = g
        hb["gpu_free_mb"] = g
    with open(HB, "w", encoding="utf-8") as f:
        json.dump(hb, f, ensure_ascii=False, indent=1)
    chk2 = json.load(open(HB, encoding="utf-8"))
    assert isinstance(chk2["heartbeat_epoch_utc"], int), "epoch not int"
    assert "T" in chk2["clock_read"] and " " not in chk2["clock_read"], \
        "clock not T-form"

    # ---- round report append (marker pre 0 / post 1; bytes-safe) ----
    marker = "round 698 (bm-b)"
    with open(RR, "rb") as f:
        blob = f.read()
    txt = blob.decode("utf-8", errors="replace")
    n0 = txt.count(marker)
    assert n0 == 0, "marker count %d != 0 (double-append guard)" % n0
    line = (
        "2026-10-04T22:4x+08:00 | round 698 (bm-b) | "
        "watermark 绿（red=false·py_watermark verdict=py_low_with_work_cands"
        "=合法 RAM 门窗：free RAM 3.4GB<4GB floor·trio NULLS 三族在烧至 "
        "10-06T17/10-07T11/10-08T0x·N2 SHARD-2 本机 ready 候窗 daemon 自燃·"
        "CONTEST-RC bm-a 已认领候窗·r691 帽律按在飞批 ETA）"
        "｜当前活=trio NULLS 三族烧录在飞（V/Q/D）+本窗承接 N2-W15 judge 段 "
        "§9 占位起草（MSG-2215 开放条款·F-04 席位声明 MSG-2026-10-04-2245）"
        "｜最近实物=research/PERPETUAL_N2_W15_PREREG.md §9 全量判决面段冻结位"
        "追加（22:4x·T-22 caliber 判决格面+出场轴③ template_default 按设计测"
        "+|corr|≥0.999 入场塌缩门+D6 max|corr|≥0.7 拒收+N_eff 链头实读律+"
        "R250 judge 带 §9.1 冻结 commit 同窗登记律+runner slice-4 judge 三腿"
        "FREEZE-GATED 规格+§9.1 具体化四前置）+预演探针 results/"
        "_r698bmb_n2_judge_rehearsal.json rc0（import 面 8/8 True·p5c "
        "cutoff 2026-09-22 同栅 binding·FROZEN_CENSUS 形状锚恒等·judge 带位 "
        "derive ADMIT X_judge=545_000·N_eff 链头活读 646,799）+禁向闸复跑 "
        "ADMIT matched=[] 零命中（r484 律·results/_r698bmb_n2_judge_banned_"
        "gate.json）"
        "｜下个里程碑=N2 screen 12/12（现 11/12 done·bm-c SHARD-10 本窗收口"
        "·仅剩本机 SHARD-2 候 RAM 窗 10-06 晚 daemon 自燃）→bm-a finalize 席"
        "（MSG-2215）→§9.1 具体化冻结窗 ≤10-08→judge 池面烧录在飞 ≤10-12"
        "（O-2115 常设供给线·48h 窗节点=10-06T22:45 SHARD-2 点火条件就绪）"
        "｜S0=churn absorb cc2526641（8 lane 面与 origin 改动集零交集·r437 "
        "净路）+merge origin 3 commits 零 UU+push DELIVERED（push_verify "
        "tip==remote ahead=0）｜S0.5=orders 154/154 双侧同口径零未回执"
        "（r477 形态律）+D-19 双 MATCH（decisions SHA-256/orders SHA-1 双键"
        "口径·r690 血统 _r698bmb_d19_check.py）｜S1=smoke 48/48｜S2=板空"
        "（job_list 零+票板零 open）｜S3=satengine alive（RAM 门 3.0GB floor "
        "合法在位）·inbox=自机 r694 MSG-2130（收件 bm-a 归其处理零本机动作）"
        "·pool 探针=trio 三族 owner=bm-b ready 在烧+N2 11/12（r691 血统 "
        "_r698bmb_pool_status.py）｜S6=38/38 rc0（_r698bmb_s6_chain.py canon "
        "parity 38 腿·假日 collectors 全 no-op@cutoff 09-30·dualrun "
        "ZERO-DRIFT streak=7·compute_audit CLEAN burning-healthy·t35/"
        "scorecard/dashboard 四面 bm-a 心跳 stale 64min 法定 stale-takeover "
        "derive（O-2100 s2.4）·daily_report REPORT-2026-10-04 再生·"
        "live_usage LIVE-2026-10-04 再生（ORANGE）·token delta=0）"
        "｜post_review 面=✓45/✗0/🟡5 零活红｜attrition 4 台账 CLEAN"
        "（3 行历史 shrink healed 注记照录）｜自愈 4/4（loop pin=2 no-op·"
        "watchdog 重注册 first-fire 22:39·pre-commit/pre-push 双爪 LF 归一"
        "装）｜产品面=判决段规格+预演实物（探针可跑+回执三件）｜本地未达 "
        "origin commit 数=0（收口 push_verify DELIVERED 实证）\n")
    tail_ok = blob.endswith(b"\n") or blob.endswith(b"\r\n")
    with open(RR, "a", encoding="utf-8", newline="") as f:
        if not tail_ok:
            f.write("\n")
        f.write(line)
    with open(RR, "rb") as f:
        n1 = f.read().decode("utf-8", errors="replace").count(marker)
    assert n1 == 1, "marker count %d != 1 after append" % n1
    print("CLOSEOUT OK state=698 epoch=%d clock=%s marker=1" % (
        epoch, clock))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
