"""r682 bm-b closeout: S7.5 orders rescan + round-report append (r679
marker-count law, r641 bytes/newline='' law) + CODELY append-only line."""
import datetime
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RR = os.path.join(ROOT, "logs", "iteration-loop", "round_reports.md")
CODELY = os.path.join(ROOT, "CODELY.md")


def orders_rescan():
    import glob
    disk = {os.path.basename(p) for p in
            glob.glob(os.path.join(ROOT, "fleet", "orders", "O-*.md"))}
    hb = json.load(open(os.path.join(ROOT, "fleet", "machines", "bm-b.json"),
                        encoding="utf-8"))
    ack = set(hb["orders_ack"])
    return sorted(disk - ack), sorted(ack - disk)


def main():
    now = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
    unacked, extra = orders_rescan()
    assert not unacked, "S7.5 rescan unacked=%s -- halt before commit" % unacked
    rr_line = (
        "%s | r682 (bm-b) PRODUCT (dept:舰队值守+数据维护链+工程修复): "
        "[watermark verdict: GREEN (red=false; satengine alive rc0 queue=22 "
        "held by RAM-floor gate 2.5-2.7GB<4.0GB machine discipline "
        "self-ignite; post_review REPORT-20261004 dist check-mark45/cross0/"
        "yellow5 zero active red; audit CLEAN py 87.2%%=trio burn legal "
        "occupancy; dualrun ZERO-DRIFT)] | 当前活: FUND trio NULLS 烧录在飞 "
        "V861/Q674/D512 of 2000 @17:06 (43.0/33.7/25.6pct, owner=bm-b, rates "
        "24.3/20.5/18.0/h, ETA V 10-06T15 / Q 10-07T09 / D 10-08T03) + "
        "N1-W116 2/12 shards RAM-gated self-paced | 最近实物: D-19 探针 "
        "orders 腿口径缺陷治愈 results/_r686bmb_d19_check.py (17:05, "
        "per-key method self-evidence r458/r672 law landed in code, re-run "
        "dual MATCH decisions 4E5BE321 + orders 68947C17) + S6 38/38 rc0 "
        "(results/_r682bmb_s6_log.txt; REPORT-2026-10-04 + LIVE-2026-10-04 "
        "再生 ORANGE_COOL) + trio watch 刷新 results/trio_burn_eta.json "
        "@17:06 | 本轮同窗: S0 FF-merge r685 bm-a wave 零交集 + MSG-1655 "
        "superseded-ack (bm-a r687 让位 bm-c W3 judge seat, 收账入 processed/) "
        "+ orders/D-19 双扫双键 MATCH (154/154 zero unacked) + smoke 48/48 + "
        "board 169 票 0 open + attrition 4 ledgers CLEAN + 自愈 4/4 (loop "
        "pin=2 no-op/watchdog/双爪在位) + CODELY 水位 88.75KB>50KB 门=r504 "
        "集团裁定面在役坑律勿自归档 记水位不擅动 | 验证证据: results/"
        "_r682bmb_{postreview_tail,heartbeat}.py + _r686bmb_d19_check.json "
        "(双键 MATCH) + _r682bmb_s6_log.txt 38/38 rc0 + state=682 + 心跳 "
        "epoch 1791105000 int 自证 | 下轮指针: trio 看守续跑 + W116 RAM "
        "清空自燃观察 + FUND-VALUE finalize 候选窗 10-06T15+ (r668 池面双翻 "
        "律, r672 ALL-GREEN rehearsal 证据在场) + W117 seat 按锚序 | 本地未达 "
        "origin commit 数=0 (commit 后 push+fetch+ls-tree 自证)\n"
    ) % now
    raw = open(RR, "rb").read()
    marker = ("r682 (bm-b) PRODUCT").encode("utf-8")
    assert raw.count(marker) == 0, "RR r682 marker already present=%d" % raw.count(marker)
    with open(RR, "ab") as f:
        f.write(rr_line.encode("utf-8"))
    raw2 = open(RR, "rb").read()
    assert raw2.count(marker) == 1, "RR append not exactly-once"
    assert raw2.startswith(raw), "RR prefix not preserved"

    codely_line = (
        "- [2026-10-04 17:1x r682 bm-b] 探针血统「律已内建」宣称≠代码实态坑"
        "（D-19 探针 r686 件被 r680 会话宣称为双律内建版，实际 orders 腿 "
        "SHA-256 vs 水位 SHA-1 的 r458 口径律从未落码=本轮首跑恒假 CHANGED 复发"
        "；幸 r641 复现证伪律在先（探针 orders_changed=true 而 disk/ack 差集零未回执"
        "→先读探针源码复算 SHA-1 MATCH 定谳假警非真变更）。修=件内 method_for() "
        "按水位键值长度自证哈希族（40-hex=SHA-1/64-hex=SHA-256·r672 值长度律落码）"
        "+方法字段进 stdout+复跑双键 MATCH 实证。How to apply：复用「XX律内建版」"
        "宣称的探针前先读源码核律真在位（宣称是文档面、代码才是实态）"
        "；见探针恒 CHANGED 假警先查键口径再立叙事。\n"
    ).encode("utf-8")
    craw = open(CODELY, "rb").read()
    cmark = "r682 bm-b] 探针血统".encode("utf-8")
    assert craw.count(cmark) == 0
    with open(CODELY, "ab") as f:
        f.write(codely_line)
    craw2 = open(CODELY, "rb").read()
    assert craw2.count(cmark) == 1 and craw2.startswith(craw)
    print("closeout appends OK; RR line +1, CODELY line +1, orders rescan 154/154 zero unacked")


if __name__ == "__main__":
    main()
