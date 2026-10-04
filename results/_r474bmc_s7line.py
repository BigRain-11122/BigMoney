"""r474 bm-c S7-close line appender: one line to round_reports-bm-c.md
(byte-safe EOL append per r641 family). ASCII console prints only."""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORT = os.path.join(ROOT, "round_reports-bm-c.md")

LINE = (
    "2026-10-04T13:40:02｜r474 bm-c S7-close｜本地未达 origin commit 数=0"
    "（push_verify DELIVERED 四段：close commit 0b0f1e30f〔66 面·pre-commit 爪过〕"
    "+merge 0d735759f〔bm-a r678 wave·22 UU 两分法：CODELY r675 块级 union"
    "〔added==1 断言〕+token r466 per-key union+audit hist union+19 regen ts-newer〕"
    "+merge 5427d078f〔bm-b r673 wave·12 UU：x2 行级 union r656 零丢失断言+11 ts-newer"
    "+token 自动并 containment 验证〕+merge db3cf5cfa〔bm-b keepalive·零 UU〕"
    "·tip db3cf5cfa==remote tip·ahead=0/behind=0·零 --no-verify·零强推·"
    "三波 push-race 全净路收敛）｜池回退自愈同轮实证：MSG-1332 收口判据"
    "「origin trio owner_since fresh」已满足（13:38:12·age 1.6min·healthy True×3"
    "·bm-b r288 keepalive tick f4336c3d6/08fabe624 双跳落地）·nulls V775/Q602/D449"
    "（+17/+14/+13 vs r473 基线 758/588/436）｜收口实录：S0 absorb 86847bdfd"
    "（4 车道面）+merge 净零 UU→close 0b0f1e30f→push REJECTED rc1（bm-a r678 "
    "full-closure wave 在途）→merge 0d735759f 22 UU→_r474bmc_merge_resolve.py"
    "（r466 血统+r675 后落册律补腿=r466 自身教训执法·attrition 复扫 CLEAN）"
    "→push REJECTED rc1（bm-b r673 wave 在途）→merge 5427d078f 12 UU→"
    "_r474bmc_merge_resolve3.py（x2 行级 union+token containment 验证+attrition "
    "复扫 CLEAN）→push REJECTED rc1（bm-b keepalive tick）→merge db3cf5cfa 零 UU"
    "→push DELIVERED｜resolver 一字修实录：wave2 resolver 首跑 AttributeError"
    "（bytes.splitlines 产物已 bytes·.encode 冗余）当场抓回零 commit 污染·"
    "重跑即愈（r630 分步提交纪律受益面）｜inbox 处理：0 入站（1 出站 MSG-1332 "
    "在途待 bm-a/bm-b 消费）｜零清扫/归档/删除/恢复类动作轮：登记册零命中断言 "
    "N/A-无此类动作（O-2030 §二.3 自证面）｜轮产品计分：S6 38/38 log"
    "（_r474bmc_s6_log.txt）+池回退定谳证据件（_r474bmc_poolreg.txt 双轮 origin "
    "证据）+MSG-1332 协同件+22/12 UU 双 resolver 件（r466 血统+r675/r656 律补腿）"
    "+自愈实证面（_r474bmc_fundnulls_watch.json 13:40 快照 healthy True×3）"
    "+3 CEO 面 takeover derive+REPORT/LIVE-2026-10-04 再生=可跑/能看实物面"
    "（等待态声明：finalize 窗 10-05 开·N1 关+trio bm-b 属主+板空=零新面孔可烧·非空转）"
)


def main():
    with open(REPORT, "rb") as fh:
        data = fh.read()
    eol = b"\r\n" if b"\r\n" in data[-200:] else b"\n"
    prefix = b"" if data.endswith(b"\n") or data.endswith(b"\r\n") else eol
    with open(REPORT, "ab") as fh:
        fh.write(prefix + LINE.encode("utf-8") + eol)
    with open(REPORT, "rb") as fh:
        back = fh.read()
    assert back.count(LINE.encode("utf-8")) == 1, "S7-close line count != 1"
    print("S7CLOSE_LINE_OK", len(LINE.encode("utf-8")), "bytes")


if __name__ == "__main__":
    main()
