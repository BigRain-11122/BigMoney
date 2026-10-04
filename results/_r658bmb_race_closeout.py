import json, os, time
from datetime import datetime

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
now = time.time()
epoch = int(now)
clock = datetime.now().astimezone().isoformat(timespec="seconds")

# --- 1. round report supplement (bytes mode, r641 law) ---
rr = os.path.join(R, "logs", "iteration-loop", "round_reports.md")
line = (
    clock + " | round 658 supplement (bm-b) | dept:工程/舰队 轮中push-race收口: 首推撞拒(origin=bm-c r455波13 UU共享再生成面)→rebase撞13 UU按r652配方解(12面honest-ts take-mine 08:45-46>08:39-41+compute_audit行级union 212+201→213零丢失双侧100%contained+reparse与marker守卫全PASS·resolver=results/_r658bmb_merge_resolve.py)→rebase --continue零unmerged假拒绝(r501①净路commit -C原sha落位+r501③--quit+update-ref+checkout)→二推撞pre-push爪真拦截(删除集含_r665bma_merge_resolve.py: origin竞速再前移bm-a r666收据波6a12cf83b而我tip基于旧基座227b3a6b3=爪达成设计目的零--no-verify)→三段absorb(rebase净窗)+净rebase(5 picks零冲突)→push DELIVERED 6a12cf83b..37c193d13 push_verify三证tip==remote ahead=0 behind=0; 附记: S0 churn-absorb commit误标r668应r658(如实留痕不改史); 爪与钳本轮共真拦2次均按律处置零逃生口 | 证据=_r658bmb_merge_resolve.txt+_r658bmb_uu_probe2.py+push_verify DELIVERED行 | 本地未达origin commit数=0 | token零云端\n"
)
with open(rr, "ab") as f:
    f.write(line.encode("utf-8"))
print("round_report supplement appended")

# --- 2. state.json note addendum (programmatic write + self-verify) ---
sp = os.path.join(R, "state.json")
st = json.loads(open(sp, "rb").read().decode("utf-8"))
st["note"] = (st["note"] + " | SUPPLEMENT: mid-round push-race closeout -- 1st push rejected (bm-c r455 wave 13 UU regen faces), "
              "rebase resolved per r652 recipes (12 honest-ts take-mine + compute_audit row-union 212+201->213 zero-loss both-sides-contained, "
              "reparse+marker guards PASS), rebase --continue false-refusal per r501 netpath (commit -C original sha + --quit + update-ref + checkout), "
              "2nd push pre-push claw REAL catch (deletion set _r665bma_merge_resolve.py vs racing origin bm-a r666 wave 6a12cf83b -- my tip was based on stale base 227b3a6b3; "
              "no --no-verify), 3rd window absorb + clean rebase (5 picks) + push DELIVERED 6a12cf83b..37c193d13 (push_verify tip==remote ahead=0 behind=0); "
              "honest note: S0 churn-absorb commit msg mislabeled r668 should-be r658 (history kept)")
st["ts"] = clock
st["updated"] = clock
st["last_seen"] = clock
st["clock_read"] = clock
with open(sp, "w", encoding="utf-8") as f:
    json.dump(st, f, indent=1, ensure_ascii=False)
print("state addendum written")

# --- 3. heartbeat truth-sync (programmatic + int-epoch self-verify) ---
hp = os.path.join(R, "fleet", "machines", "bm-b.json")
hb = json.loads(open(hp, "rb").read().decode("utf-8"))
hb["last_seen"] = clock
hb["heartbeat_epoch_utc"] = epoch
hb["clock_read"] = clock
hb["current_task"] = ("当前活: FUND trio NULLS burn V661/D363/Q504 of 2000 each, pids 34396/57116/30208 alive | "
                      "最近实物: r658 mid-round push-race closeout DELIVERED 6a12cf83b..37c193d13 (13 UU r652 recipes, claw 2 real catches, push_verify ahead=0) + "
                      "finalize readiness gates all-3 REFUSED rc3 healthy + REPORT/LIVE-2026-10-04 refreshed | "
                      "下个里程碑: trio mechanical_ready -> finalize+E1 verdict batch, window 10-05..10-09, ETA ~10-05 late night..10-06 (within 48h)")
hb["verdict"] = ("GREEN (smoke 48/48; orders delta zero 153/153; D-19 double MATCH; WM red=false; engine alive rc0 idle; "
                 "S6 34 legs rc0 fail=0 dualrun streak 50; trio advancing pids alive, finalize gates verified REFUSED rc3 healthy; "
                 "mid-round push-race closeout DELIVERED 37c193d13 ahead=0 behind=0, claws 2 real catches handled zero escape-hatch; "
                 "attrition CLEAN; zero cloud token)")
hb["ts"] = clock
hb["updated"] = clock
with open(hp, "w", encoding="utf-8") as f:
    json.dump(hb, f, indent=1, ensure_ascii=False)
print("heartbeat truth-sync written")

# --- 4. self-verify ---
for p, key in [(sp, None), (hp, "heartbeat_epoch_utc")]:
    d = json.loads(open(p, "rb").read().decode("utf-8"))
    if key:
        assert isinstance(d[key], int), "epoch not int"
    assert "T" in d["clock_read"] and " " not in d["clock_read"], "clock not T-separated"
print("SELF-VERIFY PASS: both files parse, epoch int, clock T-separated")
