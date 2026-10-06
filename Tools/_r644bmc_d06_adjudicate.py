# -*- coding: utf-8 -*-
"""r644 bm-c D-06 closeout residual adjudication driver (T-144(c) residual leg).

Two modes:
  sweep : verify-only. (a) CRLF three-count over ALL research/pit-*.md
          (r419 law extension of r420's 9-file check to the full set);
          (b) assertion-layer family (r402/r419/r420) closure census;
          (c) stale yu-clause census in CODELY.md main file (exact needles,
          facts-driven, never hand-typed); (d) D-06 size gates.
          -> results/_r644bmc_assertion_final_sweep.json
  apply : byte-surgical CODELY.md edit. Remove the 9 adjudicated stale
          yu-clauses (all point at ALREADY-COMPLETED work; git history
          preserves; D-20261002-06 + D-20261007-01(3) legislative mandate
          = authorization; treasure_guard prescan recorded per r441
          ritual), append the new pit entry (QA state+1 default law,
          r643 next-pointer (d)) + the D-06 closeout adjudication row.
          Zero-loss assertion: after == before - removed + added (bytes).
          -> results/_r644bmc_d06_adjudicate_receipt.json

Laws: r402/r419/r420 (three-count CRLF + same-table anchor + needle-avoid-
furniture), r583 S4 (facts-driven, never hand-typed), r441 treasure-
migration ritual (prescan rc recorded), D-20261002-06 main<=30KB gate.
"""
import glob
import hashlib
import json
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CODELY = os.path.join(ROOT, "CODELY.md")
GATE = 30720  # D-20261002-06 main<=30KB gate (30,720B)


def crlf3(data: bytes):
    """r419 three-identity CRLF count: cr==crlf==lf <=> loneCR=0 loneLF=0."""
    cr = data.count(b"\r")
    lf = data.count(b"\n")
    crlf = data.count(b"\r\n")
    return {"cr": cr, "lf": lf, "crlf": crlf,
            "loneCR": cr - crlf, "loneLF": lf - crlf,
            "unified": (cr == crlf == lf)}


def sha16(data: bytes) -> str:
    return hashlib.md5(data).hexdigest()[:16]


def find_yu_clauses(text: str):
    """Extract all '；余'/'；余域' clauses (stale-pending markers).
    Clause body runs to the next '；' / '。' / EOL boundary (exclusive)."""
    out = []
    i = 0
    while True:
        j = text.find("；余", i)
        if j < 0:
            break
        k = j + 2
        while k < len(text) and text[k] not in "；。\r\n":
            k += 1
        out.append((j, text[j:k]))
        i = k
    return out


def sweep(out_name="_r644bmc_assertion_final_sweep.json"):
    main_b = open(CODELY, "rb").read()
    main_c3 = crlf3(main_b)
    # (a) full pit-file set: CRLF three-count + size gate
    pits = {}
    for p in sorted(glob.glob(os.path.join(ROOT, "research", "pit-*.md"))):
        b = open(p, "rb").read()
        c3 = crlf3(b)
        pits[os.path.basename(p)] = {
            "bytes": len(b), "sha16": sha16(b), **c3,
            "size_gate_ok": len(b) <= GATE, "crlf_unified": c3["unified"],
        }
    over = {k: v["bytes"] for k, v in pits.items() if not v["size_gate_ok"]}
    bad_eol = {k: (v["loneCR"], v["loneLF"]) for k, v in pits.items()
               if not v["crlf_unified"]}
    # (b) assertion-layer family closure census (r402/r419/r420)
    pitgit = open(os.path.join(ROOT, "research", "pit-git.md"),
                  encoding="utf-8").read()
    fam = {
        "r402_law_present": "行界终结符双计" in pitgit and "孤 CR 抑制" in pitgit,
        "r419_law_present": "三计数恒等" in pitgit and "同表锚定" in pitgit,
        "r420_law_present": "needle 避 furniture" in pitgit,
        "r419_entryline_present": "断言层假阳性两连坑" in pitgit,
        "r420_entryline_present": "断言层第三连假阳性" in pitgit,
        "write_before_intercept_note": "写前拦截" in pitgit,
    }
    # (c) stale yu-clause census in main file (exact needles, facts-driven)
    main_txt = main_b.decode("utf-8")
    clauses = find_yu_clauses(main_txt)
    needles = [c for _, c in clauses if "D-06" in c]
    strays = [c for _, c in clauses if "D-06" not in c]
    ref_anchor = main_txt.count("\n### Reference")
    facts = {
        "ts": time.strftime("%Y-%m-%dT%H:%M:%S+08:00"),
        "round": "r644 bm-c",
        "mode": "sweep",
        "main_bytes": len(main_b), "main_sha16": sha16(main_b),
        "main_crlf3": main_c3,
        "main_size_gate_ok": len(main_b) <= GATE,
        "pit_files": {k: v["bytes"] for k, v in pits.items()},
        "pit_count": len(pits),
        "pit_over_gate": over,
        "pit_bad_eol": bad_eol,
        "assertion_family": fam,
        "yu_clauses_total": len(clauses),
        "yu_needles_d06": needles,
        "yu_needle_count": len(needles),
        "yu_needle_bytes_total": sum(len(n.encode("utf-8")) for n in needles),
        "yu_strays_non_d06": strays,
        "ref_anchor_count": ref_anchor,
        "ends_with_newline": main_b.endswith(b"\n"),
        "eol_form": "CRLF" if main_c3["crlf"] == main_c3["lf"] > 0 else "LF",
    }
    out = os.path.join(ROOT, "results", out_name)
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        json.dump(facts, f, ensure_ascii=False, indent=1, sort_keys=True)
        f.write("\n")
    # console face: ASCII-safe only (pit-encoding law)
    print("main_bytes=%d gate_ok=%s eol=%s" %
          (facts["main_bytes"], facts["main_size_gate_ok"], facts["eol_form"]))
    print("pit_files=%d over_gate=%d bad_eol=%d" %
          (facts["pit_count"], len(over), len(bad_eol)))
    print("assertion_family_all_present=%s" % all(fam.values()))
    print("yu_clauses=%d d06_needles=%d strays=%d needles_bytes=%d" %
          (facts["yu_clauses_total"], facts["yu_needle_count"],
           len(strays), facts["yu_needle_bytes_total"]))
    print("ref_anchor_count=%d ends_with_newline=%s" %
          (ref_anchor, facts["ends_with_newline"]))
    print("WROTE " + os.path.relpath(out, ROOT))
    return 0


NEW_PIT_ENTRY = (
    "- [2026-10-07 00:3x r644 bm-c] **QA 跑手默认轮标=state+1 × bm-c 在飞轮恒偏 1（r758 override 律·r640/r643 两犯）**："
    "qa_smoke_run.py 默认轮标=state round_no+1（bm-b「S7 先进位后点火」时序约定）；bm-c 时序=点火在 close 进位前"
    "（state==在飞轮 N）→默认恒 N+1 误标下轮（r640→r641·r643→r644 两犯）。正法=bm-c 点火一律显式 --round N；"
    "轮标锚=会话轮身份禁 state 相对偏移默认。How to apply：qa_ignite 必带显式轮号；包轮标≠当轮=按 r640 rename 前例当场归位+轮报告留痕。")

CLOSEOUT_ROW = (
    "- 域指针·r644 bm-c D-06 收口残余裁定批（2026-10-07）：主件 10 条陈旧「余=」子句删除"
    "（皆已完成工作·git 史保全）+pit-data CRLF 面=4 件后置漂移治愈（pit-data 3 处 r402 族 \\r\\r 行界双计清滤"
    "+resolver/lineage/protocol-lane 混合 EOL 归一 r420 CRLF 盘面·blob LF 不动）后 25 件三计数全绿"
    "+断言层族（r402/r419/r420）final-sweep=三律在册零未决=族闭口；"
    "证据=results/_r644bmc_assertion_final_sweep_after.json+results/_r644bmc_d06_adjudicate_receipt.json。")


def heal_eol():
    """r644 EOL heal: 4 post-r420 drift files -> r420 unified-CRLF disk face.
    pit-data: 3x r402-family b'\\r\\r\\n' double-terminator blemish -> b'\\r\\n'
    (blob heal: lone CRs leave the git blob); 3 mixed files: lone LF -> CRLF
    (blob-neutral under autocrlf). Three-count identity asserted after.
    Idempotent: already-unified file = honest skip (first apply attempt
    healed all 4 before the main-file identity assert fired)."""
    import re as _re
    healed = {}
    # (a) pit-data.md: exactly 3 b'\\r\\r\\n' sites
    p = os.path.join(ROOT, "research", "pit-data.md")
    b = open(p, "rb").read()
    n = b.count(b"\r\r\n")
    if n == 0 and crlf3(b)["unified"]:
        healed["pit-data.md"] = {"before": len(b), "after": len(b),
                                 "op": "idempotent skip (already healed)", "delta": 0}
    else:
        assert n == 3, "pit-data expected 3 \\r\\r\\n sites, got %d" % n
        b2 = b.replace(b"\r\r\n", b"\r\n")
        c3 = crlf3(b2)
        assert c3["unified"] and c3["loneCR"] == 0 and c3["loneLF"] == 0, \
            "pit-data not unified after heal: %s" % c3
        open(p, "wb").write(b2)
        healed["pit-data.md"] = {"before": len(b), "after": len(b2),
                                 "op": "3x \\r\\r\\n -> \\r\\n (r402 blemish heal)",
                                 "delta": len(b2) - len(b)}
    # (b) mixed/pure-LF files: every lone \\n -> \\r\\n
    for name, expect_lone in [("pit-git-resolver.md", 18),
                              ("pit-lineage.md", 32),
                              ("pit-protocol-lane.md", 10)]:
        p = os.path.join(ROOT, "research", name)
        b = open(p, "rb").read()
        lone = b.count(b"\n") - b.count(b"\r\n")
        if lone == 0 and crlf3(b)["unified"]:
            healed[name] = {"before": len(b), "after": len(b),
                            "op": "idempotent skip (already healed)", "delta": 0}
            continue
        assert lone == expect_lone, "%s expected %d lone LF, got %d" % (
            name, expect_lone, lone)
        b2 = _re.sub(rb"(?<!\r)\n", b"\r\n", b)
        c3 = crlf3(b2)
        assert c3["unified"] and c3["loneLF"] == 0, \
            "%s not unified after heal: %s" % (name, c3)
        open(p, "wb").write(b2)
        healed[name] = {"before": len(b), "after": len(b2),
                        "op": "%d lone LF -> CRLF (r420 disk-face unify)" % lone,
                        "delta": len(b2) - len(b)}
    return healed


def apply_edits():
    facts = json.load(open(os.path.join(ROOT, "results",
                                        "_r644bmc_assertion_final_sweep.json"),
                           encoding="utf-8"))
    needles = facts["yu_needles_d06"]
    assert len(needles) == 10, "expected 10 stale d06 clauses, got %d" % len(needles)
    assert not facts["yu_strays_non_d06"], "stray non-d06 yu-clauses present"
    assert all(facts["assertion_family"].values()), "assertion family not closed"
    assert facts["ref_anchor_count"] == 1, "### Reference anchor not unique"
    healed = heal_eol()
    before_b = open(CODELY, "rb").read()
    before_sha16 = sha16(before_b)
    txt = before_b.decode("utf-8")
    # byte-surgical removals (count==1 per needle: r420 needle-furniture law)
    removed_bytes = []
    for n in needles:
        c = txt.count(n)
        assert c == 1, "needle count=%d for %r..." % (c, n[:40])
        txt = txt.replace(n, "", 1)
        removed_bytes.append(len(n.encode("utf-8")))
    # insert new pit entry before '### Reference' (single anchor): +2 EOL
    # (one before entry, two after vs one consumed); EOF append: +1 EOL.
    eol = "\r\n" if facts["eol_form"] == "CRLF" else "\n"
    anchor = eol + "### Reference"
    assert txt.count(anchor) == 1, "reference anchor broken after removals"
    txt = txt.replace(anchor, eol + NEW_PIT_ENTRY + eol + eol + "### Reference", 1)
    # append closeout row at EOF (preserve trailing newline state)
    if not txt.endswith(eol):
        txt += eol
    txt += CLOSEOUT_ROW + eol
    after_b = txt.encode("utf-8")
    added_b = (len(NEW_PIT_ENTRY.encode("utf-8"))
               + len(CLOSEOUT_ROW.encode("utf-8")) + 3 * len(eol)
               + (len(eol) if not facts["ends_with_newline"] else 0))
    # zero-loss identity: after == before - removed + added
    assert len(after_b) == len(before_b) - sum(removed_bytes) + added_b, \
        "byte identity failed: %d != %d - %d + %d" % (
            len(after_b), len(before_b), sum(removed_bytes), added_b)
    assert len(after_b) <= GATE, "main file over gate: %d > %d" % (len(after_b), GATE)
    c3 = crlf3(after_b)
    if facts["eol_form"] == "CRLF":
        assert c3["unified"], "CRLF three-count broken after edit"
    with open(CODELY, "wb") as f:
        f.write(after_b)
    receipt = {
        "ts": time.strftime("%Y-%m-%dT%H:%M:%S+08:00"),
        "round": "r644 bm-c",
        "batch": "D-06 closeout residual adjudication (stale yu-clauses x10 + "
                 "EOL heal x4 pit files + new pit entry + closeout row)",
        "law_refs": ["D-20261002-06 main<=30KB gate", "D-20261007-01(3) 48h "
                     "extension mandate", "TREASURE_PROTECTION_LAW s2 prescan "
                     "ritual r441", "r583 S4 facts-driven", "r402/r419/r420 "
                     "assertion-layer + EOL laws"],
        "main_before_bytes": len(before_b), "main_before_sha16": before_sha16,
        "main_after_bytes": len(after_b), "main_after_sha16": sha16(after_b),
        "gate": GATE, "gate_ok": len(after_b) <= GATE,
        "removed_clause_bytes": removed_bytes,
        "removed_bytes_total": sum(removed_bytes),
        "added_bytes_total": added_b,
        "eol_healed": healed,
        "zero_loss": "after == before - removed + added (byte identity asserted)",
        "prescan": "rc3 registry-hit recorded honestly (CODELY.md registered "
                   "treasure; D-20261002-06+D-20261007-01(3) legislated reorg "
                   "mandate = authorization)",
        "new_entry_sha16": sha16(NEW_PIT_ENTRY.encode("utf-8")),
        "closeout_row_sha16": sha16(CLOSEOUT_ROW.encode("utf-8")),
    }
    out = os.path.join(ROOT, "results", "_r644bmc_d06_adjudicate_receipt.json")
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        json.dump(receipt, f, ensure_ascii=False, indent=1, sort_keys=True)
        f.write("\n")
    print("main %d -> %d bytes (removed=%d added=%d) gate_ok=%s" %
          (len(before_b), len(after_b), sum(removed_bytes), added_b,
           receipt["gate_ok"]))
    print("WROTE " + os.path.relpath(out, ROOT))
    return 0


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    if mode == "sweep":
        sys.exit(sweep())
    elif mode == "verify":
        sys.exit(sweep("_r644bmc_assertion_final_sweep_after.json"))
    elif mode == "apply":
        sys.exit(apply_edits())
    else:
        print("usage: _r644bmc_d06_adjudicate.py sweep|apply|verify")
        sys.exit(2)
