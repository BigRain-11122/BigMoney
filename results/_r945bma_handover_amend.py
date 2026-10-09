# r945 bm-a: amend uncommitted HANDOVER 5x stamp (dead-session draft face) with
# parking burn facts. CRLF preserved, byte-asserts.
import sys

PATH = "research/HANDOVER.md"

A1 = "→r945 本窗=5x 盖章+守望续（S6 39 腿驱动器在飞·receipt 本轮吸收）。"
N1 = ("→r945 本窗=5x 盖章+**PARKING-P1 停泊域首判决批全程收口**（前窗 06:42:14 run 遗产收编："
      "runner selftest 20/20 后继复验+六员面锚逐项恒等〔3,273/797/2,204/1,570/3,266/3,273 行〕"
      "+G1' 线 5.1562 极端值线公式验真+prereg §7/§8 机器回填一次定稿"
      "+RETAIL_QUANT_TRACK §四闸记账 324→348/500；"
      "**判决 0/3 instrument 注册·0/24 格过全链·判负收线=停泊 vehicle 维持 C2 repo 代理**）"
      "+S6 39 腿 rc0 receipt 吸收（06:22-06:26·周六 no-new-bar 面板尾 2026-10-09）。")
A2 = "+state heal 940→942→945 诚实序列（r941 死窗零写）。"
N2 = ("+state heal 940→942→945 诚实序列（r941 死窗零写）+**PARKING-P1 产品族**"
      "（scripts/parking_p1.py probe/gates/run/selftest 四态+results/parking_p1.json "
      "sha16 e8abd5425ff0bf27+research/parking_p1_results.csv"
      "+research/PARKING_P1_PREREG.md §7/§8 回填 17,291→29,515B"
      "+research/RETAIL_QUANT_TRACK.md §四行 348/500"
      "+results/_r945bma_parking_rollwindow.json 滚动窗描述面"
      "+gate_attrition entries[107] 判决行 862,175）。")
A3 = "指针：**PARKING-P1 烧录 due 10-14 12:00（bm-a 车道·SEED_REGISTRY parking_p1_null_base=94_300·watchdog 在节奏）**"
N3 = ("指针：**PARKING-P1 已判负收线**（激活复活条件=复权面板数据债清偿后另开预注册；"
      "B-直池子批待 bm-c 集思录采集器建面≥10-16；"
      "10-21 回访首报数+10-31 月考停泊增益面=零增益如实呈报；"
      "exit-to-asset 工程腿 verdict-gated 不放线）")


def main():
    b = open(PATH, "rb").read()
    assert b[:3] != b"\xef\xbb\xbf", "BOM"
    assert b.count(b"\r\n") == b.count(b"\n"), "newline face"
    text = b.decode("utf-8")
    for a, n in ((A1, N1), (A2, N2), (A3, N3)):
        assert text.count(a) == 1, "anchor not unique: " + a[:30]
        text = text.replace(a, n)
    open(PATH, "wb").write(text.encode("utf-8"))
    b2 = open(PATH, "rb").read()
    assert b2.count(b"\r\n") == b2.count(b"\n") and b2[:3] != b"\xef\xbb\xbf"
    assert "PARKING-P1 已判负收线" in b2.decode("utf-8")
    print("HANDOVER stamp amended:", len(b), "->", len(b2))


if __name__ == "__main__":
    main()
