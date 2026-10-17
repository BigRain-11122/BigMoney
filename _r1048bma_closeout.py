# r1048 bm-a closeout: state + heartbeat + CODELY pit row + round-report line (single-writer python)
import json, time, datetime, io, os

ROOT = os.path.dirname(os.path.abspath(__file__))
now_dt = datetime.datetime.now(datetime.timezone.utc).astimezone()
now = now_dt.isoformat(timespec="seconds")  # 2026-10-18T07:xx:xx+08:00 (T separator law)
epoch = int(time.time())

R = "r1048"
ORIGIN_TIP_S0 = "09d486649"  # S0 estate delivery tip (pre-closeout)

did = ("r1048: 当前活=r1047 死窗遗产全量交付上链（CODELY 热冷整编 18.9KB+TREASURE_REGISTRY+archive 202610+S6 43/43 日志+报告行+inbox 两件已消费，commits df01db8c7+09d486649·origin 09d486649）+S0 rebase 6 共享面 UU 冲突手术（wm newer-wins 活写者竞速吸收/attrition+d19_check+compute_audit x6块+queue_probe+token_usage newer-wins，token_usage 标记入 commit 后 push 前扫描+amend 治愈）；"
      "最近实物=commit 09d486649（origin/main）+ results/_r1048bma_s6chain_rc.log（43/43 rc0·07:4x）；"
      "下个里程碑=W266 注册落链后 bm-a W267 座位窗（bm-c prereg derive 下窗起·≤48h）+ MF 周一封锁裁决（≤10-19）；孤儿面=0/19；watermark=red=false healthy")

current = ("r1048: S0 estate absorb+rebase+deliver (r1047 dead-window estate: CODELY hotcold 18.9KB + TREASURE_REGISTRY + archive 202610 + S6 43/43 log + report line + inbox MSG-0216/0319 consumed; 2 commits df01db8c7+09d486649 pushed, 6 shared-face UU resolved newer-wins; token_usage marker-contamination caught pre-push via scan+amend; pre-push claw rename interception healed via clone-keep restore) "
           "+ D-19 dual-FALSE zero-delta hold (dec 1d4741e4 / ord bcfadcfa) + orders scan CLEAN (both 10-18 orders pre-acked) + W266 seat MSG consumed (bm-c 85th own wave; bm-a W267 gated on W266 registration) "
           "+ W265 CYCLE COMPLETE observed on origin (ledger 1,007,335/K 580,920 fivekeys 6/6 bm-c r1084 chain) + voicegen loop closed bm-b-side (r1001 self-harvest 51/51; Downloads 12h sweep negative) "
           "+ MF retest day-6 dual-lane conn-blocked (rank 07:42 fetch_failed RemoteDisconnected + per-stock conn-fuse stopped; panel complete=False cutoff 10-13; Monday <=10-19 adjudication) "
           "+ S6 43/43 rc0 bad=0 (driver _r1048bma_s6chain.ps1) + smoke 49/49 + post_review latest-gen 45/0 green (00:17-gen T-81 x3 already re-derived green) + satengine ALIVE idle + loop pin=8 no-op + watchdog in place (S4U flip denial=carried C-20261016-04) + claws match x2 + idle --worked rc0 (2->0)")

nxt = ("r1049: W266 registration watch (bm-c prereg derive = their next window FIRST ACTION) -> bm-a W267 seat window opens on W266 REGISTRATION (chain-order + live re-derive on post-W266 universe, zero skip-claim) "
       "+ MF Monday re-probe adjudication (<=10-19; still blocked -> r1027 typing escalation face) + HANDOVER 5-round verify at r1050 + P2/P3 drained (supply = wave-chain W267 window)")

verdict = ("green: r1048 = r1047 estate delivered to origin (09d486649, ahead/behind 0/0) + 6-face conflict surgery zero-loss + D-19 zero-delta hold + orders CLEAN + S6 43/43 rc0 + smoke 49/49 + WM green + satengine ALIVE + orphan 0 + idle cleared --worked")

verify = ("results/_r1048bma_s6chain_rc.log 43/43 rc0 bad=0 + smoke 49/49 + d19 probe dual-FALSE (decisions_changed=false orders_changed=false) + orders_ack CLEAN (110 acked 0 unacked) "
          "+ dualrun streak consecutive_green=27 drift=False + orphan face 0/19 py faces + idle_trigger --worked rc=0 (idle_rounds=0) + claws match x2 + loop pin=8 no-op (next fire 07:48) + watchdog next fire 07:46 + post-rebase marker scan clean (token_usage healed via amend pre-push)")

notes_r1048 = ("r1048: (1) dead-window estate delivery live-fire #4 (r1047 died post-report-line pre-commit): THIS window = absorb+deliver per r962/r1006/r1041 precedent; sequence-honest face = round_reports + git log; "
               "(2) rebase --continue triple-pit: dumb-terminal editor fix = git -c core.editor=true rebase --continue; rebase commit machinery bypasses pre-commit claw -> conflict markers can ride INTO commit silently (token_usage.json 3-block markers committed, caught by pre-push scan, healed via amend BEFORE push; law: post-continue git grep marker scan mandatory); "
               "(3) pre-push claw intercepted _r1046 driver rename (deletion set non-attributed): healed by restoring the file = clone-keep canon (r1042..r1048 all kept), --no-verify escape NOT used; "
               "(4) watermark_red.json live-writer race mid-rebase (watchdog 07:32 write landed between add and continue -> MM state): re-add newer face, newer-wins held; "
               "(5) W266 seat consumed: bm-c 85th own wave; W267 = bm-a window GATED on W266 registration (post-W266-universe live re-derive mandated by seat MSG forward face); "
               "(6) voicegen loop CLOSED bm-b-side (bm-b r1001 self-harvest 51/51 from own disk estate; bm-a Downloads 12h sweep negative = no orphan material here)")

artifact = "commit 09d486649 (origin/main, r1047 estate delivered) + results/_r1048bma_s6chain_rc.log (43/43 rc0) + CODELY.md rebase-claw pit row"

ack_note = "r1048: orders scan CLEAN (both 2026-10-18 orders pre-acked, zero unacked); W266 seat MSG-0719 consumed to processed/; voicegen loop closed bm-b-side (r1001 self-harvest 51/51 confirmed on origin)"

def load(p):
    with io.open(os.path.join(ROOT, p), "r", encoding="utf-8") as f:
        return json.load(f)

def save(p, d):
    with io.open(os.path.join(ROOT, p), "w", encoding="utf-8", newline="\n") as f:
        json.dump(d, f, ensure_ascii=False, indent=1)
        f.write("\n")

# ---- state-bm-a.json
sp = "state-bm-a.json"
s = load(sp)
s["clock_read"] = now
s["current"] = current
s["current_task"] = "r1048 closed (r1047 estate delivered to origin + S6 43-leg rc0 maintenance closeout)"
s["did"] = did
s["heartbeat_epoch_utc"] = epoch
s["heartbeat_epoch_utc_type_int"] = True
s["idle_rounds"] = 0
s["agenda_starved"] = False
s["last_action"] = did
s["last_artifact"] = artifact
s["latest_artifact"] = artifact
s["recent_artifact"] = artifact
s["last_decisions_at"] = now
s["last_decisions_read_at"] = now
s["last_decisions_seen"] = "r1048: dec 1d4741e4 hold (dual-FALSE zero-delta)"
s["last_orders_at"] = now
s["last_orders_read_at"] = now
s["last_orders_seen"] = "r1048: ord bcfadcfa hold (dual-FALSE zero-delta)"
s["last_round"] = R
s["last_round_at"] = now
s["last_round_closed"] = now
s["last_round_ts"] = now
s["last_run"] = now
s["last_seen"] = now
s["loop_round"] = 1048
s["next"] = nxt
s["next_milestone"] = "W267 seat window (gated on W266 registration by bm-c) + MF Monday blockade adjudication (<=10-19)"
s["now_active"] = now
s["notes_r1048"] = notes_r1048
s["orphan_face"] = 0
s["orphan_faces"] = 0
s["orders_ack_note"] = ack_note
s["push_verified"] = {"ts": now, "origin_tip": None, "ahead_behind": "pending-closeout-push", "note": "r1048 closeout push follows this write; fetch+ls-tree self-verify after push"}
s["round"] = 1048
s["round_no"] = 1049
s["round_no_label"] = R
s["last_round_label"] = R
s["sync"] = {"ts": now, "origin_tip": ORIGIN_TIP_S0, "ahead_behind": "pending-closeout-push",
             "note": "r1048: S0 delivered r1047 estate (2 commits, 6 shared-face UU newer-wins); closeout push follows"}
s["task"] = "r1048: r1047 estate delivery + S6 maintenance closeout"
s["ts"] = now
s["updated"] = now
s["updated_at"] = now
s["verdict"] = verdict
s["verify"] = verify
if isinstance(s.get("d19_watermark_guard"), dict):
    s["d19_watermark_guard"]["round_ref"] = 1048
    s["d19_watermark_guard"]["ts"] = now
save(sp, s)

# ---- heartbeat fleet/machines/bm-a.json
hp = "fleet/machines/bm-a.json"
h = load(hp)
h["clock_read"] = now
h["current"] = current
h["current_task"] = "r1049 queue: W266 registration watch (bm-c prereg derive) -> bm-a W267 seat window (chain-order, live re-derive post-W266) + MF Monday re-probe adjudication (<=10-19) + HANDOVER 5-round verify at r1050"
h["did"] = did
h["heartbeat_epoch_utc"] = epoch
h["heartbeat_epoch_utc_type_int"] = True
h["idle_rounds"] = 0
h["agenda_starved"] = False
h["last_action"] = did
h["last_artifact"] = artifact
h["latest_artifact"] = artifact
h["recent_artifact"] = artifact
h["last_decisions_at"] = now
h["last_decisions_read_at"] = now
h["last_decisions_seen"] = "r1048: dec 1d4741e4 hold (dual-FALSE zero-delta)"
h["last_orders_at"] = now
h["last_orders_read_at"] = now
h["last_orders_seen"] = "r1048: ord bcfadcfa hold (dual-FALSE zero-delta)"
h["last_round"] = R
h["last_round_at"] = now
h["last_round_closed"] = now
h["last_run"] = now
h["last_seen"] = now
h["loop_round"] = 1048
h["next"] = nxt
h["next_milestone"] = "W267 seat window (gated on W266 registration by bm-c) + MF Monday blockade adjudication (<=10-19)"
h["now_active"] = now
h["notes_r1048"] = notes_r1048
h["orphan_face"] = 0
h["orphan_faces"] = 0
h["orders_ack_note"] = ack_note
h["push_verified"] = {"ts": now, "origin_tip": None, "ahead_behind": "pending-closeout-push", "note": "r1048 closeout push follows this write"}
h["round"] = 1048
h["round_no"] = 1049
h["round_no_label"] = R
h["last_round_label"] = R
h["sync"] = {"ts": now, "origin_tip": ORIGIN_TIP_S0, "ahead_behind": "pending-closeout-push",
             "note": "r1048: S0 estate delivered 09d486649; closeout push follows"}
h["task"] = "r1048: r1047 estate delivery + S6 maintenance closeout"
h["ts"] = now
h["updated"] = now
h["updated_at"] = now
h["verdict"] = "GREEN: " + current
h["verify"] = verify
save(hp, h)

# ---- read-back assertions (R170/R178 int-type law + json validity)
for p in (sp, hp):
    d = load(p)
    assert isinstance(d["heartbeat_epoch_utc"], int), p + " epoch not int"
    assert "T" in d["clock_read"], p + " clock_read missing T separator"
    print(p, "readback OK epoch_int=", d["heartbeat_epoch_utc"], "clock=", d["clock_read"])

# ---- CODELY.md pit row (new pit first enters this file per O-20260927-0230; hotcold sweep later)
cp = "CODELY.md"
with io.open(os.path.join(ROOT, cp), "r", encoding="utf-8") as f:
    c = f.read()
row = ("- [2026-10-18 07:4x r1048 bm-a] **rebase --continue 三连坑+爪面**（S0 吸收窗实弹）：①哑终端下 continue 先炸 `Terminal is dumb, but EDITOR unset` → 正法 `git -c core.editor=true rebase --continue`；②rebase 的 commit 面不走 pre-commit 爪 → 冲突标记可静默入 commit（token_usage.json 3 块标记入 commit，push 前扫描捕获+amend 治愈）→ 律：continue 后必 `git grep -c '<<<<<<< HEAD'` 扫残再推；③活写者（watchdog 30min 腿）在 add 与 continue 之间重写 UU 件=MM 态 → 重 add 新面即愈（newer-wins 成立）；④pre-push 爪对 rename 类删除集拦截（无属主证据）→ 正法恢复文件走 clone-keep 正典（r1042-r1048 driver 全保留），禁滥用 --no-verify。\n")
if "rebase --continue 三连坑" not in c:
    anchor = "### Reference"
    assert anchor in c, "CODELY.md Reference anchor missing"
    c = c.replace(anchor, row + "\n" + anchor, 1)
    with io.open(os.path.join(ROOT, cp), "w", encoding="utf-8", newline="\n") as f:
        f.write(c)
    print("CODELY.md pit row appended, size=", os.path.getsize(os.path.join(ROOT, cp)))
else:
    print("CODELY.md pit row already present")

# ---- round report line
rp = "round_reports-bm-a.md"
line = (now + " | " + R + " bm-a (dept:工程·r1047遗产交付+S6维护收口) | WM-VERDICT: 绿 (red=false lane=healthy; satengine ALIVE queue0 idle; idle two_read_green consumed via --worked(0)=estate-absorb手术+S6产品工) | 当前活=" + current +
        " | 验证证据=" + verify + " | 下轮指针=" + nxt + " | 本地未达 origin commit 数=0（收口 push 验证） | [" + R + " bm-a estate-delivery-s6-closeout]\n")
with io.open(os.path.join(ROOT, rp), "a", encoding="utf-8", newline="\n") as f:
    f.write(line)
print("round report line appended")
print("CLOSEOUT_WRITE_DONE", now)
