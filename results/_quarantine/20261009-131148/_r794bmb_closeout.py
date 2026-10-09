# r794 bm-b closeout: CODELY pit append + METHODOLOGY E40 card + round ledger line + state.json + heartbeat.
# All appends UTF-8; size gates: CODELY.md <= 30720B (D-20261002-06); epoch must be JSON int (R170/R178).
import json, time, sys

NOW = time.strftime("%Y-%m-%dT%H:%M:%S+08:00")
NOW_SHORT = time.strftime("%Y-%m-%d %H:%M")
EPOCH = int(time.time())

# ---------- 1. CODELY.md pit entry ----------
PIT = ("- [2026-10-07 04:2x r794 bm-b] **rebase 冲突窗内联 `git add -u` 循环重试 pull=冲突标记整批 staged 污染面"
       "（r804 前兆·17 面当场拦截零 origin 伤害）**：PS foreach{add -u; commit; pull} 重试器在冲突窗第一轮即把带 "
       "`<<<<<<<` 的 worktree 面 staged 且清空 ls-files -u（status 假示 all conflicts fixed）——rebase --continue 即 r804 "
       "污染入 origin 复现。正法：①rebase 冲突窗禁 add -u 循环重试（收口前只定向 add 已解析路径）；②已污染恢复通道="
       "stage2 用 git show HEAD:<path>（重放基座 ours）+stage3 用 git show <被 pick commit>:<path>（theirs）重建双侧 blob，"
       "按配方解析写净面→定向 add+add -u 吸收 daemon 活写→continue 同一 shell（r787）；③checkout -m 不可复冲突（stage 条目已清）。"
       "c3 接管 resolver 17 面 deep-ts newer-wins（tie->stage2 r140）+compute_audit/regime_state (ts,machine) values-union，"
       "receipt _r794bmb_c3_runs.jsonl；daemon 面 c2 联跑 receipt _r794bmb_c2_runs.jsonl。"
       "How to apply：rebase 停在 pick 先 ls-files -u 照单解析（c2 范式）；若 status 无 UU 而 continue 未跑=已污染，走②通道。\n")
with open("CODELY.md", "r", encoding="utf-8", newline="") as fh:
    body = fh.read()
if "r794 bm-b] **rebase 冲突窗内联" not in body:
    if not body.endswith("\n"):
        body += "\n"
    body += PIT
with open("CODELY.md", "w", encoding="utf-8", newline="") as fh:
    fh.write(body)
sz = len(body.encode("utf-8"))
assert sz <= 30720, "CODELY.md cap breach %d" % sz
print("CODELY=%dB cap-ok" % sz)

# ---------- 2. METHODOLOGY_ASSETS.md E40 ----------
CARD = ("- **E40 rebase 冲突窗 add -u 污染后双侧 stage blob 重建通道（c3 takeover resolver）**：proven（r794 bm-b 实弹 17 面）——"
        "add -u 清空 ls-files -u 后 stage2=git show HEAD:<path>、stage3=git show <被 pick commit>:<path> 重建，deep-ts "
        "newer-wins（tie->stage2 r140）+rolling-ledger (ts,machine) values-union，写净面→定向 add+add -u 吸收 daemon 活写→"
        "continue 同 shell（r787）零丢失收口；receipt _r794bmb_c3_runs.jsonl + c2 daemon-face 联跑复用（_r794bmb_resolve_c2.py）；"
        "预防律=rebase 冲突窗禁 add -u 循环重试 pull（第一轮即污染）。\n"
        "- 2026-10-07 04:2x（bm-b r794）：S0 落地手术窗捕获律 O-20261002-2100 收口步 append E40 资产卡——r804 前兆 17 面当场拦截零 origin 伤害 live 实证。\n")
with open("knowledge/METHODOLOGY_ASSETS.md", "r", encoding="utf-8", newline="") as fh:
    mbody = fh.read()
if "E40 rebase 冲突窗 add -u 污染后" not in mbody:
    if not mbody.endswith("\n"):
        mbody += "\n"
    mbody += CARD
with open("knowledge/METHODOLOGY_ASSETS.md", "w", encoding="utf-8", newline="") as fh:
    fh.write(mbody)
print("METHODOLOGY appended E40")

# ---------- 3. round ledger line (bm-b canon file) ----------
LEDGER = ("logs/iteration-loop/round_reports.md")
LINE = ("{ts}｜r794｜watermark verdict=green（red=false healthy·satengine rc0 活 idle）｜"
        "S0 落地手术接管崩溃会话（03:32 tick r794 死于 25min 超时，遗产=QA 5/5+S6 38/38 rc0 收编）：5 commit 推达 164fd7cbd"
        "（3 autofill tick+churn-absorb-3+race-absorb）·23 冲突面两轮解=17 S6 面 c3 接管 resolver（add -u 污染 17 面 git show HEAD/<pick> "
        "双侧重建 deep-ts newer-wins+双账本 union·receipt _r794bmb_c3_runs.jsonl）+6 daemon 面 c2 联跑（union/live-wins·receipt "
        "_r794bmb_c2_runs.jsonl）·推前 marker 终扫 CLEAN｜S0.5 令扫 163/163 零差集+集团双面消费（decisions ACC32216→77FFC880 零新本司行·"
        "orders 858D46C3→F1B0CC59 新 10-07 CEO 行=token 节省批零本司新动作·O-1845 bm-b 回执 r780 在册）｜S1 48/48｜"
        "QA r794 5/5（93 trades determinism=True+equity-curve-r794.png）｜三连烧录探针 Q 1920/D 1591/V 2000 COMPLETE｜"
        "S4 坑律 r794+方法卡 E40｜S7 quartet+attrition 见 state.did｜"
        "下轮指针=Q finalize first-to-2000（ETA~07:2x·r668 同窗律+G4 r638 fallback armed）+O-20261006-2358 trio 收口后 ≤1h 自领一件 backlog\n").format(ts=NOW)
with open(LEDGER, "r", encoding="utf-8", newline="") as fh:
    lbody = fh.read()
if "｜r794｜" not in lbody:
    if not lbody.endswith("\n"):
        LINE = "\n" + LINE
    with open(LEDGER, "a", encoding="utf-8", newline="") as fh:
        fh.write(LINE)
    print("ledger line appended")
else:
    print("ledger r794 line already present, skip")

# ---------- 4. state.json ----------
DEC_SHA = "77FFC880DBDFFFD349E21DDF31F63A466C90D2B67927E7353A79B173218C8CE3"
ORD_SHA = "F1B0CC59CFFAAD63B470EA4F079EFDA743B38736109A45D13EBDA9356ECD1EE8"
with open("state.json", "r", encoding="utf-8") as fh:
    st = json.load(fh)
st["round_no"] = 794
st["round_no_label"] = "r794"
st["note"] = ("r794: crashed-session takeover + S0 landing surgery: 03:32-tick r794 session died ~25min timeout post QA/S6; "
              "this round absorbed its estate (QA r794 5/5, S6 38-leg rc0) and landed 5 commits onto advanced origin "
              "(164fd7cbd = origin/main after push): 23 conflict faces resolved in 2 cycles -- 17 S6 faces via c3 takeover "
              "resolver (add -u marker-pollution intercepted pre-continue; stage blobs rebuilt via git show HEAD/<pick>; "
              "deep-ts newer-wins + compute_audit/regime_state (ts,machine) union; receipt _r794bmb_c3_runs.jsonl) + 6 daemon "
              "faces via c2 reuse (line-union/live-wins; receipt _r794bmb_c2_runs.jsonl); pre-push marker scan CLEAN. "
              "S0.5: orders 163/163 zero-delta; group decisions ACC32216->77FFC880 zero new BigMoney rows; group orders "
              "858D46C3->F1B0CC59 new 10-07 CEO row (token-saving batch) zero BigMoney face action; O-1845 bm-b receipt r780 on file. "
              "Trio probe: Q 1920/D 1591/V 2000 COMPLETE.")
st["last_round_at"] = NOW
st["ts"] = NOW
st["updated"] = NOW
st["last_seen"] = NOW
st["clock_read"] = NOW
st["last_decisions_sha"] = DEC_SHA
st["last_decisions_at"] = NOW
st["last_decisions_read_at"] = NOW
st["last_orders_sha"] = ORD_SHA
st["last_orders_read_at"] = NOW
st["last_orders_sha_note"] = ("r794: orders 163/163 zero-delta (fleet dir vs ack set-diff empty); group orders.md sha "
                              "F1B0CC59 (CEO 10-07 token-saving batch row consumed = zero BigMoney face action, O-2325 "
                              "mechanism already in-repo); decisions sha 77FFC880 zero new BigMoney dispatch")
st["last_decisions_sha_method"] = "SHA-256 hex upper of git show origin/main:docs/decisions.md raw bytes via group tree C:\\Users\\Administrator\\FluxGroup fetch+show (D-20261004-02③ real-path fallback)"
st["next"] = ("(1) trio Q finalize ~10-07 07:2x-07:4x (Q 1920/2000 rate ~0.4/min; first-to-2000 same-window per r668 law; "
              "window 10-05..10-09; G1 pending Q+D; G2 integrity + G3 rehearsal green; G4 r638 fallback armed); "
              "(2) D finalize ~10-07 22:xx..10-08 (D 1591/2000 rate ~0.36/min); (3) market reopen 10-08: S6 legs 25-28 "
              "resume + REGIME_GUARD v3 first new bar enforce; (4) O-20261006-2358 trio self-claim law: post-trio-close "
              "<=1h claim one backlog item")
st["did"] = ("r794: crashed r794-session takeover (estate absorbed: QA 5/5 + S6 38/38 rc0) + S0 landing surgery (5 commits, "
             "23-face 2-cycle conflict resolution, receipts _r794bmb_c3_runs.jsonl/_r794bmb_c2_runs.jsonl, pre-push marker "
             "scan CLEAN) + S0.5 orders 163/163 + group dual-face consumption (zero new BigMoney action) + smoke 48/48 + "
             "trio probe Q 1920/D 1591/V 2000 + S4 pit r794 + E40 methodology card + S7 quartet 4/4 + attrition scan")
st["verdict"] = ("green: S0 landing closed (HEAD 164fd7cbd pushed = origin/main); trio Q/D burns alive (1920/1591 of 2000, "
                 "V complete); orders 163/163; smoke 48/48; QA r794 5/5; satengine alive rc0 idle; boards 0 open (176 tasks "
                 "all done); CODELY %dB<=cap compliant" % sz)
st["current_task"] = ("r794 closed; next = trio Q finalize ~10-07 07:2x (first-to-2000 same-window per r668, G4 r638 fallback "
                      "armed) / D finalize late 10-07..10-08 + market reopen 10-08 (S6 legs 25-28 + REGIME_GUARD v3 first "
                      "new bar enforce)")
st["last_round_ts"] = NOW
with open("state.json", "w", encoding="utf-8", newline="\n") as fh:
    json.dump(st, fh, indent=1, ensure_ascii=False)
    fh.write("\n")
print("state.json round_no=794 written")

# ---------- 5. heartbeat ----------
hb_path = "fleet/machines/bm-b.json"
with open(hb_path, "r", encoding="utf-8") as fh:
    hb = json.load(fh)
hb["last_seen"] = NOW
hb["clock_read"] = NOW
hb["heartbeat_epoch_utc"] = EPOCH
hb["ts"] = NOW
hb["updated"] = NOW
hb["last_round_at"] = NOW
hb["round_no"] = 794
hb["round"] = 794
if len(sys.argv) > 2:
    hb["free_ram_gb"] = round(float(sys.argv[1]), 2)
    hb["gpu_free_vram_gb"] = round(float(sys.argv[2]), 3)
    hb["gpu_free_vram_mb"] = int(float(sys.argv[2]) * 1024)
hb["verdict"] = st["verdict"]
hb["current_task"] = st["current_task"]
hb["last_action"] = ("r794: crashed-session takeover + S0 landing surgery (5 commits onto advanced origin, 23-face 2-cycle "
                     "conflict resolution, add -u pollution intercepted, receipts x2) + S0.5 163/163 + group dual-face zero "
                     "BigMoney action + QA r794 5/5 + S6 38/38 rc0 (crashed session estate)")
hb["now_active"] = ("FUND trio NULLS judgment batch in-flight: Q 1920/2000 (rate ~0.4/min, ETA ~07:2x) / D 1591/2000 (rate "
                    "~0.36/min, ETA late 10-07..10-08) / V 2000/2000 COMPLETE; G1 pending Q+D, G2+G3 green, G4 r638 fallback "
                    "armed; finalize window 10-05..10-09")
hb["latest_artifact"] = ("results/_r794bmb_c3_runs.jsonl + _r794bmb_c2_runs.jsonl (23-face S0 surgery receipts) + "
                         "qa/smoke-r794.md 5/5 (93 trades determinism=True, equity-curve-r794.png) @2026-10-07T04:2x")
hb["next_milestone"] = ("trio Q finalize ~10-07 07:2x first-to-2000 same-window (r668 law, G4 r638 fallback armed) + "
                        "post-trio-close O-20261006-2358 self-claim <=1h + market reopen 10-08 (S6 legs 25-28 + REGIME_GUARD "
                        "v3 first new bar enforce) — within 48h window")
hb["task"] = "r794 closed; see state.next"
with open(hb_path, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(hb, fh, indent=1, ensure_ascii=False)
    fh.write("\n")
chk = json.loads(open(hb_path, encoding="utf-8").read())
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be int (R170/R178)"
assert "T" in chk["clock_read"] and "+" in chk["clock_read"], "clock_read must be ISO8601 T-separated (R262)"
print("heartbeat written epoch=%d (int ok) clock=%s" % (chk["heartbeat_epoch_utc"], chk["clock_read"]))
print("CLOSEOUT-OK")
