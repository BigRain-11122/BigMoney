# r586 bm-b: CODELY lesson append + targeted add + commit + push (r580 python-argv law, r375 -F law)
import subprocess, sys, os

LESSON = ("- [2026-10-02 18:0x r586 bm-b] 外科/FF 收口 commit 的 file-move 落盘滞后=D+?? 同名对伪影坑（W106 seat MSG 位移实弹）："
          "r585 收轮把 W106 seat 移入 processed/ 的 git 移动（D+新增）随 commit 推送、物理文件滞留 inbox/ 未同步落盘"
          "→本轮 S0 reset --mixed 后 status 见「processed/ D + inbox/ ??」同名对，近误判车道反向操作。治愈三步="
          "git hash-object 本地件 vs origin blob 恒等证明（双 e157a48e）→checkout 还原正主位→删 untracked 副本"
          "（恒等=零信息损失收口）。How to apply：外科/FF 收口序列 commit 后必核 file-move 面盘同步（commit 的移动必须物理发生）；"
          "下轮见 D+?? 同名对先做 blob 恒等证明再定性，禁按状态面猜车道行为。")

with open("CODELY.md", "ab") as f:
    f.write(b"\r\n" + LESSON.encode("utf-8"))
print("CODELY lesson appended")

PAYLOAD = [
    "CODELY.md", "state.json", "fleet/machines/bm-b.json", "logs/iteration-loop/round_reports.md",
    "docs/daily_report/REPORT-2026-10-02.json", "docs/daily_report/REPORT-2026-10-02.md",
    "docs/live_usage/LIVE-2026-10-02.json", "docs/live_usage/LIVE-2026-10-02.md",
    "docs/live_usage/LIVE-latest.json", "docs/live_usage/LIVE-latest.md",
    "results/astock_daily_update_status.json", "results/autofill_state.bm-b.json",
    "results/compute_audit.bm-b.json", "results/compute_audit.json",
    "results/etf_daily_pull_status.json", "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.bm-b.json", "results/futures_update_status.json",
    "results/lhb_update_status.bm-b.json", "results/lhb_update_status.json",
    "results/minute_feed_status.bm-b.json", "results/minute_feed_status.json",
    "results/p1d_gates.json", "results/pool_core_samples.jsonl", "results/pool_dualrun.bm-b.jsonl",
    "results/regime_state.bm-b.json", "results/regime_state.json",
    "results/saturation_engine/face_bm-b.json", "results/saturation_engine/history_bm-b.jsonl",
    "results/saturation_engine/ledger_bm-b.jsonl", "results/saturation_engine/state_bm-b.json",
    "results/token_usage.bm-b.json", "results/token_usage.json",
    "results/update_status.bm-b.json", "results/update_status.json",
    "results/_attrition_guard_scan.json",
    "results/_r585bmb_final_push.py", "results/_r586bmb_s0_checkout.py",
    "results/_r586bmb_s6_chain.json", "results/_r586bmb_s6_runner.py", "results/_r586bmb_close.py",
    "results/p2cal_ext/n1_w106/",
]
r = subprocess.run(["git", "add", "--"] + PAYLOAD, capture_output=True, text=True)
print("add rc=", r.returncode, r.stderr[:300] if r.returncode else "")
if r.returncode:
    sys.exit(1)

MSG = ("round 586 bm-b: W106 burn products 12/12 delivered to origin (2,200 backtests, workers=8, 96th engine wave; "
       "engine ledger 12 rows + faces + pool_core_samples +12 union ride) + S0 pure-FF surgical integration "
       "(e77cad0bb->e79dcf6b4: bm-c r377 wrap x2 + bm-a r587 wrap adopted, 55 shared/other-machine faces "
       "checkout-restored, bm-b live-writers kept, W106 seat MSG displacement healed via blob-identity proof) + "
       "W14 governance-park verified per r483 verdict (entry park honored r527 law, N2-W15 same-grammar hold, "
       "zero action) + S6 33 legs rc0 (dualrun ZERO-DRIFT 30/3, REPORT/LIVE-2026-10-02 regenerated, host-guarded "
       "faces honest skip) + WM py_low_board_clear legal idle + S7 self-heal 5/5 (loop pin=2, watchdog, claws, "
       "attrition CLEAN) + CODELY r586 lesson (file-move disk-lag D+?? artifact) + state/heartbeat r586 "
       "[via bm-b r586]")
mp = r"..\..\.codely-cli\scratch\r586bmb_msg.txt"
os.makedirs(os.path.dirname(mp), exist_ok=True)
open(mp, "w", encoding="utf-8", newline="\n").write(MSG)
r = subprocess.run(["git", "commit", "-F", mp], capture_output=True, text=True)
print("commit rc=", r.returncode)
print((r.stdout or r.stderr)[:400])
if r.returncode:
    sys.exit(1)

r = subprocess.run(["git", "push"], capture_output=True, text=True)
print("push rc=", r.returncode)
print((r.stdout or r.stderr)[:400])
