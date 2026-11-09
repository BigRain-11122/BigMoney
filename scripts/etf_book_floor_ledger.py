"""Who remembers the floor between decision bars?

r1450 published a permission (k <= 0.393073), r1455 made the order sheet print the
trim that obeys it, and r1456 measured the schedule that will erase it: `k_schedule()`
re-derives k from an expanding beta every 20th bar and carries no memory of a floor,
and a single upward step has been observed to exceed the whole cut.  So obeying the
permission once, on one sheet, is not obedience -- the floor has to be re-applied on
every decision bar, by something that knows it is still in force.

Nothing in the repo stores a floor across rounds: the permission receipt is a single
current-moment object that is regenerated from the current ticket, and the order sheet
reads it only when printing.  If the ticket is repriced, or a newer permit is issued,
or a round simply does not run the order, the floor silently disappears and the next
sheet sizes to whatever the schedule says.

This face is the ledger that does remember.  It keeps an append-only series of issued
floors and answers one question per round, without looking at the future:

    is the floor still in force, and does the path that is about to run still sit
    above it?

Three states are distinct and are printed separately, because the action differs:

  HOLDING           -- the schedule's last decision bar is at or under the floor: a
                       sheet built now inherits obedience for free.
  REAPPLY_REQUIRED  -- the sheet on disk obeys the floor, but the schedule's last
                       decision bar sits above it: the next sheet will size over the
                       floor unless the trim is applied again on that bar.
  NOT_ENFORCED      -- the schedule is above the floor AND the sheet on disk is above
                       it too: the floor is in the ledger but no reader is obeying it.

The ledger is append-only and idempotent on (decision_date, ticket_file, permitted_k);
a re-issue with a different permitted_k is a new row, never a rewrite.  A missing input
reads as UNKNOWN, never as a pass (r1108).

Read-only apart from its own ledger; no network, no engine, no admission, no booking.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE)

LEDGER = "results/etf_book_floor_ledger.json"
PERMISSION = "results/etf_book_rebalance_permission.json"
PERSISTENCE = "results/etf_book_permission_persistence.json"
CUT_RECEIPT = "results/etf_book_cut_order_gap.json"
TICKETS_DIR = "results"

K_TOL = 1e-6


# --------------------------------------------------------------------------- io
def _read_json(rel):
    p = os.path.join(BASE, rel)
    if not os.path.exists(p):
        return None
    try:
        with open(p, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except (ValueError, OSError):
        return None


def _load_ledger():
    face = _read_json(LEDGER)
    if not face:
        return {"face": "etf_book_floor_ledger", "rows": []}
    if not isinstance(face.get("rows"), list):
        return {"face": "etf_book_floor_ledger", "rows": []}
    return face


def _row_key(row):
    return (str(row.get("decision_date")), str(row.get("ticket_file")),
            round(float(row.get("permitted_k")), 6))


def append_row(face, row):
    """Append unless an identical issue is already recorded. Appends, never rewrites."""
    key = _row_key(row)
    for old in face.get("rows") or []:
        if _row_key(old) == key:
            return face, False
    rows = list(face.get("rows") or [])
    rows.append(row)
    rows.sort(key=lambda r: (str(r.get("decision_date")), str(r.get("issued_at"))))
    face["rows"] = rows
    return face, True


# ----------------------------------------------------------------------- inputs
def latest_ticket():
    """The newest TICKET-*.json under results/, by name (names carry the trade date).

    The ticket writers keep their own subdirectories (etf_book_order/,
    etf_book_order_fresh/); a top-level-only glob silently returns nothing and would
    make the stale-ticket check pass by absence. Quarantine is never a live ticket.
    """
    d = os.path.join(BASE, TICKETS_DIR)
    if not os.path.isdir(d):
        return None
    best = None
    for root, dirs, files in os.walk(d):
        dirs[:] = [x for x in dirs if x not in ("_quarantine", ".git")]
        for n in files:
            if n.startswith("TICKET-") and n.endswith(".json") and "-card" not in n:
                if best is None or n > best:
                    best = n
    return best


def sheet_floor_face(ticket_now):
    """r1497: does the sheet on disk say where its floor came from, and is that source live?

    REAPPLY_REQUIRED used to read only the schedule -- "the next sheet will size over the
    floor". That stopped being the whole story once the sheet began capping k at a floor it
    reads from disk (permission receipt, then the append-only ledger): a ticket that names a
    live source inherits the cap for free, so the standing risk is narrower -- BOTH faces
    missing -- and that is a different thing to watch than "nobody re-applies the trim".
    A sheet that predates the disclosure reads as unread, never as a pass.
    """
    if not ticket_now:
        return {"read": False, "source": None, "decision_date": None}
    d = os.path.join(BASE, TICKETS_DIR)
    for root, dirs, files in os.walk(d):
        dirs[:] = [x for x in dirs if x not in ("_quarantine", ".git")]
        if ticket_now in files:
            try:
                with open(os.path.join(root, ticket_now), encoding="utf-8") as f:
                    tk = json.load(f)
            except (OSError, ValueError):
                return {"read": False, "source": None, "decision_date": None}
            sf = tk.get("sizing_floor") or {}
            src = sf.get("source")
            return {"read": src in ("permission_receipt", "floor_ledger"),
                    "source": src, "decision_date": sf.get("decision_date"),
                    "floor": sf.get("floor")}
    return {"read": False, "source": None, "decision_date": None}


def live_tickets():
    """Every sheet the tree still carries -- the set a floor ledger may price against."""
    d = os.path.join(BASE, TICKETS_DIR)
    out = set()
    if not os.path.isdir(d):
        return out
    for root, dirs, files in os.walk(d):
        dirs[:] = [x for x in dirs if x not in ("_quarantine", ".git")]
        for n in files:
            if n.startswith("TICKET-") and n.endswith(".json") and "-card" not in n:
                out.add(n)
    return out


def issue_row(perm, ticket_now, now):
    """Turn a permission receipt into a ledger row. None when it cannot be read."""
    if not perm:
        return None
    k = perm.get("permitted_k")
    if k is None:
        return None
    try:
        k = float(k)
    except (TypeError, ValueError):
        return None
    return {
        "decision_date": str(perm.get("decision_date") or ""),
        "ticket_file": str(perm.get("ticket_file") or ticket_now or ""),
        "permitted_k": k,
        "cut_k": perm.get("cut_k"),
        "verdict_at_issue": perm.get("verdict"),
        "evidence_cutoff": str(perm.get("evidence_cutoff") or ""),
        "issued_at": now,
        "source": PERMISSION,
    }


def floor_in_force(face, tickets=None):
    """The newest issued row is the floor in force. Returns (row, n_rows, skipped).

    r1483: a row priced from a sheet the tree no longer carries is not a floor in force.
    On 2026-11-09 a permit was issued off TICKET-2026-11-09.json, a sheet priced on a bar
    the wide panel never covered (48/1,724 symbols printed it); the ticket was withdrawn,
    the ledger rewound to 2026-11-06, yet this ledger kept resolving the floor off the
    withdrawn sheet and told the operator to re-issue a permit that was already current.
    Rows are never deleted (append-only); they are skipped by name and counted.
    """
    rows = [r for r in (face.get("rows") or []) if r.get("permitted_k") is not None]
    skipped = []
    if tickets is not None:
        live = [r for r in rows if str(r.get("ticket_file") or "") in tickets]
        skipped = [r for r in rows if str(r.get("ticket_file") or "") not in tickets]
        if live:
            rows = live
    if not rows:
        return None, 0, []
    rows.sort(key=lambda r: (str(r.get("decision_date")), str(r.get("issued_at"))))
    return rows[-1], len(rows), skipped


# ---------------------------------------------------------------------- verdict
def assess(face, perm, pers, ticket_now, cut=None, tickets=None):
    """One deterministic reading. No future data, no simulation.

    Every field is either measured from a published receipt or UNKNOWN; nothing is
    filled in to make the verdict look complete.

    Two different sizes are printed and never conflated (E293): `k_order` is the size
    the ticket asks for, `k_sheet` is the size the sheet actually executes -- the trim's
    post-cut k when the published gap receipt carries one, otherwise the same as ordered.
    Obedience is judged on what is executed, not on what was requested.
    """
    floor, n_rows, skipped = floor_in_force(face, tickets)
    out = {
        "floor": None,
        "floor_issued": None,
        "floor_rows": n_rows,
        "rows_skipped_sheets": [str(r.get("ticket_file")) for r in skipped],
        "k_schedule_last": None,
        "schedule_last_date": None,
        "k_order": None,
        "k_sheet": None,
        "obeyed_now": None,
        "schedule_over_floor": None,
        "floor_kind": None,
        "ticket_superseded": None,
        "ticket_now": ticket_now,
        "missing": [],
        "verdict": None,
        "action": None,
    }
    if floor is None:
        out["missing"].append("floor: no issued row in the ledger and no readable permit")
        out["verdict"] = "NO_FLOOR"
        out["action"] = "issue a permission before sizing (r1450)"
        return out

    out["floor"] = float(floor["permitted_k"])
    out["floor_issued"] = floor.get("decision_date")
    tk_at_issue = str(floor.get("ticket_file") or "")
    if ticket_now:
        out["ticket_superseded"] = bool(tk_at_issue and tk_at_issue != ticket_now)

    # Which ticket priced THIS permit? A newer ticket means the permit's size question
    # has moved on -- the floor is still the last word, but it needs re-issuing.
    if perm:
        try:
            out["k_order"] = float(perm.get("k_now")) if perm.get("k_now") is not None else None
        except (TypeError, ValueError):
            out["k_order"] = None

    # What the sheet actually executes: the post-cut size when the gap receipt carries
    # one. A receipt that measures the gap but records no trim is not an obeyed sheet.
    k_sheet = out["k_order"]
    if cut:
        trim = cut.get("trim") or {}
        # trim_legs() publishes k_after_integer_lots; older receipts used k_after.
        raw = trim.get("k_after_integer_lots", trim.get("k_after"))
        if raw is not None:
            try:
                k_sheet = float(raw)
            except (TypeError, ValueError):
                k_sheet = None
        else:
            out["missing"].append("trim: the gap receipt carries no post-cut k, the sheet is "
                                  "judged on its ordered size")
    out["k_sheet"] = k_sheet

    if pers:
        try:
            out["k_schedule_last"] = (float(pers["k_last_decision_bar"])
                                      if pers.get("k_last_decision_bar") is not None else None)
        except (TypeError, ValueError):
            out["k_schedule_last"] = None
        out["schedule_last_date"] = pers.get("last_decision_date")
    else:
        out["missing"].append("persistence: %s unreadable, the schedule's last k is unknown" % PERSISTENCE)

    if out["k_sheet"] is not None:
        out["obeyed_now"] = bool(out["k_sheet"] <= out["floor"] + K_TOL)
    else:
        out["missing"].append("k_sheet: no readable size for the sheet on disk")

    if out["k_schedule_last"] is not None:
        out["schedule_over_floor"] = bool(out["k_schedule_last"] > out["floor"] + K_TOL)

    # A permit priced from a ticket that has since been replaced is stale in KIND:
    # the size question it answered is no longer the one being asked.
    if out["ticket_superseded"]:
        out["floor_kind"] = "STALE_TICKET"
        out["verdict"] = "REISSUE_REQUIRED"
        out["action"] = ("the permit was priced from %s and the newest ticket is %s -- "
                         "re-issue the permission on the current ticket before sizing"
                         % (tk_at_issue, ticket_now))
        return out

    out["floor_kind"] = "CURRENT_TICKET"

    if out["schedule_over_floor"] and out["obeyed_now"] is False:
        out["verdict"] = "NOT_ENFORCED"
        out["action"] = ("the schedule sits at k=%.6f over the floor %.6f and the sheet on "
                         "disk is over it too -- apply the trim now"
                         % (out["k_schedule_last"], out["floor"]))
    elif out["schedule_over_floor"] and out["obeyed_now"] is True:
        out["verdict"] = "REAPPLY_REQUIRED"
        sf = sheet_floor_face(ticket_now)
        out["sheet_reads_floor"] = sf
        if sf.get("read"):
            out["action"] = ("the sheet obeys the floor and names a live floor source (%s, "
                             "decision %s), so the next sheet inherits the cap instead of "
                             "re-applying it by hand; the standing risk is narrower -- the trim "
                             "gone only if BOTH the permission receipt and the floor ledger are "
                             "missing on that bar (r1497)"
                             % (sf.get("source"), sf.get("decision_date") or "?"))
        else:
            out["action"] = ("the sheet obeys the floor but the schedule's last decision bar is at "
                             "k=%.6f, above %.6f -- the next sheet will size over the floor unless "
                             "the same trim is applied on that bar (r1456: one up-step has erased "
                             "a whole cut)" % (out["k_schedule_last"], out["floor"]))
    elif out["schedule_over_floor"] is False:
        out["verdict"] = "HOLDING"
        out["action"] = ("the schedule's last decision bar k=%.6f is at or under the floor "
                         "%.6f -- a sheet built now inherits obedience"
                         % (out["k_schedule_last"], out["floor"]))
    else:
        out["verdict"] = "UNKNOWN"
        out["action"] = "an input is missing; cannot say whether the floor is in force"
    return out


def sentence(a):
    if a["verdict"] == "NO_FLOOR":
        return "No floor is on the ledger, so nothing can be re-applied between decision bars."
    if a["verdict"] == "REISSUE_REQUIRED":
        return ("Floor %.6f came from %s, but the newest ticket is %s; the permit answers a "
                "size question that has since moved, so it must be re-issued before it is used."
                % (a["floor"], a["floor_issued"], a["ticket_now"]))
    if a["verdict"] == "NOT_ENFORCED":
        return ("Floor %.6f is in the ledger but the schedule's last decision bar is %.6f and "
                "the sheet on disk is over the floor as well: nobody is obeying it."
                % (a["floor"], a["k_schedule_last"] or float("nan")))
    if a["verdict"] == "REAPPLY_REQUIRED":
        _sf = a.get("sheet_reads_floor") or {}
        if _sf.get("read"):
            return ("Floor %.6f holds on the sheet, and the sheet names a live floor source (%s), "
                    "so the next sheet inherits the cap: the schedule's last decision bar is %.6f "
                    "above the floor, but the trim disappears only if both floor faces go missing "
                    "on that bar."
                    % (a["floor"], _sf.get("source"), a["k_schedule_last"] or float("nan")))
        return ("Floor %.6f holds on the sheet but not on the path: the schedule's last decision "
                "bar is %.6f, so the next sheet sizes over it unless the trim is applied again "
                "on that bar." % (a["floor"], a["k_schedule_last"]))
    if a["verdict"] == "HOLDING":
        return ("Floor %.6f is above the schedule's last decision bar %.6f: the constraint is "
                "satisfied by the path itself, not only by the trim printed on a sheet."
                % (a["floor"], a["k_schedule_last"]))
    return "Inputs are missing (%s); the floor's force cannot be established." % "; ".join(a["missing"])


# ------------------------------------------------------------------------ build
def run(write=True):
    t0 = time.time()
    perm = _read_json(PERMISSION)
    pers = _read_json(PERSISTENCE)
    cut = _read_json(CUT_RECEIPT)
    ticket_now = latest_ticket()
    now = time.strftime("%Y-%m-%dT%H:%M:%S%z")

    face = _load_ledger()
    appended = False
    row = issue_row(perm, ticket_now, now)
    if row:
        face, appended = append_row(face, row)

    a = assess(face, perm, pers, ticket_now, cut, tickets=live_tickets())
    face["floor_rows"] = len(face.get("rows") or [])
    face["assessed"] = a
    face["sentence"] = sentence(a)
    face["evidence_cutoff"] = (perm or {}).get("evidence_cutoff")
    face["elapsed_sec"] = round(time.time() - t0, 2)
    face["generated"] = now
    face["appended_this_run"] = appended

    if write:
        p = os.path.join(BASE, LEDGER)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        tmp = p + ".tmp"
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump(face, fh, ensure_ascii=False, indent=1)
            fh.write("\n")
        os.replace(tmp, p)
    return face


def md_lines(face):
    a = face.get("assessed") or {}
    L = ["## 地板台账（谁在两决策 bar 之间记住额度）", ""]
    L.append("- 判定：**%s**（台账 %d 条签发记录，当期 floor=%s，签发于 %s）"
             % (a.get("verdict"), face.get("floor_rows") or 0,
                "%.6f" % a["floor"] if a.get("floor") is not None else "无",
                a.get("floor_issued") or "无"))
    L.append("- 排程末决策 bar：k=%s（%s）；票面 k_order=%s → 执行 k_sheet=%s，票面是否守floor=%s"
             % ("%.6f" % a["k_schedule_last"] if a.get("k_schedule_last") is not None else "无法核验",
                a.get("schedule_last_date") or "未知",
                "%.6f" % a["k_order"] if a.get("k_order") is not None else "无法核验",
                "%.6f" % a["k_sheet"] if a.get("k_sheet") is not None else "无法核验",
                "是" if a.get("obeyed_now") else ("否" if a.get("obeyed_now") is False else "无法核验")))
    L.append("- 该做什么：%s" % (a.get("action") or "无"))
    if a.get("missing"):
        L.append("- 缺口（缺即读成未知，不读成通过）：%s" % "; ".join(a["missing"]))
    L.append("")
    return L


# ------------------------------------------------------------------------ check
def check():
    """Re-derive the fields that move when an input moves. Any drift is RED."""
    face = _read_json(LEDGER)
    if not face:
        print("CHECK_FAIL missing ledger %s" % LEDGER)
        return 2
    perm = _read_json(PERMISSION)
    pers = _read_json(PERSISTENCE)
    cut = _read_json(CUT_RECEIPT)
    ticket_now = latest_ticket()
    a = assess(face, perm, pers, ticket_now, cut, tickets=live_tickets())
    pub = face.get("assessed") or {}
    drift = []
    for k in ("floor", "k_schedule_last", "k_order", "k_sheet", "obeyed_now",
              "schedule_over_floor", "ticket_superseded", "verdict"):
        if pub.get(k) != a.get(k):
            drift.append("%s: published=%r re-derived=%r" % (k, pub.get(k), a.get(k)))
    if drift:
        for d in drift:
            print("DRIFT " + d)
        print("CHECK_FAIL %d field(s) drifted" % len(drift))
        return 1
    print("CHECK_OK floor=%s verdict=%s rows=%d"
          % (a.get("floor"), a.get("verdict"), len(face.get("rows") or [])))
    return 0


# ---------------------------------------------------------------------- selftest
def selftest():
    fails = []

    def leg(name, cond, detail=""):
        if not cond:
            fails.append(name + ((" :: " + detail) if detail else ""))

    now = "2026-11-09T03:00:00+0800"
    perm = {"decision_date": "2026-11-11", "ticket_file": "TICKET-2026-11-06.json",
            "permitted_k": 0.393073, "k_now": 0.460253, "cut_k": 0.06718,
            "verdict": "KEEP_STANDS_ON_NON_PATH_ARGUMENT", "evidence_cutoff": "2026-11-06"}
    pers = {"k_last_decision_bar": 0.460253, "last_decision_date": "2026-10-23"}
    cut = {"trim": {"k_after_integer_lots": 0.392964, "lots_sell_total": 445}}

    # 1. issuing is deterministic and carries the numbers through
    row = issue_row(perm, "TICKET-2026-11-06.json", now)
    leg("leg01 issue carries permitted_k and ticket",
        row["permitted_k"] == 0.393073 and row["ticket_file"] == "TICKET-2026-11-06.json",
        repr(row))
    leg("leg02 issue of an unreadable permit is None", issue_row(None, None, now) is None, "")
    leg("leg03 issue without permitted_k is None",
        issue_row({"decision_date": "x"}, None, now) is None, "")

    # 4. append is idempotent on the issue key
    face = {"face": "etf_book_floor_ledger", "rows": []}
    face, added = append_row(face, row)
    leg("leg04a first append adds a row", added and len(face["rows"]) == 1, "")
    face, added = append_row(face, dict(row, issued_at="2026-11-09T04:00:00+0800"))
    leg("leg04b re-issuing the same (date,ticket,k) does not add a row",
        (not added) and len(face["rows"]) == 1, "")
    face, added = append_row(face, dict(row, permitted_k=0.412669))
    leg("leg04c a different permitted_k is a NEW row, never a rewrite",
        added and len(face["rows"]) == 2, "")

    # 5. the newest row is the floor in force
    fl, n, _sk = floor_in_force(face)
    leg("leg05 floor in force is the newest issued row", fl["permitted_k"] == 0.412669 and n == 2,
        repr(fl))
    _face_w = {"face": "x", "rows": [dict(row, ticket_file="TICKET-2026-11-06.json"),
                                     dict(row, ticket_file="TICKET-2026-11-09.json",
                                          permitted_k=0.393073,
                                          issued_at="2026-11-09T21:27:27+0800")]}
    fl_w, n_w, sk_w = floor_in_force(_face_w, tickets={"TICKET-2026-11-06.json"})
    leg("leg05b a row priced off a withdrawn sheet is skipped, not deleted, and the next live "
        "row is the floor in force",
        fl_w["ticket_file"] == "TICKET-2026-11-06.json" and n_w == 1
        and [r["ticket_file"] for r in sk_w] == ["TICKET-2026-11-09.json"], repr(sk_w))

    # 6-9. the four verdicts, each on its own fixture
    one = {"face": "x", "rows": [row]}
    a = assess(one, perm, pers, "TICKET-2026-11-06.json", cut)
    leg("leg06 sheet obeys but path is over -> REAPPLY_REQUIRED",
        a["verdict"] == "REAPPLY_REQUIRED" and a["obeyed_now"] is True
        and a["schedule_over_floor"] is True, repr(a))
    leg("leg06b the ordered size and the executed size are both printed and differ",
        a["k_order"] == 0.460253 and abs(a["k_sheet"] - 0.392964) < 1e-9, repr(a))

    a = assess(one, dict(perm, k_now=0.460253), pers, "TICKET-2026-11-06.json", None)
    leg("leg07 nothing obeys -> NOT_ENFORCED",
        a["verdict"] == "NOT_ENFORCED", repr(a["verdict"]))

    a = assess(one, dict(perm, k_now=0.38), dict(pers, k_last_decision_bar=0.38),
               "TICKET-2026-11-06.json", None)
    leg("leg08 path under the floor -> HOLDING",
        a["verdict"] == "HOLDING" and a["schedule_over_floor"] is False, repr(a["verdict"]))

    a = assess({"face": "x", "rows": []}, None, pers, "TICKET-2026-11-06.json", cut)
    leg("leg09 empty ledger -> NO_FLOOR (never a pass)", a["verdict"] == "NO_FLOOR", "")

    # 10. a permit priced from an older ticket is stale in KIND, not merely old
    a = assess(one, dict(perm, k_now=0.38), dict(pers, k_last_decision_bar=0.38),
               "TICKET-2026-11-20.json", None)
    leg("leg10 a newer ticket makes the permit STALE_TICKET -> REISSUE_REQUIRED",
        a["verdict"] == "REISSUE_REQUIRED" and a["ticket_superseded"] is True, repr(a["verdict"]))

    # 11. a missing schedule is UNKNOWN, and the missing list names it
    a = assess(one, perm, None, "TICKET-2026-11-06.json", cut)
    leg("leg11 an unreadable schedule is UNKNOWN, not a pass",
        a["verdict"] == "UNKNOWN" and any("persistence" in m for m in a["missing"]),
        repr(a["missing"]))

    # 12. the tolerance is not a free pass: one epsilon over the floor is over
    a = assess(one, dict(perm, k_now=0.393073 + 1e-5), pers, "TICKET-2026-11-06.json", None)
    leg("leg12 a sheet a hair over the floor is not 'obeying'", a["obeyed_now"] is False, "")

    # 13. sentence never claims an action under UNKNOWN
    a = assess(one, perm, None, "TICKET-2026-11-06.json", cut)
    leg("leg13 an UNKNOWN verdict reads as 'cannot be established'",
        "cannot be established" in sentence(a), sentence(a))

    # 14. the mere EXISTENCE of a trim is not obedience -- a trim that lands over the
    # floor must read as not obeying, or a bug in trim_legs would be laundered here
    a = assess(one, perm, pers, "TICKET-2026-11-06.json",
               {"trim": {"k_after_integer_lots": 0.420000}})
    leg("leg14 a trim that lands above the floor is not an obeyed sheet",
        a["obeyed_now"] is False and a["verdict"] == "NOT_ENFORCED", repr(a["verdict"]))

    # 15. a gap receipt with no trim is judged on its ordered size and says so
    a = assess(one, perm, pers, "TICKET-2026-11-06.json", {"trim": None})
    leg("leg15 a receipt with no trim falls back to the ordered size and names the gap",
        a["k_sheet"] == a["k_order"] and any("trim" in m for m in a["missing"]),
        repr(a["missing"]))

    if fails:
        for f in fails:
            print("FAIL " + f)
        print("selftest %d/%d" % (15 - len(fails), 15))
        return 1
    print("selftest 15/15")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", nargs="?", default="run", choices=["run", "check", "selftest", "md"])
    a = ap.parse_args(argv)
    if a.mode == "selftest":
        return selftest()
    if a.mode == "check":
        return check()
    if a.mode == "md":
        face = run(write=False)
        print("\n".join(md_lines(face)))
        return 0
    face = run(write=True)
    print(json.dumps(face.get("assessed"), ensure_ascii=False))
    print(face.get("sentence"))
    return 0


if __name__ == "__main__":
    sys.exit(main())