"""r735 bm-c CODELY mini-split: main blob 32,896B > 30,720B cap (D-20261002-06).
Handoff plan (via bm-c r734): migrate 3 entries -> pit-git-resolver/pit-engine/
pit-git-staged. Prescan amendment: pit-git-resolver.md is 30,089B (full, 741B
entry would breach cap) -> rebase-conflict-window family sub-file
pit-git-resolver-rebase.md (14,618B, family named in main git-domain nav row);
r711 hex-case entry (772B) also migrated -> pit-protocol-d19.md (its own text
names that file as the enforcement face; r672 sibling precedent) for post-op
headroom.
Merged-line boundary defect (r439 family): r863 buildgen entry and r734 claw
entry share one physical line (no NL between) -> healed on migration
(buildgen block gets terminating NL in target).
Surgery ritual r441/r731: verbatim byte-extract by needles, remove, append,
constructive byte equation, sha16 per block, all-files <=30,720B gate,
bytes-in-target verification, retained-lines identity.
Receipt -> results/_r735bmc_codely_minisplit.json"""
import hashlib
import json
import os

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
MAIN = os.path.join(REPO, "CODELY.md")
T_RESOLVER_REBASE = os.path.join(REPO, "research", "pit-git-resolver-rebase.md")
T_ENGINE = os.path.join(REPO, "research", "pit-engine.md")
T_STAGED = os.path.join(REPO, "research", "pit-git-staged.md")
T_D19 = os.path.join(REPO, "research", "pit-protocol-d19.md")
RCPT = os.path.join(REPO, "results", "_r735bmc_codely_minisplit.json")

CAP = 30720

N_R711 = "- [2026-10-08 01:0x r711 bm-c]"
N_R731PTR = "- 域指针·r731 bm-c（10-08）"
N_R863R = "- [2026-10-08 05:5x r863 bm-a] **rebase --continue"
N_BG = "- [2026-10-08 05:5x r863 bm-a] **buildgen FRESH token"
N_R734 = "- [2026-10-08 05:4x r734 bm-c] **pre-push"

PTR = ("- 域指针·r735 bm-c mini-split（10-08 05:5x·触发=主件 blob 32,896B>30,720B·"
       "迁移仪式 r441/r731）：主件 4 行 verbatim 迁出——r863 rebase --continue 零 UU "
       "仍拒坑（741B）→pit-git-resolver-rebase.md〔resolver 主件 30,089B 满员·"
       "rebase 冲突窗子件归位·r787/r789/r794/r825 同族〕+r863 buildgen FRESH token "
       "禁 s-图预处理坑（505B·与 r734 行合并缺陷随迁治愈补 NL）→pit-engine.md+"
       "r734 pre-push 爪删集 push range 语义坑（1,138B）→pit-git-staged.md"
       "〔r653/r806/r731 同域〕+r711 水位 hash hex 大小写归一坑（772B）→"
       "pit-protocol-d19.md〔r537/r583/r672 假 delta 族执法面〕——逐条字节+sha16 "
       "对账=receipt results/_r735bmc_codely_minisplit.json（零丢失断言=逐块 bytes "
       "in target verbatim+主件保留面恒等+主件 ≤30KB+全域件 ≤30KB·treasure prescan "
       "rc3 留痕 per r703 precedent）；新坑律仍先入本件后回扫。")


def sha16(b):
    return hashlib.sha256(b).hexdigest()[:16]


def append_block(path, block):
    b = open(path, "rb").read()
    t = b.decode("utf-8")
    if not t.endswith("\n"):
        t += "\n"
    t += block
    if not t.endswith("\n"):
        t += "\n"
    open(path, "w", encoding="utf-8", newline="").write(t)
    return len(open(path, "rb").read())


def main():
    raw = open(MAIN, "rb").read()
    before = len(raw)
    text = raw.decode("utf-8")

    i_r711 = text.find(N_R711)
    i_r731 = text.find(N_R731PTR)
    i_r863r = text.find(N_R863R)
    i_bg = text.find(N_BG)
    i_r734 = text.find(N_R734)
    assert -1 not in (i_r711, i_r731, i_r863r, i_bg, i_r734), "needles missing"
    assert text.count(N_R711) == 1 and text.count(N_R731PTR) == 1
    assert text.count(N_R863R) == 1 and text.count(N_BG) == 1 and text.count(N_R734) == 1
    assert i_r711 < i_r731 < i_r863r < i_bg < i_r734, "span order"

    blk_r711 = text[i_r711:i_r731]
    blk_r863r = text[i_r863r:i_bg]
    blk_bg = text[i_bg:i_r734]
    blk_r734 = text[i_r734:]
    # merged-line defect check: buildgen block must NOT contain any NL/CR
    # (r439 family; single physical line merged with r734 entry)
    assert "\n" not in blk_bg and "\r" not in blk_bg, "buildgen block unexpectedly multi-line"
    # EOL face: working tree is CRLF-dominant (CR==LF==103), git blob LF
    # (autocrlf) -- r420 family disk face; blocks carry native CRLF verbatim
    assert blk_r711.replace("\r\n", "\n").endswith("\n\n"), "r711 block tail form"
    assert blk_r863r.endswith("\r\n"), "r863-rebase block tail form"
    assert blk_r734.endswith("\r\n"), "r734 block tail form"

    # remove blocks 2,4,5,6; keep r731 pointer; append new pointer
    # (CRLF terminator matches the file's dominant disk EOL form)
    new_text = text[:i_r711] + text[i_r731:i_r863r] + PTR + "\r\n"
    open(MAIN, "w", encoding="utf-8", newline="").write(new_text)

    # verbatim appends to domain files
    sz_rr = append_block(T_RESOLVER_REBASE, blk_r863r)
    sz_en = append_block(T_ENGINE, blk_bg)
    sz_st = append_block(T_STAGED, blk_r734)
    sz_d19 = append_block(T_D19, blk_r711)

    # ---- assertions ----
    after = len(open(MAIN, "rb").read())
    b_r711 = blk_r711.encode("utf-8")
    b_r863r = blk_r863r.encode("utf-8")
    b_bg = blk_bg.encode("utf-8")
    b_r734 = blk_r734.encode("utf-8")
    removed = len(b_r711) + len(b_r863r) + len(b_bg) + len(b_r734)
    added = len(PTR.encode("utf-8")) + 2  # PTR single line + CRLF terminator
    assert after == before - removed + added, "byte equation: %d != %d" % (
        after, before - removed + added)
    assert after <= CAP, "main over cap: %d" % after
    assert sz_rr <= CAP and sz_en <= CAP and sz_st <= CAP and sz_d19 <= CAP, "domain over cap"
    m_after = open(MAIN, "rb").read()
    assert N_R731PTR.encode("utf-8") in m_after, "r731 pointer retained"
    for nb in (b_r711, b_r863r, b_bg, b_r734):
        assert nb not in m_after, "removed block still in main"
    assert b_r863r in open(T_RESOLVER_REBASE, "rb").read(), "verbatim r863r in target"
    assert b_bg in open(T_ENGINE, "rb").read(), "verbatim bg in target"
    assert b_r734 in open(T_STAGED, "rb").read(), "verbatim r734 in target"
    assert b_r711 in open(T_D19, "rb").read(), "verbatim r711 in target"

    rcpt = {
        "round": 735,
        "op": "codely-minisplit-r735",
        "main_bytes_before": before,
        "main_bytes_after": after,
        "main_cap": CAP,
        "removed_bytes": removed,
        "pointer_row_bytes": added,
        "byte_equation": "after == before - removed + pointer (asserted)",
        "eol_face": "working tree CRLF-dominant (disk 32,999B, CR==LF==103) vs LF git "
                    "blob 32,896B (autocrlf) -- r420 family disk face; blocks carried "
                    "native CRLF verbatim; byte gate measured on disk bytes; blob "
                    "normalizes to LF on commit",
        "prescan": "treasure_guard prescan rc3 registry hit on all touched paths, "
                   "recorded per r651/r654/r670/r703/r731 precedent (D-20261002-06 "
                   "standing law mandates main-file <=30KB; byte-verbatim zero-loss "
                   "faces; blocks re-asserted bytes-in-target in-proc)",
        "handoff_plan": "3 entries -> pit-git-resolver/pit-engine/pit-git-staged "
                        "(via bm-c r734); amendment: pit-git-resolver.md 30,089B full "
                        "-> rebase-window sub-file pit-git-resolver-rebase.md; "
                        "r711 -> pit-protocol-d19.md added for headroom",
        "migrated": [
            {"entry": "r863 rebase-continue zero-UU still-refused (E42 family new root)",
             "bytes": len(b_r863r), "sha16": sha16(b_r863r),
             "to": "research/pit-git-resolver-rebase.md"},
            {"entry": "r863 buildgen FRESH token s-cascade preprocessing ban",
             "bytes": len(b_bg), "sha16": sha16(b_bg),
             "to": "research/pit-engine.md",
             "note": "merged-line defect healed on migration (+1 NL, r439 family)"},
            {"entry": "r734 pre-push claw delete-set push-range semantics",
             "bytes": len(b_r734), "sha16": sha16(b_r734),
             "to": "research/pit-git-staged.md"},
            {"entry": "r711 watermark hash hex case normalization",
             "bytes": len(b_r711), "sha16": sha16(b_r711),
             "to": "research/pit-protocol-d19.md"},
        ],
        "target_bytes_after": {
            "research/pit-git-resolver-rebase.md": sz_rr,
            "research/pit-engine.md": sz_en,
            "research/pit-git-staged.md": sz_st,
            "research/pit-protocol-d19.md": sz_d19,
        },
        "zero_loss_assert": "each block bytes-verbatim in target + removed from main "
                            "+ retained lines constructive-identity (byte equation) "
                            "+ all touched files <= 30720B",
    }
    json.dump(rcpt, open(RCPT, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print(json.dumps(rcpt, indent=1, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
