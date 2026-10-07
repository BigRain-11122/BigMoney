"""r735 bm-c mini-split finisher: first-pass PTR row (929B) overshot the
30,720B disk cap by 50B (blocks already verbatim-migrated + byte equation
verified in-pass-1; only the pointer row is fat). Trim PTR to fit, re-assert
all zero-loss faces, dump receipt with two-pass honest note.
Zero new information loss: migrated blocks untouched; pointer row is nav-only."""
import hashlib
import json
import os

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
MAIN = os.path.join(REPO, "CODELY.md")
T_RR = os.path.join(REPO, "research", "pit-git-resolver-rebase.md")
T_EN = os.path.join(REPO, "research", "pit-engine.md")
T_ST = os.path.join(REPO, "research", "pit-git-staged.md")
T_D19 = os.path.join(REPO, "research", "pit-protocol-d19.md")
RCPT = os.path.join(REPO, "results", "_r735bmc_codely_minisplit.json")
CAP = 30720

PTR_START = "- 域指针·r735 bm-c mini-split（10-08 05:5x·触发=主件 blob 32,896B>30,720B·"

PTR2 = ("- 域指针·r735 bm-c mini-split（10-08 05:5x·主件 blob 32,896B>30,720B 触发·"
        "仪式 r441/r731）：主件 4 行 verbatim 迁出——r863 rebase --continue 零 UU "
        "仍拒坑（741B）→pit-git-resolver-rebase.md〔resolver 主件 30,089B 满员·"
        "rebase 冲突窗子件归位〕+r863 buildgen FRESH token 禁 s-图预处理坑"
        "（505B·行合并缺陷随迁治愈）→pit-engine.md+r734 pre-push 爪删集 push "
        "range 语义坑（1,138B）→pit-git-staged.md〔r806 同域〕+r711 水位 hash "
        "hex 大小写归一坑（772B）→pit-protocol-d19.md〔假 delta 族执法面〕——"
        "逐条字节+sha16 对账=receipt results/_r735bmc_codely_minisplit.json"
        "（零丢失断言=逐块 bytes in target verbatim+主件保留面恒等+主/域件 ≤30KB·"
        "prescan rc3 留痕）；新坑律仍先入本件后回扫。")

N_R731PTR = "- 域指针·r731 bm-c（10-08）"
BLOCK_SHA_NEEDLES = {
    "r863_rebase_continue": ("- [2026-10-08 05:5x r863 bm-a] **rebase --continue", T_RR),
    "r863_buildgen_fresh": ("- [2026-10-08 05:5x r863 bm-a] **buildgen FRESH token", T_EN),
    "r734_prepush_claw": ("- [2026-10-08 05:4x r734 bm-c] **pre-push", T_ST),
    "r711_hex_case": ("- [2026-10-08 01:0x r711 bm-c]", T_D19),
}


def sha16(b):
    return hashlib.sha256(b).hexdigest()[:16]


def main():
    raw = open(MAIN, "rb").read()
    before = len(raw)
    text = raw.decode("utf-8")
    i = text.find(PTR_START)
    assert i >= 0, "first-pass PTR row not found"
    assert text.count(PTR_START) == 1, "PTR row not unique"
    j = text.find("\r\n", i)
    assert j > 0, "PTR row terminator"
    old_ptr = text[i:j + 2]
    new_text = text[:i] + PTR2 + "\r\n" + text[j + 2:]
    open(MAIN, "w", encoding="utf-8", newline="").write(new_text)

    after = len(open(MAIN, "rb").read())
    assert after == before - len(old_ptr.encode("utf-8")) + len(PTR2.encode("utf-8")) + 2, "trim equation"
    assert after <= CAP, "main over cap: %d" % after

    m_after = open(MAIN, "rb").read()
    assert N_R731PTR.encode("utf-8") in m_after, "r731 pointer retained"
    assert PTR2.encode("utf-8") in m_after, "trimmed PTR in main"

    migrated = []
    for name, (needle, tpath) in BLOCK_SHA_NEEDLES.items():
        tb = open(tpath, "rb").read()
        ti = tb.decode("utf-8").find(needle)
        assert ti >= 0, "block missing in target: %s" % name
        t_text = tb.decode("utf-8")
        # extract block: to next "\n- " or "\r\n- " boundary or EOF
        nxt = t_text.find("\r\n- ", ti + 1)
        nxt2 = t_text.find("\n- ", ti + 1)
        cands = [x for x in (nxt, nxt2) if x >= 0]
        end = (min(cands) + 2) if cands else len(t_text)
        block = t_text[ti:end]
        assert needle not in open(MAIN, "rb").read().decode("utf-8"), "block still in main: %s" % name
        migrated.append({
            "entry": name,
            "bytes": len(block.encode("utf-8")),
            "sha16": sha16(block.encode("utf-8")),
            "to": "research/" + os.path.basename(tpath),
        })

    sizes = {os.path.basename(p): len(open(p, "rb").read())
             for p in (T_RR, T_EN, T_ST, T_D19)}
    for k, v in sizes.items():
        assert v <= CAP, "domain over cap: %s=%d" % (k, v)

    rcpt = {
        "round": 735,
        "op": "codely-minisplit-r735",
        "main_bytes_before": 32999,
        "main_bytes_after": after,
        "main_cap": CAP,
        "removed_bytes": 3160,
        "pointer_row_bytes": len(PTR2.encode("utf-8")) + 2,
        "two_pass_note": "pass-1 PTR 931B overshot cap by 50B (30,770B); pass-2 "
                         "trimmed pointer row in-place to %dB (nav-only trim, zero "
                         "loss to migrated blocks); blocks+targets untouched in pass-2"
                         % (len(PTR2.encode("utf-8")) + 2),
        "byte_equation": "pass-1 constructive identity asserted; pass-2 trim equation "
                         "asserted (after == before - old_ptr + new_ptr)",
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
        "migrated": migrated,
        "target_bytes_after": {"research/" + k: v for k, v in sizes.items()},
        "zero_loss_assert": "each block bytes-verbatim in target + removed from main "
                            "+ retained lines constructive-identity (byte equations "
                            "pass-1 and pass-2) + all touched files <= 30720B",
    }
    json.dump(rcpt, open(RCPT, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print(json.dumps(rcpt, indent=1, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
