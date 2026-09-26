# -*- coding: utf-8 -*-
# r237 bm-b final closeout: orders_ack 74->77, T-73->T-76 reference fixups, addendum2 line, heartbeat refresh
import io, json, time, datetime

REPO = r"C:\Users\Administrator\Desktop\Bigmoney"
now = time.time()
ts = datetime.datetime.fromtimestamp(now).astimezone()

def rd(p): return io.open(p, encoding="utf-8").read()
def wr(p, t): open(p, "wb").write(t.encode("utf-8"))

# 1) round report: fix r237 line refs + append addendum2
p = REPO + r"\logs\iteration-loop\round_reports.md"
t = rd(p)
n_before = t.count("T-2026-09-26-73-P1")
assert n_before >= 1
# only the r237 line references T-73-P1 (bm-a's own lines reference T-2026-09-26-73 (no -P1) in their report file, not this one)
t = t.replace("T-2026-09-26-73-P1 (external-mining-wave10) 预开", "T-2026-09-26-76-P1 (external-mining-wave10) 预开〔票号让路 bm-a 同窗 CEO 令票 T-73·fleet/README §4 commit 时间序·rebase 重放时重编号〕")
t = t.replace("fleet/tasks/T-2026-09-26-73-P1.json（open→claimed+progress_r237·json.loads 往返+CRLF 无 BOM 镜像）", "fleet/tasks/T-2026-09-26-76-P1.json（open→claimed+progress_r237·json.loads 往返+CRLF 无 BOM 镜像·renumber 披露在票内）")
assert "T-2026-09-26-73-P1" not in t, "leftover wrong refs"
if not t.endswith("\n"): t += "\n"
add2 = (
    "R237 addendum2 (bm-b): S7 push rejected (bm-a R238+addendum1-3+O-0932/O-0940 landed mid-round window) -> pull --rebase 3-commit replay, 2 conflict batches (step1: 1-AA ticket + 11-UU; step3: 3-UU tail) -> binding==source re-sync verified first (R219 law, 4418B equal) -> per-class recipes: "
    "TICKET ADD/ADD = bm-a CEO-order ticket T-73 (cn-schools, commit-time priority) kept at 73, mine renumbered -> T-2026-09-26-76-P1.json with in-ticket disclosure; "
    "autofill launches union 50|50->50 cap50 + last_tick whole-dict take-new 09:30:02 (isinstance dict-assert OK, no str() compare, CRLF mirror); "
    "compute_audit latest take-new 09:26:08 + history union 201|201->202 zero-loss (indent=2 canon per r237 indent law, base-blob probe); "
    "dashboard twins take-side WHOLE BYTES by twin meta.generated_at 09:28:23>09:23:21 (r226 law, js wrapper intact); "
    "regime state-face take-new by updated + history union by asof; snapshots take-new by named ts/updated/generated keys (fundamental/futures/heat/lhb/update_status); "
    "post_review.jsonl 535|535->551 zero-loss union both batches (519 base + bm-a 16 + bm-b 16); REPORT take-new 09:30:13; "
    "E1 self-catch x2 pre-add: (a) regime history union first keyed on ts/date but rows use 'asof' -> 2|2 collapsed to 1 = row loss caught, re-union by asof -> 2 rows exact (09-23/09-24); (b) token_usage empty-vs-empty ts default-side hazard (r226 family) -> real key = 'generated', corrected take-new 09:28:24 mine; "
    "poison scan 3 commits line-start 0 markers + HEAD json parse ALL OK + anchors (launches 50/last_tick dict/history 202/post_review 551); push fbd0d04d..979425cc zero force. "
    "S0.5 late-window orders scan (rebase brought O-20260926-0926/0932/0940): 3 new CEO orders read+processed -> orders_ack 74->77: "
    "O-0926 (CN schools panorama) verified T-73 claimed+started by bm-a R238 s1 scaffold (DIGEST-20260926-t73-cn-schools-s1.md in tree); "
    "O-0932 (market-clock combo) + O-0940 (autonomous ops+daily battle report): tickets T-74/T-75 created open by bm-a live GM session (human-author commits 09:30:03/09:31:18) with zero claim -> bm-b DEFERS claim per anti-dup lane discipline (creator session active, bm-a heartbeat 12.1min fresh <20min stale-takeover window); TAKEOVER TRIGGER recorded: any healthy machine claims T-74/T-75 if still open + creator heartbeat stale >20min at next round check; "
    "resolver provenance=%TEMP%\\r237b_replay_resolver.py + step drivers (r231 out-of-repo law) [" + ts.strftime("%H:%M") + "]\n"
)
t += add2
wr(p, t)
print("round_reports: refs fixed, addendum2 appended")

# 2) CODELY 2 lines renumber
p = REPO + r"\CODELY.md"
t = rd(p)
c_before = t.count("T-2026-09-26-73-P1.json")
t = t.replace("T-2026-09-26-73-P1.json", "T-2026-09-26-76-P1.json")
t = t.replace("（bm-b r237 预开+开票即认领 slice-1 face(b) GM_REVIEW_MEMOS 同轮交付）", "（bm-b r237 预开+开票即认领 slice-1 face(b) GM_REVIEW_MEMOS 同轮交付·本地票号 73 让路 bm-a 同窗 CEO 令票后重编号为 76）")
assert "T-2026-09-26-73-P1.json" not in t
wr(p, t)
print("CODELY renumber OK, size:", len(t.encode("utf-8")))

# 3) GM_REVIEW_MEMOS renumber
p = REPO + r"\research\GM_REVIEW_MEMOS.md"
t = rd(p)
t = t.replace("T-2026-09-26-73 face (b)", "T-2026-09-26-76 face (b) (renumbered from local 73: same-window collision with bm-a CEO-order ticket T-73, yield per fleet/README s4)")
wr(p, t)
print("GM_REVIEW_MEMOS renumber OK")

# 4) MSG content correction note (r173 style)
p = REPO + r"\fleet\inbox\MSG-20260926-0927-bm-b-claim-t73-wave10-slice1.md"
t = rd(p)
t = t.replace("T-2026-09-26-73", "T-2026-09-26-76")
if not t.endswith("\n"): t += "\n"
t += "\n- RENUMBER CORRECTION (2026-09-26 09:4x): ticket locally created as T-2026-09-26-73 same-window as bm-a CEO-order ticket T-73 (CN schools panorama, commit-time priority per fleet/README s4) -> yielded number, renumbered to T-2026-09-26-76 at rebase replay; filename kept (identifier), content refs corrected.\n"
wr(p, t)
print("MSG correction OK")

# 5) state.json current_task update
p = REPO + r"\logs\iteration-loop\state.json"
st = json.load(io.open(p, encoding="utf-8"))
st["current_task"] = "T-76 wave-10 (renumbered from local 73 per bm-a same-window CEO ticket) claimed slice-1 delivered (GM memos 2 PENDING); 3 new CEO orders acked (O-0926 verified T-73 in-flight; T-74/T-75 defer to active bm-a session, takeover trigger = open + creator heartbeat stale >20min at next round)"
st["next"] = "T-74/T-75 takeover check next round (if open + bm-a stale>20min -> claim; else creator session executes); southbound daylight window 12:00-13:40; T-76 faces (a)/(c)/(d)/(e) open any healthy machine; 09-28 Monday new-bar full-chain relay; 10-01 monthly three-suite"
st["updated_at"] = ts.isoformat()
raw = json.dumps(st, indent=1, ensure_ascii=False)
wr(p, raw)
print("state.json current_task updated")

# 6) heartbeat: orders_ack 77 + fresh epoch + current_task
p = REPO + r"\fleet\machines\bm-b.json"
h = json.load(io.open(p, encoding="utf-8"))
ack = h["orders_ack"].split()
for tok in ["O-20260926-0926-bm-a.md", "O-20260926-0932-bm-a.md", "O-20260926-0940-bm-a.md"]:
    assert tok not in ack
    ack.append(tok)
h["orders_ack"] = " ".join(ack)
h["heartbeat_epoch_utc"] = int(now)
h["clock_read"] = ts.isoformat()
h["last_seen"] = ts.strftime("%Y-%m-%d %H:%M:%S")
h["current_task"] = "r237 done+pushed: O-1721 chain closure (T-76 wave-10 pre-opened+claimed, slice-1 GM memos delivered, renumbered from local 73 after bm-a same-window CEO ticket) + S7 push-collision 15-file rebase resolved zero-loss + 3 new CEO orders acked (T-74/T-75 defer to active bm-a session, takeover trigger recorded)"
h["round_no"] = 237
h["verdict"] = "py_low_board_clear legal idle (board 0 open for bm-b lanes; T-74/T-75 = bm-a live-session queue defer; pool 0 ready; southbound window 12:00-13:40 pending)"
raw = json.dumps(h, indent=1, ensure_ascii=False)
wr(p, raw)
back = json.load(io.open(p, encoding="utf-8"))
assert isinstance(back["heartbeat_epoch_utc"], int) and len(back["orders_ack"].split()) == 77
print("heartbeat: epoch int", back["heartbeat_epoch_utc"], "orders_ack 77 tokens")

# verify all jsons parse
for f in [r"\logs\iteration-loop\state.json", r"\fleet\machines\bm-b.json", r"\fleet\tasks\T-2026-09-26-76-P1.json"]:
    json.load(io.open(REPO + f, encoding="utf-8-sig"))
print("FINAL FIXUPS ALL VERIFIED")
