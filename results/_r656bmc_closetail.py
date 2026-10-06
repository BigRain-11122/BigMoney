# -*- coding: utf-8 -*-
# r656 bm-c close-tail addendum: honest attribution correction (misattribution
# self-caught at delivery verify). The ledger ROW is append-only (not rewritten);
# this appends an erratum line + surgically fixes the mutable state did/note
# fields. bm-c 04:4x-04:5x commits were SELF (r654 close family), not bm-b.
# True bm-b burner-lane evidence: deb9baf30 [via bm-b] 04:33:31 + fabe270a6
# autofill keepalive (fund-quality/divlowvol nulls faces) 04:34:21.
import json, os, time, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOW = datetime.datetime.now().astimezone()
TS = NOW.strftime("%Y-%m-%dT%H:%M:%S+08:00")
EPOCH = int(time.time())

def load_json(p):
    raw = open(p, "rb").read()
    bom = raw.startswith(b"\xef\xbb\xbf")
    return json.loads(raw.decode("utf-8-sig")), bom

def save_json(p, obj, bom):
    with open(p, "w", encoding="utf-8-sig" if bom else "utf-8") as f:
        json.dump(obj, f, indent=1, ensure_ascii=False)

# ---------- (1) ledger erratum line (append-only) ----------
RR = os.path.join(ROOT, "logs", "iteration-loop", "round_reports-bm-c.md")
rb = open(RR, "rb").read()
assert rb.endswith(b"\r\n")
row = ("{ts} | r656 bm-c close-tail 勘注 | 台账行内 trio 观察断言「bm-b 侧 origin 提交 04:4x-04:5x 活跃在飞」归属错误"
       "——送达自证窗复核 via 后缀实测：04:4x-04:5x 三提交（d92b1286b/6a7be8563/1a6f438e4）= bm-c 自家 r654 收口族"
       "（自我误归属·close-tail 自查抓获）；bm-b 正主车道真实证据=deb9baf30〔via bm-b〕r795 daemon ticks 04:33:31+"
       "fabe270a6 autofill keepalive（fund-quality-p1-nulls-0of1+fund-divlowvol-p1-nulls-0of1 两面 keepalive tick）"
       "04:34:21+nulls.jsonl mtime 04:35:38——bm-b 在飞态结论不变（正主车道·零代烧·池面 ready 维持），仅证据行归属勘正 | "
       "state-bm-c.json did/note 同步外科勘正（可变摘要字段·git 史保全） | 本行=append-only 勘注·原行不回改（r307 律）\n"
       "").format(ts=TS)
open(RR, "wb").write(rb + row.encode("utf-8").replace(b"\n", b"\r\n"))

# ---------- (2) state did/note surgical fix ----------
SP = os.path.join(ROOT, "state-bm-c.json")
st, bom = load_json(SP)
WRONG = "bm-b rightful burner lane (recent bm-b-side commits 04:4x-04:5x observed on origin)"
RIGHT = ("bm-b rightful burner lane (evidence: deb9baf30 [via bm-b] daemon ticks 04:33:31 + fabe270a6 autofill "
         "keepalive on fund-Q/D nulls faces 04:34:21 + nulls mtime 04:35:38; the 04:4x-04:5x commits were bm-c's "
         "own r654 close family -- misattribution self-caught and corrected at r656 close-tail)")
n = 0
for k in ("did", "last_round", "last_action"):
    v = st.get(k, "")
    if WRONG in v:
        st[k] = v.replace(WRONG, RIGHT)
        n += 1
st["note"] = ("r656: clean standing-guard round, zero new pits (blob 29,509B live-derived, headroom 1,211B); QA r656 5/5 "
              "explicit --round; S6 38/38; DEC/ORD double-sweep MATCH 163/163; attrition CLEAN; trio V complete, Q 1927, "
              "D 1597 (bm-b lane, zero-growth sampling face; evidence corrected at close-tail: bm-b keepalive ticks "
              "04:33-04:35, 04:4x commits were bm-c self).")
for k in ("last_round_summary",):
    v = st.get(k, "")
    if "bm-b lane, zero-growth sampling face" in v and "evidence corrected" not in v:
        st[k] = v.replace("bm-b lane, zero-growth sampling face",
                          "bm-b lane, zero-growth sampling face; r656 close-tail evidence-correction apply")
st["did"] = st["did"] + (" (close-tail: r656 ledger trio-evidence attribution erratum landed -- see round_reports-bm-c.md "
                         "close-tail line; mutable state summary surgically corrected, git history preserved)")
st["last_round"] = st["did"]
st["last_action"] = st["did"]
for k in ("clock_read", "ts", "last_seen", "last_seen_at", "updated", "updated_at", "last_round_at", "current_task_at"):
    st[k] = TS
save_json(SP, st, bom)

# ---------- (3) heartbeat ts refresh (same content face) ----------
HP = os.path.join(ROOT, "fleet", "machines", "bm-c.json")
hb, bom2 = load_json(HP)
for k in ("clock_read", "ts", "last_seen", "last_seen_at", "updated", "updated_at", "current_task_at"):
    hb[k] = TS
hb["heartbeat_epoch_utc"] = EPOCH
hb["note"] = ("r656 close-tail: trio-evidence attribution erratum (04:4x commits were bm-c self r654 family; true bm-b "
              "evidence = keepalive ticks 04:33-04:35); lane verdict unchanged (bm-b rightful burner, no proxy burn).")
save_json(HP, hb, bom2)

# ---------- self-verify ----------
hb2 = json.loads(open(HP, "rb").read().decode("utf-8-sig"))
assert isinstance(hb2["heartbeat_epoch_utc"], int)
st2 = json.loads(open(SP, "rb").read().decode("utf-8-sig"))
assert st2["round_no"] == 657
assert RIGHT in st2["did"]
print("CLOSETAIL_OK ts=%s did_fixed_fields=%d" % (TS, n))
