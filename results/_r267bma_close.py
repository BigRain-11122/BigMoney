"""R267 bm-a closeout: state-bm-a.json + heartbeat + round-report line append.

Face-mirror law R254/R255/R257 (BOM/EOL/indent/ensure_ascii/trailing-newline probed from
HEAD blobs; all three targets = LF, indent=1, no BOM, no trailing newline, ASCII-safe).
Round report EOL probed from the file itself (R209 mirror-the-producer).
"""
import json, subprocess, time, datetime

ROOT = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"


def git_bytes(path):
    return subprocess.run(["git", "show", "HEAD:" + path], capture_output=True, cwd=ROOT).stdout


def dump_face(obj):
    return json.dumps(obj, indent=1).encode()


# ---- state-bm-a.json -------------------------------------------------------
state = {
    "round_no": 267,
    "did": "R267 maintenance round (board empty + all queues closed + real payload externally blocked): S0 up-to-date, S6 full chain exit 0, post_review re-derive 29 YES/0 NO/5 WAIT, no fabricated batch per O-1137",
    "verdict": "R267: watermark green (red=false lane=healthy; audit pool_starvation flag = same O-1137 legal-idle adjudication as R266: weekend no-new-bar, board 0 open + bandit 0 + pool 49/49 done, MF_IC_P1 awaits moneyflow panel 53/5222 source-blocked self-heal); smoke 25/25; post_review zero NO",
    "next": "(1) 09-28 Monday new-bar chain (cutoff 09-24); (2) MF_IC_P1 IC batch when moneyflow panel completes (bm-a lane, source-block self-heal); (3) 10-01 monthly trio + REGIME_GUARD v3 date gate (governance slot discharged, no double-run); (4) R270 5x HANDOVER recon",
    "ts": "2026-09-26 20:05",
    "last_round_ts": "2026-09-26 20:05",
    "updated_at": "2026-09-26 20:05",
    "current_task": "R267 closed (maintenance round)",
    "last_run": "2026-09-26 20:05",
    "last_round_at": "2026-09-26 20:05",
    "last_round": 267,
    "updated": "2026-09-26 20:05",
}
prev_keys = list(json.loads(git_bytes("state-bm-a.json").decode("utf-8")).keys())
assert list(state.keys()) == prev_keys, ("state key order drift", prev_keys)
b = dump_face(state)
assert not b.endswith(b"\n") and b"\r" not in b
open(ROOT + r"\state-bm-a.json", "wb").write(b)
rt = json.loads(open(ROOT + r"\state-bm-a.json", "rb").read().decode("utf-8"))
assert rt["round_no"] == 267 and isinstance(rt["round_no"], int)

# ---- fleet/machines/bm-a.json (heartbeat) ----------------------------------
hb_path = ROOT + r"\fleet\machines\bm-a.json"
hb = json.load(open(hb_path, encoding="utf-8"))
hb["last_seen"] = "2026-09-26 20:05"
hb["current_task"] = "R267 closed (maintenance round: S6 full chain exit 0, board empty, MF_IC_P1 awaiting panel)"
hb["cpu_pct"] = 10.7
hb["free_ram_gb"] = 56.9
hb["gpu_free_vram_gb"] = 5.6
hb["verdict"] = ("GREEN R267: maintenance round -- S6 ~28 legs all exit 0 (weekend no-ops cutoff 09-24, regime ORANGE "
                 "shadow, clock ORANGE_COOL 4/0), post_review 29 YES/0 NO/5 WAIT, pool 49/49 done, audit "
                 "pool_starvation = O-1137 legal-idle (board/bandit/pool all closed; MF_IC_P1 awaiting moneyflow panel "
                 "53/5222 source-blocked)")
hb["heartbeat_epoch_utc"] = int(time.time())
assert isinstance(hb["heartbeat_epoch_utc"], int)
hb["clock_read"] = datetime.datetime.now().astimezone().isoformat()
assert "T" in hb["clock_read"] and "+" in hb["clock_read"]
hb["cores"] = 32
hb["gpu_free_vram_mb"] = 5762.0
hb["gpu_idle_vram_gb"] = 5.6
hb["task"] = ("R267 done: maintenance closure verification; next = 09-28 Mon new-bar chain (cutoff 09-24), "
              "MF_IC_P1 on panel completion, 10-01 monthly trio + REGIME_GUARD v3 date gate, R270 5x HANDOVER")
hb["free_ram_mb"] = 58265
hb["gpu"] = {"present": True, "idle_vram_free_gb": 5.6, "note": "nvidia-smi: 12282 MiB total - 6520 used = 5762 free"}
hb["round_no"] = 267
hb["gpu_idle_vram_mb"] = 5762
hb["gpu_total_vram_mb"] = 12282.0
hb["idle_ram_gb"] = 56.9
hb["gpu0_free_vram_gb"] = 5.6
b = dump_face(hb)
assert not b.endswith(b"\n") and b"\r" not in b and b[:3] != b"\xef\xbb\xbf"
open(hb_path, "wb").write(b)
chk = json.loads(open(hb_path, "rb").read().decode("utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int) and not isinstance(chk["heartbeat_epoch_utc"], bool)
assert "T" in chk["clock_read"]
print("state+hb written; epoch:", chk["heartbeat_epoch_utc"], "clock:", chk["clock_read"])

# ---- round report line append (EOL probed) ---------------------------------
rp_path = ROOT + r"\logs\iteration-loop\round_reports-bm-a.md"
raw = open(rp_path, "rb").read()
eol = b"\r\n" if b"\r\n" in raw[-200:] else b"\n"
tail_nl = raw.endswith(b"\n")
line = (
    "2026-09-26 20:07 | R267 bm-a | (dept:工程/舰队) 水位=绿（19:50 probe red=false lane=healthy；20:02 复测 verdict="
    "insufficient_history n=2 span 14.8min 诚实短窗；审计旗 pool_starvation 60min=R266 同面 O-1137 legal-idle 白名单"
    "裁决如实呈：周末无新 bar、板 0 open、bandit 0、池 49/49 done、零可跑候选，唯一真载体=MF_IC_P1 待 moneyflow "
    "面板 53/5222 源阻断自愈——禁造数凑烧恒在）。did: S0 stash→pull-rebase→pop 零新 commit（up to date）；S0.5 "
    "orders 83/83 差集空（正典工具双扫）+decisions 尾行 D-20260926-11=R265 回执边界零新行；S1 smoke 25/25；S2 "
    "job_list 空+板 0 open（30 票全 claimed：bm-a 12/bm-b 15/bm-c 3，T-76 全 faces 闭环待 GM 裁量、T-73 科学面 "
    "R264 全闭、T-83 余 s3=GM 保留面）+inbox 0 未读；S3=维护性闭环核查（board 空+全队列闭环：town.html v5 八部门"
    "对齐已在位实证 drawAlloc L224、Optuna 仍 gated（在册 validated<8 冻结判据未触发）、PLAN 未勾项全 P1-gated/"
    "物理依赖/已被治理取代——无合法可开活，遵 no-fabrication 不造工）；S6 ~28 legs ALL exit 0（周末 no-op 族："
    "daily 0 rows cutoff 09-24、regime ORANGE d2 shadow（hs300<MA200+breadth 0.77）、clock CALL-2026-09-24 "
    "ORANGE_COOL sleeves 4/0 幂等、lhb 30min 节流、heat 周末、futures+options cutoff 覆盖零网络、moneyflow "
    "rank-spawn 节流 14.7min<30min、sina_mf/ths 当日幂等、AH spawn 节流 14min+面板未完备自愈中、fund_premium "
    "bm-c 车道诚实 no-op、fundamental 22.6h 新鲜跳过、b_layer 5222 掩码全门过、promotion gate 0/22 eligible "
    "诚实、aggr/grid/alloc marks no-op、export 18 pos equity 5,996,645 幂等、scorecard 6/28/7、daily_report "
    "faces=4、build_status 432combos、token delta=0）+周六无新 bar→live.paper/t35v/t24-paper 条件腿合法跳过；"
    "月度三件套非月首轮（10-01 下窗）；产品再生后复审按 r270 序律 re-derive=29 YES/0 NO/5 WAIT 零 ✗；S7 "
    "schtasks R49 法双任务在册（IterationLoop Running next 20:08 + Watchdog Ready next 20:20）｜evidence: S6 exit "
    "codes 28x0 in transcript + smoke 25/25 + post_review.jsonl 本轮 run 行 + commit（本轮）｜next: (1) 09-28 "
    "周一新 bar 链（cutoff 09-24：daily→live.paper REGIME_GUARD v3 enforce→t35v→t24×2→aggr/grid marks→export→"
    "scorecard→daily_report）；(2) MF_IC_P1 面板完备后 IC 参考批（bm-a 车道）；(3) 10-01 月首轮三件套+REGIME_GUARD "
    "v3 日期门（治理审视槽位已 discharge 勿双跑）；(4) R270 5x HANDOVER 核对"
)
with open(rp_path, "ab") as f:
    if not tail_nl:
        f.write(eol)
    f.write(line.encode("utf-8") + eol)
print("round report line appended, eol=", eol, "tail_nl_was=", tail_nl)
