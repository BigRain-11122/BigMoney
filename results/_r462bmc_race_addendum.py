"""r462 bm-c post-report race addendum: append one receipt line to
round_reports-bm-c.md (bytes mode) + patch state-bm-c.json did/verify with
the 32-UU race-resolution truth. My lane faces only. json.dump+loads
self-verify (r645 law)."""
import datetime
import json

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
STATE = ROOT + r"\state-bm-c.json"
REPORT = ROOT + r"\round_reports-bm-c.md"

NOW = datetime.datetime.now().astimezone().isoformat(timespec="seconds")

ADDENDUM = (
    NOW[:19] + "+08:00｜r462 补行｜dept:工程｜S7 后 push-race 收口回执：首推被拒（bm-a r670 "
    "THEME-JUDGE 判决批+bm-b r664 值守波+daemon 波 7 commit 在途）→fetch+merge 32 UU→"
    "canon 解（28 再生面 newer-wins 全 ours〔10:41-42 vs 10:35-37·ts 归一比较〕+"
    "x2_watch_log 行级 union 2694=2688+6+6 双侧零丢失+pool_core_samples union 1188+"
    "token_usage machines per-key max-union〔side-picks>0 断言〕+compute_audit history "
    "恒等 union）→reparse+marker 门 32/32 PASS（resolver=results/_r462bmc_merge_resolve.py·"
    "证据 results/_r462bmc_merge_resolve.json+双侧结构探针 _r462bmc_uu_probe.json+三歧义面 "
    "diff _r462bmc_ambig_diff.txt）→merge commit f75f8a0bb→push_verify DELIVERED "
    "ahead=0/behind=0·零强推零 --no-verify零信息丢失｜竞态波新条目核毕：CODELY 新增=bm-a "
    "r670 runner 参数双轨坑律 1 条（通用参考件·明晨 finalize 窗判决批参考）·T-165/T-167 "
    "均 bm-a done·零 bm-c 指令零新令｜本地未达 origin commit 数: 0"
)

DID_ADD = (
    " (10) POST-REPORT RACE CLOSURE: first push rejected (7 in-flight commits: bm-a r670 "
    "THEME-JUDGE-P1 judged_negative closure + bm-b r664 watch wave + daemon waves) -> "
    "fetch+merge 32 UU -> canon resolve (28 regen newer-wins all-ours by ts-normalized "
    "probe 10:41-42 vs 10:35-37; x2_watch_log line-union 2694 zero-loss both sides; "
    "pool_core_samples union 1188; token_usage machines per-key max-union side-picks>0; "
    "compute_audit history identity-union) -> reparse+marker gates 32/32 PASS -> "
    "merge f75f8a0bb -> push_verify DELIVERED ahead=0/behind=0, zero force-push, zero "
    "--no-verify, zero information loss. Incoming-wave scan: zero bm-c directives "
    "(1 new bm-a CODELY pit law consumed as reference for finalize-window runner work)."
)

VERIFY_ADD = (
    " | post-report race: 32-UU canon resolve 32/32 reparse+marker PASS "
    "(results/_r462bmc_merge_resolve.json), push_verify DELIVERED f75f8a0bb ahead=0/behind=0"
)


def main():
    # state patch (json programmatic write + self-verify)
    with open(STATE, "rb") as f:
        raw = f.read()
    has_cr = b"\r\n" in raw
    st = json.loads(raw.decode("utf-8-sig"))
    st["did"] = st.get("did", "") + DID_ADD
    st["verify"] = st.get("verify", "") + VERIFY_ADD
    st["last_round"] = (
        "r462 bm-c: golden-week watch + fund-trio V702/Q539/D394 (owners healthy) + "
        "S6 38/38 rc0 + post-report 32-UU push-race canon-resolved DELIVERED f75f8a0bb; "
        "smoke 48/48; orders/D-19 double MATCH; post_review zero-x; zero new pit lines"
    )
    st["round_no"] = 462
    for k in ("clock_read", "last_seen", "last_round_at", "updated", "updated_at"):
        st[k] = NOW
    text = json.dumps(st, ensure_ascii=False, indent=1)
    with open(STATE, "wb") as f:
        f.write(text.replace("\n", "\r\n" if has_cr else "\n").encode("utf-8"))
    chk = json.loads(open(STATE, "rb").read().decode("utf-8-sig"))
    assert chk["round_no"] == 462 and isinstance(chk["heartbeat_epoch_utc"], int)

    # report bytes-append
    with open(REPORT, "rb") as f:
        f.seek(0, 2)
        size = f.tell()
        f.seek(max(0, size - 400))
        probe = f.read()
    crlf = probe.count(b"\r\n")
    bare_lf = probe.count(b"\n") - crlf
    eol_b = b"\r\n" if crlf > bare_lf else b"\n"
    with open(REPORT, "ab") as f:
        if not probe.endswith(b"\n"):
            f.write(eol_b)
        f.write(ADDENDUM.encode("utf-8") + eol_b)
    print("ADDENDUM_DONE", NOW)


if __name__ == "__main__":
    main()
